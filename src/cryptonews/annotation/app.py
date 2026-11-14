"""Outil d'annotation à l'aveugle (Streamlit).

Lancer :  streamlit run src/cryptonews/annotation/app.py

- Affiche un titre à la fois, sans date ni source ; la description n'apparaît qu'à la demande.
- Chaque clic écrit immédiatement dans data/annotation/*.csv (aucune perte si on ferme l'onglet).
- Mode « Ré-annotation (kappa) » : 100 titres annotés il y a >= 7 jours, labels précédents cachés.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from cryptonews.annotation import store

st.set_page_config(page_title="Annotation Solana", page_icon="🏷️", layout="centered")

GUIDE = "docs/guide_annotation.md"
BUTTONS = [("positive", "🟢 Positive / Bullish"), ("neutral", "⚪ Neutral"), ("negative", "🔴 Negative / Bearish")]

ss = st.session_state
ss.setdefault("show_desc", False)
ss.setdefault("form_key", 0)


def reset_item_state() -> None:
    ss.show_desc = False
    ss.form_key += 1  # réinitialise les widgets (case « ambigu », note)


def save(kind: str, doc_id: str, label: str | None, exclude: bool) -> None:
    k = ss.form_key
    store.append_label(kind, doc_id, label, exclude,
                       ambiguous=ss.get(f"amb_{k}", False),
                       used_description=ss.show_desc,
                       note=ss.get(f"note_{k}", ""))
    reset_item_state()


def undo(kind: str) -> None:
    store.undo_last(kind)
    reset_item_state()


# ------------------------------------------------------------------ barre latérale
with st.sidebar:
    st.header("Annotation Solana")
    mode = st.radio("Mode", ["Annotation", "Ré-annotation (kappa)"], on_change=reset_item_state)
    kind = "main" if mode == "Annotation" else "reannot"
    labels = store.load_labels(kind)
    today = datetime.now(timezone.utc).date().isoformat()
    n_today = int(labels["annotated_at"].astype(str).str.startswith(today).sum()) if not labels.empty else 0
    st.metric("Annotés aujourd'hui (UTC)", n_today, help="Objectif indicatif : ~180 / jour")
    if not labels.empty:
        dist = labels.loc[labels["exclude"].astype(str) != "1", "label"].value_counts()
        st.caption("Répartition : " + " · ".join(f"{k} {v}" for k, v in dist.items()))
        st.caption(f"Exclus : {int((labels['exclude'].astype(str) == '1').sum())} · "
                   f"Ambigus : {int((labels['ambiguous'].astype(str) == '1').sum())}")
    st.button("↩️ Retour (annuler le dernier)", on_click=undo, args=(kind,), disabled=labels.empty)
    st.caption(f"Guide : `{GUIDE}` — question : *pour un détenteur de SOL, bonne, neutre ou "
               "mauvaise nouvelle ?* Ne consultez aucun graphique de prix.")

# ------------------------------------------------------------------ file d'attente
if not store.files()["items"].exists():
    st.error("`data/annotation/to_annotate.csv` absent : lancer `python -m cryptonews.annotation.sample`.")
    st.stop()

if kind == "main":
    todo, n_valid, target = store.queue_main()
    st.progress(min(n_valid / target, 1.0), text=f"{n_valid} / {target} titres annotés (hors exclus)")
else:
    items, msg = store.reannotation_items()
    if items is None:
        st.info(msg)
        st.stop()
    todo = items[~items["doc_id"].isin(labels["doc_id"])]
    n_done = len(items) - len(todo)
    st.progress(n_done / len(items), text=f"Ré-annotation : {n_done} / {len(items)}")

if todo.empty:
    st.success("Terminé pour ce mode 🎉")
    st.stop()

item = todo.iloc[0]
k = ss.form_key

# ------------------------------------------------------------------ carte de l'article
st.markdown(f"#### {item['title']}")
if ss.show_desc:
    st.info(item["description"] or "*(pas de description)*")
elif not str(item.get("solana_in_title", "True")) in ("True", "true", "1"):
    st.caption("ℹ️ Solana n'apparaît pas dans ce titre : la description peut aider.")
st.button("Afficher la description", key=f"desc_{k}", disabled=ss.show_desc,
          on_click=lambda: ss.update(show_desc=True))

cols = st.columns(3)
for col, (lab, text) in zip(cols, BUTTONS):
    col.button(text, key=f"{lab}_{k}", use_container_width=True,
               on_click=save, args=(kind, item["doc_id"], lab, False))

c1, c2 = st.columns([1, 2])
c1.checkbox("Ambigu", key=f"amb_{k}")
c1.button("🚫 Exclure (inexploitable)", key=f"excl_{k}", on_click=save, args=(kind, item["doc_id"], None, True))
c2.text_input("Note (cas ambigu, règle utilisée…)", key=f"note_{k}")
st.caption(f"Titre n° {item['order']} · id `{item['doc_id']}`")
