import schedule
import time
from datetime import datetime
from alpaca_trade_api.rest import REST
import config
from API.api import AlpacaAPI
from TradingStrategy.strategy import *


# Function to check if the market is open
def is_market_open(alpaca_api_client):
    clock = alpaca_api_client.get_clock()
    return clock.is_open


# Function to execute trading strategy
def run_strategy():
    API_KEY = config.ALPACA_PAPER_API_KEY
    SECRET_KEY = config.ALPACA_PAPER_API_SECRET
    BASE_URL = "https://paper-api.alpaca.markets"
    
    alpaca_api_client = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")
    
    # Check if the market is open before proceeding with strategy
    if not is_market_open(alpaca_api_client):
        print("Market is closed or it's a holiday. Skipping trade.")
        return

    alpaca_api = AlpacaAPI(alpaca_api_client)
    strategy = BuyLowSellHighStrategy(alpaca_api)  # Use Alpaca API

    SYMBOL = "NVDA"
    strategy.run(SYMBOL)


# Schedule the strategy to run every weekday at 05:30 Pacific Time/9:30 AM ET
schedule.every().monday.at("05:30").do(run_strategy)
schedule.every().tuesday.at("05:30").do(run_strategy)
schedule.every().wednesday.at("05:30").do(run_strategy)
schedule.every().thursday.at("05:30").do(run_strategy)
schedule.every().friday.at("05:30").do(run_strategy)


# Keep the script running
if __name__ == "__main__":
    print("Waiting for market open...")

    while True:
        print(datetime.datetime.now())
        schedule.run_pending()
        time.sleep(2)  # Check schedule every 30 seconds
