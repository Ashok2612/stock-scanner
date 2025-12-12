import pandas as pd
import mplfinance as mpf

# --- CONFIGURATION ---
SYMBOL = "ABB"          # Let's check ABB from your result list
DAYS_TO_SHOW = 100      # Zoom in on the last 100 days
MA_PERIOD = 61          # Your logic

try:
    # 1. Load Data
    df = pd.read_csv("all_stock_data.csv")
    
    # 2. Filter for the specific stock
    stock_df = df[df['Symbol'] == SYMBOL].copy()
    
    # 3. Prepare Data for Plotting (Needs specific Index)
    stock_df['Date'] = pd.to_datetime(stock_df['Date'], format='%d-%m-%Y')
    stock_df = stock_df.set_index('Date')
    stock_df = stock_df.sort_index()
    
    # Take only the recent history
    recent_data = stock_df.tail(DAYS_TO_SHOW)
    
    # 4. Calculate the 61 SMA for the chart
    # (We calculate it on the full data first to be accurate, then slice)
    stock_df['MA_61'] = stock_df['Close'].rolling(window=MA_PERIOD).mean()
    ma_line = stock_df['MA_61'].tail(DAYS_TO_SHOW)

    # 5. Plot
    print(f"Generating chart for {SYMBOL}...")
    
    # Create the plot with the Moving Average line
    mpf.plot(
        recent_data,
        type='candle',
        style='charles',
        title=f"{SYMBOL} - Swing Trade Setup (61 SMA)",
        ylabel='Price (INR)',
        volume=True,
        mav=(MA_PERIOD), # This automatically draws the MA line
        savefig=f"{SYMBOL}_chart.png" # Saves the image instead of opening it
    )
    
    print(f"Success! Chart saved as: {SYMBOL}_chart.png")
    print("Check your file explorer to see it!")

except Exception as e:
    print("Error:", e)