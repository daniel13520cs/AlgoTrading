
from alpaca_trade_api.rest import REST
import config
from API.api import AlpacaAPI
from TradingStrategy.strategy import *


# Main function to run the strategy
def main():
    # Example API client (replace with actual Alpaca API client or another broker's client)
    API_KEY = config.ALPACA_PAPER_API_KEY
    SECRET_KEY = config.ALPACA_PAPER_API_SECRET
    BASE_URL = "https://paper-api.alpaca.markets"
    alpaca_api_client = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

    # Initialize the Alpaca API
    alpaca_api = AlpacaAPI(alpaca_api_client)
    strategy = BuyLowSellHighStrategy(alpaca_api)  # Use Alpaca API

    # Strategy parameters
    SYMBOL = "NVDA"  # Stock symbol to trade

    # Run the strategy
    strategy.run(SYMBOL)

if __name__ == "__main__":
    main()
