from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from fyers_apiv3 import fyersModel
import webbrowser
import os
import pandas as pd
import datetime
import time

app = Flask(__name__)
CORS(app)

# ==============================================================================
# 👇 YOUR KEYS 👇
# ==============================================================================
client_id = "J3PIUDQS20-100"      # <--- PASTE YOUR ID HERE
secret_key = "8TM69GG411"       # <--- PASTE YOUR SECRET HERE
redirect_uri = "https://stock-scanner-vcza.onrender.com/login"
# ==============================================================================

access_token = None
fyers = None

# --- GLOBAL WATCHLIST STORAGE ---
# This acts as your database for now.
watchlist = ["NSE:NIFTY50-INDEX", "NSE:RELIANCE-EQ", "NSE:HDFCBANK-EQ", "NSE:ZOMATO-EQ"]

# Helper: Calculate RSI manually
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@app.route('/')
def home():
    return "<h1>Server is Running! 🚀</h1><p>Go to <a href='/login'>/login</a> to authenticate.</p>"



@app.route('/login')
def login():
    global fyers, access_token
    auth_code = request.args.get('auth_code')
    if auth_code:
        session = fyersModel.SessionModel(
            client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri,
            response_type="code", grant_type="authorization_code"
        )
        session.set_token(auth_code)
        response = session.generate_token()
        access_token = response['access_token']
        fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path=os.getcwd())
        return "<h1>Login Successful! Server is Ready. You can close this tab.</h1>"
    
    session = fyersModel.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri, response_type="code")
    return redirect(session.generate_authcode())

# --- 1. REMOVE STOCK ENDPOINT ---
@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    global watchlist
    try:
        data = request.json
        symbol_to_remove = data.get('symbol')
        
        # Remove from our global list if it exists
        if symbol_to_remove in watchlist:
            watchlist.remove(symbol_to_remove)
            print(f"Removed: {symbol_to_remove}") # Print to console for verification
            return jsonify({"status": "success", "message": f"{symbol_to_remove} removed"})
        else:
            # Even if not found, return success so UI doesn't break
            return jsonify({"status": "success", "message": "Symbol was not in list"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- 2. GET STOCK DATA ENDPOINT ---
@app.route('/api/stock')
def get_stock():
    global fyers
    symbol = request.args.get('symbol')
    
    if not fyers or not access_token:
        return jsonify({"error": "Login required"}), 401

    try:
        # A. Get Live Price
        quote_data = {"symbols": symbol}
        quote_resp = fyers.quotes(data=quote_data)
        
        if 'd' not in quote_resp or not quote_resp['d']: 
            return jsonify({"error": "Symbol not found"}), 404
        
        stock = quote_resp['d'][0]['v']
        
        # B. Get Historical Data (For RSI)
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=150)
        
        history_data = {
            "symbol": symbol,
            "resolution": "D",
            "date_format": "1",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": today.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }
        
        hist_resp = fyers.history(data=history_data)
        
        rsi_val = 50 
        signal = "WAIT"
        
        if 'candles' in hist_resp:
            df = pd.DataFrame(hist_resp['candles'], columns=['date', 'open', 'high', 'low', 'close', 'vol'])
            df['rsi'] = calculate_rsi(df['close'])
            rsi_val = round(df['rsi'].iloc[-1], 2)
            
            if rsi_val < 30: signal = "BUY"
            elif rsi_val > 70: signal = "SELL"
            else: signal = "HOLD"

        # C. Return COMPLETE Data (Added Open, High, Low)
        return jsonify({
            "symbol": stock.get('short_name', symbol),
            "price": stock.get('lp'),         # Last Price
            "change": stock.get('chp'),       # Change %
            "volume": stock.get('volume'),    # Volume
            "open": stock.get('open_price'),  # <--- Added Open
            "high": stock.get('high_price'),  # <--- Added High
            "low": stock.get('low_price'),    # <--- Added Low
            "rsi": rsi_val,
            "signal": signal
        })

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000/login")

    app.run(port=5000)


