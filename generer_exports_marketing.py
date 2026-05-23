# -*- coding: utf-8 -*-
"""
Exports marketing — Atelier Zydka Manuel

Version propre V2.1 :
génère une sélection contrôlée de citations marketing premium.

Objectif :
éviter les citations cassées, titres d'annexes, emojis mal rendus,
fragments Markdown ou textes trop longs dans les visuels réseaux.
"""

from __future__ import annotations

from pathlib import Path


OUTPUT_DIR = Path("exports/reseaux/citations")
OUTPUT_FILE = OUTPUT_DIR / "citations_extraites.md"


CITATIONS = [
    "Un beat prêt à vendre est un beat prêt à livrer.",
    "Votre catalogue doit devenir consultable en moins de deux minutes.",
    "Un beat mal nommé est un beat presque mort.",
    "Un beatmaker organisé ne produit pas plus. Il vend mieux.",
    "Vous ne vendez pas juste des fichiers WAV. Vous vendez des droits, de la clarté et de la confiance.",
    "Le cadre ne tue pas la vibe. Il protège la vibe.",
    "Un contrat simple vaut mieux qu’une promesse floue.",
    "La protection commence par la traçabilité.",
    "L’IA augmente les beatmakers organisés et noie les beatmakers dispersés.",
    "L’international commence par un catalogue propre.",
    "Avant de chercher plus de visibilité, rendez votre catalogue exploitable.",
    "Ne rangez pas tout votre disque dur aujourd’hui. Commencez par 10 beats.",
    "Un paiement ne remplace pas une licence.",
    "Une split sheet simple évite des mois de tension.",
    "Votre force ne vient pas du ton. Elle vient de la clarté du dossier.",
    "Un vrai professionnel accepte la vérification. Un arnaqueur insiste sur l’urgence.",
    "Un beatmaker sérieux ne vend pas au hasard. Il sait ce qu’il autorise.",
    "Les revenus passifs commencent par un catalogue actif bien organisé.",
    "Une preview doit donner envie. Un WAV doit laisser de la marge.",
    "Un disque dur plein ne prouve rien. Un beat terminé, nommé, livré et utilisé vaut plus que 50 brouillons oubliés.",
]


def write_output() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Citations extraites — Atelier Zydka Manuel",
        "",
        "Fichier généré automatiquement depuis une sélection éditoriale contrôlée.",
        "",
        f"Nombre de citations : {len(CITATIONS)}",
        "",
        "---",
        "",
    ]

    for index, citation in enumerate(CITATIONS, start=1):
        lines.append(f"## Citation {index:02d}")
        lines.append("")
        lines.append(f"> {citation}")
        lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    write_output()

    print(f"Exports marketing générés : {OUTPUT_FILE}")
    print(f"Citations extraites : {len(CITATIONS)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
