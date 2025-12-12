import pandas as pd
import numpy as np

# --- CONFIGURATION ---
SIGNAL_MA = 61          # 61 SMA Crossover
RSI_MIN = 55            # RSI Bottom
RSI_MAX = 65            # RSI Top
TREND_LONG = 200        # Price > 200 SMA
TREND_SHORT = 50        # Price > 50 SMA
MIN_VOLUME = 50000      # Liquidity

print("--- STARTING MASTER SCAN (ROBUST MODE) ---")

# 1. Helper: RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 2. Load Data
try:
    print("Loading database...", end=" ")
    df = pd.read_csv("all_stock_data.csv")
    df.columns = [c.strip() for c in df.columns] 
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    df = df.sort_values(by=['Symbol', 'Date'])
    
    # --- THE CRITICAL FIX: Convert Columns to Numbers ---
    cols_to_fix = ['Close', 'Open', 'High', 'Low', 'Volume']
    for col in cols_to_fix:
        # 1. Force to string first
        df[col] = df[col].astype(str)
        # 2. Remove commas (e.g. "1,200" -> "1200")
        df[col] = df[col].str.replace(',', '')
        # 3. Convert to number (Coerce errors to NaN)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    print("Done & Cleaned.")
    
except FileNotFoundError:
    print("Error: 'all_stock_data.csv' not found.")
    exit()

# 3. Analysis Logic
def check_strategies(stock_df):
    if len(stock_df) < 200: return None, None

    closes = stock_df['Close']
    
    # Calculate MAs
    ma_signal = closes.rolling(window=SIGNAL_MA).mean()
    ma_200 = closes.rolling(window=TREND_LONG).mean()
    ma_50 = closes.rolling(window=TREND_SHORT).mean()
    rsi = calculate_rsi(closes)
    
    # Get Today values
    today_close = closes.iloc[-1]
    today_rsi = rsi.iloc[-1]
    today_200 = ma_200.iloc[-1]
    today_50 = ma_50.iloc[-1]
    today_vol = stock_df['Volume'].iloc[-1]
    
    # Get Yesterday values
    prev_close = closes.iloc[-2]
    prev_signal_ma = ma_signal.iloc[-2]
    cur_signal_ma = ma_signal.iloc[-1]

    # Skip NaN
    if pd.isna(today_rsi) or pd.isna(today_200): return None, None

    # Volume Filter
    if today_vol < MIN_VOLUME: return None, None

    # --- LOGIC 1: BUY SIGNAL ---
    signal_result = None
    crossed = (prev_close < prev_signal_ma) and (today_close > cur_signal_ma)
    rsi_ok = (today_rsi >= RSI_MIN) and (today_rsi <= RSI_MAX)
    
    if crossed and rsi_ok:
        signal_result = {
            'Symbol': stock_df['Symbol'].iloc[-1],
            'Close': today_close,
            'Type': 'Buy Signal',
            'RSI': round(today_rsi, 2)
        }

    # --- LOGIC 2: UPTREND ---
    trend_result = None
    if (today_close > today_200) and (today_close > today_50):
        trend_result = {
            'Symbol': stock_df['Symbol'].iloc[-1],
            'Close': today_close,
            'SMA_50': round(today_50, 2),
            'SMA_200': round(today_200, 2)
        }

    return signal_result, trend_result

# 4. Run Scan
buy_signals = []
watchlist = []
grouped = df.groupby('Symbol')
total = len(grouped)

print(f"Scanning {total} stocks...")

for i, (symbol, stock_data) in enumerate(grouped):
    if i % 100 == 0: print(f"Scanning... [{i}/{total}]", end="\r")
    try:
        sig, trend = check_strategies(stock_data)
        if sig: buy_signals.append(sig)
        if trend: watchlist.append(trend)
    except: continue

print(f"Scanning... [{total}/{total}] - Done!      ")

# 5. Save Results
print("\n" + "="*40)
print(f"RESULTS REPORT")
print("="*40)

if buy_signals:
    df_sig = pd.DataFrame(buy_signals)
    df_sig.to_csv("buy_signals.csv", index=False)
    print(f" [!] FOUND {len(df_sig)} BUY SIGNALS")
    print(df_sig.to_string(index=False))
else:
    print(" [ ] No Buy Signals found today.")

print("-" * 40)

if watchlist:
    df_watch = pd.DataFrame(watchlist)
    df_watch.to_csv("uptrend_watchlist.csv", index=False)
    print(f" [i] Found {len(df_watch)} stocks in Strong Uptrend")
    print(f"     (Top 5 examples)")
    print(df_watch.head().to_string(index=False))
else:
    print(" [ ] No Uptrend stocks found.")