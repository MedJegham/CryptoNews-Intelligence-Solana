"""Construction du corpus Solana V1 (semaine 1, jour 4).

Usage : python -m cryptonews.data.build_corpus

Étapes (chaque étape est comptée dans reports/corpus_v1_stats.json) :
 1. chargement des sources (b) — CoinDesk HF + CryptoVision — vers un schéma commun ;
 2. nettoyage du texte (entités HTML, espaces) ; suppression des titres vides ;
 3. dates normalisées en UTC ; dates invalides ou hors [date_min, date_max] supprimées ;
 4. filtre Solana (strict + écosystème, titre + description) ;
 5. suppression des titres trop courts (< min_title_words mots : « Solana », « X icon »...) ;
 6. doublons exacts (titre normalisé) : on garde la plus ancienne occurrence ;
 7. quasi-doublons (rapidfuzz token_sort_ratio >= seuil ET <= 7 jours d'écart) : parcours
    chronologique glouton, un titre est retiré s'il est trop proche d'un titre déjà conservé ;
 8. marquage `in_dlt` : titre (normalisé) également présent dans DLT-Sentiment-News (a),
    utilisé plus tard pour éviter la fuite entre (a) et le val/test Solana.

Le texte original n'est PAS mis en minuscules ni dépouillé de sa ponctuation (V4 §4) ;
la normalisation ne sert qu'à la détection des doublons.
"""
from __future__ import annotations

import hashlib
import html
import json
import re

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from cryptonews.config import PROJECT_ROOT, load_config, path
from cryptonews.data.solana_filter import SOLANA_ECOSYSTEM, SOLANA_STRICT, solana_mask

_WS = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^0-9a-z$ ]+")


# --------------------------------------------------------------------------- utilitaires
def clean_text(s) -> str | None:
    if not isinstance(s, str):
        return None
    s = _WS.sub(" ", html.unescape(s)).strip()
    return s or None


def norm_title(s: str) -> str:
    """Clé de dédoublonnage : minuscules, ponctuation retirée (sauf $), espaces réduits."""
    s = s.lower().replace("’", "'").replace("'", "")
    return _WS.sub(" ", _NON_ALNUM.sub(" ", s)).strip()


def doc_id(source: str, url, title: str) -> str:
    key = f"{source}|{url or ''}|{title}"
    return f"{source[:2]}_{hashlib.sha1(key.encode('utf-8')).hexdigest()[:12]}"


def outlet_from_url(url) -> str | None:
    if not isinstance(url, str):
        return None
    m = re.match(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1).lower() if m else None


def matched_terms(text) -> str:
    if not isinstance(text, str):
        return ""
    found = {m.group(0) for m in SOLANA_STRICT.finditer(text)}
    found |= {m.group(0) for m in SOLANA_ECOSYSTEM.finditer(text)}
    return "|".join(sorted(found))


# --------------------------------------------------------------------------- chargement
COLUMNS = ["source_dataset", "outlet", "title", "description", "description_from_body",
           "published_at_utc", "url", "cv_coin_type"]


def load_coindesk(n_chars: int) -> pd.DataFrame:
    df = pd.read_parquet(path("raw") / "coindesk.parquet")
    # CryptoCompare renvoie des timestamps Unix (UTC) ; la colonne est naïve -> UTC.
    return pd.DataFrame({
        "source_dataset": "coindesk_hf",
        "outlet": df["source"].astype("string").str.lower(),
        "title": df["title"],
        "description": df["body"].astype("string").str.slice(0, n_chars),
        "description_from_body": True,
        "published_at_utc": pd.to_datetime(df["published_on"], utc=True, errors="coerce"),
        "url": df["url"],
        "cv_coin_type": pd.NA,
    })


def load_cryptovision() -> pd.DataFrame:
    files = sorted(path("raw").joinpath("cryptovision").glob("**/Raw*.csv"))
    if not files:
        print("[warn] CryptoVision introuvable (data/raw/cryptovision/**/Raw*.csv) — ignoré")
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(files[0], low_memory=False)
    return pd.DataFrame({
        "source_dataset": "cryptovision",
        "outlet": df["URL"].map(outlet_from_url),
        "title": df["Title"],
        "description": df["Description"],
        "description_from_body": False,
        "published_at_utc": pd.to_datetime(df["Date Time"], utc=True, errors="coerce", format="mixed"),
        "url": df["URL"],
        "cv_coin_type": df["Coin Type"],
    })


# --------------------------------------------------------------------------- quasi-doublons
def near_duplicate_drop(keys: list[str], times: pd.Series, threshold: int, window_days: float,
                        chunk: int = 1000) -> tuple[np.ndarray, list]:
    """`keys` triées chronologiquement. Retourne (masque à garder, paires (i, j, score)).

    Glouton : j est retiré s'il existe i < j CONSERVÉ avec score >= threshold et publié
    au plus `window_days` jours avant j (même news reprise par plusieurs sites). Les titres
    au même format publiés à des dates éloignées (« Price analysis 10/7 » vs « 1/27 ») restent.
    """
    n = len(keys)
    t = times.to_numpy(dtype="datetime64[ns]").astype("int64")
    window_ns = int(window_days * 86400 * 1e9)
    neighbours: dict[int, list[tuple[int, int]]] = {}
    for start in range(0, n, chunk):
        block = keys[start:start + chunk]
        scores = process.cdist(block, keys, scorer=fuzz.token_sort_ratio,
                               score_cutoff=threshold, dtype=np.uint8, workers=-1)
        rows, cols = np.nonzero(scores)
        for r, c in zip(rows, cols):
            j = start + r
            if c < j and t[j] - t[c] <= window_ns:  # titres antérieurs, dans la fenêtre
                neighbours.setdefault(j, []).append((int(c), int(scores[r, c])))
    keep = np.ones(n, dtype=bool)
    pairs = []
    for j in range(n):
        for i, s in neighbours.get(j, []):
            if keep[i]:
                keep[j] = False
                pairs.append((i, j, s))
                break
    return keep, pairs


# --------------------------------------------------------------------------- pipeline
def build() -> pd.DataFrame:
    cfg = load_config()["corpus"]
    fcfg = cfg["solana_filter"]
    stats: dict[str, dict | int] = {}

    df = pd.concat([load_coindesk(fcfg["body_as_description_chars"]), load_cryptovision()],
                   ignore_index=True)
    stats["1_loaded"] = df["source_dataset"].value_counts().to_dict()

    df["title"] = df["title"].map(clean_text)
    df["description"] = df["description"].map(clean_text)
    df = df[df["title"].notna()]
    stats["2_non_empty_title"] = len(df)

    lo = pd.Timestamp(cfg["date_min"], tz="UTC")
    hi = pd.Timestamp(cfg["date_max"], tz="UTC")
    df = df[df["published_at_utc"].between(lo, hi)]
    stats["3_valid_dates"] = len(df)

    df = df[solana_mask(df, ["title", "description"], include_ecosystem=fcfg["include_ecosystem"])]
    stats["4_solana_filter"] = df["source_dataset"].value_counts().to_dict()

    df = df.assign(n_words=df["title"].str.split().str.len())
    df = df[df["n_words"] >= cfg["min_title_words"]]
    stats["5_min_words"] = len(df)

    # Doublons exacts : on garde la plus ancienne ; à date égale, celle qui a une vraie description.
    df = df.assign(title_norm=df["title"].map(norm_title))
    df = df.sort_values(["published_at_utc", "description_from_body"]).reset_index(drop=True)
    df = df.drop_duplicates("title_norm", keep="first").reset_index(drop=True)
    stats["6_exact_dedup"] = len(df)

    keep, pairs = near_duplicate_drop(df["title_norm"].tolist(), df["published_at_utc"],
                                      cfg["near_duplicate_threshold"], cfg["near_duplicate_window_days"])
    sample = pd.DataFrame([{
        "kept_title": df.at[i, "title"], "kept_date": df.at[i, "published_at_utc"],
        "dropped_title": df.at[j, "title"], "dropped_date": df.at[j, "published_at_utc"], "score": s,
    } for i, j, s in pairs])
    df = df[keep].reset_index(drop=True)
    stats["7_near_dedup"] = len(df)

    dlt = pd.read_parquet(path("raw") / "dlt_sentiment_news.parquet", columns=["title"])
    dlt_keys = set(dlt["title"].dropna().map(clean_text).dropna().map(norm_title))
    df["in_dlt"] = df["title_norm"].isin(dlt_keys)

    eco = fcfg["include_ecosystem"]
    df["solana_in_title"] = solana_mask(df, ["title"], include_ecosystem=eco)
    df["solana_terms"] = df["title"].map(matched_terms)
    df["doc_id"] = [doc_id(s, u, t) for s, u, t in zip(df["source_dataset"], df["url"], df["title"])]

    stats["final"] = {
        "n": len(df),
        "by_source": df["source_dataset"].value_counts().to_dict(),
        "by_year": {int(k): int(v) for k, v in df["published_at_utc"].dt.year.value_counts().sort_index().items()},
        "solana_in_title": int(df["solana_in_title"].sum()),
        "in_dlt": int(df["in_dlt"].sum()),
        "date_min": str(df["published_at_utc"].min()),
        "date_max": str(df["published_at_utc"].max()),
    }

    cols = ["doc_id", "source_dataset", "outlet", "published_at_utc", "title", "description",
            "description_from_body", "url", "solana_in_title", "solana_terms", "n_words",
            "in_dlt", "cv_coin_type", "title_norm"]
    df = df[cols]

    out = path("interim") / "solana_corpus_v1.parquet"
    df.to_parquet(out, index=False)
    reports = PROJECT_ROOT / "reports"
    (reports / "corpus_v1_stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    sample.sample(min(200, len(sample)), random_state=load_config()["seed"]).sort_values("score").to_csv(
        reports / "near_duplicates_sample.csv", index=False, encoding="utf-8-sig")

    print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))
    print(f"[ok] {len(df):,} articles -> {out.relative_to(PROJECT_ROOT)}")
    print(f"[ok] {len(pairs):,} quasi-doublons retirés (échantillon : reports/near_duplicates_sample.csv)")
    return df


if __name__ == "__main__":
    build()
