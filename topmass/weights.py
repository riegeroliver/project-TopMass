"""Event weighting for ATLAS Open Data.

Monte-Carlo events must be reweighted to the integrated luminosity of the
recorded data before they can be compared with it. The standard open-data
normalisation is

    weight = lumi * (xsec * kfac * filteff / sum_of_weights)
                  * mcWeight * (product of ScaleFactor_* corrections)

All of ``xsec``, ``kfac``, ``filteff``, ``sum_of_weights`` and ``mcWeight`` are
per-event branches in the NTuple (constant per sample for the first four), so
the weight is computed directly from the streamed arrays.

Real **data** carries no MC weight — its per-event weight is 1.
"""
from __future__ import annotations

import awkward as ak
import numpy as np

from .io import LUMI_PB, SAMPLES

# Scale-factor branches multiplied into the MC weight when present.
SCALE_FACTORS = (
    "ScaleFactor_PILEUP",
    "ScaleFactor_ELE",
    "ScaleFactor_MUON",
    "ScaleFactor_BTAG",
    "ScaleFactor_ElTRIGGER",
    "ScaleFactor_MuTRIGGER",
)


def _scale_factor_product(events: ak.Array) -> ak.Array:
    """Multiply together whichever ScaleFactor_* branches are present."""
    product = None
    fields = set(events.fields)
    for sf in SCALE_FACTORS:
        if sf in fields:
            product = events[sf] if product is None else product * events[sf]
    if product is None:
        return ak.ones_like(events.mcWeight)
    return product


def mc_weight(events: ak.Array, lumi: float = LUMI_PB) -> ak.Array:
    """Per-event MC weight normalised to ``lumi`` (pb^-1)."""
    norm = lumi * events.xsec * events.kfac * events.filteff / events.sum_of_weights
    return norm * events.mcWeight * _scale_factor_product(events)


def data_weight(events: ak.Array) -> ak.Array:
    """Per-event weight for real data: all ones."""
    return ak.ones_like(events.met)


def weight_for(name: str, events: ak.Array, lumi: float = LUMI_PB) -> ak.Array:
    """Return the appropriate weight array for a named process.

    ``name`` is a key of :data:`topmass.io.SAMPLES` (``"ttbar"``,
    ``"single_top"``, ``"diboson"`` or ``"data"``).
    """
    info = SAMPLES.get(name)
    if info is not None and info.is_data:
        return data_weight(events)
    # Fall back to MC weighting; if MC branches are missing, treat as data.
    if "mcWeight" not in events.fields:
        return data_weight(events)
    return mc_weight(events, lumi=lumi)


def to_numpy_weight(weight: ak.Array) -> np.ndarray:
    """Flatten a (possibly awkward) weight array to a 1-D numpy array."""
    return np.asarray(ak.to_numpy(weight), dtype=float)
