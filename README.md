# Project TopMass

A Python lab course on measuring the top-quark mass from **semileptonic `tt̄` decays** at the LHC, using **real [ATLAS Open Data](https://opendata.atlas.cern/)** (13 TeV, 2025 release). The course is split between two student groups working on the same dataset from complementary sides:

- **Group L — leptonic top:** reconstruct `m(ℓ, ν, b)` after solving the W-mass constraint for the neutrino's longitudinal momentum.
- **Group H — hadronic top:** reconstruct `m(j₁, j₂, b)` after a W-jet pairing step.

Both groups should converge on `m_top ≈ 173 GeV` from independent observables, and compare simulation against real recorded data.

## Course structure

| Chapter | Contents | Audience |
|---|---|---|
| [Chapter 1](Chapter1/) | NTuple I/O with `uproot` & `awkward`, event loops, invariant mass, detector resolution. | both groups |
| [Chapter 2](Chapter2/) | Event selection and signal/background separation. | split: [`leptonic/`](Chapter2/leptonic), [`hadronic/`](Chapter2/hadronic) |
| [Chapter 3](Chapter3/) | Reconstruction of the top mass and the actual fit. | split: [`leptonic/`](Chapter3/leptonic), [`hadronic/`](Chapter3/hadronic) |

Theoretical background and dataset description: [`data/README.md`](data/README.md).

## Setup

The course uses an isolated [pixi](https://pixi.sh) environment with the standard Python HEP stack (`uproot`, `awkward`, `vector`, `mplhep`, `iminuit`, `hist`, `jupyterlab`) plus [`atlasopenmagic`](https://opendata.atlas.cern/docs/data/atlasopenmagic) for streaming the data. **No data files are downloaded into the repository** — they are streamed on demand and cached under `.cache/`.

### 1. Install pixi (one-time)

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

See the [pixi installation guide](https://pixi.sh/latest/#installation) for other options.

### 2. Clone

```bash
git clone https://gitlab.cern.ch/jarieger/project-TopMass.git
cd project-TopMass
```

### 3. Launch JupyterLab

```bash
pixi run lab
```

The first run solves and installs the `topmass` environment from `pixi.toml` (the local
`topmass/` package is installed editable automatically, so `from topmass import ...`
works from any chapter directory), then opens JupyterLab.

Other handy commands:

```bash
pixi shell        # drop into an activated shell, then run e.g. `jupyter lab`
pixi run test     # run the test suite
pixi run docs     # preview the documentation site
```

Open `Chapter1/01_uproot_intro.ipynb` to get started. The first cell streams a
small fraction of the ATLAS Open Data:

```python
from topmass import io
io.setup()                                       # select the 2025 13 TeV release
samples = io.build_samples()                     # skim "3J1LMET30", https
events  = io.load_process("ttbar", samples, fraction=0.1)
```

The first run streams over the network (and caches to `.cache/`); later runs
read the cache. Raise `fraction` toward `1.0` for the final measurement.

### How the exercises work

The notebooks are aimed at first-year students with little coding experience, so
you never write code from scratch. Cells marked **✏️ Your turn** already run as
they are — change only the line(s) flagged with `# ✏️`, re-run with **Shift+Enter**,
and see how the result changes. Each task ends with a physics question for your
report and an optional **Stretch** for one extra tweak.

## Repository layout

```
project-TopMass/
├── topmass/        # importable helper package (I/O, weights, kinematics, fitting, plotting)
├── Chapter1/       # shared introduction
├── Chapter2/       # event selection (split per group)
├── Chapter3/       # mass measurement (split per group)
├── data/           # data card (the data itself is streamed, not stored)
├── docs/           # MkDocs course site
└── tests/          # pytest sanity checks for `topmass`
```

## Documentation site

The full course material is rendered via MkDocs and published to GitLab Pages from `master`. Preview locally with:

```bash
pixi run docs
```
