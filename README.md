# SAIFA Quant Edge 1.0 — Round 1

**Risk Across Tails and Timescales**  
Wavelet–copula market-risk framework for multi-horizon lower-tail dependence on a US sector ETF portfolio.

## One-command reproduce

```bash
make reproduce
```

Or manually:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
QUANT_EDGE_FAST=1 .venv/bin/python -m src.run_all
.venv/bin/python scripts/build_report_pdf.py
```

This regenerates every number and figure used in `report/QuantEdge_Round1_Report.pdf` under `outputs/` and `report/assets/`.

Set `QUANT_EDGE_FAST=0` for denser OOS refits (every 20 trading days instead of 120).

## Research question

Does tail dependence change with the investment horizon, and what does ignoring this do to measured portfolio risk?

## Locked design (short)

| Piece | Choice |
|-------|--------|
| Assets | Equal-weight XLE, XLF, XLK, XLV, XLI, XLU, SPY |
| Data | Yahoo Finance daily adjusted closes from 1999 |
| Margins | GARCH(1,1)-t → PIT uniforms |
| Wavelets | MODWT db2, J=6 → bands H1/H2/H3 |
| Copulas | Gaussian, Student-t, Clayton; AIC select |
| Risk | 1-day VaR/ES 95% & 99% (MC, seed=42) |
| Benchmark | Single-horizon Gaussian (no wavelets) |
| OOS | 2020→ ; window 750; refit 120d (fast) |

## Key result (from last run)

- λ_L (Clayton) ≈ **0.66–0.69** across H1/H2/H3 (high at all horizons).
- OOS 95% VaR hit rate: **wavelet–copula ~5.2%** vs **Gaussian ~7.0%** (target 5%).
- Mean 99% ES: WC **higher** than Gaussian (~28% understatement if tails ignored).

See `outputs/manager_recommendation.txt` for the actionable desk note.

## Layout

```
src/           pipeline (data → margins → MODWT → copulas → risk → backtest)
outputs/       CSV/JSON/PNG from the run
report/        PDF + figure assets
scripts/       PDF builder
research_notes/  literature notes
reports/       synthesized research brief
data/          cached ETF prices (or re-downloaded)
```

## AI disclosure

AI tools assisted with literature synthesis, coding, debugging, and drafting. The team is responsible for every methodological choice, line of code, and claim. Material AI use is also disclosed in the report appendix.

## Competition checklist

1. Run `make reproduce` and confirm `report/QuantEdge_Round1_Report.pdf` exists.
2. Zip the submission (see `scripts/make_submission_zip.sh`).
3. Upload ZIP (≤25 MB) + Google Drive link with open access.
4. Form type: **General / Final Submission**. Deadline: **7 Oct 2026 23:59 Sri Lanka time**.
