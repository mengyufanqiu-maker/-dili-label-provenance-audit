# DILI reference-label provenance audit — reproduction package

Companion materials for:

> **Version drift and source-dependent binary labeling of ambiguous drugs in a
> drug-induced liver injury benchmark: a provenance audit**
> (`DILI_LABEL_STABILITY_DATA_NOTE_v0.5.md` + `_v0.5_SI.md`)

This package reproduces Tables 1–4 and Figures 1–2 from the raw inputs.
No model is trained or re-run; the only prediction-level file used is the
previously reproduced held-out probability vector (see "Prediction inputs").

## Contents

| Path | What it is |
|---|---|
| `generate_analysis.py` | Reproduces Tables 1–4; writes `repro_outputs/` (read-only w.r.t. inputs). Python 3.10 + pandas |
| `make_figures.py` | Generates `figures/fig1_*.png`, `fig2_*.png` (matplotlib; any recent Python 3) |
| `repro_outputs/full_match_table_tierB.csv` | Per-drug match table (Tier B): name, class, channel, toxicity, match tier, conflict flag |
| `repro_outputs/table1_reclassification.csv` | The 49 reclassified drugs (v1 → v2 classes) |
| `repro_outputs/sensitivity_summary.csv` | Tier A/B matched-row counts for Table 4 |
| `repro_outputs/INPUT_MANIFEST.md` | Input paths, sizes, sha256 checksums |

## How to run

```bash
# 1. install dependencies (pandas; Python 3.10 used in our runs)
pip install pandas

# 2. place the raw inputs at the paths listed in repro_outputs/INPUT_MANIFEST.md
#    and verify their sha256 against the manifest

# 3. reproduce Tables 1-4
python -I generate_analysis.py          # from the project root

# 4. reproduce Figures 1-2 (separate env; matplotlib)
pip install matplotlib
python -I make_figures.py
```

All printed numbers must match the manuscript: Table 1 (0 removed / 300 added /
49 = 18 + 27 + 4, no defined-class downgrades), Table 2 (556 + 88 tallied;
476/476; 80 negative / 30 positive), Table 4 (Tier A 358/30, 44/17, 313/314;
Tier B 559/89, 80/30, 476/476; Tier C 556/88), §3.3 (28 in-Seal; 14/13/1).

## Raw input sources (to be fetched by the reader; not redistributed here)

| Input | Source |
|---|---|
| `data/DILIrank_FDA_official_both_versions.xlsx` | FDA DILIrank 2.0 dataset page — `fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/drug-induced-liver-injury-rank-dilirank-20-dataset` (official workbook containing both version sheets) |
| `data/mapping/pubchem_candidates_full_*.csv` | Our earlier PubChem PUG REST name-lookup pass (curl, CSV-quoted); re-generable via PUG REST, or shipped on request |
| `repo/data/DILI_Goldstandard_1111.csv`, split files | Seal et al. public repository — `github.com/srijitseal/DILI` (paper: Chem Res Toxicol 2024;37(8):1290–1305, doi:10.1021/acs.chemrestox.4c00015) |
| Held-out probability vector + Youden threshold (0.6386) | Our earlier independent reproduction of the Seal et al. pipeline (AUC-PR 0.7875; verified against the authors' published predictions to floating-point precision); see `d2_pilot/D2_label_stability_alignment.csv` for the five held-out probabilities used in Table S1 |

Download dates and exact file versions are recorded in `repro_outputs/INPUT_MANIFEST.md`
(checksums) and, for the FDA workbook, in the workbook metadata.

## Environment note

`generate_analysis.py` was run with Python 3.10 / pandas 2.x in a dedicated
venv; `make_figures.py` with Python 3.13 / matplotlib in a separate venv.
Neither script trains models or requires the reproduction environment
(sklelearn 1.1.1 / numpy 1.26.4) used for the Seal pipeline reproduction.
