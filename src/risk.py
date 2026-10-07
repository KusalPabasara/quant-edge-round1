"""Monte Carlo portfolio VaR / Expected Shortfall."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.copulas_fit import CopulaResult, simulate_uniforms
from src.margins import MarginFit, invert_t_margin


@dataclass
class RiskNumbers:
    var_95: float
    es_95: float
    var_99: float
    es_99: float


def portfolio_var_es(
    copula: CopulaResult,
    fits: dict[str, MarginFit],
    tickers: list[str],
    n_sim: int,
    rng: np.random.Generator,
) -> RiskNumbers:
    dim = len(tickers)
    u = simulate_uniforms(copula, n_sim, dim, rng)
    u = np.clip(u, 1e-6, 1 - 1e-6)
    rets = np.zeros((n_sim, dim), dtype=np.float64)
    for j, t in enumerate(tickers):
        f = fits[t]
        rets[:, j] = invert_t_margin(u[:, j], f.nu, f.mu, f.last_vol)
    rp = rets.mean(axis=1)  # equal weight

    def var_es(alpha: float) -> tuple[float, float]:
        q = np.quantile(rp, alpha)
        var = -float(q)  # loss convention
        tail = rp[rp <= q]
        es = -float(tail.mean()) if len(tail) else var
        return var, es

    v95, e95 = var_es(0.05)
    v99, e99 = var_es(0.01)
    return RiskNumbers(v95, e95, v99, e99)
