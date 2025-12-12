import os
import time
from datetime import date

# Get today's date for the log
today = date.today().strftime("%Y-%m-%d")

print("==================================================")
print(f"   🚀 STARTING DAILY STOCK SCAN: {today}")
print("==================================================")

# 1. Update the Database (Fetch Prices)
print("\n[STEP 1/3] Downloading latest prices...")
exit_code = os.system("python fetch_prices.py")

if exit_code != 0:
    print("❌ Error: Download failed. Please check your internet or script.")
    exit()

# 2. Analyze the Market (Find Trades)
print("\n[STEP 2/3] Scanning for Buy Signals...")
exit_code = os.system("python analyze_stocks.py")

if exit_code != 0:
    print("❌ Error: Analysis crashed. Check analyze_stocks.py for typos.")
    exit()

# 3. Push to GitHub (Go Live)
print("\n[STEP 3/3] Uploading Results to GitHub...")

# Add all changes
os.system("git add .")

# Commit with a dynamic message
commit_message = f"Daily Update: {today}"
os.system(f'git commit -m "{commit_message}"')

# Push to the cloud
os.system("git push")

print("\n==================================================")
print("   ✅ SUCCESS! Your Website is now UPDATED.")
print("   See the results live on your Render App.")
print("==================================================")