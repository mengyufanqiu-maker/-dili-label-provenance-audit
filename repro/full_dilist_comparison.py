# -*- coding: utf-8 -*-
"""
full_dilist_comparison.py — full-DILIst x DILIrank-1.0 same-drug cross-source
comparison, frozen per FULL_DILIST_ANALYSIS_PLAN.md (2026-10-16).

Reads: FDA DILIst workbook, DILIrank 1.0 workbook, existing PubChem candidate
shards; queries PubChem PUG REST (per name) for DILIst names not yet mapped,
with incremental save/resume. Matches structures with the same three-tier
rules as generate_analysis.py (full-InChIKey priority; InChIKey14 fallback;
multi-class conflict rows flagged and excluded from tallies).

Outputs (repro_outputs/):
  pubchem_candidates_dilist_new.csv   (new PubChem lookups, resume-safe)
  full_dilist_match_table.csv         (per-drug match table)
  full_dilist_agreement.json          (tier A/B agreement matrices + counts)
"""

import json
import os
import sys
import time
import urllib.parse

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_BASE = os.environ.get("DILI_RAW_INPUTS", os.path.join(ROOT, "raw_inputs"))
OUT = os.path.join(ROOT, "repro_outputs")
os.makedirs(OUT, exist_ok=True)

DILIST_XLSX = os.path.join(INPUT_BASE, "data", "DILIst_FDA_official.xlsx")
WORKBOOK = os.path.join(INPUT_BASE, "data", "DILIrank_FDA_official_both_versions.xlsx")
_SHARD_NAMES = ["pubchem_candidates_full_s0_e260.csv",
                "pubchem_candidates_full_s260_e520.csv",
                "pubchem_candidates_full_s520_e780.csv",
                "pubchem_candidates_full_s780_e1036.csv"]


def resolve(base_rel, repo_rel):
    p = os.path.join(INPUT_BASE, base_rel)
    if not os.path.exists(p) and repo_rel:
        q = os.path.join(ROOT, repo_rel)
        if os.path.exists(q):
            return q
    return p


SHARDS = [resolve(os.path.join("data", "mapping", n), os.path.join("data", "mapping", n))
          for n in _SHARD_NAMES]
NEW_CSV = os.path.join(ROOT, "repro_outputs", "pubchem_candidates_dilist_new.csv")


def norm(s):
    return str(s).strip().lower()


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


SALT_TOKENS = {
    "sulfate", "hydrochloride", "hcl", "hydrobromide", "maleate", "mesylate",
    "tartrate", "citrate", "fumarate", "succinate", "phosphate", "sodium",
    "potassium", "calcium", "acetate", "lactate", "gluconate", "chloride",
    "bromide", "iodide", "nitrate", "pamoate", "besylate", "tosylate",
    "camsylate", "edisylate", "estolate", "xinafoate", "teoclate", "lauryl",
    "dihydrate", "monohydrate", "hemihydrate", "hydrate", "trihydrate",
    "disodium", "monosodium", "dipropionate", "embonate", "napsylate",
    "oxalate", "malate", "benzoate", "salicylate", "bitartrate",
    "propionate", "butyrate", "valerate", "mononitrate", "dinitrate",
}


def name_variants(name):
    """Yield lookup candidates: the name, then salt-suffix-trimmed prefixes."""
    yield name
    parts = name.split()
    for cut in range(len(parts) - 1, 0, -1):
        if parts[cut].lower().rstrip(".,;") in SALT_TOKENS:
            yield " ".join(parts[:cut])
        else:
            return


def variant_list(name):
    """Materialize up to 3 lookup variants (full name + salt-stripped prefixes)."""
    out = []
    for v in name_variants(name):
        out.append(v)
        if len(out) >= 3:
            break
    return out


def pubchem_cid_by_name(name):
    """Per-name GET: name -> first CID (PUG list POST is not failure-aligned)."""
    import subprocess
    url = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
           + urllib.parse.quote(name) + "/cids/JSON")
    out = subprocess.run(["curl", "-s", "--max-time", "30", url],
                         capture_output=True, text=True, timeout=45)
    try:
        data = json.loads(out.stdout or "{}")
    except Exception:
        return None
    ids = data.get("IdentifierList", {}).get("CID", [])
    return ids[0] if ids else None


def pubchem_props_by_cids(cids):
    """Batch CID->InChIKey via PUG REST list POST."""
    import subprocess
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/InChIKey/JSON"
    body = "cid=" + ",".join(str(c) for c in cids)
    out = subprocess.run(["curl", "-s", "--max-time", "120", "-X", "POST",
                          "-d", body, url],
                         capture_output=True, text=True, timeout=150)
    try:
        data = json.loads(out.stdout)
    except Exception:
        return []
    return data.get("PropertyTable", {}).get("Properties", [])


def main():
    smoke = "--smoke" in sys.argv
    # ---- load inputs ----
    dil = pd.read_excel(DILIST_XLSX)
    dil["name_n"] = dil["CompoundName"].map(norm)
    dil["label"] = dil["DILIst Classification "].astype(int)
    print(f"DILIst rows: {len(dil)} | label counts: {dil.label.value_counts().to_dict()}")

    xl = pd.ExcelFile(WORKBOOK)
    v1 = xl.parse("version 1", header=1)
    v1.columns = [str(c).strip() for c in v1.columns]
    n1 = [c for c in v1.columns if "Name" in c][0]
    c1 = [c for c in v1.columns if "vDILI" in c][0]
    v1["name_n"] = v1[n1].map(norm)
    v1["cls"] = v1[c1].map(norm_cls)
    print(f"DILIrank 1.0 rows: {len(v1)} | classes: {v1.cls.value_counts().to_dict()}")

    cand = pd.concat([pd.read_csv(f) for f in SHARDS], ignore_index=True)
    cand["name_n"] = cand["query_name"].map(norm)
    cand_by_name = {n: g for n, g in cand.groupby("name_n")}
    print(f"existing candidates: {len(cand)} rows / {len(cand_by_name)} names")

    # ---- new lookups with resume ----
    if os.path.exists(NEW_CSV):
        new = pd.read_csv(NEW_CSV)
        done = set(new.query_name.map(norm)) | {"__no_hit__"}
        done_no_hit = set(pd.read_csv(NEW_CSV.replace(".csv", "_nohit.csv")).query_name.map(norm)) \
            if os.path.exists(NEW_CSV.replace(".csv", "_nohit.csv")) else set()
    else:
        new = pd.DataFrame(columns=["query_name", "cid", "inchikey", "inchikey14"])
        done = set()
        done_no_hit = set()

    missing = sorted(set(dil.name_n) - set(cand_by_name) - done - done_no_hit)
    print(f"missing names needing lookups: {len(missing)}", flush=True)

    # lookup: round 0 = full name, rounds 1-2 = salt-stripped variants;
    # per-name GET (threaded) for name->CID, aligned batch POST for CID->InChIKey
    from concurrent.futures import ThreadPoolExecutor
    nohit = []
    if missing:
        pending = list(missing)
        found = {}   # name -> (variant, cid)
        for rnd in range(3):
            if not pending:
                break
            req = []
            for n in pending:
                vl = variant_list(n)
                req.append((n, vl[rnd] if rnd < len(vl) else vl[-1]))
            still = []
            with ThreadPoolExecutor(max_workers=8) as ex:
                cids = list(ex.map(pubchem_cid_by_name, [v for (_, v) in req]))
            for (n, v), cid in zip(req, cids):
                if cid:
                    found[n] = (v, cid)
                else:
                    still.append(n)
            print(f"  round {rnd}: {len(pending) - len(still)} found, {len(still)} remaining",
                  flush=True)
            pending = still

        prop_rows = []
        cids = []
        names_by_cid = {}
        for n, (v, cid) in found.items():
            names_by_cid.setdefault(cid, []).append(n)
            cids.append(cid)
        for cs in range(0, len(cids), 100):
            chunk = cids[cs:cs + 100]
            props = pubchem_props_by_cids(chunk)
            cid2ik = {p.get("CID"): p.get("InChIKey") for p in props}
            for cid in chunk:
                ik = cid2ik.get(cid)
                for n in names_by_cid[cid]:
                    prop_rows.append({
                        "query_name": n, "lookup_variant": found[n][0], "cid": cid,
                        "inchikey": ik,
                        "inchikey14": ik.split("-")[0] if ik else None,
                    })
            time.sleep(0.3)

        new = pd.DataFrame(prop_rows, columns=["query_name", "lookup_variant", "cid",
                                               "inchikey", "inchikey14"])
        nohit = pending
        new.to_csv(NEW_CSV, index=False)
        pd.DataFrame({"query_name": nohit}).to_csv(NEW_CSV.replace(".csv", "_nohit.csv"), index=False)
        print(f"new lookups: {len(new)} rows | no-hit after 3 variant rounds: {len(nohit)}",
              flush=True)
    else:
        print("no new lookups needed (resuming from committed lookup CSVs)", flush=True)

    # ---- per-name keys ----
    name_keys = {}   # name_n -> (set full, set ik14)
    for n, g in cand.groupby("name_n"):
        name_keys[n] = (set(g.inchikey.dropna()), set(g.inchikey14.dropna()))
    for n, g in new.groupby("query_name"):
        nn = norm(n)
        name_keys.setdefault(nn, (set(), set()))
        f, k = name_keys[nn]
        f |= set(g.inchikey.dropna())
        k |= set(g.inchikey14.dropna())
        name_keys[nn] = (f, k)

    # v1 drug keys: name_n -> (full set, ik14 set, cls)
    v1_keys = {}
    for _, r in v1.iterrows():
        nn = r["name_n"]
        if nn in name_keys:
            v1_keys[nn] = (name_keys[nn][0], name_keys[nn][1], r["cls"])
    # build reverse indexes over v1 drugs
    full_idx = {}
    ik_idx = {}
    for nn, (fset, kset, cls) in v1_keys.items():
        for k in fset:
            full_idx.setdefault(k, set()).add((nn, cls))
        for k in kset:
            ik_idx.setdefault(k, set()).add((nn, cls))

    # ---- tier matching: DILIst name -> matched v1 drugs ----
    rows = []
    for _, r in dil.iterrows():
        nn = r["name_n"]
        keys = name_keys.get(nn, (set(), set()))
        fset, kset = keys
        hits = set()
        tier = None
        for k in fset:
            if k in full_idx:
                hits |= full_idx[k]
                tier = tier or "full"
        if not hits:
            for k in kset:
                if k in ik_idx:
                    hits |= ik_idx[k]
                    tier = tier or "ik14"
        if not hits:
            rows.append({"dilist_name": r["CompoundName"], "dilist_label": r["label"],
                         "match": "none", "tier": None, "v1_names": "", "v1_classes": "",
                         "conflict": False})
            continue
        classes = {c for (_, c) in hits}
        conflict = len(classes) > 1
        rows.append({"dilist_name": r["CompoundName"], "dilist_label": r["label"],
                     "match": "hit", "tier": tier,
                     "v1_names": ";".join(sorted(n for (n, _) in hits)),
                     "v1_classes": ";".join(sorted(classes)),
                     "conflict": conflict})
    tab = pd.DataFrame(rows)
    tab.to_csv(os.path.join(OUT, "full_dilist_match_table.csv"), index=False)
    print(f"match table: {len(tab)} rows; hits={int((tab.match=='hit').sum())}; "
          f"tier dist: {tab.tier.value_counts(dropna=False).to_dict()}; "
          f"conflicts: {int(tab.conflict.sum())}")

    # ---- agreement matrices ----
    def agreement(t):
        sub = t[(t.match == "hit") & (~t.conflict)].copy()
        sub["cls"] = sub.v1_classes
        sub = sub[sub.v1_classes.isin(["most", "less", "no", "ambiguous"])]
        m = pd.crosstab(sub.cls, sub.dilist_label)
        # non-ambiguous agreement within defined classes
        def_ok = int(((sub.cls.isin(["most", "less"])) & (sub.dilist_label == 1)).sum()
                     + ((sub.cls == "no") & (sub.dilist_label == 0)).sum())
        def_tot = int((sub.cls != "ambiguous").sum())
        amb = sub[sub.cls == "ambiguous"].dilist_label.value_counts().to_dict()
        return {"matrix": m.to_dict(), "defined_agreement": f"{def_ok}/{def_tot}",
                "ambiguous_label_counts": amb,
                "ambiguous_n": int((sub.cls == "ambiguous").sum()),
                "matched_n": int(len(sub)),
                "conflict_n": int((t.match == 'hit').sum() - len(sub)),
                "no_match_n": int((t.match == "none").sum())}

    res = {"tier_B_main": agreement(tab)}
    # tier A = full-key hits only
    tabA = tab.copy()
    tabA.loc[tabA.tier != "full", "match"] = "none"
    res["tier_A_strict"] = agreement(tabA)
    with open(os.path.join(OUT, "full_dilist_agreement.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(res, f, indent=2, default=str)
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
