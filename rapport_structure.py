# -*- coding: utf-8 -*-
"""
RAPPORT STRUCTURE — ATELIER ZYDKA MANUEL
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

        rows.append((idx, chapter, counter))

        if not chapter.blocks:
            alerts.append(f"- Chapitre vide : `{chapter.title}`")

        if len(chapter.title) > 95:
            alerts.append(f"- Titre très long : `{chapter.title}`")

        if counter.get("table", 0) >= 3:
            alerts.append(f"- Beaucoup de tableaux dans : `{chapter.title}`")

        if counter.get("paragraph", 0) > 80:
            alerts.append(f"- Chapitre très dense : `{chapter.title}`")

    lines = []
    lines.append("# Rapport de structure — Atelier Zydka Manuel")
    lines.append("")
    lines.append("## Synthèse")
    lines.append("")
    lines.append(f"- Chapitres détectés : **{len(chapters)}**")
    lines.append(f"- Blocs détectés : **{sum(global_counter.values())}**")
    lines.append(f"- Paragraphes : **{global_counter.get('paragraph', 0)}**")
    lines.append(f"- Titres internes : **{global_counter.get('heading', 0)}**")
    lines.append(f"- Listes : **{global_counter.get('list_item', 0)}**")
    lines.append(f"- Tableaux : **{global_counter.get('table', 0)}**")
    lines.append(f"- Images : **{global_counter.get('image', 0)}**")
    lines.append(f"- Citations : **{global_counter.get('quote', 0)}**")
    lines.append(f"- Encadrés : **{global_counter.get('callout', 0)}**")
    lines.append(f"- Sauts de page : **{global_counter.get('pagebreak', 0)}**")
    lines.append("")

    lines.append("## Structure par chapitre")
    lines.append("")
    lines.append("| # | Chapitre | Type | Blocs | Paragraphes | Titres | Listes | Tableaux | Images | Citations | Encadrés |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for idx, chapter, counter in rows:
        title = chapter.title.replace("|", "\\|")
        lines.append(
            f"| {idx} | {title} | {chapter.kind} | "
            f"{len(chapter.blocks)} | "
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
    lines.append("## Détail des blocs")
    lines.append("")

    for idx, chapter, counter in rows:
        lines.append(f"### {idx:02d}. {chapter.title}")
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
    print(f"Blocs détectés : {sum(global_counter.values())}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
