# Hadronic channel — Group H

Reconstruct the top-quark mass from the **hadronic** top: `m(j₁, j₂, b_had)`.

## Roadmap

1. **Chapter 1** (shared with Group L) — framework introduction.
2. **Chapter 2 — hadronic selection**
    - ≥ 4 jets, ≥ 1 (or ≥ 2) b-tags (`jet_btag_quantile`).
    - Lepton is still present (from the leptonic top) — used downstream to assign the b-jets, not to veto the event.
    - Backgrounds: single-top, diboson; real data overlaid.
3. **Chapter 3 — mass measurement**
    - Pair the two light (non-b-tagged) jets whose invariant mass is closest to $m_W \approx 80.4$ GeV.
    - Identify the hadronic-side b-jet (the one **not** assigned to the lepton).
    - Build `m(j₁, j₂, b_had)`.
    - Fit Gaussian + polynomial background → extract m<sub>top</sub>.

## Jet-pairing strategy

The light-jet pair is chosen to minimise $|m_{jj} - m_W|$. This is implemented in `topmass.pairing.best_W_pair`. Combinatorial backgrounds (wrong jet assignment) broaden the peak and shift it slightly — this is one of the main systematic effects students should discuss in their report.

The b-jet assignment uses the smallest-ΔR(ℓ, b) rule **on the opposite side**: the b-jet farther from the lepton is the hadronic one. See `topmass.pairing.assign_bjets`.

## Closure

As for the leptonic side, validate by checking the fitted m<sub>top</sub>
against the generator value (≈ 172.5 GeV) on the `ttbar` MC, optionally
truth-matching the light jets and b-jet to `truth_jet_*`.

## Deliverable

Report m<sub>top</sub> ± σ<sub>stat</sub> from the fit, plus a discussion of:

- jet energy scale and resolution,
- combinatorial background from wrong jet pairing,
- comparison with Group L's leptonic-side result.
