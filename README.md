# DILI reference-label provenance audit — publication repository

Companion repository for:

> **Version drift and source-dependent binary labeling of ambiguous drugs in a
> drug-induced liver injury benchmark: a provenance audit**

A descriptive provenance audit of DILI reference labels: (i) the directionally
asymmetric DILIrank 1.0→2.0 reclassification pattern (18 concern escalations,
31 resolutions of classification uncertainty, 0 defined-class downgrades);
(ii) the source-dependent binary labeling of the ambiguous class in the
Seal et al. (2024) DILIPredictor benchmark (80 negative via the DILIst-sourced
channel, 30 positive via the DILIrank-derived "CP Overlap" channel, in the
matched ambiguous subset); (iii) a three-tier match-stringency sensitivity
analysis.

No model was trained or re-run; no label was modified.

## Contents

| Path | What it is |
|---|---|
| `manuscript/DILI_LABEL_STABILITY_DATA_NOTE_v0.5.md` | Main manuscript (research note / data note) |
| `manuscript/DILI_LABEL_STABILITY_DATA_NOTE_v0.4_SI.md` | Supplementary Information (Table S1: five held-out reclassified drugs) |
| `repro/generate_analysis.py` | Reproduces Tables 1–4 from raw inputs (Python 3.10, pandas) |
| `repro/make_figures.py` | Generates Figures 1–2 (matplotlib) |
| `repro/README.md` | Reproduction instructions: input sources, run commands, expected outputs |
| `repro_outputs/` | Full per-drug match table (Tier B), 49-row reclassification table, sensitivity summary, input manifest (sizes + sha256) |
| `figures/` | Figure 1 (reclassification directions), Figure 2 (cross-source filtering flowchart) |
| `data/D2_label_stability_alignment.csv` | Per-drug alignment table for the 49 reclassified drugs |

## Raw inputs

Raw inputs (official FDA DILIrank workbook, Seal et al. public repository files,
PubChem mapping shards) are not redistributed here; fetch instructions, versions,
and sha256 checksums are in `repro/README.md` and `repro_outputs/INPUT_MANIFEST.md`.

## Status

Draft — not yet submission-ready. Target journals under consideration:
Computational Toxicology; Journal of Cheminformatics (Data note);
JCIM (Application Notes). License to be added before submission.
