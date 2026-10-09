#Fetch necessary libraries
import ccxt
import os
import psycopg
from dotenv import load_dotenv
from datetime import datetime, timezone

#Load envs
load_dotenv()

#Build connection
connection = ccxt.binance({
    'API': os.getenv("BINANCE_API_KEY"),
    "API_SECRET": os.getenv("BINANCE_API_SECRET_KEY"),
    "enableRateLimit": True ,
})

try: 
    ohlcv = connection.fetch_ohlcv(
        "BTC/USDT",
        timeframe="2h",
        limit=500
    )
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
    ) as db:
        with db.cursor() as cur:
            for candle in ohlcv:
                timestamp, open_, high, low, close, volume = candle
                candle_time = datetime.fromtimestamp(
                    timestamp / 1000,
                    tz=timezone.utc
                )
                cur.execute (
                    """INSERT INTO ohlcv(symbol, timeframe, candle_time, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timeframe, candle_time)
                    DO NOTHING""",
                    ("BTC/USDT",
                        "2h",
                        candle_time,
                        open_,
                        high,
                        low,
                        close,
                        volume,
                    )
                )
    print(f"Fetched {len(ohlcv)} candles.")
    print("Candles saved to PostgreSQL.")

except Exception as e:
    print(f"Error: {e}")