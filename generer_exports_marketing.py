# -*- coding: utf-8 -*-
"""
Exports marketing — Atelier Zydka Manuel

Génère un premier fichier de citations exploitables
à partir du manuscrit.
"""

from __future__ import annotations

import re
from pathlib import Path


INPUT = Path("manuscrit_beatmakers.txt")
OUTPUT_DIR = Path("exports/reseaux/citations")
OUTPUT_FILE = OUTPUT_DIR / "citations_extraites.md"


KEY_PATTERNS = [
    "À retenir",
    "Erreur à éviter",
    "Objectif",
    "Le problème",
    "La méthode",
    "Commencez",
    "Un beat",
    "Votre catalogue",
    "La protection",
    "La visibilité",
]


def clean_line(line: str) -> str:
    line = line.strip()
    line = line.replace("**", "")
    line = line.replace("__", "")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def is_strong_line(line: str) -> bool:
    clean = clean_line(line)

    if len(clean) < 45:
        return False

    if len(clean) > 230:
        return False

    if clean.startswith("|"):
        return False

    if clean.startswith("["):
        return False

    return any(pattern.lower() in clean.lower() for pattern in KEY_PATTERNS)


def main() -> int:
    if not INPUT.exists():
        print(f"Fichier introuvable : {INPUT}")
        return 1

    raw = INPUT.read_text(encoding="utf-8")
    citations = []
    seen = set()

    for line in raw.splitlines():
        clean = clean_line(line)

        if not is_strong_line(clean):
            continue

        if clean in seen:
            continue

        seen.add(clean)
        citations.append(clean)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    content = [
        "# Citations extraites — Atelier Zydka Manuel",
        "",
        "Fichier généré automatiquement depuis `manuscrit_beatmakers.txt`.",
        "",
        f"Nombre de citations : {len(citations)}",
        "",
        "---",
        "",
    ]

    for i, quote in enumerate(citations, start=1):
        content.append(f"## Citation {i:02d}")
        content.append("")
        content.append(f"> {quote}")
        content.append("")

    OUTPUT_FILE.write_text("\n".join(content), encoding="utf-8")

    print(f"Exports marketing générés : {OUTPUT_FILE}")
    print(f"Citations extraites : {len(citations)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
