from abc import ABC, abstractmethod
import os
import datetime
import pandas as pd

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
        """Fetch historical data using Alpaca's free API calls or load from file if it exists."""
        DATA_FILE = f"{symbol}_historical_data.csv"  # File to save the data

        # Check if the data file exists
        if os.path.exists(DATA_FILE):
            print(f"Loading data from {DATA_FILE}...")
            bars = pd.read_csv(DATA_FILE, index_col="timestamp", parse_dates=True)
            return bars
        else:
            # Define the start and end date for the data
            start_date = (datetime.datetime.now() - datetime.timedelta(days=100)).date()
            end_date = (datetime.datetime.now() - datetime.timedelta(days=30)).date()

            try:
                # Fetch historical data using Alpaca's get_bars method
                bars = self.api.get_bars(
                    symbol,
                    '1Day',  # Use daily time frame
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
        """Calculate percentage change between the open and close prices."""
        if bars is None or bars.empty:
            return None
        latest_bar = bars.iloc[-1]
        return (latest_bar['close'] - latest_bar['open']) / latest_bar['open']  # (close - open) / open

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
