"""Full d-dimensional Gaussian, Student-t and Clayton copulas.

All three log-likelihoods are exact joint copula densities on the same
pseudo-observations, so their AIC values are directly comparable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar
from scipy.special import gammaln

EPS = 1e-10


@dataclass
class CopulaResult:
    family: str
    loglik: float
    k: int
    lambda_l: float
    lambda_u: float
    params: dict = field(default_factory=dict)

    @property
    def aic(self) -> float:
        return -2.0 * self.loglik + 2.0 * self.k


def _clip(u: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(u, dtype=np.float64), EPS, 1.0 - EPS)


def nearest_corr(r: np.ndarray, floor: float = 1e-6) -> np.ndarray:
    """Project a symmetric matrix onto the positive-definite correlations (eigenvalue clipping)."""
    r = 0.5 * (r + r.T)
    w, v = np.linalg.eigh(r)
    r = (v * np.clip(w, floor, None)) @ v.T
    d = np.sqrt(np.diag(r))
    r = r / np.outer(d, d)
    np.fill_diagonal(r, 1.0)
    return r


def kendall_matrix(u: np.ndarray) -> np.ndarray:
    d = u.shape[1]
    tau = np.eye(d)
    for i in range(d):
        for j in range(i + 1, d):
            t, _ = stats.kendalltau(u[:, i], u[:, j])
            tau[i, j] = tau[j, i] = 0.0 if not np.isfinite(t) else t
    return tau


def _offdiag_mean(m: np.ndarray) -> float:
    return float(m[~np.eye(m.shape[0], dtype=bool)].mean())


# ---------------------------------------------------------------- log-densities

def gaussian_logpdf(u: np.ndarray, corr: np.ndarray) -> np.ndarray:
    z = stats.norm.ppf(_clip(u))
    inv = np.linalg.inv(corr)
    _, logdet = np.linalg.slogdet(corr)
    q = np.einsum("ij,jk,ik->i", z, inv - np.eye(corr.shape[0]), z)
    return -0.5 * logdet - 0.5 * q


def student_logpdf(u: np.ndarray, corr: np.ndarray, nu: float) -> np.ndarray:
    d = corr.shape[0]
    x = stats.t.ppf(_clip(u), df=nu)
    inv = np.linalg.inv(corr)
    _, logdet = np.linalg.slogdet(corr)
    q = np.einsum("ij,jk,ik->i", x, inv, x)
    const = gammaln((nu + d) / 2.0) + (d - 1) * gammaln(nu / 2.0) - d * gammaln((nu + 1.0) / 2.0) - 0.5 * logdet
    return const - (nu + d) / 2.0 * np.log1p(q / nu) + (nu + 1.0) / 2.0 * np.log1p(x**2 / nu).sum(axis=1)


def clayton_logpdf(u: np.ndarray, theta: float) -> np.ndarray:
    u = _clip(u)
    d = u.shape[1]
    s = np.power(u, -theta).sum(axis=1) - d + 1.0
    const = np.log1p(theta * np.arange(d)).sum()
    return const - (1.0 + theta) * np.log(u).sum(axis=1) - (d + 1.0 / theta) * np.log(s)


# ---------------------------------------------------------------- fitting

def fit_gaussian(u: np.ndarray) -> CopulaResult:
    u = _clip(u)
    d = u.shape[1]
    corr = nearest_corr(np.corrcoef(stats.norm.ppf(u), rowvar=False))
    ll = float(gaussian_logpdf(u, corr).sum())
    return CopulaResult("gaussian", ll, d * (d - 1) // 2, 0.0, 0.0, {"corr": corr, "rho_avg": _offdiag_mean(corr)})


def student_pair_lambda(rho: np.ndarray, nu: float) -> np.ndarray:
    return 2.0 * stats.t.cdf(-np.sqrt((nu + 1.0) * (1.0 - rho) / (1.0 + rho)), df=nu + 1.0)


def fit_student(u: np.ndarray, tau: np.ndarray | None = None) -> CopulaResult:
    u = _clip(u)
    d = u.shape[1]
    tau = kendall_matrix(u) if tau is None else tau
    corr = nearest_corr(np.sin(np.pi * tau / 2.0))
    opt = minimize_scalar(lambda nu: -student_logpdf(u, corr, nu).sum(), bounds=(2.5, 60.0), method="bounded")
    nu = float(opt.x)
    lam = student_pair_lambda(corr[~np.eye(d, dtype=bool)], nu).mean()
    return CopulaResult(
        "student", -float(opt.fun), d * (d - 1) // 2 + 1, float(lam), float(lam),
        {"corr": corr, "nu": nu, "rho_avg": _offdiag_mean(corr)},
    )


def fit_clayton(u: np.ndarray) -> CopulaResult:
    u = _clip(u)
    opt = minimize_scalar(lambda th: -clayton_logpdf(u, th).sum(), bounds=(1e-3, 20.0), method="bounded")
    theta = float(opt.x)
    return CopulaResult(
        "clayton", -float(opt.fun), 1, float(2.0 ** (-1.0 / theta)), 0.0, {"theta": theta, "dim": u.shape[1]}
    )


FITTERS = {"gaussian": fit_gaussian, "student": fit_student, "clayton": fit_clayton}


def fit_family(u: np.ndarray, family: str) -> CopulaResult:
    return FITTERS[family](np.asarray(u, dtype=np.float64))


def fit_all_families(u: np.ndarray) -> list[CopulaResult]:
    return [fit_family(u, f) for f in FITTERS]


def select_copula(u: np.ndarray) -> CopulaResult:
    return min(fit_all_families(u), key=lambda c: c.aic)


# ---------------------------------------------------------------- simulation

def simulate_uniforms(res: CopulaResult, n: int, rng: np.random.Generator) -> np.ndarray:
    if res.family == "clayton":
        theta, d = res.params["theta"], res.params["dim"]
        v = rng.gamma(1.0 / theta, 1.0, size=n)
        e = rng.exponential(1.0, size=(n, d))
        return _clip(np.power(1.0 + e / v[:, None], -1.0 / theta))
    corr = res.params["corr"]
    g = rng.standard_normal((n, corr.shape[0])) @ np.linalg.cholesky(corr).T
    if res.family == "gaussian":
        return _clip(stats.norm.cdf(g))
    nu = res.params["nu"]
    w = np.sqrt(nu / rng.chisquare(nu, size=n))[:, None]
    return _clip(stats.t.cdf(g * w, df=nu))
