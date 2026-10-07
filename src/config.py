"""Locked design constants for Quant Edge Round 1."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
REPORT_ASSETS = ROOT / "report" / "assets"

TICKERS = ["XLE", "XLF", "XLK", "XLV", "XLI", "XLU", "SPY"]
START = "1999-01-01"
END = None  # through run date

SEED = 42
N_SIM = 10_000
N_SIM_SENS = 50_000
ALPHAS = (0.05, 0.01)  # 95% and 99% VaR/ES

WINDOW = 750
REFIT_EVERY = 20
OOS_START = "2020-01-01"
J_LEVELS = 6
WAVELET = "db2"

# For speed on laptop: full rolling uses REFIT_EVERY; set FAST_MODE via env
FAST_REFIT_EVERY = 120  # used when QUANT_EDGE_FAST=1
