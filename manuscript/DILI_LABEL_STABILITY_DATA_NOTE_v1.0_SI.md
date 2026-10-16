# Supplementary Information — DILI label stability data note (v1.0)

**Table S1. The five Tier-B held-out reclassified drugs (all carry a "less" label in DILIrank 2.0).**

| Drug | Change (1.0 → 2.0) | Match quality | P(y=1) | Predicted at Youden (0.6386) |
|---|---|---|---|---:|
| raloxifene | no → less | full InChIKey | 0.693 | positive |
| flavoxate | no → less | full InChIKey | 0.717 | positive |
| saxagliptin | no → less | InChIKey14-only | 0.515 | negative |
| tadalafil | ambiguous → less | InChIKey14-only | 0.625 | negative |
| oseltamivir | ambiguous → less | InChIKey14-only | 0.576 | negative |

Provenance: probabilities are the previously reproduced 223-compound held-out probability vector of the Seal et al. FeatureNet model, verified against the authors' published predictions to floating-point precision; the threshold (0.6386) is the published Youden value reported by Seal et al. and was not refitted on the held-out set. All five drugs are DILIst-negative in the benchmark (`TOXICITY = 0`, `Source_rank = 1`). Under strict full-InChIKey matching, only raloxifene and flavoxate remain (both predicted positive).

**Table S2. Out-of-fold predictions for the 23 training-set reclassified drugs (Tier B; threshold 0.6386).**

| Drug | Change (1.0 → 2.0) | Match quality | OOF P(y=1) | Predicted at Youden (0.6386) |
|---|---|---|---|---:|
| vinblastine | no → less | InChIKey14-only | 0.576 | negative |
| diazepam | ambiguous → less | full InChIKey | 0.808 | positive |
| flurbiprofen | ambiguous → less | full InChIKey | 0.870 | positive |
| tretinoin | ambiguous → less | identity-conflict* | 0.740 | positive |
| trifluoperazine | ambiguous → less | full InChIKey | 0.655 | positive |
| mepivacaine | no → less | full InChIKey | 0.506 | negative |
| oxycodone | no → less | InChIKey14-only | 0.438 | negative |
| tolterodine | no → less | InChIKey14-only | 0.579 | negative |
| rizatriptan | no → less | full InChIKey | 0.533 | negative |
| dofetilide | no → less | full InChIKey | 0.703 | positive |
| olmesartan | ambiguous → less | full InChIKey | 0.797 | positive |
| aripiprazole | ambiguous → less | full InChIKey | 0.645 | positive |
| solifenacin | ambiguous → less | InChIKey14-only | 0.466 | negative |
| anidulafungin | ambiguous → most | InChIKey14-only | 0.557 | negative |
| cladribine | ambiguous → less | InChIKey14-only | 0.605 | negative |
| paliperidone | no → less | full InChIKey | 0.621 | negative |
| posaconazole | ambiguous → most | InChIKey14-only | 0.674 | positive |
| doxazosin | ambiguous → less | full InChIKey | 0.738 | positive |
| ribavirin | ambiguous → less | InChIKey14-only | 0.523 | negative |
| tramadol | ambiguous → less | InChIKey14-only | 0.504 | negative |
| capecitabine | ambiguous → less | InChIKey14-only | 0.672 | positive |
| pyridostigmine | no → less | full InChIKey | 0.457 | negative |
| oxybutynin | no → less | full InChIKey | 0.371 | negative |

\* Identity-conflict row (skeleton InChIKey shared with isotretinoin); shown for completeness, not reliably attributable (see main text).

Provenance and conventions: the OOF probabilities are the 4-fold `cross_val_predict` values of the selected final FeatureNet model on the 888-compound training set — the identical computation the original pipeline performs to derive the published Youden threshold (0.6386). The hyperparameter/model selection itself used all 888 training labels, following the original pipeline exactly; this convention is disclosed rather than presented as leakage-free. The 23 rows are reported separately from the 5 held-out compounds (Table S1); the two groups are not pooled and no inferential claims are made. Summary: 10 predicted positive / 13 negative at the published threshold; |P−0.5| ranges 0.004–0.370.

**Table S3. Comparison of the i-DILI overlap analysis and this audit.**

| Dimension | i-DILI (Shende & Tembhurne 2026 [4]) | This audit |
|---|---|---|
| DILIrank version | 2.0 only | 1.0 and 2.0 (version drift quantified) |
| DILIst input | multi-source integrated labels | full official FDA DILIst workbook (1,279 drugs) |
| Overlap statistic | Cohen's kappa = 0.888 over 480 shared drugs | 836 structure-matched drugs; defined-class agreement 707/708 (Tier A) / 713/714 (Tier B); 707/707 and 713/713 excluding the identified entity-normalization anomaly |
| Binarization | most/less → positive, no → negative; ambiguous excluded | four classes preserved; ambiguous handled per source and reported per channel and per matching tier |
| Matching method | not examined in this audit | structure-based (PubChem InChIKey; full-key priority, tiered) |
| Notes | The overlap counts are not directly comparable: different DILIrank versions, label rules, and inclusion criteria are involved; the difference is not presented as evidence of novelty. | |

**Figure captions.**

Figure 1. DILIrank 1.0 → 2.0 reclassification directions (n = 49): 18 escalations within the defined concern categories (no → less) and 31 resolutions of classification uncertainty from the ambiguous category (27 to less, 4 to most); zero defined-class downgrades. Transition widths are proportional to counts.

Figure 2. Cross-source sample filtering. (a) The ambiguous-class pathway from DILIrank 1.0 into the Seal et al. benchmark: 254 ambiguous drugs, 231 with a resolvable structure, 112 InChIKey14 hits in the gold standard, 2 identity-conflict hits excluded, 110 tallied (80 negative via the DILIst-sourced channel; 30 positive via the "CP Overlap" channel). (b) Gold-standard matching tallies by source channel (Tier B).
