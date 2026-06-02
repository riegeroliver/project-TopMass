# Leptonic channel — Group L

Reconstruct the top-quark mass from the **leptonic** top: `m(ℓ, ν, b_lep)`.

## Roadmap

1. **Chapter 1** (shared with Group H) — framework introduction.
2. **Chapter 2 — leptonic selection**
    - 1 isolated lepton (pT, η, medium ID, loose isolation),
    - ≥ 4 jets, ≥ 1 b-tag (`jet_btag_quantile`),
    - MET cut. Backgrounds: single-top, diboson; real data overlaid.
3. **Chapter 3 — mass measurement**
    - Solve the quadratic for `p_z(ν)` from the W-mass constraint.
    - Pick the b-jet closest in ΔR to the lepton.
    - Build `m(ℓ, ν, b_lep)`.
    - Fit Gaussian + polynomial background → extract m<sub>top</sub>.

## Neutrino-`p_z` quadratic

From $M_W^2 = (E_\ell + E_\nu)^2 - |\vec p_\ell + \vec p_\nu|^2$ with $\vec p_T^\nu = $ MET:

$$
p_z^{\nu\,2}\,(p_T^\ell)^2 - 2\,p_z^\nu\,\mu\,p_z^\ell + (E_\ell)^2(E_T^\nu)^2 - \mu^2 = 0,
\qquad \mu = \tfrac{1}{2} M_W^2 + \vec p_T^\ell \cdot \vec p_T^\nu .
$$

When the discriminant is positive, two real roots exist. The standard heuristic in the helper `topmass.neutrino` is the **smallest-|p_z|** root, which tends to give the narrower top-mass peak.

When the discriminant is negative, MET is implicitly rescaled to make it vanish (common ad-hoc fix in top-physics analyses).

## Closure

There is no truth top-mass branch in the open data. Validate the method by
checking the fitted m<sub>top</sub> against the generator value (≈ 172.5 GeV) on
the `ttbar` MC, optionally truth-matching the b-jet to `truth_jet_*`.

## Deliverable

Report m<sub>top</sub> ± σ<sub>stat</sub> from the fit, plus a discussion of the two leading systematic effects (jet energy scale, b-jet pairing efficiency, choice of neutrino root, …).
