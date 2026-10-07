"""VaR and ES backtests.

Sign convention: VaR and ES are positive loss numbers; a hit is r < -VaR.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def kupiec_uc(hits: np.ndarray, alpha: float) -> tuple[float, float]:
    """Kupiec (1995) unconditional coverage LR test."""
    hits = np.asarray(hits, dtype=bool)
    n, x = len(hits), int(hits.sum())
    ll0 = x * np.log(alpha) + (n - x) * np.log(1 - alpha)
    phat = x / n
    ll1 = (x * np.log(phat) if x else 0.0) + ((n - x) * np.log(1 - phat) if x < n else 0.0)
    lr = max(0.0, -2.0 * (ll0 - ll1))
    return lr, float(stats.chi2.sf(lr, 1))


def christoffersen_ind(hits: np.ndarray) -> tuple[float, float]:
    """Christoffersen (1998) first-order Markov independence LR test."""
    h = np.asarray(hits, dtype=int)
    prev, cur = h[:-1], h[1:]
    n00 = int(((prev == 0) & (cur == 0)).sum())
    n01 = int(((prev == 0) & (cur == 1)).sum())
    n10 = int(((prev == 1) & (cur == 0)).sum())
    n11 = int(((prev == 1) & (cur == 1)).sum())

    def xlogy(a, p):
        return a * np.log(p) if a > 0 else 0.0

    p01 = n01 / max(n00 + n01, 1)
    p11 = n11 / max(n10 + n11, 1)
    p = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
    ll1 = xlogy(n00, 1 - p01) + xlogy(n01, p01) + xlogy(n10, 1 - p11) + xlogy(n11, p11)
    ll0 = xlogy(n00 + n10, 1 - p) + xlogy(n01 + n11, p)
    lr = max(0.0, -2.0 * (ll0 - ll1))
    return lr, float(stats.chi2.sf(lr, 1))


def fz0_loss(r: np.ndarray, var: np.ndarray, es: np.ndarray, alpha: float) -> np.ndarray:
    """FZ0 loss of Patton, Ziegel & Chen (2019); lower is better. Inputs are positive loss numbers."""
    v, e = -np.asarray(var), -np.asarray(es)  # quantile and ES of returns (negative)
    hit = (r <= v).astype(float)
    return -hit * (v - r) / (alpha * e) + v / e + np.log(-e) - 1.0


def diebold_mariano(loss_a: np.ndarray, loss_b: np.ndarray) -> tuple[float, float]:
    """DM test of equal mean loss with Newey-West HAC variance; negative stat favours model a."""
    d = np.asarray(loss_a) - np.asarray(loss_b)
    n = len(d)
    lag = int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
    dc = d - d.mean()
    s = dc @ dc / n
    for k in range(1, lag + 1):
        s += 2.0 * (1 - k / (lag + 1)) * (dc[k:] @ dc[:-k]) / n
    stat = d.mean() / np.sqrt(max(s, 1e-18) / n)
    return float(stat), float(2 * stats.norm.sf(abs(stat)))


def mcneil_frey(r: np.ndarray, var: np.ndarray, es: np.ndarray, n_boot: int = 2000, seed: int = 0) -> dict:
    """McNeil & Frey (2000) bootstrap test that ES is not under-estimated.

    Exceedance residuals are standardised by the forecast ES (loss/ES - 1); H0 mean = 0,
    H1 mean > 0 (one-sided). Returns the mean residual and the bootstrap p-value.
    """
    hit = r < -var
    if hit.sum() < 3:
        return {"n_exc": int(hit.sum()), "mean_resid": float("nan"), "p_value": float("nan")}
    e = (-r[hit]) / es[hit] - 1.0
    rng = np.random.default_rng(seed)
    centred = e - e.mean()
    boot = rng.choice(centred, size=(n_boot, len(e)), replace=True).mean(axis=1)
    return {"n_exc": int(hit.sum()), "mean_resid": float(e.mean()), "p_value": float((boot >= e.mean()).mean())}


def evaluate(r: np.ndarray, var: np.ndarray, es: np.ndarray, alpha: float) -> dict:
    r, var, es = map(np.asarray, (r, var, es))
    hits = r < -var
    lr_uc, p_uc = kupiec_uc(hits, alpha)
    lr_ind, p_ind = christoffersen_ind(hits)
    lr_cc = lr_uc + lr_ind
    exc_loss = float((-r[hits]).mean()) if hits.any() else float("nan")
    exc_es = float(es[hits].mean()) if hits.any() else float("nan")
    return {
        "n": int(len(r)),
        "hits": int(hits.sum()),
        "hit_rate": float(hits.mean()),
        "expected": alpha,
        "p_uc": p_uc,
        "p_ind": p_ind,
        "p_cc": float(stats.chi2.sf(lr_cc, 2)),
        "mean_var": float(var.mean()),
        "mean_es": float(es.mean()),
        "exc_loss_over_es": exc_loss / exc_es if hits.any() else float("nan"),
        "fz0": float(fz0_loss(r, var, es, alpha).mean()),
        **{f"mf_{k}": v for k, v in mcneil_frey(r, var, es).items()},
    }
