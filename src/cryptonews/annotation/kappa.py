"""Accord intra-annotateur (semaine 2, jour 6).

Usage : python -m cryptonews.annotation.kappa
Compare la 1re passe (solana_annotations.csv) et la 2e passe (solana_reannotation.csv).
"""
from __future__ import annotations

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

from cryptonews.annotation.store import LABELS, load_items, load_labels
from cryptonews.config import load_config


def main() -> None:
    a, b = load_labels("main"), load_labels("reannot")
    if b.empty:
        print("Pas encore de ré-annotation.")
        return
    m = a.merge(b, on="doc_id", suffixes=("_1", "_2"))
    excl = (m["exclude_1"].astype(str) == "1") | (m["exclude_2"].astype(str) == "1")
    print(f"Titres comparés : {len(m)} (dont {int(excl.sum())} exclus dans une des passes, retirés)")
    m = m[~excl]
    kappa = cohen_kappa_score(m["label_1"], m["label_2"], labels=LABELS)
    target = load_config()["corpus"]["kappa_target"]
    print(f"Accord brut : {(m['label_1'] == m['label_2']).mean():.1%}")
    print(f"Kappa de Cohen : {kappa:.3f}  (cible >= {target} : {'OK' if kappa >= target else 'NON atteinte'})")
    cm = pd.DataFrame(confusion_matrix(m["label_1"], m["label_2"], labels=LABELS),
                      index=[f"passe1_{x}" for x in LABELS], columns=[f"passe2_{x}" for x in LABELS])
    print(cm)
    dis = m[m["label_1"] != m["label_2"]].merge(load_items()[["doc_id", "title"]], on="doc_id")
    print("\nDésaccords :")
    for _, r in dis.iterrows():
        print(f"  [{r.label_1} -> {r.label_2}] {r.title}")


if __name__ == "__main__":
    main()
