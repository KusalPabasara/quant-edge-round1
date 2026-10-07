"""
One-command reproduction for SAIFA Quant Edge Round 1.

Usage (from repo root):
  .venv/bin/python -m src.run_all
  QUANT_EDGE_FAST=1 .venv/bin/python -m src.run_all   # fewer OOS refits
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# allow `python -m src.run_all` from repo root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.backtest import es_shortfall_stats, full_var_backtest
from src.config import (
    ALPHAS,
    FAST_REFIT_EVERY,
    N_SIM,
    OOS_START,
    OUTPUT_DIR,
    REFIT_EVERY,
    REPORT_ASSETS,
    SEED,
    TICKERS,
    WINDOW,
)
from src.copulas_fit import fit_all_families, select_copula
from src.data import download_prices, log_returns
from src.margins import fit_all_margins, std_resid_matrix, to_uniforms
from src.risk import portfolio_var_es
from src.wavelets import decompose_residuals


def _refit_step() -> int:
    if os.environ.get("QUANT_EDGE_FAST", "1") == "1":
        return FAST_REFIT_EVERY
    return REFIT_EVERY


def analyze_bands(z: pd.DataFrame) -> pd.DataFrame:
    bands = decompose_residuals(z)
    rows = []
    for name, mat in bands.items():
        u = to_uniforms(mat)
        for res in fit_all_families(u):
            rows.append(
                {
                    "band": name,
                    "family": res.family,
                    "aic": res.aic,
                    "loglik": res.loglik,
                    "lambda_l": res.lambda_l,
                    "lambda_u": res.lambda_u,
                    **{f"p_{k}": v for k, v in res.params.items() if isinstance(v, (int, float))},
                }
            )
        best = select_copula(u)
        rows.append(
            {
                "band": name,
                "family": f"AIC_winner:{best.family}",
                "aic": best.aic,
                "loglik": best.loglik,
                "lambda_l": best.lambda_l,
                "lambda_u": best.lambda_u,
            }
        )
    return pd.DataFrame(rows)


def rolling_oos(returns: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(SEED)
    step = _refit_step()
    oos_start = pd.Timestamp(OOS_START)
    dates = returns.index
    oos_idx = dates[dates >= oos_start]
    records = []
    cache_wc = None
    cache_g = None
    cache_until = None
    t0 = time.time()

    for i, dt in enumerate(oos_idx):
        # estimation window ends previous day
        loc = dates.get_loc(dt)
        if isinstance(loc, slice):
            loc = loc.start
        if loc < WINDOW:
            continue
        # refit on schedule
        need_refit = cache_wc is None or cache_until is None or dt > cache_until
        if need_refit:
            window = returns.iloc[loc - WINDOW : loc]
            fits = fit_all_margins(window)
            z = std_resid_matrix(fits)
            if len(z) < 200:
                continue
            bands = decompose_residuals(z)
            u_h1 = to_uniforms(bands["H1"])
            wc = select_copula(u_h1)
            # benchmark: gaussian on raw std residuals (no wavelet)
            u_raw = to_uniforms(z)
            from src.copulas_fit import fit_gaussian

            g = fit_gaussian(u_raw.to_numpy())
            risk_wc = portfolio_var_es(wc, fits, TICKERS, N_SIM, rng)
            risk_g = portfolio_var_es(g, fits, TICKERS, N_SIM, rng)
            cache_wc = (wc, fits, risk_wc)
            cache_g = (g, fits, risk_g)
            # hold forecasts for next `step` days
            hold_end_loc = min(loc + step - 1, len(dates) - 1)
            cache_until = dates[hold_end_loc]
            if i % 5 == 0:
                print(f"  refit @ {dt.date()} H1={wc.family} λL={wc.lambda_l:.3f}  ({time.time()-t0:.0f}s)", flush=True)

        rp = float(returns.loc[dt, TICKERS].mean())
        _, _, r_wc = cache_wc
        _, _, r_g = cache_g
        records.append(
            {
                "date": dt,
                "r_p": rp,
                "var95_wc": r_wc.var_95,
                "es95_wc": r_wc.es_95,
                "var99_wc": r_wc.var_99,
                "es99_wc": r_wc.es_99,
                "var95_g": r_g.var_95,
                "es95_g": r_g.es_95,
                "var99_g": r_g.var_99,
                "es99_g": r_g.es_99,
                "hit95_wc": int(rp < -r_wc.var_95),
                "hit99_wc": int(rp < -r_wc.var_99),
                "hit95_g": int(rp < -r_g.var_95),
                "hit99_g": int(rp < -r_g.var_99),
            }
        )

    df = pd.DataFrame(records).set_index("date")
    summary = {}
    for label, hit_col, var_col, es_col, alpha in [
        ("wc_95", "hit95_wc", "var95_wc", "es95_wc", 0.05),
        ("wc_99", "hit99_wc", "var99_wc", "es99_wc", 0.01),
        ("g_95", "hit95_g", "var95_g", "es95_g", 0.05),
        ("g_99", "hit99_g", "var99_g", "es99_g", 0.01),
    ]:
        bt = full_var_backtest(df[hit_col].to_numpy(), alpha)
        es = es_shortfall_stats(df["r_p"].to_numpy(), df[var_col].to_numpy(), df[es_col].to_numpy())
        summary[label] = {
            "n": bt.n,
            "hits": bt.hits,
            "hit_rate": bt.hit_rate,
            "expected": bt.expected,
            "lr_uc": bt.lr_uc,
            "p_uc": bt.p_uc,
            "lr_ind": bt.lr_ind,
            "p_ind": bt.p_ind,
            "lr_cc": bt.lr_cc,
            "p_cc": bt.p_cc,
            **es,
            "mean_var": float(df[var_col].mean()),
            "mean_es": float(df[es_col].mean()),
        }
    return df, summary


def make_figures(band_df: pd.DataFrame, oos: pd.DataFrame) -> None:
    REPORT_ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # λ_L by band for AIC winners
    winners = band_df[band_df["family"].astype(str).str.startswith("AIC_winner")]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(winners["band"], winners["lambda_l"], color="#1f4e79")
    ax.set_ylabel(r"Lower-tail dependence $\lambda_L$")
    ax.set_xlabel("Horizon band")
    ax.set_title("AIC-selected copula: $\\lambda_L$ by investment horizon")
    fig.tight_layout()
    fig.savefig(REPORT_ASSETS / "lambda_l_by_band.png", dpi=150)
    fig.savefig(OUTPUT_DIR / "lambda_l_by_band.png", dpi=150)
    plt.close(fig)

    # OOS VaR vs returns
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(oos.index, oos["r_p"], color="#888", lw=0.6, label="Portfolio return")
    ax.plot(oos.index, -oos["var95_wc"], color="#c0392b", lw=1.0, label="WC −VaR 95%")
    ax.plot(oos.index, -oos["var95_g"], color="#2980b9", lw=1.0, ls="--", label="Gaussian −VaR 95%")
    ax.set_title("OOS 2020+: equal-weight sector portfolio vs 95% VaR")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(REPORT_ASSETS / "oos_var_paths.png", dpi=150)
    fig.savefig(OUTPUT_DIR / "oos_var_paths.png", dpi=150)
    plt.close(fig)


def write_recommendation(band_df: pd.DataFrame, summary: dict) -> str:
    winners = band_df[band_df["family"].astype(str).str.startswith("AIC_winner")].set_index("band")
    lam = {b: float(winners.loc[b, "lambda_l"]) if b in winners.index else float("nan") for b in ["H1", "H2", "H3"]}
    fam = str(winners.loc["H1", "family"]).replace("AIC_winner:", "") if "H1" in winners.index else "?"
    wr = summary["wc_95"]["hit_rate"] * 100
    gr = summary["g_95"]["hit_rate"] * 100
    es_wc = summary["wc_99"]["mean_es"]
    es_g = summary["g_99"]["mean_es"]
    text = (
        f"Desk / book: Sector ETF equal-weight prototype (XLE,XLF,XLK,XLV,XLI,XLU,SPY)\n"
        f"Regulatory LH anchor: 10d ES / internal 1d limit\n"
        f"Horizon diagnostic: λ_L(H1)={lam['H1']:.3f}, λ_L(H2)={lam['H2']:.3f}, λ_L(H3)={lam['H3']:.3f}; "
        f"AIC winner H1: {fam}\n"
        f"Stress contrast: OOS 2020–present 95% VaR hit rate wavelet–copula {wr:.2f}% vs Gaussian {gr:.2f}% "
        f"(expected 5%); mean 99% ES WC={es_wc:.4f} vs Gaussian={es_g:.4f}\n"
        f"Action: "
    )
    if lam["H3"] - lam["H1"] > 0.15 or (es_g > 0 and es_wc > 1.25 * es_g):
        text += (
            "Tighten tactical limits and size hedges to the H1 band; elevated coarse-horizon "
            "tail dependence also flags strategic diversification for SA high-ρ review.\n"
        )
    elif wr < gr:
        text += (
            "Prefer horizon-matched (H1) AIC copula ES for daily limits; single-horizon Gaussian "
            "produced worse VaR coverage in the COVID+ OOS window.\n"
        )
    else:
        text += (
            "Retain Gaussian as core capital engine but monitor λ_L by horizon monthly; "
            "wavelet–copula is an internal overlay until PLA-validated.\n"
        )
    text += (
        "Governance note: Wavelet–copula is an internal overlay; FRTB capital remains HS / MAR33 ES "
        "until validated.\n"
    )
    return text


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_ASSETS.mkdir(parents=True, exist_ok=True)
    print("== Quant Edge Round 1 pipeline ==")
    print("Downloading / loading prices...")
    prices = download_prices()
    rets = log_returns(prices)
    print(f"  prices {prices.index.min().date()} → {prices.index.max().date()}  n={len(prices)}")

    # In-sample through 2019 for scale λ_L
    train = rets.loc[: "2019-12-31"]
    print("Fitting in-sample GARCH margins (≤2019)...")
    fits = fit_all_margins(train)
    z = std_resid_matrix(fits)
    print("MODWT + copulas by horizon band...")
    band_df = analyze_bands(z)
    band_df.to_csv(OUTPUT_DIR / "band_copula_results.csv", index=False)
    print(band_df.to_string(index=False))

    print(f"Rolling OOS from {OOS_START} (refit every {_refit_step()} days)...")
    oos, summary = rolling_oos(rets)
    oos.to_csv(OUTPUT_DIR / "oos_forecasts.csv")
    with open(OUTPUT_DIR / "backtest_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    make_figures(band_df, oos)
    rec = write_recommendation(band_df, summary)
    (OUTPUT_DIR / "manager_recommendation.txt").write_text(rec)
    print("\n== Manager recommendation ==")
    print(rec)

    # point-in-time risk comparison on last window
    rng = np.random.default_rng(SEED)
    last = rets.iloc[-WINDOW:]
    fits_l = fit_all_margins(last)
    z_l = std_resid_matrix(fits_l)
    bands = decompose_residuals(z_l)
    wc = select_copula(to_uniforms(bands["H1"]))
    from src.copulas_fit import fit_gaussian

    g = fit_gaussian(to_uniforms(z_l).to_numpy())
    r_wc = portfolio_var_es(wc, fits_l, TICKERS, N_SIM, rng)
    r_g = portfolio_var_es(g, fits_l, TICKERS, N_SIM, rng)
    point = {
        "wc_family": wc.family,
        "wc_lambda_l": wc.lambda_l,
        "var95_wc": r_wc.var_95,
        "es95_wc": r_wc.es_95,
        "var99_wc": r_wc.var_99,
        "es99_wc": r_wc.es_99,
        "var95_g": r_g.var_95,
        "es95_g": r_g.es_95,
        "var99_g": r_g.var_99,
        "es99_g": r_g.es_99,
        "delta_es99": r_wc.es_99 - r_g.es_99,
    }
    with open(OUTPUT_DIR / "point_risk.json", "w") as f:
        json.dump(point, f, indent=2)
    print("Point risk:", json.dumps(point, indent=2))
    print(f"\nOutputs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
