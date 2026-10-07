#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="submission/QuantEdge_Round1_submission.zip"
mkdir -p submission
rm -f "$OUT"

# Exclude venvs, caches, large intermediates
zip -r "$OUT" \
  README.md \
  requirements.txt \
  Makefile \
  src \
  scripts \
  report/QuantEdge_Round1_Report.pdf \
  report/assets \
  outputs/band_copula_results.csv \
  outputs/backtest_summary.json \
  outputs/manager_recommendation.txt \
  outputs/point_risk.json \
  outputs/oos_forecasts.csv \
  outputs/lambda_l_by_band.png \
  outputs/oos_var_paths.png \
  data/etf_prices.csv \
  data/download_meta.txt \
  reports/Wavelet\ copula\ horizon\ risk.md \
  research_notes \
  20261002114514_36365bae65d9.pdf \
  -x '*/__pycache__/*' '*.pyc' '.venv/*' 'submission/*'

ls -lh "$OUT"
echo "ZIP ready: $OUT"
echo
echo "=== Drive checklist ==="
echo "1. Upload this folder (or ZIP) to Google Drive"
echo "2. Share: Anyone with the link can view (or grant judges full access)"
echo "3. Paste the Drive link as External Project Link"
echo "4. Submit ZIP as General / Final Submission before 23:59 SL time"
