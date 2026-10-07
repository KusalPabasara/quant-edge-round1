"""Sub-period backtests and refit-stability figure, computed from the saved OOS forecasts.

    .venv/bin/python -m src.subperiods
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.backtest import evaluate
from src.config import OUTPUT_DIR, REPORT_ASSETS

SUBPERIODS = {
    "2020 (COVID)": ("2020-01-01", "2020-12-31"),
    "2021-2022 (rate shock)": ("2021-01-01", "2022-12-31"),
    "2023-2026 (calm)": ("2023-01-01", "2026-12-31"),
}
SUB_MODELS = ("raw-gaussian", "raw-student", "raw-clayton", "H1-student", "FHS", "HS")
SUB_ALPHA = 0.025


def subperiod_table(daily: pd.DataFrame, alpha: float = SUB_ALPHA) -> dict:
    out = {}
    for name, (a, b) in SUBPERIODS.items():
        blk = daily.loc[a:b]
        r = blk["realised"].to_numpy()
        out[name] = {"n": int(len(blk))}
        for m in SUB_MODELS:
            ev = evaluate(r, blk[f"{m}|VaR{alpha}"].to_numpy(), blk[f"{m}|ES{alpha}"].to_numpy(), alpha)
            out[name][m] = {k: ev[k] for k in ("hits", "hit_rate", "p_uc", "mf_p_value", "exc_loss_over_es", "fz0", "mean_es")}
    return out


def fig_refit(aic: pd.DataFrame, daily: pd.DataFrame, alpha: float = SUB_ALPHA) -> None:
    dates = pd.to_datetime(aic["date"])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.0))
    for src, col in (("raw", "#1f4e79"), ("H1", "#c0392b"), ("H2", "#27ae60")):
        axes[0].plot(dates, aic[f"{src}-student"] - aic[f"{src}-gaussian"], color=col, lw=1.1, label=src)
    axes[0].axhline(0, color="k", lw=0.6)
    axes[0].set_title("(a) AIC(t) − AIC(Gaussian) at each refit (below 0: t preferred)", fontsize=8.5)
    axes[0].legend(fontsize=7)
    g = daily[f"raw-gaussian|ES{alpha}"]
    for m, col in (("raw-student", "#c0392b"), ("raw-clayton", "#e67e22"), ("FHS", "#7f8c8d")):
        axes[1].plot(daily.index, daily[f"{m}|ES{alpha}"] / g, color=col, lw=0.9, label=m)
    axes[1].axhline(1, color="k", lw=0.6)
    axes[1].set_title(f"(b) 1-day ES {1 - alpha:.1%} relative to the Gaussian copula", fontsize=8.5)
    axes[1].legend(fontsize=7)
    for ax in axes:
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    for d in (REPORT_ASSETS, OUTPUT_DIR):
        fig.savefig(d / "fig_refit_stability.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def run(daily: pd.DataFrame, aic: pd.DataFrame) -> dict:
    res = subperiod_table(daily)
    g = daily[f"raw-gaussian|ES{SUB_ALPHA}"]
    res["es_ratio_quantiles"] = {
        m: {q: float(np.quantile(daily[f"{m}|ES{SUB_ALPHA}"] / g, float(q))) for q in ("0.1", "0.5", "0.9")}
        for m in ("raw-student", "raw-clayton", "FHS")
    }
    (OUTPUT_DIR / "backtest_subperiods.json").write_text(json.dumps(res, indent=2, default=float))
    fig_refit(aic, daily)
    return res


if __name__ == "__main__":
    daily = pd.read_csv(OUTPUT_DIR / "oos_daily_forecasts.csv", index_col=0, parse_dates=True)
    aic = pd.read_csv(OUTPUT_DIR / "oos_refit_aic.csv")
    r = run(daily, aic)
    for k, v in r.items():
        if k != "es_ratio_quantiles":
            print(k, v["n"], {m: (v[m]["hits"], round(v[m]["mf_p_value"], 3), round(v[m]["exc_loss_over_es"], 2)) for m in SUB_MODELS})
    print(r["es_ratio_quantiles"])
