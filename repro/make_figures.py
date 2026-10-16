# -*- coding: utf-8 -*-
"""
make_figures.py — generates the two manuscript figures for
DILI_LABEL_STABILITY_DATA_NOTE v0.4.

Outputs (300 dpi PNG, light surface):
  figures/fig1_reclassification_directions.png
  figures/fig2_cross_source_filtering.png

Palette: dataviz reference palette, light mode, validated by
scripts/validate_palette.js (#2a78d6,#eb6834,#1baf7a, mode light, all PASS).
All marks carry direct labels (no color-alone encoding).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#0b0b0b"
SEC = "#52514e"
MUT = "#898781"
SURF = "#fcfcfb"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
GRAY_FILL = "#f0efec"
GRAY_LINE = "#c3c2b7"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "text.color": INK,
    "axes.edgecolor": GRAY_LINE,
})

OUT = r"C:\Users\15446\k-dense-byok\projects\dili_project\figures"
import os
os.makedirs(OUT, exist_ok=True)


def box(ax, x, y, w, h, label, sub=None, fill=SURF, lw=1.0, ls="-"):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.004,rounding_size=0.012",
                       linewidth=lw, edgecolor=INK, facecolor=fill, linestyle=ls)
    ax.add_patch(p)
    if sub:
        ax.text(x + w / 2, y + h / 2 + 0.016, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h / 2 - 0.016, sub, ha="center", va="center",
                fontsize=8, color=SEC)
    else:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=INK)


def arrow(ax, p0, p1, color, lw, label=None, lab_dx=0, lab_dy=0, ls="-"):
    a = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=13,
                        linewidth=lw, color=color, linestyle=ls,
                        shrinkA=2, shrinkB=2,
                        connectionstyle="arc3,rad=0.0")
    ax.add_patch(a)
    if label:
        ax.text((p0[0] + p1[0]) / 2 + lab_dx, (p0[1] + p1[1]) / 2 + lab_dy,
                label, ha="center", va="center", fontsize=9,
                fontweight="bold", color=INK)


# ----------------------------------------------------------------------
# Figure 1 — reclassification directions
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=300)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)

LW = 0.02
# left column (DILIrank 1.0), top -> bottom: most, less, ambiguous, no
left = [("most", "n = 192, 0 reclassified"), ("less", "n = 278, 0 reclassified"),
        ("ambiguous", "n = 254"), ("no", "n = 312")]
ly = [0.86, 0.66, 0.46, 0.26]
for (name, sub), y in zip(left, ly):
    faded = "0 reclassified" in sub
    box(ax, 0.03, y, 0.17, 0.13, name, sub,
        fill=GRAY_FILL if faded else SURF, lw=1.0)
# right column (DILIrank 2.0)
box(ax, 0.80, 0.86, 0.17, 0.13, "most", "+4")
box(ax, 0.80, 0.66, 0.17, 0.13, "less", "+45")
box(ax, 0.80, 0.46, 0.17, 0.13, "no", "0 reclassified", fill=GRAY_FILL)

# arrows (exits/entries on box edges)
arrow(ax, (0.20, 0.325), (0.80, 0.700), BLUE, 12.0,
      label="n = 18\nconcern escalation", lab_dx=-0.12, lab_dy=0.02)
arrow(ax, (0.20, 0.490), (0.80, 0.690), ORANGE, 16.0,
      label="n = 27", lab_dx=0.10, lab_dy=0.06)
arrow(ax, (0.20, 0.525), (0.80, 0.905), AQUA, 4.0,
      label="n = 4", lab_dx=0.20, lab_dy=-0.04)
ax.text(0.50, 0.415, "resolution of classification\nuncertainty (ambiguous \u2192 defined)",
        ha="center", va="center", fontsize=8, color=SEC)

# zero-downgrade annotation
ax.plot([0.83, 0.17], [0.40, 0.24], ls=(0, (4, 3)), color=GRAY_LINE, lw=1.2)
ax.text(0.50, 0.175, "defined-class downgrades (most/less \u2192 no): 0",
        ha="center", va="center", fontsize=9, color=MUT)

ax.text(0.115, 1.015, "DILIrank 1.0", ha="center", va="center", fontsize=9,
        fontweight="bold", color=INK, transform=ax.transAxes)
ax.text(0.885, 1.015, "DILIrank 2.0", ha="center", va="center", fontsize=9,
        fontweight="bold", color=INK, transform=ax.transAxes)
ax.text(0.05, -0.045, "n = 49 reclassified drugs. Zero defined-class downgrades. "
        "Transition widths are proportional to counts.",
        ha="left", va="center", fontsize=8, color=MUT, transform=ax.transAxes)

fig.savefig(os.path.join(OUT, "fig1_reclassification_directions.png"),
            dpi=300, bbox_inches="tight", facecolor=SURF)
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 2 — cross-source sample filtering flowchart
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.6, 8.8), dpi=300)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)

def flow_box(x, y, w, h, title, sub, fill=SURF, lw=1.0, title_color=INK, sub_color=SEC):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.004,rounding_size=0.012",
                       linewidth=lw, edgecolor=INK, facecolor=fill)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h - 0.028, title, ha="center", va="center",
            fontsize=9, fontweight="bold", color=title_color)
    ax.text(x + w / 2, y + 0.024, sub, ha="center", va="center",
            fontsize=8, color=sub_color)

def down_arrow(x, y0, y1, lw=1.4):
    a = FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>", mutation_scale=13,
                        linewidth=lw, color=INK, shrinkA=2, shrinkB=2)
    ax.add_patch(a)

# ---- Panel A: ambiguous pathway (top half, y 0.52..1) ----
ax.text(0.03, 1.00, "a", fontsize=12, fontweight="bold", va="top")
flow_box(0.15, 0.905, 0.70, 0.075, "DILIrank 1.0 (official workbook)",
         "1,036 drugs \u2014 most 192 / less 278 / no 312 / ambiguous 254")
down_arrow(0.50, 0.905, 0.865)
flow_box(0.15, 0.790, 0.70, 0.075, "ambiguous with a resolvable structure",
         "231 drugs (23 unmatchable: biologics, antibodies, peptides)")
down_arrow(0.50, 0.790, 0.750)
flow_box(0.15, 0.675, 0.70, 0.075, "InChIKey14 hits in the Seal et al. gold standard",
         "112 raw hits (93 in the 888-compound training set / 19 in the 223-compound held-out set)")
down_arrow(0.50, 0.675, 0.635)
flow_box(0.15, 0.545, 0.70, 0.09, "exclude 4 identity-conflict rows (MULTI)",
         "amphet./dextroamphet., armodafinil/modafinil, tretinoin/isotretinoin, ofloxacin/levofloxacin",
         fill=GRAY_FILL, lw=1.0)
down_arrow(0.50, 0.545, 0.505)
flow_box(0.03, 0.415, 0.445, 0.09, "DILIst-sourced channel",
         "80 negative / 0 positive", fill=BLUE, title_color="white", sub_color="white")
flow_box(0.525, 0.415, 0.445, 0.09, "\u201cCP Overlap\u201d channel",
         "30 positive / 0 negative", fill=ORANGE, title_color="white", sub_color="white")
ax.text(0.50, 0.46, "of the 110 tallied", ha="center", va="center", fontsize=8, color=SEC)

# ---- Panel B: gold-standard matching (bottom half, y 0.02..0.38) ----
ax.text(0.03, 0.385, "b", fontsize=12, fontweight="bold", va="top")
flow_box(0.15, 0.300, 0.70, 0.075, "Seal et al. gold standard (1,111 rows)",
         "DILIst-sourced: 990 rows  |  \u201cCP Overlap\u201d (DILIrank-derived, pre-binarized): 121 rows")
down_arrow(0.50, 0.300, 0.262)
flow_box(0.15, 0.187, 0.70, 0.075, "matched to a DILIrank-1.0 class (InChIKey14, Tier B)",
         "DILIst-sourced: 559 matched  |  \u201cCP Overlap\u201d: 89 matched")
down_arrow(0.50, 0.187, 0.149)
flow_box(0.15, 0.060, 0.70, 0.089, "exclude identity-conflict rows \u2192 tallied",
         "DILIst-sourced: 556 (3 conflicts)  |  \u201cCP Overlap\u201d: 88 (1 conflict)")
down_arrow(0.50, 0.060, 0.022)
flow_box(0.03, -0.075, 0.445, 0.097, "non-ambiguous: 476/476 agree",
         "most/less \u2192 positive, no \u2192 negative\n(construction-consistent: DILIst built on DILIrank [2])",
         fill=GRAY_FILL)
flow_box(0.525, -0.075, 0.445, 0.097, "ambiguous: 80 neg. / 30 pos.",
         "DILIst-sourced channel \u2192 80 negative\n\u201cCP Overlap\u201d channel \u2192 30 positive",
         fill=GRAY_FILL)

fig.savefig(os.path.join(OUT, "fig2_cross_source_filtering.png"),
            dpi=300, bbox_inches="tight", facecolor=SURF)
plt.close(fig)
print("figures written")
