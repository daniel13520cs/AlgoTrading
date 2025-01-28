import datetime
import time
import os
import pandas as pd
from abc import ABC, abstractmethod
from alpaca_trade_api.rest import REST
import config

# APISwitcher: The class responsible for switching between different APIs
class APISwitcher(ABC):
    @abstractmethod
    def get_historical_data(self, symbol):
        pass

    @abstractmethod
    def calculate_daily_change(self, bars):
        pass

    @abstractmethod
    def place_order(self, symbol, qty, side):
        pass


# Alpaca API Implementation
class AlpacaAPI(APISwitcher):
    def __init__(self, api):
        self.api = api  # The Alpaca API client

    def get_historical_data(self, symbol):
        return
        """Fetch historical data using Alpaca's free API calls or load from file if it exists."""
        DATA_FILE = f"{symbol}_historical_data.csv"  # File to save the data

        # Check if the data file exists
        if os.path.exists(DATA_FILE):
            print(f"Loading data from {DATA_FILE}...")
            bars = pd.read_csv(DATA_FILE, index_col="timestamp", parse_dates=True)
            return bars
        else:
            # Define the start and end date for the data
            start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).date()
            end_date = datetime.datetime.now().date()

            try:
                # Fetch historical data using Alpaca's get_bars method
                bars = self.api.get_bars(
                    symbol,
                    'day',  # Use daily time frame
                    start=start_date,
                    end=end_date
                ).df  # Converts the returned data to a pandas DataFrame

                # Save the data to a CSV file for future use
                bars.to_csv(DATA_FILE)
                print(f"Historical data saved to {DATA_FILE}.")
                return bars
            except Exception as e:
                print(f"Error fetching historical data: {e}")
                return None

    def calculate_daily_change(self, bars):
        return
        """Calculate percentage change between the open and close prices."""
        if bars is None or bars.empty:
            return None
        latest_bar = bars.iloc[-1]
        return (latest_bar['c'] - latest_bar['o']) / latest_bar['o']  # (close - open) / open

    def place_order(self, symbol, qty, side):
        """Place a market order."""
        try:
            self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type="market",
                time_in_force="gtc",
            )
            print(f"Order placed: {side} {qty} shares of {symbol}.")
        except Exception as e:
            print(f"Error placing order: {e}")


# TradingStrategy: The class that runs the trading strategy and makes decisions based on the API
class TradingStrategy():
    def setAPISwitcher(self,api_switcher: APISwitcher):
        pass
    def run(self, symbol, buy_threshold, sell_threshold, position_size):
        pass

class BaseStrategy():
    def __init__(self, api_switcher: APISwitcher):
        self.api_switcher = api_switcher
    def setAPISwitcher(self, api_switcher: APISwitcher):
        self.api_switcher = api_switcher
        
class BuyLowSellHighStrategy(BaseStrategy):
    def __init__(self, api_switcher: APISwitcher):
        self.api_switcher = api_switcher

    def setAPISwitcher(self,api_switcher: APISwitcher):
        self.api_switcher = api_switcher

    def run(self, symbol, buy_threshold, sell_threshold, position_size):
        """Run the trading strategy."""
        print("Starting trading strategy...")

        # Fetch historical data
        bars = self.api_switcher.get_historical_data(symbol)
        if bars is None or bars.empty:
            print("Failed to retrieve data.")
            return

        daily_change = self.api_switcher.calculate_daily_change(bars)
        if daily_change is None:
            print("No valid data available.")
            return

        # Check for existing positions (this could be an external check with your broker)
        has_position = False  # Replace this with real check from your API
        
        # Buy condition: Price dipped by the threshold
        if daily_change < buy_threshold and not has_position:
            print(f"Buying {position_size} shares of {symbol}.")
            self.api_switcher.place_order(symbol, position_size, "buy")

        # Sell condition: Price increased by the threshold
        elif daily_change > sell_threshold and has_position:
            print(f"Selling {position_size} shares of {symbol}.")
            self.api_switcher.place_order(symbol, position_size, "sell")

        # Wait before checking again (e.g., wait for the next day to run strategy again)
        print("Waiting for the next check...")
        time.sleep(86400)  # Wait 24 hours


class SimpleStrategy(BaseStrategy):
    def run(self, symbol, buy_threshold, sell_threshold, position_size):
        self.api_switcher.place_order(symbol, position_size, "buy")


# Main function to run the strategy
def main():
    # Example API client (replace with actual Alpaca API client or another broker's client)
    API_KEY = config.ALPACA_API_KEY
    SECRET_KEY = config.ALPACA_API_SECRET
    BASE_URL = "https://paper-api.alpaca.markets"
    alpaca_api_client = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

    # Initialize the Alpaca API
    alpaca_api = AlpacaAPI(alpaca_api_client)
    strategy = SimpleStrategy(alpaca_api)  # Use Alpaca API

    # Strategy parameters
    SYMBOL = "NVDA"  # Stock symbol to trade
    BUY_THRESHOLD = -0.03  # 3% price dip
    SELL_THRESHOLD = 0.05  # 5% price increase
    POSITION_SIZE = 10  # Number of shares to buy

    # Run the strategy
    strategy.run(SYMBOL, BUY_THRESHOLD, SELL_THRESHOLD, POSITION_SIZE)

if __name__ == "__main__":
    main()
