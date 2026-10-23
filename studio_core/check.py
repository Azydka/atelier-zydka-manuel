# -*- coding: utf-8 -*-
"""
Vérificateur de manuscrit — Manuscript Studio by Atelier Zydka

Objectif :
Détecter les erreurs éditoriales courantes avant génération PDF.

Points d'entrée : check_manuscript(texte, dossier_images) et format_report(...).
(ou : python make.py check)
"""

from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List

from .parser import parse_manuscript

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
    return [chapter.title for chapter in parse_manuscript(raw)]


def check_manuscript(raw: str, images_dir: Path) -> List[Issue]:
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
                image_path = Path(images_dir) / image_name
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


def has_errors(issues: List[Issue]) -> bool:
    return any(issue.level == "ERROR" for issue in issues)


def format_report(path: Path, issues: List[Issue], raw: str) -> str:
    """Rapport de vérification lisible (texte brut)."""
    chapters = detect_chapters(raw)
    lines: List[str] = [
        "",
        "=== Vérification manuscrit — Atelier Zydka ===",
        f"Fichier : {path}",
        f"Chapitres détectés : {len(chapters)}",
    ]

    if chapters:
        lines += ["", "Chapitres :"]
        lines += [f"  {i:02d}. {title}" for i, title in enumerate(chapters, start=1)]

    lines.append("")
    if not issues:
        lines.append("OK — Aucun problème bloquant détecté.")
        return "\n".join(lines)

    errors = [i for i in issues if i.level == "ERROR"]
    warnings = [i for i in issues if i.level == "WARN"]

    lines += [
        f"Problèmes détectés : {len(issues)}",
        f"Erreurs : {len(errors)}",
        f"Avertissements : {len(warnings)}",
        "",
    ]

    for issue in issues:
        location = f"ligne {issue.line}" if issue.line else "global"
        lines.append(f"[{issue.level}] {location} — {issue.message}")
        if issue.content:
            lines.append(f"  > {issue.content[:160]}")
        lines.append("")

    return "\n".join(lines)
