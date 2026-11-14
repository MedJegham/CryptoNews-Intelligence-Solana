# Sources de données et licences

Vérifié le 2026-11-14. À compléter au fil de la collecte (semaine 1, jours 2–3).

| Rôle (V4) | Source | Accès | Licence | Remarques |
|---|---|---|---|---|
| (a) Entraînement général | **DLT-Sentiment-News** — ExponentialScience, arXiv 2602.22045 | Hugging Face `ExponentialScience/DLT-Sentiment-News` | **CC-BY-NC 4.0** (recherche) | 23 301 titres CryptoPanic (2021-01 → 2025-05), un seul split `train`. Colonnes : `timestamp`, `title`, `description`, `text`, `market_direction` (0 = neutral, 1 = bearish, 2 = bullish), `vote_counts`, `total_votes`, `url`, `source_url`. Étiquettes par votes communautaires (seuils aux 25e/75e percentiles). |
| (b) Corpus Solana — principal | **CryptoVision** — Mendeley Data, DOI 10.17632/wvjjxr8bxx.2 (v2, 26/05/2026) | Téléchargement manuel (« Download All ») → `data/raw/cryptovision/` | **CC BY 4.0** | ~188 k articles (2017–2025), ~118 k après nettoyage. Colonnes brutes : `URL`, `Title`, `Description`, `Date Time`, `Coin`, `Type`. Étiquettes FinBERT présentes : **non utilisées comme vérité terrain**. |
| (b) Corpus Solana — secondaire | **CoinDesk 2020–2025** | Hugging Face `maryamfakhari/crypto-news-coindesk-2020-2025` | **CC-BY-NC 4.0** (et non « usage académique » seulement) | ~229 k lignes, 79 sources différentes (pas uniquement CoinDesk), dates dès 2019-10. Colonnes : `published_on`, `title`, `body`, `url`, `tags`, `categories`, `source`, `upvotes`, `downvotes`. |
| (d) Marché | API publique d'une bourse (à confirmer) — OHLCV horaires SOL/USDT, BTC/USDT | API REST | Conditions d'usage à citer | Semaine 6. |

## Obligations
- **CC-BY-NC 4.0** : usage non commercial, attribution (citer l'article/la fiche), pas de redistribution commerciale.
- **CC BY 4.0** : attribution (citer le DOI).
- Les données brutes ne sont **pas versionnées** dans Git (`.gitignore`) ; seuls les scripts qui les reproduisent et nos propres annotations le sont.

## Références à citer
- DLT-Corpus: A Large-Scale Text Collection for the Distributed Ledger Technology Domain, arXiv:2602.22045.
- CryptoVision: A Comprehensive Dataset for Crypto News and Sentiment Analysis, Mendeley Data, v2, doi:10.17632/wvjjxr8bxx.2.
- maryamfakhari, crypto-news-coindesk-2020-2025, Hugging Face Datasets.
