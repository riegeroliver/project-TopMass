# Project TopMass

A Python lab course on measuring the top-quark mass from **semileptonic `tt̄` decays**.

Two student groups, one dataset, two complementary analyses:

- **Group L** measures m<sub>top</sub> from the leptonic top: `m(ℓ, ν_reco, b)`.
- **Group H** measures m<sub>top</sub> from the hadronic top: `m(j₁, j₂, b)`.

## Course material

1. **[Physics background](physics-background.md)** — `tt̄` production, semileptonic topology, why m<sub>top</sub> matters.
2. **[Setup and tools](user-guide.md)** — installing the environment with pixi, running JupyterLab.
3. **[Leptonic channel (Group L)](leptonic-channel.md)** — neutrino reconstruction, `m(ℓνb)` fit.
4. **[Hadronic channel (Group H)](hadronic-channel.md)** — light-jet pairing, `m(jjb)` fit.

The notebooks live in the repository under `Chapter1/`, `Chapter2/` and `Chapter3/`. Open them in JupyterLab with `pixi run lab` (or `pixi shell` then `jupyter lab`).
