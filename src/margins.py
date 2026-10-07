"""GARCH(1,1)-t margins, daily one-step-ahead volatility filter, and PIT uniforms."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats


@dataclass
class MarginFit:
    """Parameters in decimal-return units."""

    ticker: str
    mu: float
    omega: float
    alpha: float
    beta: float
    nu: float
    std_resid: pd.Series
    sigma2_last: float  # conditional variance on the last in-sample day
    eps_last: float  # demeaned return on the last in-sample day

    def next_var(self) -> float:
        return self.omega + self.alpha * self.eps_last**2 + self.beta * self.sigma2_last


def fit_garch_t(returns: pd.Series, ticker: str = "") -> MarginFit:
    y = returns.dropna() * 100.0
    res = arch_model(y, mean="Constant", vol="GARCH", p=1, q=1, dist="t", rescale=False).fit(
        disp="off", show_warning=False
    )
    p = res.params
    vol = np.asarray(res.conditional_volatility) / 100.0
    mu = float(p["mu"]) / 100.0
    std = pd.Series(np.asarray(res.std_resid), index=y.index).replace([np.inf, -np.inf], np.nan).dropna()
    return MarginFit(
        ticker=ticker,
        mu=mu,
        omega=float(p["omega"]) / 1e4,
        alpha=float(p["alpha[1]"]),
        beta=float(p["beta[1]"]),
        nu=float(p["nu"]),
        std_resid=std,
        sigma2_last=float(vol[-1] ** 2),
        eps_last=float(returns.dropna().iloc[-1] - mu),
    )


def fit_all_margins(returns: pd.DataFrame) -> dict[str, MarginFit]:
    return {c: fit_garch_t(returns[c], c) for c in returns.columns}


def filter_vol(fit: MarginFit, future: pd.Series) -> pd.Series:
    """One-step-ahead sigma for each date in `future`, using fixed parameters and only past returns."""
    s2 = fit.next_var()
    out = np.empty(len(future))
    for i, r in enumerate(future.to_numpy()):
        out[i] = np.sqrt(s2)
        s2 = fit.omega + fit.alpha * (r - fit.mu) ** 2 + fit.beta * s2
    return pd.Series(out, index=future.index)


def std_resid_matrix(fits: dict[str, MarginFit]) -> pd.DataFrame:
    return pd.DataFrame({k: v.std_resid for k, v in fits.items()}).dropna(how="any")


def to_uniforms(z: pd.DataFrame | np.ndarray) -> np.ndarray:
    """Pseudo-observations: ranks / (n + 1)."""
    z = pd.DataFrame(z)
    return (z.rank(method="average") / (len(z) + 1.0)).to_numpy()


def std_t_ppf(u: np.ndarray, nu: float) -> np.ndarray:
    """Quantile of the unit-variance Student-t used by the GARCH innovations."""
    return stats.t.ppf(u, df=nu) * np.sqrt((nu - 2.0) / nu)
