"""Minimal MODWT (maximal overlap DWT) using NumPy circular convolution."""

from __future__ import annotations

import numpy as np
import pywt


def _circ_conv(x: np.ndarray, filt: np.ndarray) -> np.ndarray:
    """Circular convolution via FFT (periodized)."""
    n = len(x)
    m = len(filt)
    # FFT size
    N = n
    xf = np.fft.rfft(x, n=N)
    # filter padded / time-reversed for convolution convention of DWT
    # PyWavelets MODWT uses filtering with periodization
    ff = np.zeros(N, dtype=np.float64)
    ff[:m] = filt
    ff_f = np.fft.rfft(ff, n=N)
    return np.fft.irfft(xf * ff_f, n=N)


def modwt(x: np.ndarray, wavelet: str = "db2", level: int = 6) -> tuple[list[np.ndarray], np.ndarray]:
    """
    MODWT decomposition (circular / periodized).
    Returns (details[D1..DJ], smooth SJ) where D1 is highest frequency.
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    w = pywt.Wavelet(wavelet)
    h0 = np.asarray(w.dec_lo, dtype=np.float64) / np.sqrt(2.0)
    g0 = np.asarray(w.dec_hi, dtype=np.float64) / np.sqrt(2.0)

    details: list[np.ndarray] = []
    v = x.copy()
    for j in range(1, level + 1):
        up = 2 ** (j - 1)
        hj = np.zeros(len(h0) * up - (up - 1), dtype=np.float64)
        gj = np.zeros(len(g0) * up - (up - 1), dtype=np.float64)
        hj[::up] = h0
        gj[::up] = g0
        d = _circ_conv(v, gj)
        v = _circ_conv(v, hj)
        details.append(d)
    return details, v


def mra_bands(details: list[np.ndarray], smooth: np.ndarray) -> dict[str, np.ndarray]:
    """Aggregate MODWT details into H1/H2/H3 horizon bands (locked design)."""
    d = details
    h1 = d[0] + d[1]
    h2 = d[2] + d[3]
    h3 = d[4] + d[5] + smooth
    return {"H1": h1, "H2": h2, "H3": h3}
