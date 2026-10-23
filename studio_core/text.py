# -*- coding: utf-8 -*-
"""
Nettoyage de texte — un seul endroit pour toutes les fonctions de nettoyage.

- clean_line   : ligne de manuscrit avant parsing (garde le Markdown utile) ;
- squash_spaces: espaces multiples réduits à un seul, bords supprimés ;
- clean_text   : texte prêt pour le rendu PDF (supprime les artefacts Markdown) ;
- clean_quote  : citation prête pour un visuel (guillemets français).
"""

from __future__ import annotations

import re


def clean_line(line: str) -> str:
    """Nettoyage léger sans détruire le Markdown utile."""
    return (
        line.replace(" ", " ")
        .replace("“", '"')
        .replace("”", '"')
        .replace("…", "...")
        .rstrip()
    )


def squash_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def clean_text(s: str) -> str:
    """
    Nettoyage éditorial centralisé avant rendu PDF.
    Supprime les artefacts Markdown et corrige les petites coquilles
    qui ne doivent jamais apparaître dans le PDF final.
    """
    if s is None:
        return ""

    s = str(s)

    # Nettoyage Markdown courant
    s = s.replace("**", "")
    s = s.replace("__", "")
    s = s.replace("[[TABLE_BLOCK]]", "")

    # Coquille Annexe D
    s = s.replace("positions juridiques ont évolu", "positions juridiques ont évolué")

    # Sécurité : lignes parasites composées uniquement de #
    if re.fullmatch(r"[ \\t\\u00a0]*#+[ \\t\\u00a0]*", s):
        return ""

    # Sécurité : # collé après la phrase finale
    s = re.sub(r"(Commencez par là\\.)\\s*#+\\s*", r"\\1", s)

    return s.strip()


def clean_quote(text: str) -> str:
    text = text.replace("“", "«")
    text = text.replace("”", "»")
    return squash_spaces(text)
