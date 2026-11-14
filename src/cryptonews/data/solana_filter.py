"""Détection des articles qui mentionnent Solana / SOL.

Règles (strictes par défaut, pour limiter les faux positifs) :
- « Solana » quelle que soit la casse (Solana, SOLANA, solana) ;
- le ticker « $SOL » ;
- « SOL » en MAJUSCULES comme mot isolé (le mot « sol » en minuscules est ignoré :
  espagnol/portugais, « sol-gel », etc.) ;
- les paires de cotation SOL/USDT, SOLUSDT, SOL-USD.
Les termes de l'écosystème (Phantom, Jupiter, Raydium, pump.fun...) sont activés via
`include_ecosystem=True` (choix du projet, cf. configs/config.yaml). On garde des formes
non ambiguës (« Jupiter exchange », « $JUP », pas « Jupiter » seul = planète).
"""
from __future__ import annotations

import re

import pandas as pd

SOLANA_STRICT = re.compile(
    r"(?i:\bsolana\b)"              # Solana, toute casse
    r"|\$SOL\b"                      # ticker $SOL
    r"|(?<![A-Za-z0-9$])SOL\b"       # SOL majuscule isolé
    r"|\bSOL[/\-]?(?:USDT?|USDC)\b"  # SOL/USDT, SOLUSDT, SOL-USD
)

SOLANA_ECOSYSTEM = re.compile(
    r"(?i:\b(?:phantom wallet|raydium|jupiter (?:exchange|aggregator|dex)|jito|pump\.fun|"
    r"marinade finance|firedancer|saga phone|bonk|orca dex|magic eden|helium mobile)\b)"
    r"|\$(?:JUP|RAY|JTO|BONK|WIF)\b"
)


def mentions_solana(text: str | None, include_ecosystem: bool = False) -> bool:
    if not isinstance(text, str) or not text:
        return False
    if SOLANA_STRICT.search(text):
        return True
    return include_ecosystem and bool(SOLANA_ECOSYSTEM.search(text))


def solana_mask(df: pd.DataFrame, columns: list[str], include_ecosystem: bool = False) -> pd.Series:
    """Masque booléen : True si au moins une des colonnes mentionne Solana."""
    mask = pd.Series(False, index=df.index)
    for col in columns:
        if col in df.columns:
            mask |= df[col].map(lambda t: mentions_solana(t, include_ecosystem))
    return mask
