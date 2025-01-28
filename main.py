import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import time
import config 

# Alpaca API credentials
API_KEY = config.ALPACA_API_KEY
SECRET_KEY = config.ALPACA_API_SECRET
BASE_URL = "https://paper-api.alpaca.markets"  # Use the paper trading URL

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

# Strategy parameters
SYMBOL = "AAPL"  # Stock symbol to trade
BUY_THRESHOLD = -0.03  # 3% price dip
SELL_THRESHOLD = 0.05  # 5% price increase
POSITION_SIZE = 10  # Number of shares to buy

def get_historical_data(symbol):
    """Fetch historical stock data."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    barset = api.get_barset(symbol, "day", start=start_date.isoformat(), end=end_date.isoformat())
    bars = barset[symbol]
    return bars

def calculate_daily_change(bars):
    """Calculate percentage change between the open and close prices."""
    if not bars:
        return None
    latest_bar = bars[-1]
    return (latest_bar.c - latest_bar.o) / latest_bar.o  # (close - open) / open

def place_order(symbol, qty, side):
    """Place a market order."""
    try:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type="market",
            time_in_force="gtc",
        )
        print(f"Order placed: {side} {qty} shares of {symbol}.")
    except Exception as e:
        print(f"Error placing order: {e}")

def run_strategy():
    """Main function to run the trading strategy."""
    print("Starting trading strategy...")
    while True:
        # Fetch historical data and calculate price change
        bars = get_historical_data(SYMBOL)
        daily_change = calculate_daily_change(bars)

        if daily_change is None:
            print("No data available.")
            time.sleep(60)
            continue

        # Check for existing positions
        positions = api.list_positions()
        has_position = any(pos.symbol == SYMBOL for pos in positions)

        # Buy condition: Price dipped by the threshold
        if daily_change < BUY_THRESHOLD and not has_position:
            print(f"Buying {POSITION_SIZE} shares of {SYMBOL}.")
            place_order(SYMBOL, POSITION_SIZE, "buy")

        # Sell condition: Price increased by the threshold
        elif daily_change > SELL_THRESHOLD and has_position:
            print(f"Selling {POSITION_SIZE} shares of {SYMBOL}.")
            place_order(SYMBOL, POSITION_SIZE, "sell")

        # Wait before checking again
        print("Waiting for the next check...")
        time.sleep(300)  # Wait 5 minutes

# Run the strategy
if __name__ == "__main__":
    run_strategy()
