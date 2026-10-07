"""GARCH(1,1)-t margins and PIT uniforms."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats


@dataclass
class MarginFit:
    ticker: str
    std_resid: pd.Series
    cond_vol: pd.Series
    last_vol: float
    nu: float
    mu: float
    success: bool


def fit_garch_t(returns: pd.Series, ticker: str = "") -> MarginFit:
    """Fit GARCH(1,1) with Student-t; returns in decimal, scaled to % for arch."""
    y = returns.dropna() * 100.0  # arch prefers percent
    am = arch_model(y, mean="Constant", vol="Garch", p=1, q=1, dist="t", rescale=False)
    try:
        res = am.fit(disp="off", show_warning=False)
        std = pd.Series(res.std_resid, index=y.index).replace([np.inf, -np.inf], np.nan).dropna()
        vol = pd.Series(res.conditional_volatility, index=y.index) / 100.0
        nu = float(res.params.get("nu", 8.0))
        mu = float(res.params.get("mu", 0.0)) / 100.0
        last_vol = float(vol.iloc[-1])
        return MarginFit(ticker, std, vol, last_vol, nu, mu, True)
    except Exception:
        # fallback: standardize by rolling vol
        vol = y.rolling(60, min_periods=30).std().bfill() / 100.0
        std = (y / 100.0) / vol.replace(0, np.nan)
        std = std.replace([np.inf, -np.inf], np.nan).dropna()
        return MarginFit(ticker, std, vol.reindex(std.index), float(vol.iloc[-1]), 8.0, 0.0, False)


def fit_all_margins(returns: pd.DataFrame) -> dict[str, MarginFit]:
    return {c: fit_garch_t(returns[c], c) for c in returns.columns}


def std_resid_matrix(fits: dict[str, MarginFit]) -> pd.DataFrame:
    cols = {k: v.std_resid for k, v in fits.items()}
    return pd.DataFrame(cols).dropna(how="any")


def to_uniforms(z: pd.DataFrame) -> pd.DataFrame:
    """Empirical PIT ranks clipped away from {0,1}."""
    n = len(z)
    u = z.rank(method="average") / (n + 1.0)
    return u.clip(1e-6, 1.0 - 1e-6)


def invert_t_margin(u: np.ndarray, nu: float, mu: float, sigma: float) -> np.ndarray:
    """Map uniforms to return shocks via Student-t then scale by cond vol."""
    z = stats.t.ppf(u, df=max(nu, 2.1))
    # standardize t to unit variance roughly
    if nu > 2:
        z = z / np.sqrt(nu / (nu - 2.0))
    return mu + sigma * z
