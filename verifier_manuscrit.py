# -*- coding: utf-8 -*-
"""
Vérificateur de manuscrit — Atelier Zydka Manuel

Objectif :
Détecter les erreurs éditoriales courantes avant génération PDF.

Usage :
python3 verifier_manuscrit.py
python3 verifier_manuscrit.py manuscrit_beatmakers.txt
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List


DEFAULT_MANUSCRIPT = "manuscrit_beatmakers.txt"
IMAGES_DIR = Path("images")

KNOWN_TAGS = [
    "[IMAGE:",
    "[CALLOUT:",
    "[QUOTE:",
    "[OPENING_IMAGE:",
    "[PAGE_BREAK]",
]


@dataclass
class Issue:
    level: str
    line: int
    message: str
    content: str = ""


def read_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    return path.read_text(encoding="utf-8")


def is_markdown_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not is_markdown_table_line(stripped):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(cell and set(cell) <= {"-", ":", " "} for cell in cells)


def extract_image_name(tag_line: str) -> str | None:
    """
    Extrait le nom de fichier depuis :
    [IMAGE: fichier.png | légende]
    [OPENING_IMAGE: fichier.png | titre]
    """
    match = re.match(r"^\[(?:IMAGE|OPENING_IMAGE):\s*([^|\]]+)", tag_line.strip(), re.I)
    if not match:
        return None
    return match.group(1).strip()


def detect_chapters(raw: str) -> List[str]:
    try:
        from parser_manuscrit import parse_manuscript
        return [chapter.title for chapter in parse_manuscript(raw)]
    except Exception:
        return []


def check_manuscript(raw: str) -> List[Issue]:
    issues: List[Issue] = []
    lines = raw.splitlines()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not stripped:
            continue

        # 1. Caractères parasites
        if re.fullmatch(r"#+", stripped):
            issues.append(Issue("ERROR", idx, "Ligne parasite composée uniquement de #.", line))

        if "[[TABLE_BLOCK]]" in line:
            issues.append(Issue("ERROR", idx, "Artefact interne [[TABLE_BLOCK]] présent dans le manuscrit.", line))

        # 2. Markdown gras
        # Le générateur nettoie déjà ** via clean_text().
        # On ne le signale pas pour éviter le bruit.

        # 3. Balises inconnues
        # Les checklists Markdown [ ] sont du contenu éditorial normal.
        if stripped.startswith("[") and "]" in stripped:
            if stripped.startswith("[ ]") or stripped.lower().startswith("[x]"):
                pass
            elif not any(stripped.startswith(tag) for tag in KNOWN_TAGS):
                issues.append(Issue("WARN", idx, "Balise inconnue ou non prise en charge.", line))

        # 4. Images manquantes
        if stripped.startswith("[IMAGE:") or stripped.startswith("[OPENING_IMAGE:"):
            image_name = extract_image_name(stripped)
            if not image_name:
                issues.append(Issue("ERROR", idx, "Balise image illisible.", line))
            else:
                image_path = IMAGES_DIR / image_name
                if not image_path.exists():
                    issues.append(Issue("ERROR", idx, f"Image introuvable : {image_path}", line))

        # 5. Tableaux Markdown suspects
        if is_markdown_table_line(line) and not is_table_separator(line):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) >= 5:
                issues.append(Issue("WARN", idx, "Tableau large détecté : risque de mauvais rendu en A5.", line))

        # 6. Titre suspect trop court
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            if len(title) <= 2:
                issues.append(Issue("WARN", idx, "Titre Markdown trop court ou suspect.", line))

    # 7. Chapitre Table des matières revenu par erreur
    chapters = detect_chapters(raw)
    for title in chapters:
        if title.strip().lower() == "table des matières":
            issues.append(Issue("ERROR", 0, "Le manuscrit contient encore un faux chapitre “Table des matières”.", title))

    # 8. Nombre de chapitres
    if chapters:
        if len(chapters) < 10:
            issues.append(Issue("WARN", 0, f"Peu de chapitres détectés : {len(chapters)}.", ""))
        if len(chapters) > 40:
            issues.append(Issue("WARN", 0, f"Trop de chapitres détectés : {len(chapters)}. Risque de faux chapitres.", ""))

    return issues


def print_report(path: Path, issues: List[Issue], raw: str) -> int:
    chapters = detect_chapters(raw)

    print("")
    print("=== Vérification manuscrit — Atelier Zydka ===")
    print(f"Fichier : {path}")
    print(f"Chapitres détectés : {len(chapters)}")

    if chapters:
        print("")
        print("Chapitres :")
        for i, title in enumerate(chapters, start=1):
            print(f"  {i:02d}. {title}")

    print("")
    if not issues:
        print("OK — Aucun problème bloquant détecté.")
        return 0

    errors = [i for i in issues if i.level == "ERROR"]
    warnings = [i for i in issues if i.level == "WARN"]

    print(f"Problèmes détectés : {len(issues)}")
    print(f"Erreurs : {len(errors)}")
    print(f"Avertissements : {len(warnings)}")
    print("")

    for issue in issues:
        location = f"ligne {issue.line}" if issue.line else "global"
        print(f"[{issue.level}] {location} — {issue.message}")
        if issue.content:
            print(f"  > {issue.content[:160]}")
        print("")

    return 1 if errors else 0


def main() -> int:
    manuscript_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_MANUSCRIPT)

    try:
        raw = read_file(manuscript_path)
    except Exception as exc:
        print(f"ERREUR : {exc}")
        return 1

    issues = check_manuscript(raw)
    return print_report(manuscript_path, issues, raw)


if __name__ == "__main__":
    raise SystemExit(main())
