"""Plotting helpers: weighted stacked histograms with a Data/MC ratio panel,
resolution ratio plots, and cut-flow tables."""
from __future__ import annotations

from typing import Iterable, Mapping

import awkward as ak
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import pandas as pd
from hist import Hist

from . import style  # noqa: F401  -- registers the ATLAS style on import
from .io import SAMPLES

# Order in which MC backgrounds are stacked (bottom to top), signal last.
MC_STACK_ORDER = ["diboson", "single_top", "ttbar"]


def make_hist(
    values: ak.Array | np.ndarray,
    *,
    bins: int,
    range: tuple[float, float],
    weight: ak.Array | np.ndarray | None = None,
    name: str = "x",
) -> Hist:
    """Build a weighted 1-D :class:`hist.Hist` filled with ``values``."""
    h = Hist.new.Reg(bins, *range, name=name).Weight()
    v = ak.to_numpy(ak.flatten(values, axis=None))
    if weight is not None:
        w = ak.to_numpy(ak.flatten(weight, axis=None))
        h.fill(**{name: v}, weight=w)
    else:
        h.fill(**{name: v})
    return h


def stacked_plot(
    histograms: Mapping[str, Hist],
    *,
    xlabel: str = "",
    ylabel: str = "Events",
    label: str = "Open Data",
    lumi: float | None = 36,
    logy: bool = False,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Stacked MC with real Data overlaid as points and a Data/MC ratio panel.

    Keys of ``histograms`` must be names from :data:`topmass.io.SAMPLES`
    (``"ttbar"``, ``"single_top"``, ``"diboson"``, ``"data"``).
    """
    fig, (ax, rax) = plt.subplots(
        2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1], "hspace": 0.07}
    )

    mc_keys = [k for k in MC_STACK_ORDER if k in histograms]
    if mc_keys:
        hep.histplot(
            [histograms[k] for k in mc_keys],
            stack=True,
            histtype="fill",
            label=[SAMPLES[k].label for k in mc_keys],
            color=[SAMPLES[k].colour for k in mc_keys],
            ax=ax,
        )
        mc_total = sum(histograms[k].values() for k in mc_keys)
    else:
        mc_total = None

    if "data" in histograms:
        data_h = histograms["data"]
        centres = data_h.axes[0].centers
        counts = data_h.values()
        ax.errorbar(
            centres, counts, yerr=np.sqrt(np.maximum(counts, 0)),
            fmt="ko", markersize=4, label="Data",
        )
        # Ratio panel
        if mc_total is not None:
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = np.where(mc_total > 0, counts / mc_total, np.nan)
                rerr = np.where(mc_total > 0, np.sqrt(np.maximum(counts, 0)) / mc_total, np.nan)
            rax.errorbar(centres, ratio, yerr=rerr, fmt="ko", markersize=4)

    rax.axhline(1.0, color="grey", linestyle="--", linewidth=0.8)
    rax.set_ylim(0.5, 1.5)
    rax.set_ylabel("Data / MC")
    rax.set_xlabel(xlabel)

    if logy:
        ax.set_yscale("log")
    hep.atlas.label(label, lumi=lumi, ax=ax)
    ax.set_ylabel(ylabel)
    ax.legend(loc="best")
    return fig, (ax, rax)


def resolution_ratio_plot(
    numerator: Hist,
    denominator: Hist,
    *,
    xlabel: str = "",
    ylabel: str = "Events",
    ratio_label: str = "Reco / Truth",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Two-panel plot: distributions on top, their ratio underneath."""
    fig, (ax, rax) = plt.subplots(
        2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05}
    )
    hep.histplot(numerator,   ax=ax, label="numerator", histtype="step", linewidth=2)
    hep.histplot(denominator, ax=ax, label="denominator", histtype="step", linewidth=2)
    ax.set_ylabel(ylabel)
    ax.legend()

    num = numerator.values()
    den = denominator.values()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(den > 0, num / den, np.nan)
    centres = numerator.axes[0].centers
    rax.plot(centres, r, "o", markersize=3)
    rax.axhline(1.0, color="grey", linestyle="--", linewidth=0.8)
    rax.set_ylabel(ratio_label)
    rax.set_xlabel(xlabel)
    rax.set_ylim(0.5, 1.5)
    return fig, (ax, rax)


def cutflow_table(flows: Mapping[str, Mapping[str, int]]) -> pd.DataFrame:
    """Render a {sample: {cut: n}} mapping as a tidy DataFrame.

    Adds a final "eff." column with the efficiency relative to the first
    ("skim") column.
    """
    df = pd.DataFrame(flows).T
    if df.shape[1] >= 1:
        df["eff."] = (df.iloc[:, -1] / df.iloc[:, 0]).round(4)
    return df


def significance(signal: Iterable[float], background: Iterable[float]) -> float:
    """Weighted cut-and-count significance :math:`S/\\sqrt{S + B}`."""
    s = float(np.sum(signal))
    b = float(np.sum(background))
    return s / np.sqrt(s + b) if (s + b) > 0 else 0.0
