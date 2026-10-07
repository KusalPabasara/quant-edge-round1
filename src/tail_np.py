"""Model-free lower-tail dependence: lambda_L(q) = P(U_i < q, U_j < q) / q, averaged over pairs.

Confidence intervals use the stationary bootstrap of Politis & Romano (1994), resampling the
same time indices for every band so that band differences are tested on paired samples.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import BLOCK_LEN, N_BOOT, SEED


def pseudo_obs(x: np.ndarray) -> np.ndarray:
    ranks = np.argsort(np.argsort(x, axis=0), axis=0) + 1.0
    return ranks / (x.shape[0] + 1.0)


def lambda_l(x: np.ndarray, q: float) -> float:
    """Average pairwise empirical lower-tail dependence at threshold q (ranks taken within x)."""
    low = pseudo_obs(np.asarray(x, dtype=np.float64)) < q
    joint = (low.T.astype(float) @ low.astype(float)) / len(low)
    d = joint.shape[0]
    return float(joint[~np.eye(d, dtype=bool)].mean() / q)


def stationary_bootstrap_indices(n: int, block: float, n_boot: int, rng: np.random.Generator) -> np.ndarray:
    p = 1.0 / block
    idx = np.empty((n_boot, n), dtype=np.int64)
    starts = rng.integers(0, n, size=(n_boot, n))
    new_block = rng.random((n_boot, n)) < p
    idx[:, 0] = starts[:, 0]
    for t in range(1, n):
        idx[:, t] = np.where(new_block[:, t], starts[:, t], (idx[:, t - 1] + 1) % n)
    return idx


def band_tail_table(bands: dict[str, pd.DataFrame], qs, n_boot: int = N_BOOT, block: float = BLOCK_LEN, seed: int = SEED) -> dict:
    """lambda_L by band with bootstrap CIs and a paired test of H3 - H1, on a common index."""
    common = bands["H3"].index
    for b in bands.values():
        common = common.intersection(b.index)
    mats = {k: v.loc[common].to_numpy() for k, v in bands.items()}
    rng = np.random.default_rng(seed)
    idx = stationary_bootstrap_indices(len(common), block, n_boot, rng)
    out = {"n": int(len(common)), "q": {}}
    for q in qs:
        est = {k: lambda_l(m, q) for k, m in mats.items()}
        boot = {k: np.array([lambda_l(m[i], q) for i in idx]) for k, m in mats.items()}
        diff = boot["H3"] - boot["H1"]
        out["q"][str(q)] = {
            "bands": {k: {"est": est[k], "lo": float(np.quantile(boot[k], 0.025)), "hi": float(np.quantile(boot[k], 0.975))} for k in mats},
            "diff_H3_H1": est["H3"] - est["H1"],
            "diff_lo": float(np.quantile(diff, 0.025)),
            "diff_hi": float(np.quantile(diff, 0.975)),
            "p_diff": float(min(1.0, 2 * min((diff <= 0).mean(), (diff >= 0).mean()))),
        }
    return out


def aggregate(z: pd.DataFrame, h: int) -> pd.DataFrame:
    """Non-overlapping h-day sums of standardized residuals."""
    n = (len(z) // h) * h
    arr = z.iloc[:n].to_numpy().reshape(-1, h, z.shape[1]).sum(axis=1)
    return pd.DataFrame(arr, index=z.index[h - 1 : n : h], columns=z.columns)


def horizon_tail_table(z: pd.DataFrame, horizons, qs, n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """lambda_L of non-overlapping h-day aggregated residuals; a check that needs no wavelet."""
    rng = np.random.default_rng(seed)
    out = {}
    for h in horizons:
        a = aggregate(z, h).to_numpy()
        idx = stationary_bootstrap_indices(len(a), max(2.0, BLOCK_LEN / h), n_boot, rng)
        out[str(h)] = {"n": int(len(a))}
        for q in qs:
            boot = np.array([lambda_l(a[i], q) for i in idx])
            out[str(h)][str(q)] = {"est": lambda_l(a, q), "lo": float(np.quantile(boot, 0.025)), "hi": float(np.quantile(boot, 0.975))}
    return out


def regime_tail_table(bands: dict[str, pd.DataFrame], windows: dict, q: float) -> dict:
    """lambda_L by band inside each crisis window vs all other days; ranks use the full sample."""
    out = {}
    pobs = {k: pd.DataFrame(pseudo_obs(v.to_numpy()), index=v.index) for k, v in bands.items()}
    for name, (a, b) in windows.items():
        out[name] = {}
        for k, u in pobs.items():
            sub = u.loc[a:b].to_numpy() < q
            joint = (sub.T.astype(float) @ sub.astype(float)) / max(len(sub), 1)
            d = joint.shape[0]
            out[name][k] = {"est": float(joint[~np.eye(d, dtype=bool)].mean() / q), "n": int(len(sub))}
    out["Calm (other days)"] = {}
    for k, u in pobs.items():
        mask = np.ones(len(u), dtype=bool)
        for a, b in windows.values():
            mask &= ~((u.index >= pd.Timestamp(a)) & (u.index <= pd.Timestamp(b)))
        sub = u.to_numpy()[mask] < q
        joint = (sub.T.astype(float) @ sub.astype(float)) / len(sub)
        d = joint.shape[0]
        out["Calm (other days)"][k] = {"est": float(joint[~np.eye(d, dtype=bool)].mean() / q), "n": int(mask.sum())}
    return out
