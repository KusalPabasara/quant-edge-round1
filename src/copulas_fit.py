"""Fast pairwise / correlation-based copula fits for competition runtime."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class CopulaResult:
    family: str
    aic: float
    params: dict
    loglik: float
    lambda_l: float
    lambda_u: float
    model: object | None = None


def _aic(ll: float, k: int) -> float:
    return -2.0 * ll + 2.0 * k


def _avg_pairwise_rho(corr: np.ndarray) -> float:
    d = corr.shape[0]
    mask = ~np.eye(d, dtype=bool)
    vals = corr[mask]
    return float(np.nanmean(vals))


def student_tail_dep(rho: float, nu: float) -> float:
    if nu <= 0 or abs(rho) >= 1:
        return 0.0
    x = -np.sqrt((nu + 1.0) * (1.0 - rho) / (1.0 + rho))
    return float(2.0 * stats.t.cdf(x, df=nu + 1.0))


def clayton_lambda_l(theta: float) -> float:
    if theta <= 0:
        return 0.0
    return float(2.0 ** (-1.0 / theta))


def fit_gaussian(u: np.ndarray) -> CopulaResult:
    d = u.shape[1]
    z = stats.norm.ppf(np.clip(u, 1e-6, 1 - 1e-6))
    corr = np.corrcoef(z, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0)
    # nearest PD
    eigvals, eigvecs = np.linalg.eigh(corr)
    eigvals = np.clip(eigvals, 1e-6, None)
    corr = (eigvecs * eigvals) @ eigvecs.T
    # renormalize diagonal
    dstd = np.sqrt(np.diag(corr))
    corr = corr / np.outer(dstd, dstd)
    np.fill_diagonal(corr, 1.0)
    try:
        ll = float(np.sum(stats.multivariate_normal.logpdf(z, mean=np.zeros(d), cov=corr, allow_singular=True)))
        # subtract univariate norm logdensities to approximate copula loglik
        ll -= float(np.sum(stats.norm.logpdf(z)))
    except Exception:
        ll = -1e6
    rho = _avg_pairwise_rho(corr)
    k = d * (d - 1) // 2
    return CopulaResult("gaussian", _aic(ll, k), {"rho_avg": rho, "corr": corr}, ll, 0.0, 0.0, None)


def fit_student(u: np.ndarray) -> CopulaResult:
    d = u.shape[1]
    g = fit_gaussian(u)
    corr = g.params["corr"]
    rho = g.params["rho_avg"]
    # grid search nu on pairwise composite likelihood (fast)
    best_nu, best_ll = 8.0, -1e18
    for nu in (3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 30.0):
        ll = 0.0
        t = stats.t.ppf(np.clip(u, 1e-6, 1 - 1e-6), df=nu)
        # meta-elliptical approx: mv-t loglik minus margins
        try:
            scale = corr * (nu / (nu - 2.0)) if nu > 2 else corr
            # use gaussian of t-scores as proxy for speed
            ll = float(np.sum(stats.multivariate_normal.logpdf(t, mean=np.zeros(d), cov=corr, allow_singular=True)))
            ll -= float(np.sum(stats.t.logpdf(t, df=nu)))
        except Exception:
            continue
        if ll > best_ll:
            best_ll, best_nu = ll, nu
    lam = student_tail_dep(rho, best_nu)
    k = d * (d - 1) // 2 + 1
    return CopulaResult(
        "student",
        _aic(best_ll, k),
        {"rho_avg": rho, "nu": best_nu, "corr": corr},
        best_ll,
        lam,
        lam,
        None,
    )


def fit_clayton(u: np.ndarray) -> CopulaResult:
    d = u.shape[1]
    thetas = []
    ll = 0.0
    for i in range(d):
        for j in range(i + 1, d):
            tau, _ = stats.kendalltau(u[:, i], u[:, j])
            tau = float(tau) if np.isfinite(tau) else 0.0
            tau = min(max(tau, 1e-4), 0.95)
            theta = 2.0 * tau / (1.0 - tau)
            thetas.append(theta)
            a = np.clip(u[:, i], 1e-6, 1 - 1e-6)
            b = np.clip(u[:, j], 1e-6, 1 - 1e-6)
            th = theta
            term = (
                np.log(1 + th)
                - (1 + th) * (np.log(a) + np.log(b))
                - (2.0 + 1.0 / th) * np.log(np.maximum(a ** (-th) + b ** (-th) - 1.0, 1e-12))
            )
            ll += float(np.sum(term))
    theta = float(np.mean(thetas)) if thetas else 0.5
    return CopulaResult("clayton", _aic(ll, 1), {"theta": theta}, ll, clayton_lambda_l(theta), 0.0, None)


def select_copula(u_df: pd.DataFrame) -> CopulaResult:
    u = np.asarray(u_df, dtype=np.float64)
    cands = [fit_gaussian(u), fit_student(u), fit_clayton(u)]
    return min(cands, key=lambda c: c.aic if np.isfinite(c.aic) else 1e18)


def fit_all_families(u_df: pd.DataFrame) -> list[CopulaResult]:
    u = np.asarray(u_df, dtype=np.float64)
    return [fit_gaussian(u), fit_student(u), fit_clayton(u)]


def simulate_uniforms(result: CopulaResult, n: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    if result.family == "gaussian":
        corr = result.params.get("corr")
        if corr is None:
            rho = float(result.params.get("rho_avg", 0.3))
            corr = np.full((dim, dim), rho)
            np.fill_diagonal(corr, 1.0)
        z = rng.multivariate_normal(np.zeros(dim), corr, size=n)
        return stats.norm.cdf(z)
    if result.family == "student":
        nu = float(result.params.get("nu", 8.0))
        corr = result.params.get("corr")
        if corr is None:
            rho = float(result.params.get("rho_avg", 0.3))
            corr = np.full((dim, dim), rho)
            np.fill_diagonal(corr, 1.0)
        g = rng.multivariate_normal(np.zeros(dim), corr, size=n)
        chi = rng.chisquare(nu, size=n)[:, None]
        t = g * np.sqrt(nu / chi)
        return stats.t.cdf(t, df=nu)
    theta = max(float(result.params.get("theta", 0.5)), 1e-3)
    v = rng.gamma(1.0 / theta, 1.0, size=n)
    e = rng.exponential(1.0, size=(n, dim))
    return np.power(1.0 + e / v[:, None], -1.0 / theta)
