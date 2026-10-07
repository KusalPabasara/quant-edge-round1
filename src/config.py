"""Locked design constants for Quant Edge Round 1."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
REPORT_ASSETS = ROOT / "report" / "assets"

TICKERS = ["XLE", "XLF", "XLK", "XLV", "XLI", "XLU", "SPY"]
START = "1999-01-01"
END = "2026-09-30"  # inclusive; fixed so every run sees the same sample

SEED = 42
N_SIM = 20_000
ALPHAS = (0.05, 0.025, 0.01)  # 95%, 97.5% (FRTB ES level) and 99%

TRAIN_END = "2019-12-31"
OOS_START = "2020-01-01"
WINDOW = 1000  # rolling estimation window (trading days); must exceed the J=6 boundary length
REFIT_EVERY = 20
HS_WINDOW = 500

J_LEVELS = 6
WAVELET = "db2"
HORIZONS = (1, 5, 20)

TAIL_QS = (0.05, 0.10)
N_BOOT = 500
BLOCK_LEN = 20

CRISIS_WINDOWS = {
    "GFC 2007-09": ("2007-07-01", "2009-06-30"),
    "COVID 2020": ("2020-02-01", "2020-12-31"),
}
