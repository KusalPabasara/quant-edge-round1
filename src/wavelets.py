"""MODWT-MRA horizon bands of standardized residuals, boundary-trimmed."""

from __future__ import annotations

import pandas as pd

from src.config import J_LEVELS, WAVELET
from src.modwt import band_trim, modwt_mra, mra_bands


def decompose_residuals(z: pd.DataFrame, trim: bool = True) -> dict[str, pd.DataFrame]:
    """H1/H2/H3 band DataFrames aligned with z; rows touched by the boundary are dropped per band."""
    cols: dict[str, dict[str, pd.Series]] = {}
    for c in z.columns:
        details, smooth = modwt_mra(z[c].to_numpy(), wavelet=WAVELET, level=J_LEVELS)
        for name, arr in mra_bands(details, smooth).items():
            cols.setdefault(name, {})[c] = pd.Series(arr, index=z.index)
    out = {}
    for name, d in cols.items():
        df = pd.DataFrame(d)[z.columns]
        if trim:
            b = band_trim(name, WAVELET)
            df = df.iloc[b:-b] if len(df) > 2 * b + 50 else df
        out[name] = df
    return out
