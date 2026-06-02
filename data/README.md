# Data — ATLAS Open Data (13 TeV, 2025 release)

This course runs on **real ATLAS Open Data**, release `2025e-13tev-beta`, streamed
over the network with the [`atlasopenmagic`](https://opendata.atlas.cern/docs/data/atlasopenmagic)
package. **No ROOT files are stored in this repository** — they are streamed on
demand and (optionally) cached locally under `./.cache/` (git-ignored).

## Physics background

At the LHC, top–antitop (`tt̄`) pairs are produced abundantly. Each top decays to
a W boson and a b-quark (`t → W b`); the W decays hadronically (`W → qq'`, ≈ 67 %)
or leptonically (`W → ℓν`, ≈ 33 %). The **semileptonic** channel — one top
hadronic, one leptonic — gives one isolated lepton, missing transverse energy
(MET) from the neutrino, and ≥ 4 jets (two b-tagged).

| Group | Top side | Observable | Key technique |
|---|---|---|---|
| **L** | leptonic | `m(ℓ, ν_reco, b_lep)` | solve quadratic for `p_z(ν)` from `M_W² = (p_ℓ + p_ν)²` |
| **H** | hadronic | `m(j₁, j₂, b_had)`     | light-jet pair closest to `M_W ≈ 80.4 GeV` |

## Accessing the data

```python
import atlasopenmagic as atom
from atlasopenmagic import install_from_environment
install_from_environment()          # one-time, installs the streaming deps

from topmass import io
io.setup()                          # atom.set_release("2025e-13tev-beta")
samples = io.build_samples()        # skim="3J1LMET30", protocol="https"
events  = io.load_process("ttbar", samples, fraction=0.1)
```

`io.build_samples()` wraps:

```python
mc   = atom.build_mc_dataset(io.MC_DEFS, skim="3J1LMET30", protocol="https")
data = atom.build_data_dataset("3J1LMET30", name="Data", protocol="https")
samples = {**data, **mc}
```

`fraction` controls how much of each file is read — keep it small (0.01–0.1)
while developing, raise it for the final measurement.

## Samples

| Process key | Role | DIDs |
|---|---|---|
| `ttbar`      | **signal** (`tt̄`)        | 601495, 410081, 410470 |
| `single_top` | background (single top)   | 601355, 601487, 601627, 601628, 601631, 601761–601764 |
| `diboson`    | background (WW/WZ/ZZ)     | 700488–700493, 700495, 700496 |
| `data`       | **real recorded data**    | — (via `build_data_dataset`) |

## Skim

The default skim **`3J1LMET30`** pre-selects the semileptonic-top topology:
**≥ 3 jets (pT > 20 GeV) + 1 tight lepton (pT > 7 GeV) + MET > 30 GeV**. This
streams far fewer events than the inclusive `1LMET30` skim while keeping signal.
Change it via `io.build_samples(skim=...)`.

## Branch dictionary

All momenta and energies are in **GeV**. Lepton and jet branches are **jagged**
(one variable-length list per event).

### Leptons (jagged, length `lep_n`)

| Branch | Type | Description |
|---|---|---|
| `lep_n` | int | Number of preselected leptons |
| `lep_pt`, `lep_eta`, `lep_phi`, `lep_e` | float[] | 4-momentum (GeV, rad) |
| `lep_type` | int[] | 11 = electron, 13 = muon |
| `lep_charge` | int[] | ±1 |
| `lep_isMediumID` | bool[] | Medium identification |
| `lep_isLooseIso` | bool[] | Loose isolation |
| `lep_isTrigMatched` | bool[] | Lepton matched to the trigger |

### Jets (jagged, length `jet_n`)

| Branch | Type | Description |
|---|---|---|
| `jet_n` | int | Number of preselected jets |
| `jet_pt`, `jet_eta`, `jet_phi`, `jet_e` | float[] | 4-momentum (GeV, rad) |
| `jet_btag_quantile` | int[] | DL1dv01 b-tag quantile (higher = more b-like) |
| `jet_jvt` | float[] | Jet-vertex-tagger score (pileup-jet rejection) |

> **b-tagging.** A jet is treated as b-tagged when `jet_btag_quantile >= 4`
> (course default, configurable in `topmass.selection.SemilepCuts`). The exact
> integer → efficiency-working-point mapping is given in the
> [official release details](https://opendata.atlas.cern/docs/data/for_education/13TeV25_details).

### MET, triggers, bookkeeping

| Branch | Type | Description |
|---|---|---|
| `met`, `met_phi` | float | Missing transverse energy (GeV, rad) |
| `trigE`, `trigM` | bool | Single-electron / single-muon trigger fired |
| `eventNumber` | uint64 | Event identifier |

### Weights (MC only)

| Branch | Type | Description |
|---|---|---|
| `mcWeight` | float | Generator event weight |
| `xsec` | float | Process cross-section (pb) |
| `filteff` | float | Filter efficiency |
| `kfac` | float | Higher-order k-factor |
| `sum_of_weights` | double | Sum of generated weights (normalisation) |
| `ScaleFactor_PILEUP`, `_ELE`, `_MUON`, `_BTAG`, `_ElTRIGGER`, `_MuTRIGGER` | float | Reco/efficiency corrections |

The full event weight (see `topmass.weights.mc_weight`):

```
weight = lumi · (xsec · kfac · filteff / sum_of_weights) · mcWeight · ∏ ScaleFactor_*
```

with `lumi = 36000 pb⁻¹`. **Real data** has weight 1.

### Truth (MC only, per-object)

`truth_jet_{pt,eta,phi,m,n}`, `truth_elec_*`, `truth_muon_*`, `truth_met`,
`truth_met_phi`. Used for the resolution study (Chapter 1) and closure tests
(Chapter 3). **Note:** there is *no* truth top/W mass branch — closure compares
the fitted mass to the generator value (≈ 172.5 GeV) and/or truth-matches jets.

Proceed to **[Chapter 1](../Chapter1/)**.
