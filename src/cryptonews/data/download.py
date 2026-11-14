"""Téléchargement des sources Hugging Face vers data/raw/ (format parquet).

Usage :
    python -m cryptonews.data.download            # toutes les sources HF
    python -m cryptonews.data.download dlt        # une seule source

CryptoVision (Mendeley) n'a pas d'API simple : télécharger manuellement via
« Download All » sur https://data.mendeley.com/datasets/wvjjxr8bxx et extraire
les fichiers dans data/raw/cryptovision/.
"""
from __future__ import annotations

import sys

from datasets import load_dataset

from cryptonews.config import load_config, path

HF_SOURCES = {
    "dlt": "dlt_sentiment_news",
    "coindesk": "coindesk",
}


def download(short_name: str) -> None:
    key = HF_SOURCES[short_name]
    hf_id = load_config()["sources"][key]["hf_id"]
    out = path("raw") / f"{key}.parquet"
    if out.exists():
        print(f"[skip] {out.name} existe déjà")
        return
    print(f"[download] {hf_id} ...")
    ds = load_dataset(hf_id, split="train")
    df = ds.to_pandas()
    df.to_parquet(out, index=False)
    print(f"[ok] {len(df):,} lignes -> {out}")
    print(f"     colonnes : {list(df.columns)}")


def main(argv: list[str]) -> None:
    names = argv or list(HF_SOURCES)
    for name in names:
        download(name)


if __name__ == "__main__":
    main(sys.argv[1:])
