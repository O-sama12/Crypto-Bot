import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

exchange = ccxt.binance({
    "apiKey": os.getenv("BINANCE_API_KEY"),
    "secret": os.getenv("BINANCE_API_SECRET_KEY"),
    "enableRateLimit": True,
})

try:
    balance = exchange.fetch_balance()

    print("Connected to Binance successfully!")

    print("\nUSDT Balance:")
    print("Free:", balance["USDT"]["free"])
    print("Used:", balance["USDT"]["used"])
    print("Total:", balance["USDT"]["total"])
    print("Other balances:")
    for currency, data in balance["total"].items():
       if data >= 0:
           print(currency, data) 

except ccxt.AuthenticationError:
    print("Authentication failed. Check your API key and secret.")

except Exception as e:
    print("Error:", e)
