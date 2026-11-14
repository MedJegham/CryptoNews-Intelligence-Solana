"""Lecture / écriture des fichiers d'annotation (CSV versionnés dans data/annotation/)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from cryptonews.config import load_config, path

LABELS = ["positive", "neutral", "negative"]
COLUMNS = ["doc_id", "label", "exclude", "ambiguous", "used_description", "note", "annotated_at"]
KAPPA_SAMPLE = 100
KAPPA_MIN_DAYS = 7


def files() -> dict[str, Path]:
    d = path("annotation")
    return {
        "items": d / "to_annotate.csv",
        "main": d / "solana_annotations.csv",
        "reannot": d / "solana_reannotation.csv",
        "reannot_items": d / "reannotation_sample.csv",
    }


def load_items() -> pd.DataFrame:
    return pd.read_csv(files()["items"], encoding="utf-8-sig", keep_default_na=False)


def load_labels(kind: str) -> pd.DataFrame:
    f = files()[kind]
    if not f.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(f, encoding="utf-8-sig", keep_default_na=False, dtype={"note": str})


def _write(df: pd.DataFrame, f: Path) -> None:
    tmp = f.with_suffix(".tmp")
    df[COLUMNS].to_csv(tmp, index=False, encoding="utf-8-sig")
    tmp.replace(f)  # écriture atomique : pas de CSV corrompu si l'app est fermée brutalement


def append_label(kind: str, doc_id: str, label: str | None, exclude: bool, ambiguous: bool,
                 used_description: bool, note: str) -> None:
    df = load_labels(kind)
    df = df[df["doc_id"] != doc_id]
    row = {
        "doc_id": doc_id, "label": "" if exclude else label, "exclude": int(exclude),
        "ambiguous": int(ambiguous), "used_description": int(used_description),
        "note": note.strip().replace("\n", " "),
        "annotated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _write(pd.concat([df, pd.DataFrame([row])], ignore_index=True), files()[kind])


def undo_last(kind: str) -> str | None:
    df = load_labels(kind)
    if df.empty:
        return None
    last = df.iloc[-1]["doc_id"]
    _write(df.iloc[:-1], files()[kind])
    return last


def queue_main() -> tuple[pd.DataFrame, int, int]:
    """File d'attente : lot principal puis réserve, jusqu'à `annotation_target` labels valides."""
    items, done = load_items(), load_labels("main")
    target = load_config()["corpus"]["annotation_target"]
    n_valid = int((done["exclude"].astype(str) != "1").sum()) if not done.empty else 0
    todo = items[~items["doc_id"].isin(done["doc_id"])].sort_values("order")
    if n_valid >= target:
        todo = todo.iloc[0:0]
    return todo, n_valid, target


def reannotation_items() -> tuple[pd.DataFrame | None, str]:
    """100 titres annotés il y a >= 7 jours (hors `exclude`), tirage figé dans un CSV."""
    f = files()["reannot_items"]
    if f.exists():
        return pd.read_csv(f, encoding="utf-8-sig", keep_default_na=False), ""
    done = load_labels("main")
    if done.empty:
        return None, "Aucune annotation pour l'instant."
    done = done[done["exclude"].astype(str) != "1"].copy()
    done["ts"] = pd.to_datetime(done["annotated_at"], utc=True)
    cutoff = pd.Timestamp.now(tz="UTC") - timedelta(days=KAPPA_MIN_DAYS)
    eligible = done[done["ts"] <= cutoff]
    if len(eligible) < KAPPA_SAMPLE:
        ready = done["ts"].sort_values().iloc[min(KAPPA_SAMPLE, len(done)) - 1] + timedelta(days=KAPPA_MIN_DAYS)
        return None, (f"{len(eligible)} titre(s) éligible(s) sur {KAPPA_SAMPLE} requis "
                      f"(annotés il y a au moins {KAPPA_MIN_DAYS} jours). "
                      f"Disponible vers le {ready:%Y-%m-%d %H:%M} UTC si 100 titres sont annotés d'ici là.")
    pick = eligible.sample(KAPPA_SAMPLE, random_state=load_config()["seed"])[["doc_id"]]
    items = load_items().merge(pick, on="doc_id").sample(frac=1, random_state=load_config()["seed"])
    items["order"] = range(1, len(items) + 1)
    items.to_csv(f, index=False, encoding="utf-8-sig")
    return items, ""
