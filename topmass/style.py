"""Central matplotlib / mplhep style for the course.

Importing this module (or calling :func:`use_atlas_style`) registers the
ATLAS style with sensible figure-size and font defaults.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import mplhep as hep

# Process → colour mapping used by the plotting helpers. Edit here to recolour
# every plot in the course consistently.
PROCESS_COLOURS = {
    "ttbar":     "#e41a1c",   # red, signal
    "ttbar_dl":  "#fb9a99",   # pink
    "singletop": "#377eb8",   # blue
    "wjets":     "#4daf4a",   # green
    "qcd":       "#984ea3",   # purple
    "data":      "black",
}


def use_atlas_style() -> None:
    """Activate the ATLAS plot style. Safe to call multiple times."""
    hep.style.use("ATLAS")
    plt.rcParams.update(
        {
            "figure.figsize": (7.0, 5.0),
            "figure.dpi": 110,
            "savefig.dpi": 180,
            "axes.labelsize": 14,
            "legend.fontsize": 11,
        }
    )


# Auto-apply when imported — convenient for notebooks.
use_atlas_style()
