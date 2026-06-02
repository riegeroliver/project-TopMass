"""``iminuit`` wrappers for the fit shapes used across the course.

Two scenarios:

- **Resolution fits (Chapter 1)** : Gaussian / double-sided Crystal Ball over
  ``(reco − truth)`` or ``reco / truth``.
- **Mass fits (Chapter 3)** : Gaussian (or Crystal Ball) signal on top of a
  smooth (polynomial) background, extracting ``m_top``.

All fits use the **binned negative-log-likelihood** form of `iminuit.cost`,
which works well for the histogram sizes typical in a first-year course.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares


# ---------------------------------------------------------------------------
# Shape functions
# ---------------------------------------------------------------------------

def gaussian(x: np.ndarray, n: float, mu: float, sigma: float) -> np.ndarray:
    """Normalisation × N(μ, σ)."""
    return n * np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def crystal_ball(x: np.ndarray, n: float, mu: float, sigma: float, alpha: float, m: float) -> np.ndarray:
    """One-sided Crystal Ball (low-side tail).

    Standard parameterisation: Gaussian core stitched to a power-law tail at
    ``alpha`` standard deviations from the mean.
    """
    alpha = abs(alpha)
    z = (x - mu) / sigma
    A = (m / alpha) ** m * np.exp(-0.5 * alpha * alpha)
    B = m / alpha - alpha
    out = np.where(
        z > -alpha,
        np.exp(-0.5 * z * z),
        A * np.power(np.clip(B - z, 1e-12, None), -m),
    )
    return n * out


def polynomial_bkg(x: np.ndarray, *coeffs: float) -> np.ndarray:
    """Plain polynomial: ``c0 + c1 x + c2 x² + …`` (use as smooth background)."""
    return np.polyval(list(coeffs[::-1]), x)


def signal_plus_bkg(
    x: np.ndarray,
    n_sig: float, mu: float, sigma: float,
    c0: float, c1: float, c2: float,
) -> np.ndarray:
    """Gaussian signal + 2nd-order polynomial background."""
    return gaussian(x, n_sig, mu, sigma) + polynomial_bkg(x, c0, c1, c2)


# ---------------------------------------------------------------------------
# Fit routines
# ---------------------------------------------------------------------------

@dataclass
class FitResult:
    """Container for the most-used fit outputs."""
    params: dict[str, float]
    errors: dict[str, float]
    minuit: Minuit
    model: Callable[..., np.ndarray]

    def value(self, name: str) -> tuple[float, float]:
        return self.params[name], self.errors[name]

    def __repr__(self) -> str:
        lines = [f"{k}: {v:.4g} ± {self.errors[k]:.2g}" for k, v in self.params.items()]
        return "FitResult(" + ", ".join(lines) + ")"


def _hist_to_xy(counts: np.ndarray, edges: np.ndarray):
    centres = 0.5 * (edges[:-1] + edges[1:])
    err = np.sqrt(np.maximum(counts, 1.0))  # Poisson, floor at 1 to avoid div-by-zero
    return centres, counts, err


def fit_gaussian(counts: np.ndarray, edges: np.ndarray, *, p0: dict | None = None) -> FitResult:
    """Least-squares fit of a Gaussian to a histogram."""
    x, y, e = _hist_to_xy(counts, edges)
    cost = LeastSquares(x, y, e, gaussian)
    if p0 is None:
        p0 = {"n": y.sum() * (edges[1] - edges[0]), "mu": x[np.argmax(y)], "sigma": (edges[-1] - edges[0]) / 10}
    m = Minuit(cost, **p0)
    m.limits["sigma"] = (1e-3, None)
    m.limits["n"] = (0, None)
    m.migrad()
    return FitResult(dict(m.values.to_dict()), dict(m.errors.to_dict()), m, gaussian)


def fit_topmass(
    counts: np.ndarray,
    edges: np.ndarray,
    *,
    p0: dict | None = None,
) -> FitResult:
    """Gaussian-signal + quadratic-background fit; returns ``m_top`` via ``mu``."""
    x, y, e = _hist_to_xy(counts, edges)
    cost = LeastSquares(x, y, e, signal_plus_bkg)
    if p0 is None:
        peak = x[np.argmax(y)]
        p0 = {
            "n_sig": y.sum() * (edges[1] - edges[0]) * 0.5,
            "mu": float(peak),
            "sigma": 15.0,
            "c0": float(np.median(y)),
            "c1": 0.0,
            "c2": 0.0,
        }
    m = Minuit(cost, **p0)
    m.limits["sigma"] = (1.0, 50.0)
    m.limits["n_sig"] = (0, None)
    m.limits["mu"] = (100.0, 250.0)
    m.migrad()
    return FitResult(dict(m.values.to_dict()), dict(m.errors.to_dict()), m, signal_plus_bkg)
