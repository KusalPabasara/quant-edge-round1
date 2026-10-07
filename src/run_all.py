"""
One-command reproduction for SAIFA Quant Edge Round 1.

    .venv/bin/python -m src.run_all

Writes every table, figure and number used in the report to outputs/ and report/assets/.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.backtest import diebold_mariano, evaluate, fz0_loss
from src.config import (
    ALPHAS, CRISIS_WINDOWS, END, HORIZONS, J_LEVELS, N_BOOT, N_SIM, OOS_START, OUTPUT_DIR,
    REFIT_EVERY, REPORT_ASSETS, SEED, START, TAIL_QS, TICKERS, TRAIN_END, WAVELET, WINDOW,
)
from src.copulas_fit import fit_all_families
from src.data import download_prices, log_returns
from src.margins import fit_all_margins, std_resid_matrix, to_uniforms
from src.modwt import modwt_mra
from src import subperiods
from src.oos import FAMILIES, H_METHODS, MODEL_NAMES, run_oos
from src.tail_np import band_tail_table, horizon_tail_table, regime_tail_table
from src.wavelets import decompose_residuals

BLUE, RED, GREY, GREEN, ORANGE = "#1f4e79", "#c0392b", "#7f8c8d", "#27ae60", "#e67e22"


def _save(fig, name: str) -> None:
    for d in (REPORT_ASSETS, OUTPUT_DIR):
        fig.savefig(d / name, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _dump(obj, name: str) -> None:
    (OUTPUT_DIR / name).write_text(json.dumps(obj, indent=2, default=float))


# ---------------------------------------------------------------- in-sample

def insample_copulas(bands: dict[str, pd.DataFrame]) -> dict:
    out = {}
    for name, mat in bands.items():
        fits = fit_all_families(to_uniforms(mat))
        rows = {}
        for f in fits:
            rows[f.family] = {
                "loglik": f.loglik, "k": f.k, "aic": f.aic, "lambda_l": f.lambda_l, "lambda_u": f.lambda_u,
                **{p: f.params[p] for p in ("nu", "theta", "rho_avg") if p in f.params},
            }
        out[name] = {"n": int(len(mat)), "families": rows, "winner": min(rows, key=lambda k: rows[k]["aic"])}
    return out


# ---------------------------------------------------------------- figures

def fig_mra(z: pd.DataFrame) -> dict:
    details, smooth = modwt_mra(z["SPY"].to_numpy(), WAVELET, J_LEVELS)
    comps = details + [smooth]
    labels = [f"D{j}" for j in range(1, J_LEVELS + 1)] + [f"S{J_LEVELS}"]
    days = [f"{2**j}-{2**(j+1)}d" for j in range(1, J_LEVELS + 1)] + [f">{2**(J_LEVELS+1)}d"]
    tail = slice(-500, None)
    fig, axes = plt.subplots(len(comps) + 1, 1, figsize=(8, 7.5), sharex=True)
    axes[0].plot(z.index[tail], z["SPY"].to_numpy()[tail], color=GREY, lw=0.6)
    axes[0].set_ylabel("z", rotation=0, labelpad=12, fontsize=8)
    for ax, c, lab, dd in zip(axes[1:], comps, labels, days):
        ax.plot(z.index[tail], c[tail], color=BLUE, lw=0.7)
        ax.set_ylabel(f"{lab}\n{dd}", rotation=0, labelpad=22, fontsize=7)
    for ax in axes:
        ax.tick_params(labelsize=7)
    axes[0].set_title("MODWT multiresolution analysis of SPY standardized residuals (last 500 days of training)", fontsize=9)
    _save(fig, "fig_mra_spy.png")
    var = np.var(z["SPY"].to_numpy())
    return {lab: float(np.var(c) / var) for lab, c in zip(labels, comps)}


def fig_tail(band_np: dict, hor_np: dict, regime: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    order = ["raw", "H1", "H2", "H3"]
    for q, col, off in ((0.05, BLUE, -0.15), (0.10, ORANGE, 0.15)):
        b = band_np["q"][str(q)]["bands"]
        est = [b[k]["est"] for k in order]
        err = [[b[k]["est"] - b[k]["lo"] for k in order], [b[k]["hi"] - b[k]["est"] for k in order]]
        axes[0].errorbar(np.arange(4) + off, est, yerr=err, fmt="o", color=col, capsize=3, label=f"q={q:.0%}")
        hs = [str(h) for h in HORIZONS]
        e2 = [hor_np[h][str(q)]["est"] for h in hs]
        r2 = [[hor_np[h][str(q)]["est"] - hor_np[h][str(q)]["lo"] for h in hs], [hor_np[h][str(q)]["hi"] - hor_np[h][str(q)]["est"] for h in hs]]
        axes[1].errorbar(np.arange(len(hs)) + off, e2, yerr=r2, fmt="o", color=col, capsize=3, label=f"q={q:.0%}")
    axes[0].set_xticks(range(4), ["daily", "H1 2-8d", "H2 8-32d", "H3 >32d"], fontsize=8)
    axes[0].set_title("(a) Wavelet bands, 1999-2019", fontsize=9)
    axes[1].set_xticks(range(len(HORIZONS)), [f"{h}-day sums" for h in HORIZONS], fontsize=8)
    axes[1].set_title("(b) Non-overlapping h-day returns", fontsize=9)
    for ax in axes[:2]:
        ax.set_ylabel(r"empirical $\lambda_L(q)$", fontsize=8)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=7)
    regs = list(regime)
    for i, r in enumerate(regs):
        axes[2].bar(np.arange(4) + (i - 1) * 0.27, [regime[r][k]["est"] for k in order], width=0.27, label=r,
                    color=[RED, ORANGE, GREY][i])
    axes[2].set_xticks(range(4), ["daily", "H1", "H2", "H3"], fontsize=8)
    axes[2].set_title(r"(c) Crisis vs calm, $\lambda_L(10\%)$", fontsize=9)
    axes[2].set_ylim(0, 1)
    axes[2].legend(fontsize=7)
    fig.tight_layout()
    _save(fig, "fig_tail_dependence.png")


def fig_oos(dates, realised, daily) -> None:
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.plot(dates, realised, color=GREY, lw=0.5, label="Portfolio return")
    for m, col, ls in (("raw-gaussian", BLUE, "--"), ("raw-student", RED, "-"), ("HS", GREEN, ":")):
        ax.plot(dates, -daily[m][0.01]["var"], color=col, lw=0.9, ls=ls, label=f"{m} -VaR 99%")
    hits = realised < -daily["raw-student"][0.01]["var"]
    ax.scatter(dates[hits], realised[hits], color=RED, s=8, zorder=5, label="t-copula exceedance")
    ax.set_title("Out-of-sample 2020-2026: daily VaR 99% (re-scaled every day by GARCH volatility)", fontsize=9)
    ax.legend(fontsize=7, ncol=3)
    ax.tick_params(labelsize=7)
    _save(fig, "fig_oos_var.png")


def fig_horizon(hres: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    cols = [BLUE, ORANGE, GREEN, RED]
    for ax, h in zip(axes, [k for k in hres]):
        r = hres[h]
        x = np.arange(len(ALPHAS))
        for i, m in enumerate(H_METHODS):
            ax.bar(x + (i - 1.5) * 0.2, [r[m][str(a)]["mean_es"] for a in ALPHAS], width=0.2, color=cols[i], label=m)
        ax.scatter(x, [r["realised_tail_mean"][str(a)] for a in ALPHAS], marker="_", s=600, color="k", zorder=5,
                   label="Realised mean of worst α share")
        ax.set_xticks(x, [f"ES {1 - a:.1%}" for a in ALPHAS], fontsize=8)
        ax.set_title(f"{h}-day horizon (n={r['n']} non-overlapping)", fontsize=9)
        ax.tick_params(labelsize=7)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7, ncol=5, loc="lower center", frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    _save(fig, "fig_horizon_es.png")


# ---------------------------------------------------------------- OOS evaluation

def evaluate_daily(oos: dict) -> dict:
    r = oos["realised"]
    out = {"models": {}, "dm": {}}
    for m in MODEL_NAMES:
        out["models"][m] = {str(a): evaluate(r, oos["daily"][m][a]["var"], oos["daily"][m][a]["es"], a) for a in ALPHAS}
    pairs = [(m, "raw-gaussian") for m in MODEL_NAMES if m != "raw-gaussian"]
    pairs += [(f"H1-{f}", f"raw-{f}") for f in FAMILIES] + [("raw-student", "FHS")]
    for a in ALPHAS:
        loss = {m: fz0_loss(r, oos["daily"][m][a]["var"], oos["daily"][m][a]["es"], a) for m in MODEL_NAMES}
        out["dm"][str(a)] = {f"{x} vs {y}": dict(zip(("stat", "p"), diebold_mariano(loss[x], loss[y]))) for x, y in pairs}
    return out


def evaluate_horizon(hrec: dict) -> dict:
    out = {}
    for h, rows in hrec.items():
        realised = np.array([row["realised"] for row in rows])
        res = {"n": len(rows)}
        for m in H_METHODS:
            res[m] = {}
            for a in ALPHAS:
                v = np.array([row[(m, a)][0] for row in rows])
                e = np.array([row[(m, a)][1] for row in rows])
                res[m][str(a)] = evaluate(realised, v, e, a)
        res["realised_tail_mean"] = {}
        for a in ALPHAS:
            k = max(int(np.floor(a * len(realised))), 1)
            res["realised_tail_mean"][str(a)] = float(-np.sort(realised)[:k].mean())
        res["es_ratio_vs_sqrt_gauss"] = {
            m: {str(a): res[m][str(a)]["mean_es"] / res[H_METHODS[0]][str(a)]["mean_es"] for a in ALPHAS} for m in H_METHODS
        }
        res["dm_vs_sqrt_gauss"] = {}
        for a in ALPHAS:
            base = fz0_loss(realised, np.array([row[(H_METHODS[0], a)][0] for row in rows]),
                            np.array([row[(H_METHODS[0], a)][1] for row in rows]), a)
            res["dm_vs_sqrt_gauss"][str(a)] = {}
            for m in H_METHODS[1:]:
                lm = fz0_loss(realised, np.array([row[(m, a)][0] for row in rows]), np.array([row[(m, a)][1] for row in rows]), a)
                res["dm_vs_sqrt_gauss"][str(a)][m] = dict(zip(("stat", "p"), diebold_mariano(lm, base)))
        out[str(h)] = res
    return out


# ---------------------------------------------------------------- recommendation

def recommendation(ins: dict, band_np: dict, regime: dict, daily_ev: dict, hor: dict) -> dict:
    q = "0.05"
    b = band_np["q"][q]
    m1 = daily_ev["models"]
    a = "0.025"
    best_1d = min(MODEL_NAMES, key=lambda m: m1[m][a]["fz0"])
    h20 = hor["20"]
    sqrt_g = h20[H_METHODS[0]][a]
    best_h = min(H_METHODS, key=lambda m: h20[m][a]["fz0"])
    ratio = h20["es_ratio_vs_sqrt_gauss"][best_h][a]
    calm = regime["Calm (other days)"]["H3"]["est"]
    crisis = max(regime[k]["H3"]["est"] for k in CRISIS_WINDOWS)
    return {
        "best_1d_model": best_1d,
        "best_1d_fz0": m1[best_1d][a]["fz0"],
        "raw_gaussian_hit_rate_99": m1["raw-gaussian"]["0.01"]["hit_rate"],
        "best_1d_hit_rate_99": m1[best_1d]["0.01"]["hit_rate"],
        "lambda_flat_p": b["p_diff"],
        "lambda_H1": b["bands"]["H1"]["est"],
        "lambda_H3": b["bands"]["H3"]["est"],
        "h3_calm": calm,
        "h3_crisis": crisis,
        "best_20d_method": best_h,
        "es20_ratio_best_vs_sqrt_gauss": ratio,
        "sqrt_gauss_20d_hit_rate_975": sqrt_g["hit_rate"],
        "best_20d_hit_rate_975": h20[best_h][a]["hit_rate"],
    }


def main() -> None:
    t0 = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_ASSETS.mkdir(parents=True, exist_ok=True)
    print("== Quant Edge Round 1: wavelet-copula multi-horizon risk ==")
    prices = download_prices()
    rets = log_returns(prices)
    meta = {"start": str(rets.index.min().date()), "end": str(rets.index.max().date()), "n_days": int(len(rets)),
            "tickers": TICKERS, "train_end": TRAIN_END, "oos_start": OOS_START, "window": WINDOW,
            "refit_every": REFIT_EVERY, "n_sim": N_SIM, "n_boot": N_BOOT, "seed": SEED, "wavelet": WAVELET,
            "levels": J_LEVELS, "config_start": START, "config_end": END}
    print(f"  {meta['start']} -> {meta['end']}  n={meta['n_days']}")

    print("[1/5] In-sample margins, MODWT-MRA and copulas (<= 2019)")
    fits = fit_all_margins(rets.loc[:TRAIN_END])
    z = std_resid_matrix(fits)
    meta["garch"] = {t: {"alpha": f.alpha, "beta": f.beta, "nu": f.nu} for t, f in fits.items()}
    bands = {"raw": z, **decompose_residuals(z)}
    meta["mra_variance_share_spy"] = fig_mra(z)
    ins = insample_copulas(bands)
    _dump(ins, "insample_copulas.json")
    for k, v in ins.items():
        print(f"  {k:4s} winner={v['winner']:8s} " + "  ".join(f"{f}:AIC={r['aic']:.0f}" for f, r in v["families"].items()))

    print("[2/5] Model-free tail dependence with stationary-bootstrap CIs")
    band_np = band_tail_table(bands, TAIL_QS)
    hor_np = horizon_tail_table(z, HORIZONS, TAIL_QS)
    z_full = std_resid_matrix(fit_all_margins(rets))
    regime = regime_tail_table({"raw": z_full, **decompose_residuals(z_full)}, CRISIS_WINDOWS, 0.10)
    _dump({"bands": band_np, "horizons": hor_np, "regimes": regime}, "tail_nonparametric.json")
    fig_tail(band_np, hor_np, regime)

    print("[3/5] Rolling out-of-sample engine (daily 1-day VaR/ES + 5d/20d ES)")
    oos = run_oos(rets)
    daily_df = pd.DataFrame({"realised": oos["realised"]}, index=oos["dates"])
    for m in MODEL_NAMES:
        for a in ALPHAS:
            daily_df[f"{m}|VaR{a}"] = oos["daily"][m][a]["var"]
            daily_df[f"{m}|ES{a}"] = oos["daily"][m][a]["es"]
    daily_df.to_csv(OUTPUT_DIR / "oos_daily_forecasts.csv", float_format="%.6f")
    aic = oos["aic_log"]
    aic.to_csv(OUTPUT_DIR / "oos_refit_aic.csv", index=False)
    win_share = {}
    for src in ("raw", "H1", "H2"):
        cols = [f"{src}-{f}" for f in FAMILIES]
        w = aic[cols].idxmin(axis=1).str.replace(f"{src}-", "")
        win_share[src] = {f: float((w == f).mean()) for f in FAMILIES}
    meta["oos_refits"] = int(len(aic))
    meta["oos_days"] = int(len(oos["dates"]))
    meta["oos_aic_win_share"] = win_share

    print("[4/5] Backtests: Kupiec, Christoffersen, McNeil-Frey, FZ0 + Diebold-Mariano")
    daily_ev = evaluate_daily(oos)
    _dump(daily_ev, "backtest_1d.json")
    hor = evaluate_horizon(oos["horizon"])
    _dump(hor, "backtest_horizon.json")
    fig_oos(oos["dates"], oos["realised"], oos["daily"])
    fig_horizon(hor)
    subperiods.run(daily_df, aic)

    print("[5/5] Recommendation inputs")
    rec = recommendation(ins, band_np, regime, daily_ev, hor)
    _dump(rec, "recommendation.json")
    meta["runtime_sec"] = time.time() - t0
    _dump(meta, "meta.json")

    for m in MODEL_NAMES:
        e = daily_ev["models"][m]
        print(f"  {m:13s} " + "  ".join(f"hit{1-float(a):.1%}={e[a]['hit_rate']:.2%} fz0={e[a]['fz0']:.3f}" for a in e))
    for h, r in hor.items():
        for m in H_METHODS:
            print(f"  {h:>2}d {m:20s} " + "  ".join(f"ES{1-float(a):.1%}={r[m][a]['mean_es']:.4f} hit={r[m][a]['hit_rate']:.2%}" for a in r[m]))
    print(json.dumps(rec, indent=2))
    print(f"Done in {meta['runtime_sec']:.0f}s. Outputs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
