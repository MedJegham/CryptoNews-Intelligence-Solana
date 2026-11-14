# CryptoNews Intelligence — Solana

Classification du sentiment de marché des titres d'actualité Solana (positif/haussier, neutre,
négatif/baissier) et étude exploratoire de la réaction du marché de SOL (+1 h, +4 h, +24 h).

Projet semestriel NLP 2026–2027 — 5e année ingénieur Data Science et IA — projet individuel.

> Hors périmètre : conseil financier, prédiction du prix, trading automatisé. Aucune causalité n'est affirmée.

## Installation (Windows / PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Fine-tuning (semaine 4, GPU Colab/Kaggle) : `pip install -r requirements.txt -r requirements-transformer.txt`.

## Données

```powershell
python -m cryptonews.data.download        # DLT-Sentiment-News + CoinDesk (Hugging Face)
python -m cryptonews.data.probe_solana    # mesure du sous-ensemble Solana (jalon 1)
```

CryptoVision : téléchargement manuel depuis https://data.mendeley.com/datasets/wvjjxr8bxx
(« Download All »), puis extraction dans `data/raw/cryptovision/`.

Sources et licences : [docs/sources_licences.md](docs/sources_licences.md).

## Arborescence

```
configs/config.yaml        paramètres centraux (graines, split, chemins, marché)
src/cryptonews/            code réutilisable (package installable)
  data/                    téléchargement, filtre Solana, nettoyage
notebooks/                 EDA, expériences, figures
data/raw|interim|processed données (non versionnées)
data/annotation/           annotations manuelles (versionnées)
data/market/               OHLCV SOL/BTC (non versionnées)
models/                    modèles entraînés (non versionnés)
reports/figures/           figures du rapport
docs/                      guide d'annotation, sources, journal des décisions
```

## Planning (7 semaines)

| Semaine | Phase | Livrable |
|---|---|---|
| 1 | Préparation & données | Dataset Solana V1 + EDA |
| 2 | Annotation (~900 titres, κ ≥ 0,6) | `solana_annotated.csv` + kappa |
| 3 | Baselines (Majority, VADER, TF-IDF + LR) | Premiers résultats |
| 4 | Transformer + adaptation Solana | Modèle Transformer |
| 5 | Évaluation (5 graines, bootstrap, erreurs, ablations) | Résultats NLP finaux |
| 6 | Étude de marché SOL/BTC (event study) | Résultats marché |
| 7 | Prototype, rapport, soutenance | Projet final |

## Déclaration d'usage de l'IA

Un assistant IA (Claude, Anthropic) a aidé à rédiger la proposition et à mettre en place la structure
du dépôt et les scripts initiaux (collecte, filtrage). L'annotation des données est manuelle.
Toute aide IA significative ultérieure est consignée dans `docs/journal_decisions.md`.
