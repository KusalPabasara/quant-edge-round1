#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="submission/QuantEdge_Round1_submission.zip"
mkdir -p submission
rm -f "$OUT"

zip -r "$OUT" \
  README.md \
  requirements.txt \
  Makefile \
  src \
  scripts \
  tests \
  report/QuantEdge_Round1_Report.pdf \
  report/assets \
  outputs/insample_copulas.json \
  outputs/tail_nonparametric.json \
  outputs/backtest_1d.json \
  outputs/backtest_horizon.json \
  outputs/backtest_subperiods.json \
  outputs/recommendation.json \
  outputs/meta.json \
  outputs/oos_daily_forecasts.csv \
  outputs/oos_refit_aic.csv \
  data/etf_prices.csv \
  data/download_meta.txt \
  reports/Wavelet\ copula\ horizon\ risk.md \
  research_notes \
  -x '*/__pycache__/*' '*.pyc' '.venv/*' 'submission/*' '.pytest_cache/*'

SIZE=$(stat -c %s "$OUT")
ls -lh "$OUT"
if [ "$SIZE" -gt $((25 * 1024 * 1024)) ]; then
  echo "ERROR: ZIP exceeds 25 MB" >&2
  exit 1
fi
echo "ZIP ready: $OUT"
echo
echo "=== Drive checklist ==="
echo "1. Upload this folder (or ZIP) to Google Drive"
echo "2. Share: Anyone with the link can view (or grant judges full access)"
echo "3. Paste the Drive link as External Project Link"
echo "4. Submit ZIP as General / Final Submission before 23:59 SL time"
