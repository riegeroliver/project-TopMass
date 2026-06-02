"""Jet-pairing helpers for the hadronic top reconstruction.

Two responsibilities:

1. Among the light (non-b-tagged) jets, find the pair whose invariant mass is
   closest to ``M_W`` — these are the hadronic-W decay products.
2. Among the two b-tagged jets, decide which one belongs to the hadronic top.
   The other is the leptonic-side b-jet.

Both helpers operate event-wise on awkward arrays.
"""
from __future__ import annotations

import awkward as ak

from .constants import M_W


def best_W_pair(light_jets: ak.Array, *, m_w: float = M_W) -> tuple[ak.Array, ak.Array, ak.Array]:
    """Pick the light-jet pair closest in invariant mass to ``m_w``.

    Parameters
    ----------
    light_jets
        Jagged ``Momentum4D`` array of non-b-tagged jets per event.

    Returns
    -------
    jet1, jet2
        The two selected jets (one per event).
    m_jj
        Invariant mass of the chosen pair.
    """
    pairs = ak.combinations(light_jets, 2, fields=["j1", "j2"])
    m_jj = (pairs.j1 + pairs.j2).mass
    best = ak.argmin(abs(m_jj - m_w), axis=1, keepdims=True)
    chosen = pairs[best]
    return ak.firsts(chosen.j1), ak.firsts(chosen.j2), ak.firsts(m_jj[best])


def assign_bjets(
    b_jets: ak.Array,
    lepton_vec: ak.Array,
    *,
    rule: str = "closest_to_lepton",
) -> tuple[ak.Array, ak.Array]:
    """Split exactly two b-jets into (leptonic-side, hadronic-side).

    Parameters
    ----------
    b_jets
        Jagged ``Momentum4D`` array of b-tagged jets — must contain exactly
        two per event (filter upstream).
    lepton_vec
        Single-lepton 4-vector per event.
    rule
        - ``"closest_to_lepton"`` : the b-jet with the smaller ΔR to the
          lepton is the leptonic-side b. Simple and works well on average.
    """
    if rule != "closest_to_lepton":
        raise ValueError(f"Unknown rule {rule!r}")
    b1 = b_jets[:, 0]
    b2 = b_jets[:, 1]
    dr1 = b1.deltaR(lepton_vec)
    dr2 = b2.deltaR(lepton_vec)
    b_lep = ak.where(dr1 < dr2, b1, b2)
    b_had = ak.where(dr1 < dr2, b2, b1)
    return b_lep, b_had
