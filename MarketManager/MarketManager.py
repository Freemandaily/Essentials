import asyncio
import logging
import Utils.TokensApi as TokensApi
import Utils.TokensApi as TokensApi
import Utils.Globals as globals
from RaydiumServices.RaydiumsTokensMonitor import RaydiumTokensMonitor
from Utils.TokensApi import TokenInfo
from Utils.SolanaRpcApi import SolanaRpcApi
from pubsub import pub

logging.basicConfig(
    level=logging.INFO,
    format='%(acstime)s [ %(LevelName)s] %(message)s'
)

# Manage the token market activites
class MarketManager:
   def __init__(self,solana_rpc_api:SolanaRpcApi):
        self.ray_pool_monitor = RaydiumTokensMonitor(solana_rpc_api)
        pub.subscribe(topicName=globals.topic_token_update_event,listener= self._handle_token_update)

    
   def status(self):
       status = self.ray_pool_monitor.token_infos

       token_info = list(status.keys())[0]
       price = self.ray_pool_monitor.token_infos[token_info].price
       return price
   
   def get_price(self,token_address:str):
        token_info =   self.ray_pool_monitor.get_token_info(token_address)

        if token_info:
            return token_info.price,token_info.marketCap
        else:
            logging.info('No Token Info! Adding Token')
            lp_data =  TokensApi.get_amm_token_pool_data(token_address)

            return lp_data.price

   async def monitor_token(self,token_address):
       await self.ray_pool_monitor.monitor_token(token_address)

   def _handle_token_update(self,arg1):
        new_price,new_marketCap =  self.get_price(arg1) # arg1 is the Token_Addresss

        new_price_string = f"{new_price:.20f}"
        logging.info(f" {arg1}  Updated! Price  {new_price_string}")
        logging.info(f" {arg1}  Updated! marketCap  {new_marketCap}")

   async def start(self):
       await self.ray_pool_monitor.main()
       
