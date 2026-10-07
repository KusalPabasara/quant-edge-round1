"""Rolling out-of-sample engine.

Every REFIT_EVERY days: refit GARCH-t margins, MODWT-MRA bands and all copulas on the
previous WINDOW days, and draw standardized shock matrices once. Every day: rescale the
shocks by the one-step-ahead GARCH sigma, so VaR/ES moves with volatility daily.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from src.config import ALPHAS, HS_WINDOW, N_SIM, OOS_START, REFIT_EVERY, SEED, TICKERS, WINDOW
from src.copulas_fit import fit_family, simulate_uniforms
from src.horizon import asset_hday_sums, daily_shocks, recouple, var_es, variance_path
from src.margins import fit_all_margins, filter_vol, std_resid_matrix, std_t_ppf, to_uniforms
from src.wavelets import decompose_residuals

FAMILIES = ("gaussian", "student", "clayton")
COPULA_MODELS = [(src, fam) for src in ("raw", "H1") for fam in FAMILIES]
MODEL_NAMES = [f"{s}-{f}" for s, f in COPULA_MODELS] + ["FHS", "HS"]
H_METHODS = ("sqrt-time Gaussian", "sqrt-time t", "daily t path-sum", "horizon-matched")
H_BAND = {5: "H1", 20: "H2"}


def _tail(port: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    """VaR/ES per column of a (n_scen, n_days) matrix of simulated portfolio returns."""
    k = max(int(np.floor(alpha * port.shape[0])), 1)
    part = np.partition(port, k - 1, axis=0)[:k]
    var = -part.max(axis=0)
    es = -part.mean(axis=0)
    return var, es


def run_oos(rets: pd.DataFrame, horizons=(5, 20), log=print) -> dict:
    rng = np.random.default_rng(SEED)
    dates = rets.index
    port_ret = rets[TICKERS].mean(axis=1)
    oos_pos = np.where(dates >= pd.Timestamp(OOS_START))[0]
    refits = oos_pos[::REFIT_EVERY]

    daily = {m: {a: {"var": [], "es": []} for a in ALPHAS} for m in MODEL_NAMES}
    day_index, aic_log = [], []
    hrec = {h: [] for h in horizons}
    t0 = time.time()

    for k, p0 in enumerate(refits):
        block = dates[p0 : p0 + REFIT_EVERY]
        window = rets.iloc[p0 - WINDOW : p0]
        fits = fit_all_margins(window)
        z = std_resid_matrix(fits)
        bands = decompose_residuals(z)
        u = {"raw": to_uniforms(z), "H1": to_uniforms(bands["H1"]), "H2": to_uniforms(bands["H2"])}
        nus = np.array([fits[t].nu for t in TICKERS])
        mus = np.array([fits[t].mu for t in TICKERS])

        cops = {}
        for src in ("raw", "H1", "H2"):
            for fam in FAMILIES:
                cops[(src, fam)] = fit_family(u[src], fam)
        aic_log.append({"date": str(block[0].date()), **{f"{s}-{f}": c.aic for (s, f), c in cops.items()}})

        sig = pd.DataFrame({t: filter_vol(fits[t], rets.loc[block, t]) for t in TICKERS})[TICKERS]
        weights = sig.to_numpy() / len(TICKERS)  # (days, d)

        sims = {}
        for src, fam in COPULA_MODELS:
            uu = simulate_uniforms(cops[(src, fam)], N_SIM, rng)
            zz = np.column_stack([std_t_ppf(uu[:, j], nus[j]) for j in range(len(TICKERS))])
            sims[f"{src}-{fam}"] = mus.mean() + zz @ weights.T
        sims["FHS"] = mus.mean() + z[TICKERS].to_numpy() @ weights.T
        for m, port in sims.items():
            for a in ALPHAS:
                v, e = _tail(port, a)
                daily[m][a]["var"].extend(v)
                daily[m][a]["es"].extend(e)
        for d in block:
            pos = dates.get_loc(d)
            hist = port_ret.iloc[pos - HS_WINDOW : pos].to_numpy()
            for a in ALPHAS:
                v, e = var_es(hist, a)
                daily["HS"][a]["var"].append(v)
                daily["HS"][a]["es"].append(e)
        day_index.extend(block)

        for h in horizons:
            origins = [i for i in range(0, len(block), h) if dates.get_loc(block[i]) + h <= len(dates)]
            if not origins:
                continue
            shocks = daily_shocks(cops[("raw", "student")], nus, N_SIM, h, rng)
            for i in origins:
                pos = dates.get_loc(block[i])
                realised = float(port_ret.iloc[pos : pos + h].sum())
                s2 = sig.iloc[i].to_numpy() ** 2
                paths = np.column_stack([variance_path(fits[t], s2[j], h) for j, t in enumerate(TICKERS)])
                sums = asset_hday_sums(shocks, np.sqrt(paths), mus)
                matched = recouple(sums, cops[(H_BAND[h], _best_family(cops, H_BAND[h]))], rng)
                row = {"date": block[i], "realised": realised}
                for a in ALPHAS:
                    g = len(day_index) - len(block) + i
                    v1g, e1g = daily["raw-gaussian"][a]["var"][g], daily["raw-gaussian"][a]["es"][g]
                    v1t, e1t = daily["raw-student"][a]["var"][g], daily["raw-student"][a]["es"][g]
                    row[(H_METHODS[0], a)] = (np.sqrt(h) * v1g, np.sqrt(h) * e1g)
                    row[(H_METHODS[1], a)] = (np.sqrt(h) * v1t, np.sqrt(h) * e1t)
                    row[(H_METHODS[2], a)] = var_es(sums.mean(axis=1), a)
                    row[(H_METHODS[3], a)] = var_es(matched.mean(axis=1), a)
                hrec[h].append(row)

        if k % 10 == 0:
            log(f"  refit {k + 1}/{len(refits)} @ {block[0].date()}  ({time.time() - t0:.0f}s)")

    idx = pd.DatetimeIndex(day_index)
    return {
        "dates": idx,
        "realised": port_ret.loc[idx].to_numpy(),
        "daily": {m: {a: {k: np.asarray(v) for k, v in d.items()} for a, d in md.items()} for m, md in daily.items()},
        "aic_log": pd.DataFrame(aic_log),
        "horizon": hrec,
    }


def _best_family(cops: dict, src: str) -> str:
    return min(FAMILIES, key=lambda f: cops[(src, f)].aic)
