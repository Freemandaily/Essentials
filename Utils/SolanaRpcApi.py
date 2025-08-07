import aiohttp
import requests
from jsonrpcclient import request,parse,Ok,Error


class SolanaRpcApi:
    def __init__(self,rpc_url,wss_url):
        self.rpc_url = rpc_url
        self.wss_url = wss_url

    def run_rpc_method(self,request_name:str,params):
        json_request = request(request_name,params=params)
        response = requests.post(self.rpc_url,json=json_request)

        parsed = parse(response.json())

        if isinstance(parsed,Error):
            return None
        else:
            return parsed
       
    def get_account_balance(self,account_address:str):
        response =   self.run_rpc_method('getBalance',[account_address])
        
        if response:
            return response.result['value']
        
    def get_total_supply(self,token_address:str):
        response = self.run_rpc_method('getTokenSupply',[token_address])
        if response:
            return response.result['value']['uiAmount']
    
    @staticmethod # Research on this
    def get_account_subscibe_request(account_address:str):
        return {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "accountSubscribe",
                "params": [
                    account_address,
                    {
                    "encoding": "jsonParsed",
                    "commitment": "finalized"
                    }
                ]
                }
    

