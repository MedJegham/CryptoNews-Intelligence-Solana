# Journal des décisions

Chaque décision méthodologique est datée et justifiée (traçabilité pour le rapport).

| Date | Décision | Justification |
|---|---|---|
| 2026-11-14 | Environnement `venv` local (Python 3.11) ; fine-tuning sur Colab/Kaggle (`requirements-transformer.txt`). | Baselines sur CPU, Transformer sur GPU gratuit (V4 §6). |
| 2026-11-14 | Code réutilisable dans `src/cryptonews/`, notebooks pour l'EDA et les figures. | Reproductibilité. |
| 2026-11-14 | Données brutes exclues de Git ; annotations (`data/annotation/`) versionnées. | Licences NC + taille des fichiers. |
| 2026-11-14 | Filtre Solana strict : « Solana » (toute casse), `$SOL`, `SOL` en majuscules, paires SOL/USDT. Termes d'écosystème désactivés par défaut. | Limiter les faux positifs (« sol » en espagnol, etc.). À revoir après mesure. |
| 2026-11-14 | Filtre retenu : strict + écosystème, recherché dans titre + description (CoinDesk : 300 premiers caractères du corps). | Choix de l'étudiant après questions de validation. |
| 2026-11-14 | Mesure jalon 1 (avant dédoublonnage) : DLT-Sentiment-News 2 393 articles Solana ; CoinDesk HF 11 614 (dont 7 374 en 2024) ; CryptoVision à mesurer. Seuil O1 (≥ 1 500) largement atteint → pas de fallback. | `python -m cryptonews.data.probe_solana`. |
| 2026-11-14 | Fuite (a) → Solana : on garde (a) antérieur au début du test et on retire de (a) tout titre identique ou quasi identique à un titre Solana val/test. | Conforme V4 §5 ; (a) contient 2 393 titres Solana. |
| 2026-11-14 | Échantillon à annoter (~900) : tirage aléatoire stratifié par mois (2021–2025), graine fixe. | 2024 domine le corpus brut ; couvrir plusieurs régimes de marché. |
| 2026-11-14 | Titres multi-actifs ou avec Solana seulement dans la description : conservés. Règle d'annotation : impact probable pour SOL, « Neutral » si SOL n'est que cité dans une liste. Colonne `solana_in_title` ajoutée pour les ablations. | Garder le volume tout en rendant l'étiquette définissable. |
| 2026-11-14 | Corpus (b) = CoinDesk HF + CryptoVision ; DLT-Sentiment-News reste le corpus (a) séparé (colonne `in_dlt` = 753 titres communs). | Garder (a) et (b) distincts, conformément à la V4 §3. |
| 2026-11-14 | Colonne `Coin Type` de CryptoVision **non utilisée** pour filtrer (conservée en métadonnée `cv_coin_type`). | Peu fiable : sur 17 348 lignes « Solana », seules 4 627 mentionnent Solana ; titres sans rapport ou noms de sources (« DappRadar »). |
| 2026-11-14 | Nettoyage : dates hors [2020-01-01, 2025-12-31] retirées ; titres < 3 mots retirés ; doublons exacts (titre normalisé) → plus ancienne occurrence ; quasi-doublons = rapidfuzz `token_sort_ratio` ≥ 92 **et** ≤ 7 jours d'écart. | Sans fenêtre, des articles distincts au même format (« Price analysis 10/7 » vs « 1/27 ») étaient fusionnés. Contrôle manuel : `reports/near_duplicates_sample.csv`. |
| 2026-11-14 | Dates supposées UTC pour CoinDesk HF (timestamps CryptoCompare) ; CryptoVision déjà en +00:00. Cohérence vérifiée : pour 99 % des articles présents en double, l'écart de date est < 0,7 jour. | Contrôle des dates incohérentes (planning, jour 4). |
| 2026-11-14 | **Corpus V1 : 14 953 articles** (CoinDesk HF 10 472, CryptoVision 4 481), 2020-03 → 2025-08, 80 % avec Solana dans le titre, 69 médias. | `reports/corpus_v1_stats.json`, `notebooks/01_eda_corpus.ipynb`. |
| 2026-11-14 | Annotation : question = « impact probable sur SOL » ; 3 classes + drapeau `exclude` (remplacé depuis la réserve) + `ambiguous` ; titre seul, description à la demande (`used_description` enregistré). | Choix de l'étudiant ; aligné avec O4 et l'ablation « titre seul vs titre + description ». |
| 2026-11-14 | Outil : app Streamlit + CSV ; le CSV d'items ne contient ni date ni source ; ordre de présentation aléatoire. | Annotation à l'aveugle du prix et du temps (V4 §3c). |
| 2026-11-14 | Échantillon : 900 + 300 de réserve, stratifié par mois (quota égal, plafonné par la disponibilité), graine 42 ; 13,2 % « description seule ». | `reports/annotation_sample_manifest.json`. |
| 2026-11-14 | Licence CoinDesk HF corrigée : CC-BY-NC 4.0 (la V4 mentionnait « usage académique avec attribution »). CryptoVision : CC BY 4.0. | Vérification des fiches. |
