# -*- coding: utf-8 -*-
"""
generate_analysis.py — reproduces Tables 1-3 and the match-stringency sensitivity
analyses of DILI_LABEL_STABILITY_DATA_NOTE v0.3 from the raw local inputs.

Read-only with respect to inputs. Writes outputs to ./repro_outputs/:
  - sensitivity_summary.csv          (Table 4 numbers + checks)
  - full_match_table_tierB.csv       (per-drug alignment table, tier B, all matched drugs)
  - table1_reclassification.csv      (the 49 reclassified drugs, v1->v2)
  - INPUT_MANIFEST.md                (input paths, sizes, sha256)

Environment: Python 3.10, pandas; run from project root:
  python -I repro/generate_analysis.py
"""

import os, hashlib, json
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
# Raw inputs: point DILI_RAW_INPUTS at the directory holding data/, repo/, d2_pilot/
# (the author's project root), or place them under <repo>/raw_inputs/ (default).
INPUT_BASE = os.environ.get("DILI_RAW_INPUTS", os.path.join(ROOT, "raw_inputs"))
WORKBOOK = os.path.join(INPUT_BASE, "data", "DILIrank_FDA_official_both_versions.xlsx")
SHARDS = [
    os.path.join(INPUT_BASE, "data", "mapping", "pubchem_candidates_full_s0_e260.csv"),
    os.path.join(INPUT_BASE, "data", "mapping", "pubchem_candidates_full_s260_e520.csv"),
    os.path.join(INPUT_BASE, "data", "mapping", "pubchem_candidates_full_s520_e780.csv"),
    os.path.join(INPUT_BASE, "data", "mapping", "pubchem_candidates_full_s780_e1036.csv"),
]
GOLD = os.path.join(INPUT_BASE, "repo", "data", "DILI_Goldstandard_1111.csv")
TRAIN = os.path.join(INPUT_BASE, "repo", "test_data_ncv_DILIst_888.csv")
HELD = os.path.join(INPUT_BASE, "repo", "test_data_heldouttest_DILIst_223.csv")
ALIGN = os.path.join(INPUT_BASE, "d2_pilot", "D2_label_stability_alignment.csv")
OUT = os.path.join(ROOT, "repro_outputs")
os.makedirs(OUT, exist_ok=True)

SOURCES = {
    "data/DILIrank_FDA_official_both_versions.xlsx":
        "FDA DILIrank 2.0 dataset page (official workbook): "
        "https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/"
        "drug-induced-liver-injury-rank-dilirank-20-dataset",
    "repo/data/DILI_Goldstandard_1111.csv":
        "Seal et al. public repository: https://github.com/srijitseal/DILI",
    "repo/test_data_ncv_DILIst_888.csv":
        "Seal et al. public repository: https://github.com/srijitseal/DILI",
    "repo/test_data_heldouttest_DILIst_223.csv":
        "Seal et al. public repository: https://github.com/srijitseal/DILI",
    "d2_pilot/D2_label_stability_alignment.csv":
        "Authors' derived alignment table; included in this repository",
}

def norm_cls(v):
    s = str(v).strip().lower()
    if "ambiguous" in s:
        return "ambiguous"
    if "most" in s:
        return "most"
    if "less" in s:
        return "less"
    if "no" in s:
        return "no"
    return None

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# ---------- inputs ----------
xl = pd.ExcelFile(WORKBOOK)
v1 = xl.parse("version 1", header=1)
v2 = xl.parse("version 2", header=1)
v1.columns = [str(c).strip() for c in v1.columns]
v2.columns = [str(c).strip() for c in v2.columns]

c1 = [c for c in v1.columns if "vDILI" in c][0]
c2 = [c for c in v2.columns if "vDILI" in c][0]
v1["cls"] = v1[c1].map(norm_cls)
v2["cls"] = v2[c2].map(norm_cls)
n1 = [c for c in v1.columns if "Name" in c][0]
n2 = [c for c in v2.columns if "Name" in c][0]
v1["name"] = v1[n1].astype(str).str.strip()
v2["name"] = v2[n2].astype(str).str.strip()

cand = pd.concat([pd.read_csv(f) for f in SHARDS], ignore_index=True)
allm = cand.merge(v1[["name", "cls"]], left_on="query_name", right_on="name", how="inner")

gs = pd.read_csv(GOLD)
train = pd.read_csv(TRAIN)
held = pd.read_csv(HELD)

# ---------- Table 1: version reconciliation ----------
m = v1.merge(v2, on="LTKBID", suffixes=("_v1", "_v2"), how="outer")
m["removed"] = m.cls_v2.isna()
m["added"] = m.cls_v1.isna()
changed = m[(m.cls_v1.notna()) & (m.cls_v2.notna()) & (m.cls_v1 != m.cls_v2)]
t1 = changed.groupby(["cls_v1", "cls_v2"]).size()
print("== Table 1 checks ==")
print("v1 rows:", len(v1), "| v2 rows:", len(v2))
print("removed:", int(m.removed.sum()), "| added:", int(m.added.sum()), "| reclassified:", len(changed))
print(t1)
changed.to_csv(os.path.join(OUT, "table1_reclassification.csv"), index=False)

# ---------- per-name keys ----------
name2full = {}
name2ik14 = {}
name2cls = {}
for n, g in allm.groupby("query_name"):
    name2cls[n] = g.cls.iloc[0]
    name2full[n] = set(x for x in g.inchikey.dropna() if x == x)
    name2ik14[n] = set(x for x in g.inchikey14.dropna() if x == x)

ik2cls = {}
for ik, cls in zip(allm.inchikey14, allm.cls):
    if ik == ik:
        ik2cls.setdefault(ik, set()).add(cls)
multi_ik = {ik for ik, cs in ik2cls.items() if len(cs) > 1}

# ---------- tier matching against gold standard ----------
gs_ik14_set = set(gs.InChIKey14)
gs_full_set = set(gs.InChIKey.dropna())

def tier_matches(tier):
    """Return list of (name, gold_row_idx, tier_flag).

    Per-name precedence: full-InChIKey matches take priority; InChIKey14
    matches are used only for names with no full-key hit (tier B).
    """
    out = []
    for n, cls in name2cls.items():
        fulls = name2full.get(n, set())
        ik14s = name2ik14.get(n, set())
        full_hits = [(k, "full") for k in fulls if k in gs_full_set]
        if full_hits:
            keys = full_hits
        elif tier == "B":
            keys = [(k, "ik14") for k in ik14s if k in gs_ik14_set]
        else:
            keys = []
        seen = set()
        for k, ktype in keys:
            if ktype == "full":
                rows = gs.index[gs.InChIKey == k]
            else:
                rows = gs.index[gs.InChIKey14 == k]
            for r in rows:
                if r not in seen:
                    seen.add(r)
                    out.append((n, r, ktype))
    return out

def summarize(matches, label):
    """Gold-row-level summary of a tier."""
    rows = pd.DataFrame(matches, columns=["name", "row", "ktype"])
    rows["cls"] = rows["name"].map(name2cls)
    rows["rank"] = rows["row"].map(gs.Source_rank)
    rows["tox"] = rows["row"].map(gs.TOXICITY)
    # class assignment per gold row
    agg = rows.groupby("row").agg(
        n_names=("name", "nunique"),
        classes=("cls", lambda s: frozenset(s)),
        src_rank=("rank", "first"),
        tox=("tox", "first"),
        has_full=("ktype", lambda s: "full" in set(s)),
    ).reset_index()
    agg["conflict"] = agg["classes"].map(len) > 1
    res = {}
    for rank in [1, 13]:
        sub = agg[agg["src_rank"] == rank]
        res[rank] = {
            "matched_rows": len(sub),
            "conflict_rows": int(sub["conflict"].sum()),
            "tallied_rows": len(sub[~sub["conflict"]]),
            "full_key_rows": int(sub["has_full"].sum()),
        }
        # class x tox for non-conflict rows
        subc = sub[~sub["conflict"]].copy()
        subc["cls1"] = subc["classes"].map(lambda s: next(iter(s)))
        res[rank]["class_tox"] = (
            subc.groupby(["cls1", "tox"]).size().unstack(fill_value=0).to_dict()
        )
    amb = rows[rows["cls"] == "ambiguous"].groupby("row").first().reset_index()
    agg_idx = agg.set_index("row")
    amb["conflict"] = amb["row"].map(agg_idx["conflict"])
    amb_rank_tox = (
        amb[~amb["conflict"]].groupby(["rank", "tox"]).size().unstack(fill_value=0).to_dict()
    )
    amb_conflict_rank_tox = (
        amb[amb["conflict"]].groupby(["rank", "tox"]).size().unstack(fill_value=0).to_dict()
    )
    return res, amb_rank_tox, amb_conflict_rank_tox, rows

print()
print("== Tier summaries (gold-row level) ==")
results = {}
for tier, label in [("A", "strict full InChIKey"), ("B", "+ InChIKey14-only (main)")]:
    matches = tier_matches(tier)
    res, amb, ambconf, rows = summarize(matches, label)
    results[tier] = (res, amb, ambconf, rows)
    print(f"[{label}]")
    for rank in [1, 13]:
        print(f"  rank {rank}: matched {res[rank]['matched_rows']} "
              f"(full-key {res[rank]['full_key_rows']}, conflict {res[rank]['conflict_rows']}, "
              f"tallied {res[rank]['tallied_rows']})  class_tox: {res[rank]['class_tox']}")
    print(f"  ambiguous tallied rank x tox: {amb}")
    print(f"  ambiguous conflict rank x tox: {ambconf}")
    if tier == "B":
        # full per-drug table
        rows.to_csv(os.path.join(OUT, "full_match_table_tierB.csv"), index=False)

# tier C = tier B minus conflict rows
_, ambB, ambconfB, _ = results["B"]
ambC = ambB
print(f"[C: tier B minus conflicts] ambiguous tallied: {ambC}  (conflicts dropped: {ambconfB})")

# ---------- independence audit ----------
print()
print("== Independence audit ==")
rank1_total = int((gs.Source_rank == 1).sum())
rank13_total = int((gs.Source_rank == 13).sum())
b1 = results["B"][0][1]["matched_rows"]
b13 = results["B"][0][13]["matched_rows"]
print(f"DILIst-sourced rows: {rank1_total}; matched to DILIrank-1.0: {b1}; outside audit: {rank1_total - b1}")
print(f"CP-sourced rows: {rank13_total}; matched to DILIrank-1.0: {b13}; outside audit: {rank13_total - b13}")

# ---------- the 49 reclassified inside Seal, per tier ----------
print()
print("== 49 reclassified in Seal, per tier ==")
changed_names = set(changed.name_v1)
for tier in ["A", "B"]:
    matches = tier_matches(tier)
    msub = [(n, r) for n, r, k in matches if n in changed_names]
    sub = pd.DataFrame(msub, columns=["name", "row"])
    n_in = sub.name.nunique()
    split_hits = set()
    for _, rr in sub.iterrows():
        r = rr["row"]
        if (held.InChIKey14 == gs.loc[r, "InChIKey14"]).any():
            split_hits.add((rr["name"], "held"))
        if (train.InChIKey14 == gs.loc[r, "InChIKey14"]).any():
            split_hits.add((rr["name"], "train"))
    print(f"tier {tier}: in-Seal unique names = {n_in}; split hits = {sorted(split_hits)}")

# cross-check vs ALIGN csv
align = pd.read_csv(ALIGN)
print("ALIGN match_quality counts:")
print(align.match_quality.value_counts(dropna=False))
held_align = align[align.seal_status == "held"]
print("ALIGN held-out rows:", len(held_align))
print(held_align[["name_v1", "match_quality", "held_proba_class1"]].to_string())

# ---------- manifest ----------
print()
print("== Manifest ==")
manifest = {}
for p in [WORKBOOK] + SHARDS + [GOLD, TRAIN, HELD, ALIGN]:
    manifest[os.path.relpath(p, ROOT)] = {
        "bytes": os.path.getsize(p),
        "sha256": sha256(p),
    }
with open(os.path.join(OUT, "INPUT_MANIFEST.md"), "w", encoding="utf-8") as f:
    f.write("# INPUT_MANIFEST — raw inputs for DILI label stability audit\n\n")
    f.write("Generated by repro/generate_analysis.py (read-only). Paths are relative "
            "to the raw-inputs directory (DILI_RAW_INPUTS).\n\n")
    f.write("| file | bytes | sha256 | source |\n|---|---|---|---|\n")
    for k, v in manifest.items():
        src = SOURCES.get(k, "Authors' derived mapping via PubChem PUG REST; "
                             "included in this repository")
        f.write(f"| {k} | {v['bytes']} | {v['sha256']} | {src} |\n")
    f.write("\nDownload dates/versions: recorded at packaging time in the repository "
            "history; checksums above pin the exact bytes used.\n")
print("manifest written")

# save sensitivity summary (incl. tier C = tier B with conflicts excluded)
rows_out = []
for tier, label in [("A", "strict full InChIKey"), ("B", "main (full + InChIKey14)")]:
    res, amb, ambconf, _ = results[tier]
    for rank in [1, 13]:
        rows_out.append({
            "tier": tier, "rank": rank,
            "matched_rows": res[rank]["matched_rows"],
            "full_key_rows": res[rank]["full_key_rows"],
            "conflict_rows": res[rank]["conflict_rows"],
            "tallied_rows": res[rank]["tallied_rows"],
        })
resB, _, _, _ = results["B"]
for rank in [1, 13]:
    rows_out.append({
        "tier": "C", "rank": rank,
        "matched_rows": resB[rank]["matched_rows"],
        "full_key_rows": resB[rank]["full_key_rows"],
        "conflict_rows": 0,  # conflicts excluded by definition at tier C
        "tallied_rows": resB[rank]["tallied_rows"],
    })
pd.DataFrame(rows_out).to_csv(os.path.join(OUT, "sensitivity_summary.csv"), index=False)
print("done")
