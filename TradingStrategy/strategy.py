from API.api import APISwitcher
import time
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
