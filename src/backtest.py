"""Kupiec / Christoffersen VaR backtests and simple ES exceedance stats."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class VaRBacktest:
    n: int
    hits: int
    hit_rate: float
    expected: float
    lr_uc: float
    p_uc: float
    lr_ind: float
    p_ind: float
    lr_cc: float
    p_cc: float


def kupiec_uc(hits: np.ndarray, alpha: float) -> tuple[float, float]:
    n = len(hits)
    x = int(hits.sum())
    p = alpha
    if x == 0 or x == n:
        # boundary
        ll0 = n * np.log(1 - p) if x == 0 else n * np.log(p)
        ll1 = 0.0
    else:
        phat = x / n
        ll0 = x * np.log(p) + (n - x) * np.log(1 - p)
        ll1 = x * np.log(phat) + (n - x) * np.log(1 - phat)
    lr = max(0.0, -2.0 * (ll0 - ll1))
    pval = float(1.0 - stats.chi2.cdf(lr, 1))
    return lr, pval


def christoffersen_ind(hits: np.ndarray) -> tuple[float, float]:
    # transition counts
    h = hits.astype(int)
    n00 = n01 = n10 = n11 = 0
    for i in range(1, len(h)):
        if h[i - 1] == 0 and h[i] == 0:
            n00 += 1
        elif h[i - 1] == 0 and h[i] == 1:
            n01 += 1
        elif h[i - 1] == 1 and h[i] == 0:
            n10 += 1
        else:
            n11 += 1
    # independence LR
    def safe_p(a, b):
        return a / b if b > 0 else 0.0

    pi01 = safe_p(n01, n00 + n01)
    pi11 = safe_p(n11, n10 + n11)
    pi2 = safe_p(n01 + n11, n00 + n01 + n10 + n11)

    def ll(pi01_, pi11_):
        s = 0.0
        if n00:
            s += n00 * np.log(max(1 - pi01_, 1e-12))
        if n01:
            s += n01 * np.log(max(pi01_, 1e-12))
        if n10:
            s += n10 * np.log(max(1 - pi11_, 1e-12))
        if n11:
            s += n11 * np.log(max(pi11_, 1e-12))
        return s

    ll1 = ll(pi01, pi11)
    ll0 = ll(pi2, pi2)
    lr = max(0.0, -2.0 * (ll0 - ll1))
    pval = float(1.0 - stats.chi2.cdf(lr, 1))
    return lr, pval


def full_var_backtest(hits: np.ndarray, alpha: float) -> VaRBacktest:
    hits = np.asarray(hits, dtype=float)
    n = len(hits)
    x = int(hits.sum())
    lr_uc, p_uc = kupiec_uc(hits, alpha)
    lr_ind, p_ind = christoffersen_ind(hits)
    lr_cc = lr_uc + lr_ind
    p_cc = float(1.0 - stats.chi2.cdf(lr_cc, 2))
    return VaRBacktest(n, x, x / n if n else 0.0, alpha, lr_uc, p_uc, lr_ind, p_ind, lr_cc, p_cc)


def es_shortfall_stats(returns: np.ndarray, var: np.ndarray, es: np.ndarray) -> dict:
    """Average shortfall on VaR breach days vs predicted ES."""
    hits = returns < -var
    if hits.sum() == 0:
        return {"n_hits": 0, "avg_loss": np.nan, "avg_es": np.nan, "ratio": np.nan}
    loss = -returns[hits]
    pred = es[hits]
    return {
        "n_hits": int(hits.sum()),
        "avg_loss": float(loss.mean()),
        "avg_es": float(pred.mean()),
        "ratio": float(loss.mean() / pred.mean()) if pred.mean() else np.nan,
    }
