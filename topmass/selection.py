"""Reusable event-selection masks for ATLAS Open Data.

The default cuts are intentionally loose starting points for a first-year
course — Chapter 2 explores tightening / loosening them. Note that the
``3J1LMET30`` skim already applies ≥3 jets + 1 tight lepton + MET>30 upstream,
so these cuts refine on top of that (e.g. ≥4 jets, ≥1–2 b-tags).
"""
from __future__ import annotations

from dataclasses import dataclass

import awkward as ak
import numpy as np

# b-tag working point: a jet is b-tagged if `jet_btag_quantile >= this`.
# `jet_btag_quantile` is the DL1dv01 continuous-WP quantile (higher = more
# b-like). The exact integer→efficiency mapping is documented at
# https://opendata.atlas.cern/docs/data/for_education/13TeV25_details — the
# course default (4) follows the standard recipe.
DEFAULT_BTAG_QUANTILE = 4


@dataclass
class SemilepCuts:
    """Cut values for a semileptonic-`tt̄` baseline selection."""
    lepton_pt_min: float = 25.0
    lepton_eta_max: float = 2.5
    n_leptons: int = 1
    require_medium_id: bool = True
    require_loose_iso: bool = True
    jet_pt_min: float = 25.0
    jet_eta_max: float = 2.5
    jet_jvt_min: float = 0.5
    n_jets_min: int = 4
    n_bjets_min: int = 1
    btag_quantile_min: int = DEFAULT_BTAG_QUANTILE
    met_min: float = 30.0


def lepton_quality_mask(events: ak.Array, cuts: SemilepCuts) -> ak.Array:
    """Per-lepton quality mask (jagged): pT, |η|, medium ID, loose isolation."""
    mask = (events.lep_pt > cuts.lepton_pt_min) & (np.abs(events.lep_eta) < cuts.lepton_eta_max)
    if cuts.require_medium_id:
        mask = mask & events.lep_isMediumID
    if cuts.require_loose_iso:
        mask = mask & events.lep_isLooseIso
    return mask


def n_good_leptons(events: ak.Array, cuts: SemilepCuts) -> ak.Array:
    return ak.sum(lepton_quality_mask(events, cuts), axis=1)


def jet_quality_mask(events: ak.Array, cuts: SemilepCuts) -> ak.Array:
    """Per-jet quality mask (jagged): pT, |η|, JVT (pileup-jet rejection)."""
    return (
        (events.jet_pt > cuts.jet_pt_min)
        & (np.abs(events.jet_eta) < cuts.jet_eta_max)
        & (events.jet_jvt > cuts.jet_jvt_min)
    )


def btag_mask(events: ak.Array, cuts: SemilepCuts) -> ak.Array:
    """Per-jet b-tag mask: quality jet AND ``jet_btag_quantile >= threshold``."""
    return jet_quality_mask(events, cuts) & (events.jet_btag_quantile >= cuts.btag_quantile_min)


def n_good_jets(events: ak.Array, cuts: SemilepCuts) -> ak.Array:
    return ak.sum(jet_quality_mask(events, cuts), axis=1)


def n_bjets(events: ak.Array, cuts: SemilepCuts) -> ak.Array:
    return ak.sum(btag_mask(events, cuts), axis=1)


def semilep_preselection(events: ak.Array, cuts: SemilepCuts | None = None) -> ak.Array:
    """Full baseline selection mask. Defaults to :class:`SemilepCuts`()."""
    cuts = cuts or SemilepCuts()
    return (
        (n_good_leptons(events, cuts) == cuts.n_leptons)
        & (n_good_jets(events, cuts) >= cuts.n_jets_min)
        & (n_bjets(events, cuts) >= cuts.n_bjets_min)
        & (events.met > cuts.met_min)
    )


def cutflow(events: ak.Array, cuts: SemilepCuts | None = None) -> dict[str, int]:
    """Return a sequential cut-flow as an ordered dict of names → counts.

    Each entry is the number of events passing *all* cuts up to and including
    the one named. The first row ("skim") is the number of events delivered by
    the upstream skim.
    """
    cuts = cuts or SemilepCuts()
    n_total = len(events)

    lep = n_good_leptons(events, cuts) == cuts.n_leptons
    njets_ok = n_good_jets(events, cuts) >= cuts.n_jets_min
    nbjets_ok = n_bjets(events, cuts) >= cuts.n_bjets_min
    met_ok = events.met > cuts.met_min

    return {
        "skim":     n_total,
        "lepton":   int(ak.sum(lep)),
        "+ jets":   int(ak.sum(lep & njets_ok)),
        "+ b-tag":  int(ak.sum(lep & njets_ok & nbjets_ok)),
        "+ MET":    int(ak.sum(lep & njets_ok & nbjets_ok & met_ok)),
    }
