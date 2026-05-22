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
        return "Structure saine. Optionnel : ajouter une phrase-pivot pour renforcer la mémorisation."

    return "Structure équilibrée."




def priority_level(score: int) -> str:
    if score < 60:
        return "priorité haute"
    if score < 75:
        return "priorité moyenne"
    if score < 90:
        return "surveillance"
    return "OK"


def global_reading(rows: list[dict]) -> list[str]:
    dense = [row for row in rows if row["density"] in {"dense", "très dense"}]
    low_scores = [row for row in rows if row["score"] < 75]
    table_heavy = [row for row in rows if row["counter"].get("table", 0) >= 3]
    list_heavy = [row for row in rows if row["counter"].get("list_item", 0) > 45]

    lines = []

    if not rows:
        return ["Aucune donnée exploitable."]

    if len(low_scores) <= 3:
        lines.append("La structure générale est saine : peu de chapitres nécessitent une reprise lourde.")
    else:
        lines.append("Plusieurs chapitres demandent une reprise éditoriale : le manuscrit est solide, mais encore dense.")

    if dense:
        titles = ", ".join(row["chapter"].title for row in dense[:3])
        lines.append(f"Les zones les plus denses sont : {titles}.")

    if table_heavy:
        lines.append("Les tableaux sont concentrés sur quelques sections : vérifier leur lisibilité en A5.")

    if list_heavy:
        lines.append("Plusieurs chapitres utilisent fortement les listes : utile pédagogiquement, mais à équilibrer avec plus de respiration narrative.")

    if not dense and not table_heavy and not list_heavy:
        lines.append("La densité éditoriale est bien répartie.")

    return lines


def action_plan(rows: list[dict]) -> list[str]:
    priorities = sorted(rows, key=lambda row: row["score"])
    actions = []

    for row in priorities:
        title = row["chapter"].title
        score = row["score"]
        density = row["density"]
        counter = row["counter"]

        if density == "séparateur":
            continue

        if score < 60:
            actions.append(
                f"Alléger **{title}** : réduire la densité, simplifier les tableaux et créer plus de respirations."
            )
        elif score < 75:
            if counter.get("list_item", 0) > 45:
                actions.append(
                    f"Reprendre **{title}** : regrouper certaines listes et transformer les passages répétitifs en paragraphes courts."
                )
            elif counter.get("table", 0) >= 3:
                actions.append(
                    f"Reprendre **{title}** : déplacer ou simplifier certains tableaux pour le format A5."
                )
            else:
                actions.append(
                    f"Revoir **{title}** : équilibrer la densité avec des intertitres, citations ou encadrés."
                )

        if len(actions) >= 5:
            break

    if not actions:
        actions.append("Aucune reprise prioritaire : le manuscrit peut passer en phase de finition visuelle.")

    return actions

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
                "priority": priority_level(score),
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

    lines.append("## Lecture stratégique")
    lines.append("")

    for item in global_reading(rows):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Plan d’action recommandé")
    lines.append("")

    for idx, action in enumerate(action_plan(rows), start=1):
        lines.append(f"{idx}. {action}")

    lines.append("")
    lines.append("## Seuils d’interprétation")
    lines.append("")
    lines.append("- **90 à 100** : section saine, prête pour finition.")
    lines.append("- **75 à 89** : section correcte, à surveiller.")
    lines.append("- **60 à 74** : reprise utile avant version finale.")
    lines.append("- **0 à 59** : priorité éditoriale forte.")
    lines.append("")

    lines.append("## Diagnostic éditorial")
    lines.append("")
    lines.append("| # | Chapitre | Densité | Score | Priorité | Recommandation |")
    lines.append("|---:|---|---|---:|---|---|")

    for row in rows:
        title = row["chapter"].title.replace("|", "\\|")
        reco = row["recommendation"].replace("|", "\\|")
        lines.append(
            f"| {row['idx']} | {title} | {row['density']} | {row['score']} | {row['priority']} | {reco} |"
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
