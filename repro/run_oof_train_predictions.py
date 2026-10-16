#!/usr/bin/env python3
"""OOF variant of run_independent_reproduction.py.

IDENTICAL pipeline to the faithful reproduction, with ONE addition: the
888-compound cross_val_predict probabilities (computed at the threshold step,
line ~180 of the original) are saved together with row identifiers, giving
out-of-fold predictions for every training-set compound (used for the 23
training-set reclassified drugs and the 93 training-set ambiguous drugs).

Model code is byte-identical in behavior to the original script; this variant
only persists an intermediate the original computed but discarded.

Usage:
    python -c "from sklearn.experimental import enable_halving_search_cv; \
import runpy; runpy.run_path(r'<this file>', run_name='__main__')"
"""
from __future__ import annotations
import argparse, hashlib, json, pickle, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import randint
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold, HalvingRandomSearchCV, cross_val_predict
from sklearn.metrics import (roc_curve, roc_auc_score, average_precision_score,
                             confusion_matrix, balanced_accuracy_score, matthews_corrcoef,
                             f1_score, precision_score)

REPO = Path(__file__).resolve().parents[1] / "repo"
ZIP = REPO / "local_implementation.zip"
NCV_CSV = REPO / "test_data_ncv_DILIst_888.csv"
HELDOUT_CSV = REPO / "test_data_heldouttest_DILIst_223.csv"
OUT = Path(__file__).resolve().parents[1] / "reproduction_outputs"

IDENTIFIERS = ["smiles_r", "TOXICITY", "Source_rank", "Source", "Data",
               "InChIKey", "InChIKey14", "protonated_smiles_r"]

PARAM_GRID = {
    'max_depth': randint(5, 20),
    'max_features': randint(30, 50),
    'min_samples_leaf': randint(5, 15),
    'min_samples_split': randint(5, 15),
    'n_estimators': [200, 300, 400, 500, 600],
    'bootstrap': [True, False],
    'oob_score': [False],
    'random_state': [42],
    'criterion': ['gini', 'entropy'],
    'n_jobs': [40],
    'class_weight': [None, 'balanced_subsample', 'balanced'],
}
SEEDS = list(range(42, 53))          # frozen, 42..52


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_feature_names() -> list[str]:
    with zipfile.ZipFile(ZIP) as z:
        names = [n for n in z.namelist() if n.endswith('features_morgan_mordred_maccs_physc.txt')]
        if len(names) != 1:
            raise FileNotFoundError("expected exactly one features_*.txt in the zip")
        return [ln for ln in z.read(names[0]).decode().splitlines() if ln.strip()]


def _unpickle(raw: bytes):
    import io
    try:
        return pickle.loads(raw)
    except Exception:
        import joblib
        return joblib.load(io.BytesIO(raw))


def load_proxy_models():
    with zipfile.ZipFile(ZIP) as z:
        sav = [n for n in z.namelist() if 'models/' in n and n.endswith('.sav') and 'final_dili' not in n]
    cmax_names = ["median pMolar unbound plasma concentration",
                  "median pMolar total plasma concentration"]
    items = []
    for stem in cmax_names:
        n = next(x for x in sav if x.endswith(f'bestlivmodel_{stem}_model.sav'))
        with zipfile.ZipFile(ZIP) as z:
            items.append((stem, _unpickle(z.read(n)), 'regressor'))
    proxy_ranks = [3, 5, 6, 7, 8, 11, 14, 15, 16]
    for sid in proxy_ranks:
        n = next(x for x in sav if x.endswith(f'bestlivmodel_{sid}_model.sav'))
        with zipfile.ZipFile(ZIP) as z:
            items.append((sid, _unpickle(z.read(n)), 'classifier'))
    return items


def build_feature_matrix(df: pd.DataFrame, feat: list[str], proxies):
    struct = df[feat].copy()          # preserves feat order
    for name, model, mode in proxies:
        if mode == 'classifier':
            struct[name] = model.predict_proba(df[feat].values)[:, 1]
        else:
            struct[name] = model.predict(df[feat].values)
    return struct.to_numpy(dtype=float), list(struct.columns)


def nested_cv_best_params(X_ncv, y_ncv, seeds):
    best_auc, best_params = -1.0, None
    for i in seeds:
        outer = KFold(n_splits=5, random_state=i, shuffle=True)
        for split, (tr_idx, te_idx) in enumerate(outer.split(X_ncv)):
            X_tr, y_tr = X_ncv[tr_idx], y_ncv[tr_idx]
            X_te, y_te = X_ncv[te_idx], y_ncv[te_idx]
            inner_cv = KFold(n_splits=4, random_state=i, shuffle=True)
            rf = RandomForestClassifier(n_jobs=-1, random_state=i)
            rsh = HalvingRandomSearchCV(rf, PARAM_GRID, factor=2, random_state=i,
                                        n_jobs=-1, verbose=0, cv=inner_cv)
            rsh.fit(X_tr, y_tr)
            clf = rsh.best_estimator_
            clf.fit(X_tr, y_tr)
            auc = roc_auc_score(y_te, clf.predict_proba(X_te)[:, 1])
            print(f"  seed={i} fold={split}  n_train={len(y_tr)}  AUC={auc:.6f}", flush=True)
            if auc > best_auc:
                best_auc, best_params = auc, clf.get_params()
    return best_params, best_auc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--smoke', action='store_true', help='tiny run: 1 seed, 1 fold')
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    print("== 1/5 load 857 selected features ==", flush=True)
    feat = load_feature_names()
    print(f"  {len(feat)} features", flush=True)

    print("== 2/5 load proxy/Cmax models from zip ==", flush=True)
    proxies = load_proxy_models()
    print(f"  {len(proxies)} models: {[ (n, m) for n,_,m in proxies ]}", flush=True)

    print("== 3/5 build FeatureNet matrices (888 / 223) ==", flush=True)
    ncv = pd.read_csv(NCV_CSV, low_memory=False)
    held = pd.read_csv(HELDOUT_CSV, low_memory=False)
    X_ncv, cols = build_feature_matrix(ncv, feat, proxies)
    X_held, _ = build_feature_matrix(held, feat, proxies)
    y_ncv = ncv['TOXICITY'].astype(int).values
    y_held = held['TOXICITY'].astype(int).values
    print(f"  X_ncv={X_ncv.shape}  X_held={X_held.shape}  n_features={X_ncv.shape[1]}", flush=True)

    print("== 4/5 nested CV (select best params by AUC) ==", flush=True)
    seeds = SEEDS[:1] if args.smoke else SEEDS
    best_params, best_auc = nested_cv_best_params(X_ncv, y_ncv, seeds)
    print(f"  best AUC (fold) = {best_auc:.6f}", flush=True)

    print("== 5/5 retrain on 888, threshold via CV, predict 223 ==", flush=True)
    clf = RandomForestClassifier(**best_params)
    clf.fit(X_ncv, y_ncv)
    inner_cv = KFold(n_splits=4, random_state=53, shuffle=True)
    cv_prob = cross_val_predict(clf, X_ncv, y_ncv, cv=inner_cv, method='predict_proba', n_jobs=-1)[:, 1]
    # ---- OOF addition (the only difference from the original script) ----
    oof = ncv[IDENTIFIERS].copy()
    oof["oof_proba_class1"] = cv_prob
    oof.to_csv(OUT / "oof_888_predictions.csv", index=False)
    print(f"  saved OOF predictions for {len(oof)} training compounds", flush=True)
    # ---------------------------------------------------------------------
    fpr, tpr, thresh = roc_curve(y_ncv, cv_prob)
    best_thresh = thresh[np.argmax(tpr - fpr)]
    y_proba = clf.predict_proba(X_held)[:, 1]
    y_pred = (y_proba > best_thresh).astype(int)
    ap = average_precision_score(y_held, y_proba)
    auc = roc_auc_score(y_held, y_proba)
    tn, fp, fn, tp = confusion_matrix(y_held, y_pred).ravel()
    res = {
        "n_features": int(X_ncv.shape[1]),
        "n_train_888": int(len(y_ncv)), "n_test_223": int(len(y_held)),
        "best_fold_auc": float(best_auc),
        "best_params": {k: str(v) for k, v in best_params.items()},
        "best_threshold": float(best_thresh),
        "auc_pr_heldout": float(ap), "auc_roc_heldout": float(auc),
        "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "ba": float(balanced_accuracy_score(y_held, y_pred)),
        "mcc": float(matthews_corrcoef(y_held, y_pred)),
    }
    print(json.dumps(res, indent=2), flush=True)
    (OUT / "oof_variant_metrics.json").write_text(json.dumps(res, indent=2))
    np.save(OUT / "y_heldout_true.npy", y_held)
    np.save(OUT / "y_heldout_proba.npy", y_proba)
    print(f"\nSaved -> {OUT}", flush=True)


if __name__ == '__main__':
    sys.exit(main())
