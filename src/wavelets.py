"""MODWT on standardized residuals → H1/H2/H3 band matrices."""

from __future__ import annotations

import pandas as pd

from src.config import J_LEVELS, WAVELET
from src.modwt import modwt, mra_bands


def decompose_residuals(z: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return aligned H-band DataFrames with same columns/index as z."""
    bands: dict[str, dict[str, pd.Series]] = {"H1": {}, "H2": {}, "H3": {}}
    for col in z.columns:
        details, smooth = modwt(z[col].to_numpy(), wavelet=WAVELET, level=J_LEVELS)
        mb = mra_bands(details, smooth)
        for name, arr in mb.items():
            bands[name][col] = pd.Series(arr, index=z.index)
    return {k: pd.DataFrame(v)[z.columns] for k, v in bands.items()}
