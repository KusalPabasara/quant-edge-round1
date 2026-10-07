"""Download and cache ETF adjusted closes."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import DATA_DIR, END, START, TICKERS


def _download() -> pd.DataFrame:
    import yfinance as yf

    end_exclusive = (pd.Timestamp(END) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    frames = []
    for t in TICKERS:
        df = yf.download(t, start=START, end=end_exclusive, auto_adjust=True, progress=False, threads=False)
        s = df["Close"]
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
        s.name = t
        frames.append(s)
    return pd.concat(frames, axis=1)


def download_prices(force: bool = False) -> pd.DataFrame:
    """Daily adjusted closes for TICKERS, START..END inclusive, inner-joined."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = DATA_DIR / "etf_prices.csv"
    if cache.exists() and not force:
        px = pd.read_csv(cache, index_col=0, parse_dates=True)
    else:
        px = _download()
        px.to_csv(cache)
        (DATA_DIR / "download_meta.txt").write_text(
            f"downloaded_utc={pd.Timestamp.utcnow().isoformat()}\nsource=Yahoo Finance via yfinance, auto_adjust=True\n"
        )
    px = px[TICKERS].dropna(how="any").sort_index()
    return px.loc[START:END]


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices / prices.shift(1)).dropna(how="any")
