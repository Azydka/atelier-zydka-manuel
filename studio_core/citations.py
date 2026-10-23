# -*- coding: utf-8 -*-
"""
Citations marketing — Manuscript Studio by Atelier Zydka

Sources, par ordre de priorité :
1. citations.txt du projet (une citation par ligne, # = commentaire) ;
2. sinon (fichier absent ou sans citation) le manuscrit : blocs [QUOTE: …],
   blocs [CALLOUT: …] titrés « À retenir » et lignes « À retenir : … ».

Le résultat est écrit en Markdown (une citation par bloc « > »), lu ensuite
par le générateur de visuels.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .parser import parse_manuscript
from .text import squash_spaces

KEY_TAKEAWAY_TITLE = "à retenir"
KEY_TAKEAWAY = re.compile(r"^À retenir\s*:\s*(.+)$", re.IGNORECASE)


def citations_from_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [squash_spaces(line) for line in lines if line.strip() and not line.lstrip().startswith("#")]


def citations_from_manuscript(manuscript_text: str) -> list[str]:
    citations: list[str] = []

    for chapter in parse_manuscript(manuscript_text):
        for block in chapter.blocks:
            if block.type == "quote":
                citations.append(squash_spaces(block.text))
            elif block.type == "callout" and block.meta.get("title", "").strip().lower() == KEY_TAKEAWAY_TITLE:
                citations.append(squash_spaces(block.text))
            elif block.type == "paragraph":
                match = KEY_TAKEAWAY.match(block.text.strip())
                if match:
                    citations.append(squash_spaces(match.group(1)))

    return citations


def collect_citations(manuscript_text: str, citations_source: Optional[Path] = None) -> tuple[list[str], str]:
    """Renvoie (citations sans doublon, description de la source)."""
    citations: list[str] = []
    if citations_source is not None and citations_source.exists():
        citations, source = citations_from_file(citations_source), citations_source.name
    if not citations:
        citations, source = citations_from_manuscript(manuscript_text), "le manuscrit"

    return list(dict.fromkeys(c for c in citations if c)), source


def build_citations(manuscript_text: str, output_file: Path, citations_source: Optional[Path] = None) -> Path:
    """Écrit le fichier Markdown des citations marketing et renvoie son chemin."""
    citations, source = collect_citations(manuscript_text, citations_source)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Citations extraites — Manuscript Studio by Atelier Zydka",
        "",
        f"Fichier généré automatiquement depuis {source}.",
        "",
        f"Nombre de citations : {len(citations)}",
        "",
        "---",
        "",
    ]

    for index, citation in enumerate(citations, start=1):
        lines.append(f"## Citation {index:02d}")
        lines.append("")
        lines.append(f"> {citation}")
        lines.append("")

    output_file.write_text("\n".join(lines), encoding="utf-8")

    return output_file
