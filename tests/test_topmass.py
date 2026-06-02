"""Sanity tests for the topmass helper package (ATLAS Open Data version).

These do not touch the network — they verify the helpers on small synthetic
awkward arrays using the **real** open-data branch names. Run with
``pytest tests/``.
"""
from __future__ import annotations

import awkward as ak
import numpy as np
import vector

vector.register_awkward()

from topmass import kinematics, neutrino, pairing, selection, weights
from topmass.constants import M_W, M_MU


# ---------------------------------------------------------------------------
# kinematics
# ---------------------------------------------------------------------------

def test_invariant_mass_two_back_to_back_muons():
    """Two back-to-back muons of equal energy E give m = 2E (up to muon mass)."""
    E = 50.0
    p = np.sqrt(E**2 - M_MU**2)
    a = ak.zip({"px": [p], "py": [0.0], "pz": [0.0], "energy": [E]}, with_name="Momentum4D")
    b = ak.zip({"px": [-p], "py": [0.0], "pz": [0.0], "energy": [E]}, with_name="Momentum4D")
    m = kinematics.invariant_mass(a, b)
    assert np.isclose(float(m[0]), 2 * E, atol=1e-6)


def test_leading_lepton_picks_first():
    """leading_lepton returns the first entry of the jagged lepton collection."""
    events = ak.Array(
        {
            "lep_pt": [[60.0, 10.0], [35.0]],
            "lep_eta": [[0.1, -1.0], [0.5]],
            "lep_phi": [[0.0, 1.0], [2.0]],
            "lep_e": [[61.0, 11.0], [36.0]],
        }
    )
    lead = kinematics.leading_lepton(events)
    assert np.isclose(float(lead.pt[0]), 60.0)
    assert np.isclose(float(lead.pt[1]), 35.0)


# ---------------------------------------------------------------------------
# neutrino
# ---------------------------------------------------------------------------

def test_neutrino_solver_consistency():
    """Given a synthetic W → ℓν, the solver's roots must reproduce M_W."""
    lep_px, lep_py, lep_pz, lep_E = 50.0, 0.0, 30.0, np.sqrt(50.0**2 + 30.0**2)
    nu_pz_true = 20.0
    nu_px, nu_py = 0.0, 40.0
    nu_E_true = np.sqrt(nu_px**2 + nu_py**2 + nu_pz_true**2)

    Wpx, Wpy, Wpz = lep_px + nu_px, lep_py + nu_py, lep_pz + nu_pz_true
    WE = lep_E + nu_E_true
    M_synth = np.sqrt(WE**2 - (Wpx**2 + Wpy**2 + Wpz**2))

    pz_plus, pz_minus, has_real = neutrino.solve_pz(
        np.array([lep_px]), np.array([lep_py]), np.array([lep_pz]), np.array([lep_E]),
        np.array([nu_px]), np.array([nu_py]),
        m_w=M_synth,
    )
    assert has_real[0]
    assert np.isclose(min(abs(pz_plus[0] - nu_pz_true), abs(pz_minus[0] - nu_pz_true)), 0.0, atol=1e-6)


def test_neutrino_solver_negative_discriminant_does_not_crash():
    """Force a configuration with no real root and check the fallback runs."""
    pz_plus, pz_minus, has_real = neutrino.solve_pz(
        np.array([1000.0]), np.array([0.0]), np.array([0.0]), np.array([1000.0]),
        np.array([0.0]), np.array([10.0]),
        m_w=M_W,
    )
    assert not has_real[0]
    assert np.isfinite(pz_plus[0]) and np.isfinite(pz_minus[0])
    assert np.isclose(pz_plus[0], pz_minus[0])


# ---------------------------------------------------------------------------
# pairing
# ---------------------------------------------------------------------------

def test_best_W_pair_picks_pair_closest_to_mW():
    """Among three light jets, the helper must pick the pair giving m_jj closest to M_W."""
    jets = ak.zip(
        {
            "pt": ak.Array([[50.0, 50.0, 30.0]]),
            "eta": ak.Array([[0.0, 0.5, 1.5]]),
            "phi": ak.Array([[0.0, 1.5, 0.7]]),
            "energy": ak.Array([[55.0, 55.0, 35.0]]),
        },
        with_name="Momentum4D",
    )
    pairs = ak.combinations(jets, 2, fields=["a", "b"])
    all_masses = (pairs.a + pairs.b).mass[0]
    _, _, m_jj = pairing.best_W_pair(jets)
    # The chosen mass must be the one closest to M_W among all pairs.
    best = min(all_masses, key=lambda m: abs(m - M_W))
    assert np.isclose(float(m_jj[0]), float(best))


# ---------------------------------------------------------------------------
# selection (real open-data branch names)
# ---------------------------------------------------------------------------

def _toy_events(n: int = 200, seed: int = 0) -> ak.Array:
    """Synthetic events matching the open-data schema (only the branches we cut on)."""
    rng = np.random.default_rng(seed)
    jet_lengths = rng.integers(2, 8, n)
    lep_lengths = rng.integers(1, 3, n)
    return ak.Array(
        {
            # leptons (jagged)
            "lep_pt": ak.Array([list(rng.uniform(20, 80, k)) for k in lep_lengths]),
            "lep_eta": ak.Array([list(rng.uniform(-3, 3, k)) for k in lep_lengths]),
            "lep_isMediumID": ak.Array([list(rng.integers(0, 2, k).astype(bool)) for k in lep_lengths]),
            "lep_isLooseIso": ak.Array([list(rng.integers(0, 2, k).astype(bool)) for k in lep_lengths]),
            # jets (jagged)
            "jet_pt": ak.Array([list(rng.uniform(20, 100, k)) for k in jet_lengths]),
            "jet_eta": ak.Array([list(rng.uniform(-3, 3, k)) for k in jet_lengths]),
            "jet_jvt": ak.Array([list(rng.uniform(0, 1, k)) for k in jet_lengths]),
            "jet_btag_quantile": ak.Array([list(rng.integers(0, 6, k)) for k in jet_lengths]),
            # event scalars
            "met": rng.uniform(0, 120, n),
        }
    )


def test_btag_mask_uses_quantile_threshold():
    """A jet is b-tagged iff its quantile >= the configured threshold (and passes quality)."""
    events = ak.Array(
        {
            "jet_pt": [[50.0, 50.0, 50.0]],
            "jet_eta": [[0.0, 0.0, 0.0]],
            "jet_jvt": [[1.0, 1.0, 1.0]],
            "jet_btag_quantile": [[5, 4, 3]],
        }
    )
    cuts = selection.SemilepCuts(btag_quantile_min=4)
    mask = selection.btag_mask(events, cuts)
    assert mask[0].tolist() == [True, True, False]
    assert int(selection.n_bjets(events, cuts)[0]) == 2


def test_cutflow_is_monotonically_non_increasing():
    """A cut-flow must never gain events as cuts are added."""
    flow = selection.cutflow(_toy_events(300, seed=1))
    counts = list(flow.values())
    assert counts == sorted(counts, reverse=True)
    assert counts[0] == 300


def test_semilep_preselection_is_a_boolean_mask():
    events = _toy_events(50)
    mask = selection.semilep_preselection(events)
    assert len(mask) == len(events)
    assert ak.to_numpy(mask).dtype == bool


# ---------------------------------------------------------------------------
# weights
# ---------------------------------------------------------------------------

def test_mc_weight_matches_hand_computation():
    """mc_weight = lumi * xsec * kfac * filteff / sum_of_weights * mcWeight * ∏ SF."""
    events = ak.Array(
        {
            "mcWeight": [2.0],
            "xsec": [10.0],          # pb
            "kfac": [1.1],
            "filteff": [0.5],
            "sum_of_weights": [1000.0],
            "ScaleFactor_PILEUP": [0.9],
            "ScaleFactor_ELE": [1.2],
            "met": [40.0],
        }
    )
    lumi = 36000.0
    expected = lumi * 10.0 * 1.1 * 0.5 / 1000.0 * 2.0 * (0.9 * 1.2)
    w = weights.mc_weight(events, lumi=lumi)
    assert np.isclose(float(w[0]), expected)


def test_weight_for_data_is_unity():
    """Real data carries weight 1 (no mcWeight branch)."""
    events = ak.Array({"met": [10.0, 20.0, 30.0]})
    w = weights.weight_for("data", events)
    assert np.allclose(ak.to_numpy(w), 1.0)
    assert len(w) == 3
