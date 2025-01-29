from API.api import APISwitcher
import time
import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import time
# TradingStrategy: The class that runs the trading strategy and makes decisions based on the API

class TradingStrategy():
    def setAPISwitcher(self,api_switcher: APISwitcher):
        pass
    def run(self, symbol):
        pass

class BaseStrategy():
    def __init__(self, api_switcher: APISwitcher):
        self.api_switcher = api_switcher
    def setAPISwitcher(self, api_switcher: APISwitcher):
        self.api_switcher = api_switcher
        
class BuyLowSellHighStrategy(BaseStrategy):
    def setAPISwitcher(self,api_switcher: APISwitcher):
        self.api_switcher = api_switcher
        
    def calculate_daily_change(self, bars):
        """Calculate percentage change between the open and close prices."""
        if bars is None or bars.empty:
            return None
        latest_bar = bars.iloc[-1]
        return (latest_bar['close'] - latest_bar['open']) / latest_bar['open']  # (close - open) / open

    def run(self, symbol):
        """Run the trading strategy."""
        print("Starting trading strategy...")

        # Fetch historical data
        bars = self.api_switcher.get_historical_data(symbol)
        if bars is None or bars.empty:
            print("Failed to retrieve data.")
            return

        daily_change = self.calculate_daily_change(bars)
        if daily_change is None:
            print("No valid data available.")
            return

        # Check for existing positions (this could be an external check with your broker)
        has_position = False  # Replace this with real check from your API
        
        buy_threshold = -0.05  # 3% price dip
        sell_threshold = 0.10  # 5% price increase
        position_size = 10  # Number of shares to buy
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
    def run(self, symbol):
        self.api_switcher.place_order(symbol, 10, "buy")


class MovingAverageStrategy(BaseStrategy):
    def __init__(self, api_switcher: APISwitcher, short_window=10, long_window=30):
        super().__init__(api_switcher)
        self.short_window = short_window
        self.long_window = long_window

    def run(self, symbol):
        """Run the moving average crossover strategy."""
        print(f"Running Moving Average Strategy for {symbol}...")

        # Fetch historical data
        bars = self.api_switcher.get_historical_data(symbol)
        if bars is None or bars.empty:
            print("Failed to retrieve data.")
            return

        # Calculate moving averages
        bars["SMA_Short"] = bars["close"].rolling(window=self.short_window).mean()
        bars["SMA_Long"] = bars["close"].rolling(window=self.long_window).mean()

        # Ensure we have enough data for the moving averages
        if bars["SMA_Short"].isna().sum() > 0 or bars["SMA_Long"].isna().sum() > 0:
            print("Not enough data to compute moving averages.")
            return

        # Check for existing position
        has_position = self.api_switcher.has_position(symbol)

        # Determine buy/sell signal
        latest = bars.iloc[-1]
        previous = bars.iloc[-2]
        position_size = 10
        if previous["SMA_Short"] <= previous["SMA_Long"] and latest["SMA_Short"] > latest["SMA_Long"]:
            if not has_position:
                print(f"Golden Cross detected. Buying {position_size} shares of {symbol}.")
                self.api_switcher.place_order(symbol, position_size, "buy")

        elif previous["SMA_Short"] >= previous["SMA_Long"] and latest["SMA_Short"] < latest["SMA_Long"]:
            if has_position:
                print(f"Death Cross detected. Selling {position_size} shares of {symbol}.")
                self.api_switcher.place_order(symbol, position_size, "sell")

        print("Strategy execution completed.")