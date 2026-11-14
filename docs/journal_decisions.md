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
| 2026-11-14 | Licence CoinDesk HF corrigée : CC-BY-NC 4.0 (la V4 mentionnait « usage académique avec attribution »). CryptoVision : CC BY 4.0. | Vérification des fiches. |
