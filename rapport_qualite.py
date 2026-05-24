# -*- coding: utf-8 -*-
"""
Rapport qualité éditorial — Atelier Zydka Manuel

V3.4 :
- analyse le manuscrit actif ;
- détecte les points de vigilance éditoriaux ;
- produit un rapport qualité lisible ;
- calcule un score global de publication.

Entrée :
manuscrit_beatmakers.txt

Sortie :
exports/rapports/rapport_qualite.md
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent

MANUSCRIPT_PATH = ROOT / "manuscrit_beatmakers.txt"
OUTPUT_DIR = ROOT / "exports" / "rapports"
OUTPUT_PATH = OUTPUT_DIR / "rapport_qualite.md"
SCORE_PATH = OUTPUT_DIR / "score_qualite.json"


INTERNAL_NOTE_PATTERNS = [
    r"<!--.*?-->",
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bNOTE INTERNE\b",
    r"\bÀ RELIRE\b",
    r"\bA RELIRE\b",
    r"\bBROUILLON\b",
    r"\bVÉRIFIER\b",
    r"\bVERIFIER\b",
]

STATUS_PATTERNS = [
    r"\[STATUT\s*:\s*([^\]]+)\]",
    r"<!--\s*status\s*:\s*(.*?)\s*-->",
    r"<!--\s*statut\s*:\s*(.*?)\s*-->",
]


@dataclass
class Chapter:
    title: str
    level: int
    start_line: int
    content: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.content).strip()

    @property
    def word_count(self) -> int:
        return count_words(self.text)

    @property
    def char_count(self) -> int:
        return len(self.text)

    @property
    def paragraph_count(self) -> int:
        return count_paragraphs(self.text)

    @property
    def status(self) -> str:
        return extract_status(self.text)


def read_manuscript() -> str:
    if not MANUSCRIPT_PATH.exists():
        raise FileNotFoundError(f"Manuscrit introuvable : {MANUSCRIPT_PATH}")

    return MANUSCRIPT_PATH.read_text(encoding="utf-8")


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def count_words(text: str) -> int:
    words = re.findall(r"\b[\wÀ-ÿ'-]+\b", text, flags=re.UNICODE)
    return len(words)


def count_paragraphs(text: str) -> int:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return len(paragraphs)


def extract_status(text: str) -> str:
    for pattern in STATUS_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return clean_line(match.group(1))

    return "non renseigné"


def detect_internal_notes(text: str) -> list[str]:
    notes: list[str] = []

    for pattern in INTERNAL_NOTE_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)

        for match in matches:
            if isinstance(match, tuple):
                match = " ".join(match)

            note = clean_line(str(match))
            if note:
                notes.append(note[:180])

    return notes


def detect_headings(text: str) -> list[tuple[int, str, int]]:
    headings: list[tuple[int, str, int]] = []

    for index, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        if not stripped.startswith("#"):
            continue

        match = re.match(r"^(#{1,6})\s+(.+)$", stripped)

        if not match:
            continue

        level = len(match.group(1))
        title = clean_line(match.group(2))

        if title:
            headings.append((level, title, index))

    return headings


def split_chapters(text: str) -> list[Chapter]:
    lines = text.splitlines()
    headings = detect_headings(text)

    if not headings:
        return [
            Chapter(
                title="Manuscrit complet",
                level=1,
                start_line=1,
                content=lines,
            )
        ]

    chapters: list[Chapter] = []

    for pos, (level, title, start_line) in enumerate(headings):
        start_index = start_line - 1
        end_index = headings[pos + 1][2] - 1 if pos + 1 < len(headings) else len(lines)

        content = lines[start_index + 1:end_index]

        chapters.append(
            Chapter(
                title=title,
                level=level,
                start_line=start_line,
                content=content,
            )
        )

    return chapters


def classify_density(word_count: int) -> tuple[str, str]:
    if word_count == 0:
        return "⚫", "vide"
    if word_count < 80:
        return "🟡", "très court"
    if word_count <= 900:
        return "🟢", "confortable"
    if word_count <= 1400:
        return "🟡", "dense"
    return "🔴", "trop long"


def title_warning(title: str) -> str:
    length = len(title)

    if length > 90:
        return "🔴 titre très long"
    if length > 65:
        return "🟡 titre long"

    return "🟢 ok"


def calculate_score(
    chapters: list[Chapter],
    internal_notes: list[str],
    long_titles: int,
    empty_chapters: int,
    too_long_chapters: int,
    missing_statuses: int,
) -> int:
    score = 100

    score -= min(25, len(internal_notes) * 5)
    score -= min(15, long_titles * 3)
    score -= min(20, empty_chapters * 8)
    score -= min(25, too_long_chapters * 8)

    if chapters:
        missing_ratio = missing_statuses / len(chapters)
        if missing_ratio > 0.8:
            score -= 8
        elif missing_ratio > 0.5:
            score -= 5
        elif missing_ratio > 0.25:
            score -= 3

    if len(chapters) < 3:
        score -= 8

    return max(0, min(100, score))


def score_label(score: int) -> str:
    if score >= 90:
        return "🟢 prêt à publier"
    if score >= 75:
        return "🟡 publiable avec vigilance"
    if score >= 60:
        return "🟠 corrections recommandées"
    return "🔴 corrections prioritaires"


def build_recommendations(
    internal_notes: list[str],
    long_titles: int,
    empty_chapters: int,
    too_long_chapters: int,
    missing_statuses: int,
) -> list[str]:
    recommendations: list[str] = []

    if internal_notes:
        recommendations.append(
            "Supprimer ou masquer les notes internes avant export public."
        )

    if long_titles:
        recommendations.append(
            "Raccourcir les titres trop longs pour améliorer la lisibilité du PDF."
        )

    if empty_chapters:
        recommendations.append(
            "Compléter ou supprimer les chapitres vides."
        )

    if too_long_chapters:
        recommendations.append(
            "Découper les chapitres trop longs en sections plus respirantes."
        )

    if missing_statuses:
        recommendations.append(
            "Ajouter des statuts éditoriaux aux chapitres importants : brouillon, à relire, validé, exportable."
        )

    if not recommendations:
        recommendations.append(
            "Aucune correction prioritaire détectée. Le manuscrit semble propre pour une génération de test."
        )

    return recommendations


def build_quality_data() -> dict:
    text = read_manuscript()
    chapters = split_chapters(text)

    total_words = count_words(text)
    total_chars = len(text)
    total_paragraphs = count_paragraphs(text)
    internal_notes = detect_internal_notes(text)

    long_titles = 0
    empty_chapters = 0
    too_long_chapters = 0
    missing_statuses = 0

    for chapter in chapters:
        density_icon, density_label = classify_density(chapter.word_count)
        title_status = title_warning(chapter.title)
        status = chapter.status

        if "titre long" in title_status:
            long_titles += 1

        if chapter.word_count == 0:
            empty_chapters += 1

        if density_label == "trop long":
            too_long_chapters += 1

        if status == "non renseigné":
            missing_statuses += 1

    score = calculate_score(
        chapters=chapters,
        internal_notes=internal_notes,
        long_titles=long_titles,
        empty_chapters=empty_chapters,
        too_long_chapters=too_long_chapters,
        missing_statuses=missing_statuses,
    )

    recommendations = build_recommendations(
        internal_notes=internal_notes,
        long_titles=long_titles,
        empty_chapters=empty_chapters,
        too_long_chapters=too_long_chapters,
        missing_statuses=missing_statuses,
    )

    return {
        "score": score,
        "label": score_label(score),
        "chapters_count": len(chapters),
        "total_words": total_words,
        "total_chars": total_chars,
        "total_paragraphs": total_paragraphs,
        "internal_notes_count": len(internal_notes),
        "long_titles_count": long_titles,
        "empty_chapters_count": empty_chapters,
        "too_long_chapters_count": too_long_chapters,
        "missing_statuses_count": missing_statuses,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def generate_report() -> str:
    text = read_manuscript()
    chapters = split_chapters(text)

    total_words = count_words(text)
    total_chars = len(text)
    total_paragraphs = count_paragraphs(text)
    internal_notes = detect_internal_notes(text)

    long_titles = 0
    empty_chapters = 0
    too_long_chapters = 0
    missing_statuses = 0

    chapter_rows: list[str] = []

    for index, chapter in enumerate(chapters, start=1):
        density_icon, density_label = classify_density(chapter.word_count)
        title_status = title_warning(chapter.title)
        status = chapter.status

        if "titre long" in title_status:
            long_titles += 1

        if chapter.word_count == 0:
            empty_chapters += 1

        if density_label == "trop long":
            too_long_chapters += 1

        if status == "non renseigné":
            missing_statuses += 1

        safe_title = chapter.title.replace("|", "\\|")

        chapter_rows.append(
            f"| {index} | {chapter.level} | {safe_title} | {chapter.word_count} | {chapter.paragraph_count} | {density_icon} {density_label} | {title_status} | {status} |"
        )

    score = calculate_score(
        chapters=chapters,
        internal_notes=internal_notes,
        long_titles=long_titles,
        empty_chapters=empty_chapters,
        too_long_chapters=too_long_chapters,
        missing_statuses=missing_statuses,
    )

    recommendations = build_recommendations(
        internal_notes=internal_notes,
        long_titles=long_titles,
        empty_chapters=empty_chapters,
        too_long_chapters=too_long_chapters,
        missing_statuses=missing_statuses,
    )

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    lines: list[str] = []

    lines.append("# Rapport qualité éditorial — Atelier Zydka Manuel")
    lines.append("")
    lines.append(f"Date de génération : {now}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Score global")
    lines.append("")
    lines.append(f"**Score : {score}/100**")
    lines.append("")
    lines.append(f"**Statut : {score_label(score)}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Synthèse")
    lines.append("")
    lines.append(f"- Nombre de chapitres / sections détectés : **{len(chapters)}**")
    lines.append(f"- Nombre total de mots : **{total_words}**")
    lines.append(f"- Nombre total de caractères : **{total_chars}**")
    lines.append(f"- Nombre total de paragraphes : **{total_paragraphs}**")
    lines.append(f"- Notes internes détectées : **{len(internal_notes)}**")
    lines.append(f"- Titres longs : **{long_titles}**")
    lines.append(f"- Sections vides : **{empty_chapters}**")
    lines.append(f"- Sections trop longues : **{too_long_chapters}**")
    lines.append(f"- Statuts non renseignés : **{missing_statuses}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Détail par chapitre / section")
    lines.append("")
    lines.append("| # | Niveau | Titre | Mots | Paragraphes | Densité | Titre | Statut |")
    lines.append("|---|--------|-------|------|-------------|---------|-------|--------|")
    lines.extend(chapter_rows)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Notes internes détectées")
    lines.append("")

    if internal_notes:
        for note in internal_notes[:30]:
            lines.append(f"- `{note}`")

        if len(internal_notes) > 30:
            lines.append(f"- … {len(internal_notes) - 30} notes supplémentaires non affichées.")
    else:
        lines.append("Aucune note interne détectée.")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Recommandations")
    lines.append("")

    for recommendation in recommendations:
        lines.append(f"- {recommendation}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Légende")
    lines.append("")
    lines.append("- 🟢 confortable / prêt")
    lines.append("- 🟡 dense ou à surveiller")
    lines.append("- 🟠 correction recommandée")
    lines.append("- 🔴 problème prioritaire")
    lines.append("- ⚫ section vide ou structurelle")
    lines.append("")
    lines.append("Fin du rapport.")

    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report = generate_report()
    OUTPUT_PATH.write_text(report, encoding="utf-8")

    quality_data = build_quality_data()
    SCORE_PATH.write_text(
        json.dumps(quality_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Rapport qualité généré : {OUTPUT_PATH}")
    print(f"Score qualité généré : {SCORE_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
