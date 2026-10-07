# SAIFA Quant Edge 1.0, Round 1

**Risk Across Tails and Timescales**
Does lower-tail dependence change with the investment horizon, and what does ignoring that do to 1-day, 5-day and 20-day VaR and Expected Shortfall? A wavelet–copula study on an equal-weight US sector ETF portfolio, tested out of sample.

## Reproduce

```bash
make install     # once: creates .venv and installs requirements.txt
make test        # unit tests, about 2 seconds
make reproduce   # full pipeline + report PDF, about 5 minutes on a laptop
make zip         # builds submission/QuantEdge_Round1_submission.zip (fails if > 25 MB)
```

`make reproduce` runs `python -m src.run_all` and then `python scripts/build_report_pdf.py`. Every number in `report/QuantEdge_Round1_Report.pdf` is read from `outputs/*.json`; nothing in the report is typed by hand. The report builder fails if the body exceeds 10 pages.

Prices are cached in `data/etf_prices.csv` with a fixed end date (`src/config.py`), so reruns use identical data. Delete the CSV to re-download from Yahoo Finance. The seed is 42.

## Design

| Piece | Choice |
|-------|--------|
| Assets | Equal-weight XLE, XLF, XLK, XLV, XLI, XLU, SPY; 1999-01-05 to 2026-09-30 |
| Margins | GARCH(1,1) with Student-t innovations; volatility filtered daily out of sample |
| Horizons | MODWT multiresolution analysis (db2, J = 6), boundary-trimmed: H1 = 2–8 days, H2 = 8–32 days, H3 > 32 days |
| Copulas | Full-likelihood 7-dimensional Gaussian, Student-t and Clayton, with comparable AIC |
| Model-free check | Empirical λ_L(q) with paired stationary-bootstrap intervals; crisis versus calm windows |
| Out of sample | 2020-01-02 onward; 1,000-day window, refit every 20 days, 20,000 simulations |
| Ablation | {raw, H1} × {Gaussian, t, Clayton}, plus FHS and HS |
| Multi-day ES | 5 and 20 days: sqrt-time Gaussian and t, daily t path-sum, horizon-matched band copula |
| Backtests | Kupiec, Christoffersen, McNeil–Frey, FZ0 loss with Diebold–Mariano tests |

## Main findings

- In calm periods, model-free tail dependence is flat across horizons (H3 − H1 = −0.03, p = 0.31). In the GFC and COVID windows, it jumps to about 0.9 at the long horizon.
- The t copula wins AIC in every band and at every refit, but its parametric λ_L falls with horizon only because ν rises. The model-free estimate does not fall.
- Out of sample, the wavelet band adds nothing measurable to 1-day forecasts. The copula family matters: Gaussian-copula ES is rejected by McNeil–Frey at 95%, 97.5% and 99%, and the failures are concentrated in 2020.
- For 20-day ES, sqrt-time scaling is about 17% higher than an iid path simulation, and the lower path ES is the one the backtest rejects.

The full argument, tables and the risk-manager recommendation are in the report.

## Layout

```
src/            pipeline: data, margins, modwt, copulas_fit, tail_np, oos, horizon, backtest, subperiods, run_all
tests/          pytest suite (MRA reconstruction, copula densities vs copulae, tail formulas, backtests)
outputs/        JSON/CSV/PNG produced by the run
report/         PDF and figure assets
scripts/        report builder and ZIP builder
research_notes/ literature notes; reports/ research brief
data/           cached ETF prices
```

## AI disclosure

AI coding assistants helped with literature search, code scaffolding, debugging, tests and report drafting. The team chose the question, data, model design and validation protocol, reviewed the code, and is responsible for every claim. Details are in Appendix A of the report.
