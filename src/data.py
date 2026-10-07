"""Download and cache ETF adjusted closes."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from src.config import DATA_DIR, END, START, TICKERS


def download_prices(force: bool = False) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stable = DATA_DIR / "etf_prices.csv"
    if stable.exists() and not force:
        px = pd.read_csv(stable, index_col=0, parse_dates=True)
        cols = [c for c in TICKERS if c in px.columns]
        if len(cols) == len(TICKERS):
            return px[TICKERS].dropna(how="any")

    frames = []
    for t in TICKERS:
        df = yf.download(t, start=START, end=END, auto_adjust=True, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            s = df[("Close", t)] if ("Close", t) in df.columns else df["Close"].iloc[:, 0]
        else:
            s = df["Close"]
        s.name = t
        frames.append(s)
    px = pd.concat(frames, axis=1).dropna(how="any").sort_index()
    stamp = pd.Timestamp.utcnow().strftime("%Y%m%d")
    px.to_csv(DATA_DIR / f"etf_prices_{stamp}.csv")
    px.to_csv(stable)
    (DATA_DIR / "download_meta.txt").write_text(
        f"downloaded_utc={pd.Timestamp.utcnow().isoformat()}\nrows={len(px)}\nstart={px.index.min()}\nend={px.index.max()}\n"
    )
    return px


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    import numpy as np

    return np.log(prices / prices.shift(1)).dropna(how="any")
