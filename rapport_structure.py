# -*- coding: utf-8 -*-
"""
RAPPORT STRUCTURE — ATELIER ZYDKA MANUEL
=======================================

Génère un rapport technique + éditorial du manuscrit :
- structure globale ;
- densité par chapitre ;
- alertes éditoriales ;
- recommandations concrètes.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path


from parser_manuscrit import parse_manuscript


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "manuscrit_beatmakers.txt"
OUTPUT_DIR = ROOT / "exports" / "rapports"
OUTPUT = OUTPUT_DIR / "rapport_structure.md"


def clean_excerpt(text: str, limit: int = 90) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[:limit] + "…"


def is_separator_chapter(title: str, block_count: int) -> bool:
    normalized = title.strip().lower()
    return block_count == 0 and normalized in {"annexes", "annexe", "appendices"}


def classify_density(block_count: int, title: str = "") -> str:
    if is_separator_chapter(title, block_count):
        return "séparateur"
    if block_count == 0:
        return "vide"
    if block_count < 20:
        return "court"
    if block_count <= 65:
        return "équilibré"
    if block_count <= 95:
        return "dense"
    return "très dense"


def editorial_score(counter: Counter, block_count: int, title: str = "") -> int:
    """
    Score simple sur 100.
    Ce n'est pas une note littéraire : c'est un indicateur de confort éditorial.
    """
    if is_separator_chapter(title, block_count):
        return 100

    if block_count == 0:
        return 0

    score = 100

    if block_count > 95:
        score -= 18
    elif block_count > 65:
        score -= 8

    if counter.get("heading", 0) == 0 and block_count > 25:
        score -= 12

    if counter.get("list_item", 0) > 45:
        score -= 10

    if counter.get("table", 0) >= 3:
        score -= 12

    if counter.get("quote", 0) == 0 and block_count > 45:
        score -= 5

    if counter.get("callout", 0) == 0 and block_count > 45:
        score -= 5

    return max(0, min(100, score))


def recommendation_for(counter: Counter, block_count: int, title: str) -> str:
    if is_separator_chapter(title, block_count):
        return "Page séparatrice détectée : aucun problème éditorial."

    if block_count == 0:
        return "Décider si cette entrée est une vraie section ou une simple page séparatrice."

    if counter.get("table", 0) >= 3:
        return "Vérifier les tableaux : certains pourraient être déplacés en annexe ou simplifiés."

    if counter.get("list_item", 0) > 45:
        return "Réduire ou regrouper certaines listes pour éviter un effet checklist trop massif."

    if block_count > 95:
        return "Ajouter des respirations : intertitres, citations, encadrés ou coupures de chapitre."

    if block_count > 65:
        return "Surveiller la densité : le chapitre est riche mais peut fatiguer en A5."

    if block_count < 20 and "annexe" not in title.lower():
        return "Chapitre court : vérifier qu'il apporte assez de valeur autonome."

    if counter.get("quote", 0) == 0 and block_count > 45:
        return "Ajouter une citation ou phrase-pivot pour renforcer la mémorisation."

    return "Structure équilibrée."


def main() -> int:
    if not INPUT.exists():
        print(f"ERREUR : fichier introuvable : {INPUT}")
        return 1

    raw = INPUT.read_text(encoding="utf-8")
    chapters = parse_manuscript(raw)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    global_counter = Counter()
    alerts = []
    rows = []

    for idx, chapter in enumerate(chapters, start=1):
        counter = Counter(block.type for block in chapter.blocks)
        global_counter.update(counter)

        block_count = len(chapter.blocks)
        density = classify_density(block_count, chapter.title)
        score = editorial_score(counter, block_count, chapter.title)
        recommendation = recommendation_for(counter, block_count, chapter.title)

        rows.append(
            {
                "idx": idx,
                "chapter": chapter,
                "counter": counter,
                "blocks": block_count,
                "density": density,
                "score": score,
                "recommendation": recommendation,
            }
        )

        if not chapter.blocks and not is_separator_chapter(chapter.title, block_count):
            alerts.append(f"- Chapitre vide : `{chapter.title}`")

        if len(chapter.title) > 95:
            alerts.append(f"- Titre très long : `{chapter.title}`")

        if counter.get("table", 0) >= 3:
            alerts.append(f"- Beaucoup de tableaux dans : `{chapter.title}`")

        if counter.get("list_item", 0) > 45:
            alerts.append(f"- Beaucoup de listes dans : `{chapter.title}`")

        if block_count > 95:
            alerts.append(f"- Chapitre très dense : `{chapter.title}`")

    total_blocks = sum(global_counter.values())
    average_score = round(sum(row["score"] for row in rows) / len(rows), 1) if rows else 0

    lines = []
    lines.append("# Rapport de structure — Atelier Zydka Manuel")
    lines.append("")
    lines.append("## Synthèse")
    lines.append("")
    lines.append(f"- Chapitres détectés : **{len(chapters)}**")
    lines.append(f"- Blocs détectés : **{total_blocks}**")
    lines.append(f"- Paragraphes : **{global_counter.get('paragraph', 0)}**")
    lines.append(f"- Titres internes : **{global_counter.get('heading', 0)}**")
    lines.append(f"- Listes : **{global_counter.get('list_item', 0)}**")
    lines.append(f"- Tableaux : **{global_counter.get('table', 0)}**")
    lines.append(f"- Images : **{global_counter.get('image', 0)}**")
    lines.append(f"- Citations : **{global_counter.get('quote', 0)}**")
    lines.append(f"- Encadrés : **{global_counter.get('callout', 0)}**")
    lines.append(f"- Sauts de page : **{global_counter.get('pagebreak', 0)}**")
    lines.append(f"- Score éditorial moyen : **{average_score}/100**")
    lines.append("")

    lines.append("## Diagnostic éditorial")
    lines.append("")
    lines.append("| # | Chapitre | Densité | Score | Recommandation |")
    lines.append("|---:|---|---|---:|---|")

    for row in rows:
        title = row["chapter"].title.replace("|", "\\|")
        reco = row["recommendation"].replace("|", "\\|")
        lines.append(
            f"| {row['idx']} | {title} | {row['density']} | {row['score']} | {reco} |"
        )

    lines.append("")
    lines.append("## Structure par chapitre")
    lines.append("")
    lines.append("| # | Chapitre | Type | Blocs | Paragraphes | Titres | Listes | Tableaux | Images | Citations | Encadrés |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for row in rows:
        chapter = row["chapter"]
        counter = row["counter"]
        title = chapter.title.replace("|", "\\|")
        lines.append(
            f"| {row['idx']} | {title} | {chapter.kind} | "
            f"{row['blocks']} | "
            f"{counter.get('paragraph', 0)} | "
            f"{counter.get('heading', 0)} | "
            f"{counter.get('list_item', 0)} | "
            f"{counter.get('table', 0)} | "
            f"{counter.get('image', 0)} | "
            f"{counter.get('quote', 0)} | "
            f"{counter.get('callout', 0)} |"
        )

    lines.append("")
    lines.append("## Alertes éditoriales")
    lines.append("")

    if alerts:
        lines.extend(alerts)
    else:
        lines.append("Aucune alerte structurelle majeure détectée.")

    lines.append("")
    lines.append("## Priorités de correction")
    lines.append("")

    priority_rows = sorted(rows, key=lambda row: row["score"])[:5]

    for row in priority_rows:
        lines.append(
            f"- **{row['chapter'].title}** — score {row['score']}/100 : {row['recommendation']}"
        )

    lines.append("")
    lines.append("## Détail des blocs")
    lines.append("")

    for row in rows:
        chapter = row["chapter"]
        lines.append(f"### {row['idx']:02d}. {chapter.title}")
        lines.append("")

        for block in chapter.blocks[:60]:
            level = f" niveau {block.level}" if block.level else ""
            excerpt = clean_excerpt(block.text)
            lines.append(f"- `{block.type}`{level} — {excerpt}")

        if len(chapter.blocks) > 60:
            lines.append(f"- … {len(chapter.blocks) - 60} blocs supplémentaires non affichés.")

        lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Rapport généré : {OUTPUT}")
    print(f"Chapitres détectés : {len(chapters)}")
    print(f"Blocs détectés : {total_blocks}")
    print(f"Score éditorial moyen : {average_score}/100")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
