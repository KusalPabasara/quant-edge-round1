"""Correctness checks for the building blocks used in the report."""

import numpy as np
import pytest
from scipy import stats

from src.backtest import diebold_mariano, fz0_loss, kupiec_uc, mcneil_frey
from src.copulas_fit import (
    clayton_logpdf,
    fit_clayton,
    fit_student,
    gaussian_logpdf,
    simulate_uniforms,
    student_logpdf,
)
from src.horizon import var_es
from src.modwt import boundary_len, modwt_mra
from src.tail_np import lambda_l, stationary_bootstrap_indices

RNG = np.random.default_rng(0)


# ---------------------------------------------------------------- MODWT

@pytest.mark.parametrize("n", [257, 1000, 4096])
def test_mra_reconstructs_exactly(n):
    x = np.cumsum(RNG.standard_normal(n))
    details, smooth = modwt_mra(x, "db2", 6)
    assert len(details) == 6
    assert np.max(np.abs(sum(details) + smooth - x)) < 1e-10


def test_mra_is_zero_phase():
    n = 2048
    t = np.arange(n)
    x = np.sin(2 * np.pi * t / 6.0)  # period 6 sits in the D2/D3 pass bands
    details, smooth = modwt_mra(x, "db2", 6)
    mid = slice(300, n - 300)
    lag = np.argmax(np.correlate(details[1][mid] + details[2][mid], x[mid], "full")) - (len(x[mid]) - 1)
    assert lag == 0


def test_boundary_lengths_db2():
    assert [boundary_len(j, "db2") for j in range(1, 7)] == [4, 10, 22, 46, 94, 190]


# ---------------------------------------------------------------- copulas

def _sample_t(n, d, rho, nu):
    corr = np.full((d, d), rho) + (1 - rho) * np.eye(d)
    from src.copulas_fit import CopulaResult

    res = CopulaResult("student", 0.0, 0, 0.0, 0.0, {"corr": corr, "nu": nu})
    return corr, simulate_uniforms(res, n, RNG)


def test_densities_match_copulae():
    copulae = pytest.importorskip("copulae")
    d = 4
    corr, u = _sample_t(500, d, 0.5, 5.0)
    g = copulae.GaussianCopula(dim=d)
    g.params = corr[np.triu_indices(d, 1)]
    assert np.allclose(gaussian_logpdf(u, corr), g.pdf(u, log=True), atol=1e-8)
    t = copulae.StudentCopula(dim=d)
    t.params = np.r_[5.0, corr[np.triu_indices(d, 1)]]
    assert np.allclose(student_logpdf(u, corr, 5.0), t.pdf(u, log=True), atol=1e-8)
    c = copulae.ClaytonCopula(theta=1.3, dim=d)
    assert np.allclose(clayton_logpdf(u, 1.3), c.pdf(u, log=True), atol=1e-8)


def test_gaussian_density_integrates_to_one():
    corr = np.array([[1.0, 0.6], [0.6, 1.0]])
    g = np.linspace(0.0025, 0.9975, 200)
    uu = np.array(np.meshgrid(g, g)).reshape(2, -1).T
    mass = np.exp(gaussian_logpdf(uu, corr)).mean()
    assert abs(mass - 1.0) < 0.02


def test_clayton_mle_recovers_theta_and_lambda():
    from src.copulas_fit import CopulaResult

    theta = 2.0
    u = simulate_uniforms(CopulaResult("clayton", 0, 1, 0, 0, {"theta": theta, "dim": 3}), 8000, RNG)
    res = fit_clayton(u)
    assert abs(res.params["theta"] - theta) < 0.1
    assert res.lambda_l == pytest.approx(2.0 ** (-1.0 / res.params["theta"]))
    assert res.lambda_u == 0.0


def test_student_fit_recovers_nu():
    _, u = _sample_t(6000, 5, 0.5, 6.0)
    res = fit_student(u)
    assert 4.5 < res.params["nu"] < 8.0
    assert abs(res.params["rho_avg"] - 0.5) < 0.03
    assert res.lambda_l == res.lambda_u > 0


# ---------------------------------------------------------------- tail dependence

def test_nonparametric_lambda_limits():
    x = RNG.standard_normal((20000, 3))
    assert lambda_l(x, 0.05) < 0.12  # independence -> about q
    y = np.repeat(RNG.standard_normal((20000, 1)), 3, axis=1)
    assert lambda_l(y, 0.05) == pytest.approx(1.0, abs=1e-3)


def test_stationary_bootstrap_shape_and_range():
    idx = stationary_bootstrap_indices(500, 20, 7, RNG)
    assert idx.shape == (7, 500)
    assert idx.min() >= 0 and idx.max() < 500


# ---------------------------------------------------------------- backtests

def test_kupiec_known_value():
    hits = np.zeros(1000, dtype=bool)
    hits[:10] = True
    lr, p = kupiec_uc(hits, 0.01)
    assert lr == pytest.approx(0.0, abs=1e-10)
    assert p == pytest.approx(1.0)
    hits[:25] = True
    lr, _ = kupiec_uc(hits, 0.01)
    expected = -2 * (25 * np.log(0.01) + 975 * np.log(0.99) - 25 * np.log(0.025) - 975 * np.log(0.975))
    assert lr == pytest.approx(expected)


def test_fz0_prefers_true_forecast():
    alpha, n = 0.025, 200_000
    r = RNG.standard_normal(n) * 0.01
    q = -stats.norm.ppf(alpha) * 0.01
    es = stats.norm.pdf(stats.norm.ppf(alpha)) / alpha * 0.01
    true = fz0_loss(r, np.full(n, q), np.full(n, es), alpha).mean()
    too_low = fz0_loss(r, np.full(n, 0.6 * q), np.full(n, 0.6 * es), alpha).mean()
    too_high = fz0_loss(r, np.full(n, 1.6 * q), np.full(n, 1.6 * es), alpha).mean()
    assert true < too_low and true < too_high


def test_dm_sign_and_mcneil_frey():
    a = RNG.standard_normal(2000)
    stat, p = diebold_mariano(a, a + 0.5)
    assert stat < 0 and p < 1e-6
    r = -np.abs(RNG.standard_normal(500)) * 3
    under = mcneil_frey(r, np.full(500, 0.5), np.full(500, 0.6))
    assert under["p_value"] < 0.01


def test_var_es_ordering():
    port = RNG.standard_normal(100_000)
    v, e = var_es(port, 0.025)
    assert v == pytest.approx(-stats.norm.ppf(0.025), abs=0.03)
    assert e > v
