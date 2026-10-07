"""h-day portfolio risk: square-root-of-time vs daily path sum vs horizon-matched dependence.

All three share the same GARCH-t margins, so differences isolate (i) the sqrt-time
shortcut and (ii) the dependence structure used to couple h-day asset returns.
"""

from __future__ import annotations

import numpy as np

from src.copulas_fit import CopulaResult, simulate_uniforms
from src.margins import MarginFit, std_t_ppf


def variance_path(fit: MarginFit, sigma2_0: float, h: int) -> np.ndarray:
    """Expected conditional variances for days 0..h-1 given today's one-step variance."""
    persistence = fit.alpha + fit.beta
    if persistence >= 0.999:
        return np.full(h, sigma2_0)
    v_long = fit.omega / (1.0 - persistence)
    return v_long + persistence ** np.arange(h) * (sigma2_0 - v_long)


def daily_shocks(cop: CopulaResult, nus: np.ndarray, n: int, h: int, rng: np.random.Generator) -> np.ndarray:
    """(n, h, d) unit-variance shocks, i.i.d. over days, cross-sectionally coupled by `cop`."""
    u = simulate_uniforms(cop, n * h, rng)
    z = np.column_stack([std_t_ppf(u[:, j], nus[j]) for j in range(len(nus))])
    return z.reshape(n, h, len(nus))


def asset_hday_sums(shocks: np.ndarray, sig_paths: np.ndarray, mus: np.ndarray) -> np.ndarray:
    """(n, d) simulated h-day log-return sums per asset. sig_paths is (h, d) of daily sigmas."""
    h = shocks.shape[1]
    return h * mus + np.einsum("nhd,hd->nd", shocks, sig_paths)


def recouple(asset_sums: np.ndarray, cop: CopulaResult, rng: np.random.Generator) -> np.ndarray:
    """Keep each asset's simulated h-day marginal but impose the dependence of `cop`."""
    n, d = asset_sums.shape
    sorted_sums = np.sort(asset_sums, axis=0)
    u = simulate_uniforms(cop, n, rng)
    idx = np.minimum((u * n).astype(int), n - 1)
    return np.take_along_axis(sorted_sums, idx, axis=0)


def var_es(port: np.ndarray, alpha: float) -> tuple[float, float]:
    q = np.quantile(port, alpha)
    return -float(q), -float(port[port <= q].mean())
