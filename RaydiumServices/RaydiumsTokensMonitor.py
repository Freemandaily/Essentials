import asyncio
import json
import logging
import time
import aiohttp
import websockets
import Utils.SolanaRpcApi
import Utils.Globals as globals
from pubsub import pub
import Utils.TokensApi as TokensApi
from Utils.SolanaRpcApi import SolanaRpcApi


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s : %(message)s"
)


class RaydiumTokensMonitor:
    def __init__(self,solana_rpc_api:SolanaRpcApi):
        self.token_infos = {} 
        self.updated_tokens = set()
        self.solana_rpc_api = solana_rpc_api
        self.wsocket = None
    
    def get_token_info(self,token_address):
        if token_address in self.token_infos:
            if token_address in self.updated_tokens:
                self._update_price(token_address)
                self._update_marketCap(token_address)
                self.updated_tokens.remove(token_address)
                token_info = self.token_infos[token_address]
                return token_info
    
    # Note This MarketCap is In Sol . To Get The MarketCap In USD Multiply The Updated Price with The Price Of Sol
    def _update_marketCap(self,token_address:str):
        if token_address in self.token_infos:
            token_supply = self.token_infos[token_address].token_supply
            updated_price = self.token_infos[token_address].price
            self.token_infos[token_address].marketCap = float(token_supply) * float(updated_price)

    def _update_price(self,token_address:str):
        if token_address in self.token_infos:
            sol_vault_address = self.token_infos[token_address].vault_sol_address
            sol_balance = self.solana_rpc_api.get_account_balance(sol_vault_address)
            token_info = self.token_infos[token_address]

            if sol_balance : # Add condition to check that the token_info.token_vault_ui_amount > 0
                sol_balance /= 1e9
                token_info = self.token_infos[token_address]

                token_info.price =  sol_balance/token_info.token_vault_ui_amount
               
    async def monitor_token(self,token_address:str):
        logging.info('Token Monitoring Mode Activated!!')
        while True:
            if self.wsocket:
                if token_address in self.token_infos:
                    token_info = self.token_infos[token_address]
                else:
                    token_info =  TokensApi.get_amm_token_pool_data(token_address)

                    # Adding TokenSupply to the Token Info
                    token_supply = self.solana_rpc_api.get_total_supply(token_address)
                    if token_supply:
                        if token_info:
                            token_info.token_supply = token_supply

                    if token_info:
                        self.token_infos[token_address] = token_info
                    else:
                        return
                
                request =  self.solana_rpc_api.get_account_subscibe_request(token_info.vault_token_address)

                jsonRequest = json.dumps(request)

                await self.wsocket.send(jsonRequest)
                break
            
            await asyncio.sleep(2)
    async def main(self):
        await asyncio.create_task(self._read_socket())

    async def _read_socket(self):
        while True:
            try:
                async with websockets.connect(self.solana_rpc_api.wss_url) as websocket:
                    self.wsocket = websocket
                   
                    token_addresses = list(self.token_infos.keys())
                    
                    for token_address in token_addresses:
                        await self.monitor_token(token_address)

                    try:
                        while True:

                            recieved = await websocket.recv()
                            json_data = json.loads(recieved)
                            self._process(json_data)
                    except TimeoutError as e:
                        logging.error('Error' +   str(e))
            except Exception as e:
                logging.error('Error' + str(e))

    def _process(self,data: dict):
        params = data.get('params',None)

        if params:
            parsed_info = params['result']['value']['data']['parsed']['info']

            token_address = parsed_info['mint']
            token_ui_amount = parsed_info['tokenAmount']['uiAmount']

            token_info = self.token_infos[token_address]
            token_info.token_vault_ui_amount = token_ui_amount

            self.updated_tokens.add(token_address)
            
            pub.sendMessage(topicName=globals.topic_token_update_event,arg1=token_address)
        else:
            pass
            