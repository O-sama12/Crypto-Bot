import pandas as pd
import numpy as np
import os
import psycopg
from dotenv import load_dotenv
load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
}
SYMBOL = "BTC/USDT"
TIMEFRAME = "2h"
query = """
        SELECT candle_time, open, high, low, close, volume
        FROM ohlcv
        WHERE symbol = %s AND timeframe = %s
        ORDER BY candle_time ASC;
    """
with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (SYMBOL, TIMEFRAME))
            rows = cur.fetchall()
            columns = [column.name for column in cur.description]

df = pd.DataFrame(rows, columns=columns)
if df.empty:
     raise ValueError(
            f"No candles found for {SYMBOL} at {TIMEFRAME}."
        )

numeric_columns = ["open", "high", "low", "close", "volume"]
df[numeric_columns] = df[numeric_columns].astype(float)
df["return_1"] = df["close"].pct_change()
df["sma_20"] = df["close"].rolling(window=20).mean()
df["sma_distance"] = (df["close"] - df["sma_20"]) / df["sma_20"]
df["volatility_20"] = df["return_1"].rolling(window=20).std()
df["volume_sma_20"] = df["volume"].rolling(window=20).mean()
next_close = df["close"].shift(-1)
df["target"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
valid_next = next_close.notna()
df.loc[valid_next, "target"] = (
    next_close[valid_next] > df.loc[valid_next, "close"]
).astype("int64")
print(df[["close", "target"]].tail(3))
print("Last target:", df["target"].iloc[-1])
df["relative_volume_20"] = df["volume"] / df["volume_sma_20"]
feature_columns = [
    "return_1",
    "sma_20",
    "volatility_20",
    "relative_volume_20",
    "sma_distance",
]

df = df.dropna(subset=feature_columns + ["target"]).copy()
print("Dataset shape:", df.shape)
print(df[feature_columns + ["target"]].head())
print(df["target"].value_counts())