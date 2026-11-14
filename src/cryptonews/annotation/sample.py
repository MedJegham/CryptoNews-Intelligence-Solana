"""Tirage des titres à annoter (semaine 1, jour 6).

Usage : python -m cryptonews.annotation.sample [--force]

- Tirage aléatoire **stratifié par mois** (quota égal par mois, plafonné par la disponibilité :
  « water-filling »), graine fixe.
- Au plus `annotation_desc_only_max_share` (15 %) de titres sans Solana dans le titre.
- Lot principal (`annotation_target`, 900) + lot de réserve (`reserve`, 300) tiré parmi les
  titres restants, pour remplacer les titres marqués `exclude`.
- Ordre de présentation aléatoire (pas chronologique) ; le CSV ne contient ni date ni source
  (annotation à l'aveugle).
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from cryptonews.config import PROJECT_ROOT, load_config, path

RESERVE = 300


def month_quotas(available: pd.Series, total: int) -> pd.Series:
    """Quota égal par mois, plafonné par `available`, l'excédent étant redistribué."""
    quotas = pd.Series(0, index=available.index)
    remaining, open_months = total, available.index.tolist()
    while remaining > 0 and open_months:
        share = max(remaining // len(open_months), 1)
        for m in list(open_months):
            add = min(share, available[m] - quotas[m], remaining)
            quotas[m] += add
            remaining -= add
            if quotas[m] >= available[m]:
                open_months.remove(m)
            if remaining == 0:
                break
    return quotas


def stratified_draw(pool: pd.DataFrame, total: int, desc_share: float, rng: np.random.Generator) -> pd.DataFrame:
    quotas = month_quotas(pool.groupby("month").size(), total)
    parts = []
    for month, q in quotas.items():
        if q == 0:
            continue
        g = pool[pool["month"] == month]
        in_title, desc_only = g[g["solana_in_title"]], g[~g["solana_in_title"]]
        n_desc = min(int(np.floor(q * desc_share)), len(desc_only))
        n_title = min(q - n_desc, len(in_title))
        n_desc = min(q - n_title, len(desc_only))  # compléter si trop peu de titres « in_title »
        parts.append(in_title.sample(n_title, random_state=rng.integers(1 << 31)))
        parts.append(desc_only.sample(n_desc, random_state=rng.integers(1 << 31)))
    return pd.concat(parts)


def main(force: bool = False) -> None:
    cfg = load_config()
    out = path("annotation") / "to_annotate.csv"
    labels = path("annotation") / "solana_annotations.csv"
    if out.exists() and not force:
        sys.exit(f"[stop] {out.name} existe déjà (utiliser --force pour retirer au sort).")
    if labels.exists() and not force:
        sys.exit("[stop] des annotations existent déjà : un nouveau tirage les rendrait incohérentes.")

    rng = np.random.default_rng(cfg["seed"])
    corpus = pd.read_parquet(path("interim") / "solana_corpus_v1.parquet")
    corpus["month"] = corpus["published_at_utc"].dt.strftime("%Y-%m")
    share = cfg["corpus"]["annotation_desc_only_max_share"]

    main_set = stratified_draw(corpus, cfg["corpus"]["annotation_target"], share, rng)
    reserve = stratified_draw(corpus.drop(main_set.index), RESERVE, share, rng)

    main_set = main_set.sample(frac=1, random_state=rng.integers(1 << 31)).assign(batch="main")
    reserve = reserve.sample(frac=1, random_state=rng.integers(1 << 31)).assign(batch="reserve")
    sample = pd.concat([main_set, reserve], ignore_index=True)
    sample.insert(0, "order", np.arange(1, len(sample) + 1))

    cols = ["order", "doc_id", "batch", "title", "description", "solana_in_title"]
    sample[cols].to_csv(out, index=False, encoding="utf-8-sig")

    manifest = {
        "seed": cfg["seed"], "n_main": len(main_set), "n_reserve": len(reserve),
        "desc_only_share_main": round(float((~main_set["solana_in_title"]).mean()), 3),
        "months_main": main_set.groupby("month").size().to_dict(),
        "by_year_main": main_set["published_at_utc"].dt.year.value_counts().sort_index().to_dict(),
    }
    (PROJECT_ROOT / "reports" / "annotation_sample_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, default=int), encoding="utf-8")
    print(f"[ok] {len(main_set)} principal + {len(reserve)} réserve -> {out.relative_to(PROJECT_ROOT)}")
    print(f"     part « description seule » (principal) : {manifest['desc_only_share_main']:.1%}")
    print(f"     par année (principal) : {manifest['by_year_main']}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
