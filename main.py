# This is A simulation for the Client

import asyncio
import logging
import os
from dotenv import load_dotenv
from MarketManager.MarketManager import MarketManager
from Utils.SolanaRpcApi import SolanaRpcApi

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

load_dotenv()

RPC_KEY = os.getenv('RPC_KEY')

class TokenMonitor:
    def __init__(self, market_manager):
        self.market_manager = market_manager
        self.start_task = None  # Store the start task to keep it running

    async def start_monitoring(self):
        """Start the MarketManager's monitoring process."""
        logging.info("Starting MarketManager monitoring")
        try:
            await self.market_manager.start()  # Run indefinitely
        except asyncio.CancelledError:
            logging.error("MarketManager start task cancelled")
            raise
        except Exception as e:
            logging.error(f"Error in MarketManager.start: {e}")
            raise

    async def add_token(self, token_id: str):
        """Add a token to be monitored by MarketManager."""
        try:
            logging.info(f"Adding token {token_id} to monitor")
            await self.market_manager.monitor_token(token_id)  # Add token to monitoring
        except Exception as e:
            logging.error(f"Error adding token {token_id}: {e}")

    async def status(self):
        """Get the status of MarketManager."""
        try:
            status = self.market_manager.status()
            return status
        except Exception as e:
            logging.error(f"Error fetching status: {e}")
            return None

async def main():
    http_url = f'https://mainnet.helius-rpc.com/?api-key={RPC_KEY}'
    wss_url = f'wss://mainnet.helius-rpc.com/?api-key={RPC_KEY}'

    solana_rpc_api = SolanaRpcApi(http_url, wss_url)
    market_manager = MarketManager(solana_rpc_api)
    monitor = TokenMonitor(market_manager)
 
    # addedd
    async def initiate():
        while True:
            try:
                # Handle input asynchronously to avoid blocking
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "Enter Token To Monitor (or 'status', 'exit'): "
                )
                user_input = user_input.strip()
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'status':
                    await monitor.status()
                else:
                    await monitor.add_token(user_input)
            except Exception as e:
                logging.error(f"Error handling input: {e}")
            logging.info('Adding token to monitor')
            await asyncio.sleep(0.1)  

    monitor.start_task = asyncio.create_task(monitor.start_monitoring())
    input_task = asyncio.create_task(initiate())
    await input_task

    monitor.start_task.cancel()
    try:
        await monitor.start_task 
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main())
    pass