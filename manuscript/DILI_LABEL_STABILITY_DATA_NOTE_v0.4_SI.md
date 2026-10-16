# Supplementary Information — DILI label stability data note (v0.5)

**Table S1. The five Tier-B held-out reclassified drugs (all carry a "less" label in DILIrank 2.0).**

| Drug | Change (1.0 → 2.0) | Match quality | P(y=1) | Predicted at Youden (0.6386) |
|---|---|---|---|---:|
| raloxifene | no → less | full InChIKey | 0.693 | positive |
| flavoxate | no → less | full InChIKey | 0.717 | positive |
| saxagliptin | no → less | InChIKey14-only | 0.515 | negative |
| tadalafil | ambiguous → less | InChIKey14-only | 0.625 | negative |
| oseltamivir | ambiguous → less | InChIKey14-only | 0.576 | negative |

Provenance: probabilities are the previously reproduced 223-compound held-out probability vector of the Seal et al. FeatureNet model, verified against the authors' published predictions to floating-point precision; the threshold (0.6386) is the published Youden value reported by Seal et al. and was not refitted on the held-out set. All five drugs are DILIst-negative in the benchmark (`TOXICITY = 0`, `Source_rank = 1`). Under strict full-InChIKey matching, only raloxifene and flavoxate remain (both predicted positive).
