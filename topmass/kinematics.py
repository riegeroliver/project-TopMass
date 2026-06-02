"""Lorentz-vector helpers built on the ``vector`` library.

For ATLAS Open Data the leptons and jets are **jagged collections** (one
variable-length list per event). Energies and momenta are in **GeV**. We build
``vector.Awkward`` arrays from `(pt, eta, phi, energy)` so they interoperate
with awkward broadcasting and jagged structure.
"""
from __future__ import annotations

import awkward as ak
import vector

# Register the awkward backend exactly once on import.
vector.register_awkward()


def lepton_vectors(events: ak.Array) -> ak.Array:
    """Jagged collection of lepton 4-vectors (one list per event)."""
    return ak.zip(
        {
            "pt": events.lep_pt,
            "eta": events.lep_eta,
            "phi": events.lep_phi,
            "energy": events.lep_e,
        },
        with_name="Momentum4D",
    )


def leading_lepton(events: ak.Array) -> ak.Array:
    """The highest-pT lepton per event (assumes ``lep_n >= 1``)."""
    return lepton_vectors(events)[:, 0]


def jet_vectors(events: ak.Array) -> ak.Array:
    """Jagged collection of jet 4-vectors."""
    return ak.zip(
        {
            "pt": events.jet_pt,
            "eta": events.jet_eta,
            "phi": events.jet_phi,
            "energy": events.jet_e,
        },
        with_name="Momentum4D",
    )


def met_vector(events: ak.Array) -> ak.Array:
    """MET as a massless transverse 4-vector (eta = 0, mass = 0).

    The longitudinal component must be solved separately — see
    :mod:`topmass.neutrino`.
    """
    return ak.zip(
        {
            "pt": events.met,
            "eta": ak.zeros_like(events.met),
            "phi": events.met_phi,
            "mass": ak.zeros_like(events.met),
        },
        with_name="Momentum4D",
    )


def truth_jet_vectors(events: ak.Array) -> ak.Array:
    """Jagged collection of truth-jet 4-vectors (for resolution / closure)."""
    return ak.zip(
        {
            "pt": events.truth_jet_pt,
            "eta": events.truth_jet_eta,
            "phi": events.truth_jet_phi,
            "mass": events.truth_jet_m,
        },
        with_name="Momentum4D",
    )


def invariant_mass(*objects: ak.Array) -> ak.Array:
    """Invariant mass of the four-vector sum of any number of input objects."""
    if not objects:
        raise ValueError("invariant_mass() needs at least one object")
    total = objects[0]
    for obj in objects[1:]:
        total = total + obj
    return total.mass


def delta_r(a: ak.Array, b: ak.Array) -> ak.Array:
    """ΔR = sqrt(Δη² + Δϕ²) between two 4-vector arrays (broadcastable)."""
    return a.deltaR(b)
