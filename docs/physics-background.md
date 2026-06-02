# Physics background

## Top-quark production at the LHC

The top quark is the heaviest known elementary particle (`m_top ≈ 173 GeV`). At the Large Hadron Collider, top quarks are produced predominantly in pairs (`tt̄`) via the strong interaction, mainly through gluon–gluon fusion at LHC energies. The very large top mass means the top decays well before it can hadronise, making it the only quark whose properties can be measured almost as if it were a free particle.

## Decay modes

Each top quark decays almost exclusively to a W boson and a b-quark:

$$
t \to W^+ b \qquad \bar t \to W^- \bar b
$$

The W boson then decays either:

- **Hadronically**: `W → qq'` (≈ 67% branching ratio), producing two light quarks → two jets;
- **Leptonically**: `W → ℓν` (≈ 33%, with ℓ = e, μ, τ), producing a charged lepton and a neutrino.

Combining the decay of both tops gives three event topologies:

| Topology      | Branching | Signature                                          |
|---------------|-----------|----------------------------------------------------|
| Fully hadronic | 46 %     | 6 jets (2 b-jets)                                  |
| Semileptonic   | 44 %     | 1 lepton + MET + 4 jets (2 b-jets)                 |
| Dileptonic     | 10 %     | 2 leptons + MET + 2 b-jets                         |

This course focuses on the **semileptonic** channel: best balance between statistics, signature cleanliness, and the ability to reconstruct both top decays event by event.

## Why measure the top mass?

The top mass is a fundamental Standard Model parameter. It enters precision electroweak fits (together with the W and Higgs masses) and constrains the stability of the electroweak vacuum. The world-average uncertainty is currently below 0.5 GeV — a remarkable achievement for a parameter at the 100-GeV scale.

## Reconstruction strategy

Both groups use the same **ATLAS Open Data** (signal `tt̄`, backgrounds single-top and diboson, plus real recorded data — see [`data/README.md`](https://gitlab.cern.ch/jarieger/project-TopMass/-/blob/master/data/README.md)) but reconstruct the top mass from different sides:

### Group L — leptonic top

`m_top = m(ℓ, ν, b_lep)` where:

- `ℓ` is the measured lepton (electron or muon),
- `ν` is the neutrino, whose transverse momentum is the missing transverse energy (MET) and whose longitudinal momentum `p_z(ν)` is reconstructed by imposing the W-mass constraint (a quadratic with up to two solutions),
- `b_lep` is the b-jet from the leptonic top decay, identified via the smallest `ΔR(ℓ, b)`.

### Group H — hadronic top

`m_top = m(j₁, j₂, b_had)` where:

- `j₁`, `j₂` are the two light (non-b-tagged) jets whose invariant mass is closest to `m_W ≈ 80.4 GeV` (the hadronic W's decay products),
- `b_had` is the **other** b-jet (the one not assigned to the leptonic side).

Both reconstructions should give consistent values of `m_top ≈ 173 GeV` — the pedagogical payoff of running the two analyses in parallel. Throughout, the simulated samples (ttbar + single-top + diboson) are stacked and compared against the **real recorded ATLAS data**, giving students an authentic data/MC comparison.
