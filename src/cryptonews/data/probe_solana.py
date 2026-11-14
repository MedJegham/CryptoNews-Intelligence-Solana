"""Mesure rapide de la taille du sous-ensemble Solana dans chaque source (jalon 1).

Usage : python -m cryptonews.data.probe_solana
Ne modifie aucun fichier : affiche les volumes selon trois variantes du filtre
(strict/titre, strict/titre+description, écosystème/titre+description = choix du projet)
et la répartition par année de la variante retenue.
"""
from __future__ import annotations

import pandas as pd

from cryptonews.config import load_config, path
from cryptonews.data.solana_filter import solana_mask

# source -> (fichier, colonne titre, colonne description ou None, colonne corps ou None, colonne date)
SOURCES = {
    "dlt_sentiment_news": ("dlt_sentiment_news.parquet", "title", "description", None, "timestamp"),
    "coindesk": ("coindesk.parquet", "title", None, "body", "published_on"),
}


def _parse_dates(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return pd.to_datetime(s, unit="s", utc=True, errors="coerce")
    return pd.to_datetime(s, utc=True, errors="coerce", format="mixed")


def with_description(df: pd.DataFrame, desc_col: str | None, body_col: str | None) -> pd.DataFrame:
    """Ajoute une colonne `_desc` : description, ou à défaut le début du corps."""
    n = load_config()["corpus"]["solana_filter"]["body_as_description_chars"]
    df = df.copy()
    if desc_col and desc_col in df.columns:
        df["_desc"] = df[desc_col]
    elif body_col and body_col in df.columns:
        df["_desc"] = df[body_col].astype("string").str.slice(0, n)
    else:
        df["_desc"] = pd.NA
    return df


def report(name: str, df: pd.DataFrame, title: str, date_col: str) -> None:
    eco = load_config()["corpus"]["solana_filter"]["include_ecosystem"]
    strict_title = solana_mask(df, [title])
    strict_both = solana_mask(df, [title, "_desc"])
    chosen = solana_mask(df, [title, "_desc"], include_ecosystem=eco)
    unique_titles = df.loc[chosen, title].astype(str).str.strip().str.lower().nunique()
    print(f"\n=== {name} ===")
    print(f"total                              : {len(df):>8,}")
    print(f"strict, titre                      : {int(strict_title.sum()):>8,}")
    print(f"strict, titre + description        : {int(strict_both.sum()):>8,}")
    print(f"RETENU (écosystème={eco}), titre+desc : {int(chosen.sum()):>8,}  (titres uniques : {unique_titles:,})")
    if date_col and date_col in df.columns:
        years = _parse_dates(df.loc[chosen, date_col]).dt.year.value_counts().sort_index()
        print("par année (retenu)                 :", {int(k): int(v) for k, v in years.items()})
    only_desc = chosen & ~solana_mask(df, [title], include_ecosystem=eco)
    print(f"dont Solana absent du titre        : {int(only_desc.sum()):>8,}")
    print("exemples :")
    for t in df.loc[chosen, title].head(6):
        print("   -", t)


def probe_cryptovision() -> None:
    folder = path("raw") / "cryptovision"
    files = [p for p in folder.glob("**/*") if p.suffix.lower() in {".csv", ".xlsx", ".parquet"}]
    if not files:
        print(f"\n=== cryptovision === non trouvé : déposer les fichiers dans {folder}")
        return
    for f in files:
        suffix = f.suffix.lower()
        df = (pd.read_csv(f, low_memory=False) if suffix == ".csv"
              else pd.read_excel(f) if suffix == ".xlsx" else pd.read_parquet(f))
        print(f"\n--- {f.name} : colonnes {list(df.columns)}")
        if "Coin" in df.columns:
            print("Valeurs 'Coin' (top 15) :", df["Coin"].value_counts().head(15).to_dict())
        title = next((c for c in df.columns if c.lower() == "title"), None)
        if title:
            desc = next((c for c in df.columns if c.lower() == "description"), None)
            body = next((c for c in df.columns if c.lower() == "full_text"), None)
            date_col = next((c for c in df.columns if "date" in c.lower()), "")
            report(f"cryptovision/{f.name}", with_description(df, desc, body), title, date_col)


def main() -> None:
    for name, (fname, title, desc, body, date_col) in SOURCES.items():
        f = path("raw") / fname
        if not f.exists():
            print(f"\n=== {name} === absent ({f.name}) : lancer python -m cryptonews.data.download")
            continue
        report(name, with_description(pd.read_parquet(f), desc, body), title, date_col)
    probe_cryptovision()


if __name__ == "__main__":
    main()
