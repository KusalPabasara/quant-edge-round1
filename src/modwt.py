"""MODWT and its multiresolution analysis (Percival & Walden 2000, ch. 5).

Computed in the frequency domain: the level-j MODWT wavelet filter has transfer
function H_j(f) = H(2^{j-1} f) * prod_{l<j-1} G(2^l f), with the DWT filters
rescaled by 1/sqrt(2). MRA details are D_j = IDFT(|H_j|^2 X), the smooth is
S_J = IDFT(|G_J|^2 X); they are zero-phase and sum exactly to the input.
"""

from __future__ import annotations

import numpy as np
import pywt

BANDS = {"H1": (1, 2), "H2": (3, 4), "H3": (5, 6)}  # H3 also carries the smooth S_J


def _transfer(wavelet: str, n: int, level: int) -> tuple[list[np.ndarray], np.ndarray]:
    w = pywt.Wavelet(wavelet)
    g = np.asarray(w.dec_lo, dtype=np.float64) / np.sqrt(2.0)
    h = np.asarray(w.dec_hi, dtype=np.float64) / np.sqrt(2.0)
    G = np.fft.fft(g, n)
    H = np.fft.fft(h, n)
    k = np.arange(n)
    hj, gprod = [], np.ones(n, dtype=complex)
    for j in range(1, level + 1):
        idx = (k * 2 ** (j - 1)) % n
        hj.append(H[idx] * gprod)
        gprod = gprod * G[idx]
    return hj, gprod


def modwt_mra(x: np.ndarray, wavelet: str = "db2", level: int = 6, reflect: bool = True) -> tuple[list[np.ndarray], np.ndarray]:
    """Return (details D_1..D_J, smooth S_J), each the length of x; sum(details)+smooth == x."""
    x = np.asarray(x, dtype=np.float64).ravel()
    n = len(x)
    xe = np.concatenate([x, x[::-1]]) if reflect else x
    hj, gj = _transfer(wavelet, len(xe), level)
    X = np.fft.fft(xe)
    details = [np.fft.ifft(np.abs(h) ** 2 * X).real[:n] for h in hj]
    smooth = np.fft.ifft(np.abs(gj) ** 2 * X).real[:n]
    return details, smooth


def boundary_len(level: int, wavelet: str = "db2") -> int:
    """Number of MODWT coefficients at level j affected by the boundary: L_j = (2^j - 1)(L - 1) + 1."""
    L = pywt.Wavelet(wavelet).dec_len
    return (2**level - 1) * (L - 1) + 1


def mra_bands(details: list[np.ndarray], smooth: np.ndarray) -> dict[str, np.ndarray]:
    out = {}
    for name, (a, b) in BANDS.items():
        band = details[a - 1] + details[b - 1]
        if name == "H3":
            band = band + smooth
        out[name] = band
    return out


def band_trim(name: str, wavelet: str = "db2") -> int:
    return boundary_len(BANDS[name][1], wavelet)
