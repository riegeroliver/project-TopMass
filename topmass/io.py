"""Data access for the ATLAS Open Data 13 TeV 2025 release.

Data is **streamed** over HTTPS via the `atlasopenmagic` package — there are no
local ROOT files. The flow mirrors the standard open-data recipe::

    from topmass import io
    io.setup()                                   # set the release
    samples = io.build_samples()                 # dict: process -> stream info
    events  = io.load_process("ttbar", samples)  # awkward array of events

The signal is semileptonic ``tt̄``; backgrounds are single-top and diboson;
``data`` is the real recorded ATLAS data, overlaid on the MC in later chapters.

Weight inputs (``xsec``, ``filteff``, ``kfac``, ``sum_of_weights``,
``mcWeight``) are stored as per-event branches, so event weights are computed
directly from the streamed arrays — see :mod:`topmass.weights`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import awkward as ak
import uproot

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RELEASE = "2025e-13tev-beta"
DEFAULT_SKIM = "3J1LMET30"          # >=3 jets + 1 tight lepton + MET>30 (top semileptonic)
TREE_NAME = "analysis"               # tree name inside the open-data files
LUMI_PB = 36000.0                    # integrated luminosity (pb^-1) = 36 fb^-1

# Process -> dataset IDs (DIDs). Mirrors the mc_defs from the course recipe.
MC_DEFS: dict[str, dict[str, list[int]]] = {
    "ttbar":      {"dids": [601495, 410081, 410470]},
    "single_top": {"dids": [601355, 601487, 601627, 601628, 601631, 601761, 601762, 601763, 601764]},
    "diboson":    {"dids": [700488, 700489, 700490, 700491, 700492, 700493, 700495, 700496]},
}

# Branches to read. Reco + weights + scale factors + per-object truth (for the
# resolution and closure studies in Chapters 1 and 3).
VARIABLES: list[str] = [
    # event weights / normalisation
    "mcWeight", "xsec", "filteff", "kfac", "sum_of_weights",
    # scale factors
    "ScaleFactor_PILEUP", "ScaleFactor_ELE", "ScaleFactor_MUON",
    "ScaleFactor_BTAG", "ScaleFactor_ElTRIGGER", "ScaleFactor_MuTRIGGER",
    # triggers
    "trigE", "trigM",
    # leptons
    "lep_n", "lep_pt", "lep_eta", "lep_phi", "lep_e",
    "lep_type", "lep_charge", "lep_isMediumID", "lep_isLooseIso", "lep_isTrigMatched",
    # MET
    "met", "met_phi",
    # jets
    "jet_n", "jet_pt", "jet_eta", "jet_phi", "jet_e", "jet_btag_quantile", "jet_jvt",
    # bookkeeping
    "eventNumber",
    # per-object truth (resolution / closure)
    "truth_jet_pt", "truth_jet_eta", "truth_jet_phi", "truth_jet_m", "truth_jet_n",
    "truth_met", "truth_met_phi",
]


@dataclass(frozen=True)
class ProcessInfo:
    name: str
    label: str
    colour: str
    is_signal: bool
    is_data: bool


# Plotting / bookkeeping metadata, keyed by the process names used everywhere.
SAMPLES: dict[str, ProcessInfo] = {
    "data":       ProcessInfo("data",       "Data",          "black",   False, True),
    "ttbar":      ProcessInfo("ttbar",      r"$t\bar{t}$",   "#e41a1c", True,  False),
    "single_top": ProcessInfo("single_top", "single top",    "#377eb8", False, False),
    "diboson":    ProcessInfo("diboson",    "diboson",       "#4daf4a", False, False),
}

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"


# ---------------------------------------------------------------------------
# Setup and sample building
# ---------------------------------------------------------------------------

def setup(release: str = RELEASE) -> None:
    """Set the active ATLAS Open Data release. Call once per notebook."""
    import atlasopenmagic as atom

    atom.set_release(release)


def build_samples(skim: str = DEFAULT_SKIM, protocol: str = "https") -> dict:
    """Build the merged {process: stream-info} dict (MC + real Data).

    Thin wrapper around ``atlasopenmagic.build_mc_dataset`` /
    ``build_data_dataset``. The exact value type is whatever atlasopenmagic
    returns (a list of URLs, or a structure carrying URLs + metadata);
    :func:`load_process` handles both via :func:`_urls_from_entry`.
    """
    import atlasopenmagic as atom

    mc = atom.build_mc_dataset(MC_DEFS, skim=skim, protocol=protocol)
    data = atom.build_data_dataset(skim, name="Data", protocol=protocol)
    return {**data, **mc}


def _urls_from_entry(entry) -> list[str]:
    """Extract a list of file URLs from one value of the ``samples`` dict.

    Robust to the two shapes atlasopenmagic may return: a bare list of URL
    strings, or a mapping that contains a ``"list"``/``"urls"``/``"file_list"``
    field.
    """
    if isinstance(entry, dict):
        for key in ("list", "urls", "file_list", "files"):
            if key in entry:
                return list(entry[key])
        # Fall back: a dict of {did: [urls]} -> flatten.
        flat: list[str] = []
        for v in entry.values():
            if isinstance(v, (list, tuple)):
                flat.extend(v)
        if flat:
            return flat
        raise TypeError(f"Could not find URLs in sample entry with keys {list(entry)}")
    if isinstance(entry, (list, tuple)):
        return list(entry)
    raise TypeError(f"Unexpected sample entry type: {type(entry)!r}")


# ---------------------------------------------------------------------------
# Loading / streaming
# ---------------------------------------------------------------------------

def _resolve_key(name: str, samples: dict) -> str:
    """Map a friendly process name to the key actually present in ``samples``."""
    if name in samples:
        return name
    # atlasopenmagic uses "Data" for the real-data entry; we expose "data".
    if name == "data":
        for candidate in ("Data", "data"):
            if candidate in samples:
                return candidate
    raise KeyError(f"Process {name!r} not in samples (have: {list(samples)})")


def load_process(
    name: str,
    samples: dict,
    *,
    fraction: float = 0.1,
    branches: Iterable[str] | None = None,
    use_cache: bool = True,
) -> ak.Array:
    """Stream one process and return its events as an awkward record array.

    Parameters
    ----------
    name
        ``"ttbar"``, ``"single_top"``, ``"diboson"`` or ``"data"``.
    samples
        The dict returned by :func:`build_samples`.
    fraction
        Fraction of each file's entries to read (keeps runtime manageable for
        a classroom). ``1.0`` reads everything.
    branches
        Branch list; defaults to :data:`VARIABLES`. For real data the truth and
        ``mcWeight`` branches are dropped automatically.
    use_cache
        If ``True``, cache the result as parquet under ``./.cache`` keyed by
        (name, fraction) so repeated runs do not re-stream.
    """
    key = _resolve_key(name, samples)
    is_data = SAMPLES.get(name, SAMPLES.get("data")).is_data if name in SAMPLES else (key.lower() == "data")

    requested = list(branches) if branches is not None else list(VARIABLES)
    if is_data:
        # Data has no MC weights or truth; keep only reco/bookkeeping branches.
        drop = {"mcWeight", "xsec", "filteff", "kfac", "sum_of_weights"}
        requested = [b for b in requested if not b.startswith("truth_") and b not in drop]

    cache_file = CACHE_DIR / f"{name}_{skim_tag(samples)}_frac{fraction:g}.parquet"
    if use_cache and cache_file.exists():
        return ak.from_parquet(cache_file)

    urls = _urls_from_entry(samples[key])
    chunks: list[ak.Array] = []
    for url in urls:
        with uproot.open({url: TREE_NAME}) as tree:
            n = tree.num_entries
            stop = max(1, int(n * fraction)) if fraction < 1.0 else None
            present = [b for b in requested if b in tree.keys()]
            chunks.append(tree.arrays(present, entry_stop=stop, library="ak"))

    events = ak.concatenate(chunks) if len(chunks) > 1 else chunks[0]

    if use_cache:
        CACHE_DIR.mkdir(exist_ok=True)
        ak.to_parquet(events, cache_file)
    return events


def skim_tag(samples: dict) -> str:
    """Best-effort skim identifier for cache file names."""
    return getattr(samples, "skim", DEFAULT_SKIM) if not isinstance(samples, dict) else DEFAULT_SKIM


def list_samples() -> list[str]:
    """Return the process names known to the plotting/metadata layer."""
    return list(SAMPLES.keys())
