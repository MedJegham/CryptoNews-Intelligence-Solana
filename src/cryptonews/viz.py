"""Style graphique commun (figures du rapport) — palette catégorielle validée, ordre fixe."""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

from cryptonews.config import path

# Palette catégorielle (ordre fixe, jamais recyclé) et encre
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SURFACE, INK, INK_2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

# Couleurs fixées par entité (la couleur suit l'entité, pas son rang)
SOURCE_COLORS = {"coindesk_hf": SERIES[0], "cryptovision": SERIES[1]}
# Classes de sentiment : pôles divergents bleu/rouge, neutre gris
LABEL_COLORS = {"positive": "#2a78d6", "neutral": "#898781", "negative": "#e34948"}


def apply_style() -> None:
    mpl.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"], "font.size": 10,
        "text.color": INK, "axes.labelcolor": INK_2, "axes.titlecolor": INK,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK_2, "ytick.labelcolor": INK_2,
        "lines.linewidth": 2, "legend.frameon": False, "figure.dpi": 110, "savefig.dpi": 200,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
    })


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(path("figures") / f"{name}.png", bbox_inches="tight")
