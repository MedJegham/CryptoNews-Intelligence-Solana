# Guide d'annotation — sentiment de marché Solana (version 1.0, brouillon)

**Statut :** brouillon du 2026-11-14, à valider avant la semaine 2. Toute modification après
le début de l'annotation est datée dans le journal des modifications (en fin de document).

## 1. La question à se poser

> **« Pour un détenteur de SOL, cette actualité est-elle plutôt une bonne nouvelle, une nouvelle
> sans effet clair, ou une mauvaise nouvelle ? »**

On juge l'**impact probable de l'information sur le marché de SOL**, tel qu'un lecteur averti le
percevrait **au moment de la publication**, et non le ton général du titre ni ce qui s'est passé
ensuite.

| Label | Code | Définition |
|---|---|---|
| **Positive / Bullish** | `positive` | L'information est favorable à SOL : adoption, croissance, hausse de prix, produit financier (ETF), mise à niveau, flux entrants, prévision haussière… |
| **Neutral** | `neutral` | Pas d'effet clair sur SOL : information factuelle ou descriptive, titre informatif sans direction, SOL simplement cité dans une liste, effets positifs et négatifs équilibrés, question réellement ouverte. |
| **Negative / Bearish** | `negative` | L'information est défavorable à SOL : panne, piratage, baisse de prix, régulation hostile, ventes massives, déblocage de jetons, prévision baissière… |

Drapeaux complémentaires (indépendants du label) :

| Drapeau | Quand le cocher |
|---|---|
| `exclude` | Titre inexploitable : sans rapport avec la crypto ou le marché, rubrique, titre de podcast ou de page (« FOMO HOUR 184 », « Magic Eden Company Intelligence »), texte tronqué ou illisible. **Aucun label n'est saisi** ; le titre sera remplacé par un titre de réserve. |
| `ambiguous` | On hésite vraiment entre deux labels. On choisit quand même le plus probable et on écrit une note. |
| `used_description` | Enregistré automatiquement si la description a été affichée. |

## 2. Conditions d'annotation (aveugle)

1. **Ne jamais consulter un graphique de prix**, ni chercher l'article ou sa date pendant
   l'annotation. L'outil n'affiche ni date ni source : c'est voulu.
2. **Aucun pré-étiquetage automatique** (ni VADER, ni FinBERT, ni étiquettes CryptoVision ou DLT).
3. On annote d'abord **le titre seul**. La description n'est affichée **qu'en cas de besoin**
   (titre sans mention de Solana, ou impossible à juger).
4. Environ 180 titres par jour, en sessions de 45 minutes au plus avec des pauses (la fatigue fait
   dériver les labels).
5. On ne revient pas sur un label déjà enregistré, sauf erreur de clic évidente (bouton « Retour »).

## 3. Procédure de décision (dans l'ordre)

1. **Est-ce exploitable ?** Si non → `exclude`.
2. **SOL / Solana est-il le sujet, ou directement concerné ?**
   - Oui → aller à l'étape 3.
   - Non, SOL est seulement cité dans une liste ou en arrière-plan → **`neutral`**, sauf si le
     titre donne une direction commune à tout le marché (« Bitcoin, Ether and Solana Plunge… »
     → `negative`).
3. **Quelle direction pour SOL ?** Appliquer les règles de la section 4. Si les éléments positifs
   et négatifs s'équilibrent, ou si l'on ne peut pas décider → `neutral` (+ `ambiguous` si on
   hésite).

## 4. Règles par type d'information

| # | Situation | Label | Exemple réel du corpus |
|---|---|---|---|
| R1 | Hausse de prix, record, rallye de SOL | positive | *Solana (SOL) Analyst Predicts Strong Rally as Correction Ends* |
| R2 | Baisse, chute, liquidations sur SOL | negative | *SOL price drop to $120 looks likely, but there's a silver lining* |
| R3 | Mouvement commun à tout le marché, SOL cité explicitement | direction du mouvement | *Bitcoin, Dogecoin and Solana Plunge as Jobs Data… Spook Investors* → negative |
| R4 | Analyse de prix multi-actifs sans direction (« Price analysis 6/13: BTC, ETH, … SOL ») | neutral | *Price analysis 12/11: SPX, DXY, BTC, ETH, BNB, XRP, SOL, ADA, DOGE, AVAX* |
| R5 | Panne, arrêt du réseau, congestion grave | negative | *Solana Network Faces Outages Amid Surging Memecoin Transactions* |
| R6 | Reprise après une panne | neutral si le titre est factuel ; positive si l'accent est mis sur la reprise | *SOL Price Regains $100 Looking Past the Solana Outage Episode* → positive |
| R7 | Piratage, exploit, arnaque **dans l'écosystème Solana** | negative | *Solana DeFi Protocol Loopscale Halts Lending After $5.8M Exploit* |
| R8 | Piratage hors Solana, ou arnaque qui utilise seulement le nom de Solana | neutral | *Activision Blizzard Twitter Account Hacked to Shill Solana Crypto Scam* |
| R9 | ETF Solana : dépôt, approbation, intérêt institutionnel | positive | *BREAKING: First Spot Solana ETF Filing Officially Submitted In The US* |
| R10 | ETF Solana : rejet, report, retrait | negative | *Solana ETFs may take until 2026: Bloomberg Intelligence* |
| R11 | Déblocage de jetons, ventes d'un gros détenteur (FTX, baleines) | negative | *FTX gets green light to sell $3.4B in bitcoin, ethereum, solana* |
| R12 | Listing ou intégration de SOL ou d'un jeton Solana, partenariat, adoption | positive | *Travala integrates Solana, expands crypto travel options…* |
| R13 | Délisting, abandon, départ d'un projet de Solana | negative | — |
| R14 | Mise à niveau, nouveau client, amélioration technique (Firedancer…) | positive | *Coinshares' 2025 Crypto Trends Report Highlights L2 Adoption and Solana Upgrades* |
| R15 | Procès, régulation, SOL qualifié de *security* | negative | — |
| R16 | Mème-coins Solana qui montent (activité, frais, volume pour Solana) | positive | *Solana Memecoin Triggers Frenzy as Traders Make 100x Profits* |
| R17 | Mème-coin Solana qui s'effondre ou rug pull | negative | *Not So 'Chill Guy': Solana Meme Coin Plummets After IP Creator's Accounts Hacked* |
| R18 | Promotion d'un jeton tiers (prévente, « will explode 15,000% ») où SOL n'est qu'un décor | neutral | *Donald's Bitcoin (DONBTC) Solana Memecoin Will Explode 15,000%…* |
| R19 | Question orientée (« Will Solana Hit $290…? Analysts Predict Bullish Surge ») | direction suggérée | → positive |
| R20 | Question ouverte (« Is it too late to invest in Solana? ») | neutral | — |
| R21 | Comparaison avec un concurrent : SOL gagne ou perd | positive / negative | *Solana NFT adoption rises: 3x more users than Ethereum, Polygon* → positive |
| R22 | Information concernant uniquement un concurrent (ETH, ADA…) | neutral | *Ethereum (ETH) vs. Solana (SOL): Whose Upgrade Will Have the Most Impact?* → neutral |
| R23 | Négation : lire le sens réel | selon le sens | *No Significant Pullback in Sight for Bitcoin As Solana Positions for Major Rally* → positive |
| R24 | Titre mitigé (« …but there's a silver lining ») | l'information principale l'emporte (avant le « but ») | voir R2 |
| R25 | Ironie, sarcasme | sens voulu ; cocher `ambiguous` en cas de doute | *Solana 'roast' reveals painful truths* → negative |

## 5. Ce qu'on ne fait pas

- On n'utilise pas ses connaissances de ce qui s'est passé **après** la publication.
- On ne juge pas la qualité, la fiabilité ou le sensationnalisme du média : un titre racoleur
  haussier reste `positive`.
- On ne cherche pas l'article en ligne.

## 6. Cas ambigus (registre)

Chaque titre coché `ambiguous` reçoit une note courte. En fin de semaine 2, on relit ces notes
pour compléter ce guide (nouvelles règles R26+), sans réannoter rétroactivement le gold set, sauf
décision explicite consignée dans le journal.

## 7. Contrôle de cohérence (kappa intra-annotateur)

- Au moins 7 jours après la première annotation, on réannote **100 titres tirés au hasard** (mode
  « Ré-annotation » de l'outil), sans voir les labels précédents.
- On calcule le kappa de Cohen sur les 3 classes (titres `exclude` mis à part). Cible V4 : **κ ≥ 0,6**.
- On rapporte aussi la matrice de confusion entre les deux passes et les titres en désaccord.

## 8. Format des fichiers

| Fichier | Contenu |
|---|---|
| `data/annotation/to_annotate.csv` | `order, doc_id, title, description, solana_in_title` (**ni date ni source**) |
| `data/annotation/solana_annotations.csv` | `doc_id, label, exclude, ambiguous, used_description, note, annotated_at` |
| `data/annotation/solana_reannotation.csv` | même schéma, 2e passe (kappa) |

`label ∈ {positive, neutral, negative}`, vide si `exclude = 1`. `annotated_at` est en UTC (ISO 8601).

## Journal des modifications du guide

| Date | Version | Modification |
|---|---|---|
| 2026-11-14 | 1.0 | Brouillon initial (25 règles, exemples tirés du corpus V1). |
