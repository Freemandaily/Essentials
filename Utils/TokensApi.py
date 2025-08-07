import asyncio
import sys
import aiohttp
import requests
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


class TokenInfo:
    def __init__(self,token_address):
        self.token_address = token_address
        self.market_id = ''
        self.price = ''
        self.token_supply = 0
        self.marketCap = 0
        self.token_vault_ui_amount = 0
        self.vault_sol_address = ''  # used for getting the price by querying the  balance
        self.vault_token_address = '' # used for getting the price by querying the  balance

def _get_request(request_url:str)->dict:

    response = requests.get(request_url)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

def get_amm_token_pool_data(token_address)-> TokenInfo:
    ray_url = "https://api-v3.raydium.io/pools"
    ray_url_market_id_url = ray_url + "/info/mint?mint1=" + token_address + "&poolType=standard&poolSortField=default&sortType=desc&pageSize=1&page=1"
   
    # Make API Call
    data =  _get_request(ray_url_market_id_url)



    if len(data) > 0:
        try:
           token_info = TokenInfo(token_address)

           token_info.market_id = data['data']['data'][0]['id']
           token_info.price = data['data']['data'][0]['price']

           if float(token_info.price) > 2:
               token_info.price = 1/float(token_info.price)
            
           # Requesting for Vault Addresses (Will Be Used Later To Calculate Token Prices By Quering Their Balances)
           vault_address_url = 'https://api-v3.raydium.io/pools/key/ids?ids=' + token_info.market_id
           data =  _get_request(vault_address_url)

           if len(data) > 0:
               mintAddressA = data['data'][0]['mintA']['address']
               vaultA = data['data'][0]['vault']['A']
               vaultB = data['data'][0]['vault']['B']

               if mintAddressA == token_address:
                   token_info.vault_token_address = vaultA
                   token_info.vault_sol_address = vaultB
               else:
                   token_info.vault_sol_address = vaultA
                   token_info.vault_token_address = vaultB
    
               return token_info

           return token_info
        except Exception as e:
            logging.error(f'Error in TokenAPI! {e}')
