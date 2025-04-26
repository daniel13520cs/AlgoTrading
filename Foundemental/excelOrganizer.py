import pandas as pd
import yfinance as yf

def fetch_quarterly_revenue(ticker: str, years: int = 5):
    stock = yf.Ticker(ticker)
    financials = stock.quarterly_income_stmt.T
    revenue = financials[['Total Revenue']]
    revenue.index = pd.to_datetime(revenue.index)
    
    # Filter for the past 'years' years
    start_date = pd.Timestamp.today() - pd.DateOffset(years=years)
    revenue = revenue[revenue.index >= start_date]
    
    return revenue.sort_index(ascending=True)

def save_to_excel(revenue_data: pd.DataFrame, filename: str):
    revenue_data.to_excel(filename, engine='openpyxl')
    print(f"Saved to {filename}")

if __name__ == "__main__":
    ticker = "IESC"  # IES Holdings ticker symbol
    revenue_data = fetch_quarterly_revenue(ticker)
    save_to_excel(revenue_data, "IES_Holdings_Quarterly_Revenue.xlsx")

