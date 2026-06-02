"""Helper package for the project-TopMass lab course.

Modules
-------
io          : NTuple loading and the sample registry.
kinematics  : Lorentz-vector construction and invariant-mass helpers.
neutrino    : Quadratic solver for ``p_z(ν)`` from the W-mass constraint.
pairing     : Jet-pairing helpers for the hadronic side.
selection   : Reusable event-selection masks.
plotting    : `mplhep`-styled stacked plots, ratio plots, cut-flow tables.
fitting     : `iminuit` wrappers for common signal+background fit shapes.
style       : Central matplotlib + mplhep defaults.

Constants
---------
M_W, M_TOP : reference particle masses (GeV).
"""

from .constants import M_W, M_TOP, M_B, M_E, M_MU

__all__ = ["M_W", "M_TOP", "M_B", "M_E", "M_MU"]
__version__ = "0.1.0"
