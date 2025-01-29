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
        start_date = (datetime.datetime.now() - datetime.timedelta(days=100)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        data_file = f"{symbol}_historical_data.csv"

        # Load existing data if available
        if os.path.exists(data_file):
            print(f"Loading existing data from {data_file}...")
            bars = pd.read_csv(data_file, index_col="timestamp", parse_dates=True)

            # Find the latest available date
            last_available_date = bars.index[-1].date()
            if last_available_date >= end_date:
                print("Data is already up to date.")
                return bars  # No need to fetch new data

            # Fetch missing data from the last available date
            fetch_start = last_available_date + datetime.timedelta(days=1)
        else:
            bars = None
            fetch_start = start_date  # Fetch from the start if no existing data

        # Fetch only missing data
        try:
            new_bars = self.api.get_bars(
                symbol,
                '1Day',  # Use daily time frame
                start=fetch_start,
                end=end_date
            ).df  # Converts the returned data to a pandas DataFrame

            if new_bars.empty:
                print("No new data to append.")
                return bars

            # Append new data and save
            new_bars.index = pd.to_datetime(new_bars.index)  # Ensure index is datetime
            if bars is not None:
                updated_bars = pd.concat([bars, new_bars]).drop_duplicates()
            else:
                updated_bars = new_bars

            updated_bars.to_csv(data_file)
            print(f"Updated historical data saved to {data_file}.")
            return updated_bars

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return bars

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
