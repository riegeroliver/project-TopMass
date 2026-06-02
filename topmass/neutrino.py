r"""Reconstruct the neutrino longitudinal momentum from the W-mass constraint.

Imposing :math:`M_W^2 = (E_\ell + E_\nu)^2 - (\vec p_\ell + \vec p_\nu)^2` and
identifying :math:`\vec p_T^\nu` with the measured MET, the equation becomes a
quadratic in :math:`p_z^\nu`:

.. math::

    p_z^{\nu\,2}\,(p_T^\ell)^2 - 2\,p_z^\nu\,\mu\,p_z^\ell
    + (p_\ell^2)\,(E_T^\nu)^2 - \mu^2 = 0 ,

with

.. math::

    \mu = \tfrac{1}{2} M_W^2 + \vec p_T^\ell \cdot \vec p_T^\nu .

Two real solutions exist when the discriminant is positive; when it is
negative, the MET is "promoted" to the value that makes the discriminant
vanish (a standard ad-hoc fix in top-physics analyses).
"""
from __future__ import annotations

import awkward as ak
import numpy as np

from .constants import M_W


def _to_numpy(a) -> np.ndarray:
    return np.asarray(ak.to_numpy(a), dtype=float) if isinstance(a, ak.Array) else np.asarray(a, dtype=float)


def solve_pz(
    lepton_px: ak.Array | np.ndarray,
    lepton_py: ak.Array | np.ndarray,
    lepton_pz: ak.Array | np.ndarray,
    lepton_E:  ak.Array | np.ndarray,
    met_px:    ak.Array | np.ndarray,
    met_py:    ak.Array | np.ndarray,
    *,
    m_w: float = M_W,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the two ``p_z(ν)`` solutions and a real-discriminant mask.

    Returns
    -------
    pz_plus, pz_minus
        The two roots. When the discriminant is negative they are equal to
        :math:`-\\mu p_z^\\ell / (p_T^\\ell)^2` (the discriminant is set to
        zero, i.e. MET is rescaled to make the equation solvable).
    has_real
        Boolean mask, ``True`` where the original quadratic had a real
        solution (i.e. no rescaling was needed).
    """
    lx, ly, lz, lE = map(_to_numpy, (lepton_px, lepton_py, lepton_pz, lepton_E))
    nx, ny = map(_to_numpy, (met_px, met_py))

    pt_l_sq = lx * lx + ly * ly
    et_n_sq = nx * nx + ny * ny
    mu = 0.5 * m_w * m_w + lx * nx + ly * ny

    a = pt_l_sq
    b = -2.0 * mu * lz
    c = lE * lE * et_n_sq - mu * mu
    disc = b * b - 4.0 * a * c

    has_real = disc >= 0
    safe_disc = np.where(has_real, disc, 0.0)
    sqrt_disc = np.sqrt(safe_disc)

    pz_plus = (-b + sqrt_disc) / (2.0 * a)
    pz_minus = (-b - sqrt_disc) / (2.0 * a)
    return pz_plus, pz_minus, has_real


def neutrino_pz(
    lepton_vec: ak.Array,
    met_vec: ak.Array,
    *,
    selector: str = "smallest_abs",
    m_w: float = M_W,
) -> np.ndarray:
    """Return a single ``p_z(ν)`` per event using the requested selector.

    Parameters
    ----------
    lepton_vec, met_vec
        ``Momentum4D`` arrays (see :mod:`topmass.kinematics`).
    selector
        - ``"smallest_abs"`` : the solution with the smallest :math:`|p_z|`
          (default; commonly used heuristic).
        - ``"plus"`` / ``"minus"`` : pick the corresponding root.
    """
    pz_plus, pz_minus, _ = solve_pz(
        lepton_vec.px, lepton_vec.py, lepton_vec.pz, lepton_vec.E,
        met_vec.px,    met_vec.py,
        m_w=m_w,
    )
    if selector == "smallest_abs":
        return np.where(np.abs(pz_plus) < np.abs(pz_minus), pz_plus, pz_minus)
    if selector == "plus":
        return pz_plus
    if selector == "minus":
        return pz_minus
    raise ValueError(f"Unknown selector {selector!r}")


def build_neutrino(lepton_vec: ak.Array, met_vec: ak.Array, *, selector: str = "smallest_abs") -> ak.Array:
    """Return a massless ``Momentum4D`` neutrino with reconstructed ``p_z``."""
    pz = neutrino_pz(lepton_vec, met_vec, selector=selector)
    px = _to_numpy(met_vec.px)
    py = _to_numpy(met_vec.py)
    E = np.sqrt(px * px + py * py + pz * pz)
    return ak.zip(
        {"px": px, "py": py, "pz": pz, "energy": E},
        with_name="Momentum4D",
    )
