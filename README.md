## Market Manager

The **Market Manager** is one of the core component of the trading bot, designed to monitor real-time price movements of cryptocurrency tokens asynchronously using WebSocket connections. It ensures efficient tracking of market conditions to align with user-defined trading strategies.

### Features

- **Token Acceptance**: Accepts one or more cryptocurrency tokens (Raydium Tokens contracts) for price monitoring.
- **Real-Time Price Monitoring**: Utilizes WebSocket connections to receive live price updates ( Use Solana websocket connection)
- **Asynchronous Operation**: Handles multiple tokens concurrently using non-blocking I/O, ensuring scalability and performance.
- **Strategy Alignment**: Monitors token prices to match user-defined trading strategies (e.g., buy/sell at specific price thresholds ). 
- **Reliability**: Manages WebSocket disconnections, network latency, and API rate limits with automatic reconnection and fallback mechanisms.( Websocket is prefered to Normal API Call due to Rate Limit challenge)

### How It Works

1. **Initialization**: Receives token(s) 
2. **WebSocket Connection**: Establishes WebSocket connections to the (solana websocket Rpc for tracking of pool changes which is used to Calculate the token Price)
3. **Real-Time Monitoring**: Asynchronously processes incoming price data, maintaining an internal state.
5. **Multi-Token Support**: Manages multiple tokens in parallel, ensuring independent and efficient monitoring of each token's price feed.
6. **Error Handling**: Automatically reconnects on WebSocket failures, logs errors, and optionally falls back to REST API polling.

### TO DO
1. **Strategy Evaluation**: Compares market data against the user's strategy, triggering actions (e.g., trade execution notifications) when conditions are met.
   
