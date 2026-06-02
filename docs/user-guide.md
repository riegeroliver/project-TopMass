# Setup and tools

## What you will use

| Tool            | Purpose                                          |
|-----------------|--------------------------------------------------|
| `atlasopenmagic`| Stream ATLAS Open Data and fetch metadata.       |
| `uproot`        | Read ROOT files in pure Python.                  |
| `awkward`       | Manipulate jagged arrays (variable-length events).|
| `vector`        | Lorentz 4-vectors, invariant masses, ΔR.         |
| `hist`          | Histograms.                                      |
| `mplhep`        | ATLAS/CMS plot styling.                          |
| `iminuit`       | Minimisation and parameter estimation.           |
| `jupyterlab`    | Interactive notebooks.                           |

All of these are pulled in by the `pixi.toml`.

## Installing pixi

This is a **one-time** step. [pixi](https://pixi.sh) manages the environment.

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

See the [pixi installation guide](https://pixi.sh/latest/#installation) for other options.

## Activating

Every time you open a new terminal:

```bash
cd project-TopMass
pixi shell
```

The first run solves and installs the `topmass` environment from `pixi.toml`, including
the local helper package (`topmass/`) in editable mode so notebooks can
`from topmass import ...` from any chapter folder. `pixi shell` drops you into an
activated shell; type `exit` to leave it.

## Launching the notebooks

```bash
pixi run lab
```

(or just `jupyter lab` from inside `pixi shell`). Then open the chapter folder you are working on and start at `01_*.ipynb`.

## How the exercises work

You never start from a blank cell. Cells marked **✏️ Your turn** already run as
they are — your job is to change only the line(s) flagged with `# ✏️`, re-run the
cell (**Shift+Enter**), and observe how the result changes. Each task ends with a
physics question to answer in your report, plus an optional **Stretch** for one
extra tweak if you finish early.

## Streaming the data

There are no local ROOT files — data is streamed from the ATLAS Open Data
servers via `atlasopenmagic` and cached under `.cache/`:

```python
from topmass import io
io.setup()                                       # set release 2025e-13tev-beta
samples = io.build_samples()                     # skim "3J1LMET30", https
events  = io.load_process("ttbar", samples, fraction=0.05)
events.fields                                    # list the branches (all GeV)
```

Use a small `fraction` (0.01–0.1) while developing; raise it for the final fit.
Available processes: `"ttbar"` (signal), `"single_top"`, `"diboson"`, `"data"`.

## Event weights

Monte-Carlo events must be weighted to the data luminosity before comparison:

```python
from topmass import weights
w = weights.weight_for("ttbar", events)          # data gets weight 1
```

Always pass `weight=w` when filling histograms (`topmass.plotting.make_hist`).

## Running the tests

```bash
pixi run test
```

The tests cover the `topmass/` helpers (invariant mass, neutrino solver, event
weights, b-tag and selection masks). They run on a tiny synthetic dataset and
**do not** touch the network.

## Building the docs site locally

```bash
pixi run docs
```

Open <http://localhost:8000> to preview.
