# -*- coding: utf-8 -*-
"""
PARSER MANUSCRIT — ATELIER ZYDKA MANUEL
======================================

Objectif :
Transformer un manuscrit Markdown / texte enrichi en structure propre :
- chapitres réels ;
- sections ;
- paragraphes ;
- listes ;
- tableaux Markdown ;
- images ;
- citations ;
- callouts.

Ce parser remplace la logique trop rigide intégrée dans generer_livre_manuel_presence.py.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Literal, Optional


BlockType = Literal[
    "paragraph",
    "heading",
    "list_item",
    "table",
    "image",
    "quote",
    "callout",
    "pagebreak",
]


@dataclass
class Block:
    type: BlockType
    text: str = ""
    level: int = 0
    meta: dict = field(default_factory=dict)


@dataclass
class Chapter:
    title: str
    blocks: List[Block] = field(default_factory=list)
    number: Optional[str] = None
    kind: str = "chapter"


# ============================================================
# NETTOYAGE
# ============================================================

def clean_line(line: str) -> str:
    """Nettoyage léger sans détruire le Markdown utile."""
    return (
        line.replace("\u00a0", " ")
        .replace("“", '"')
        .replace("”", '"')
        .replace("…", "...")
        .rstrip()
    )


def clean_markdown_noise(text: str) -> str:
    """Nettoie les artefacts fréquents sans casser les balises utiles."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Supprime les lignes horizontales isolées.
    text = re.sub(r"(?m)^\s*[-*_]{3,}\s*$", "", text)

    # Normalise les grands espacements.
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    return text.strip()


def filter_manuscript_content(text: str) -> str:
    """
    Filtre éditorial avant parsing.

    Objectif :
    - supprimer les consignes techniques du fichier maître ;
    - démarrer directement au vrai contenu éditorial ;
    - exclure le toolkit complet et les instructions de production finales.
    """
    raw = text.replace("\r\n", "\n").replace("\r", "\n")

    # Démarrage propre : on saute l'en-tête technique et on commence
    # au premier vrai contenu publiable du livre.
    start_markers = [
        "# Avertissement légal",
        "## Avertissement légal",
        "Avertissement légal",
        "# AVERTISSEMENT LÉGAL",
        "## AVERTISSEMENT LÉGAL",
        "AVERTISSEMENT LÉGAL",
    ]

    upper_raw = raw.upper()
    start_positions = []

    for marker in start_markers:
        pos = upper_raw.find(marker.upper())
        if pos != -1:
            start_positions.append(pos)

    if start_positions:
        raw = raw[min(start_positions):]

    # Coupure avant le toolkit complet ou les instructions finales.
    end_markers = [
        "TOOLKIT BONUS — CONTENU COMPLET DES FICHIERS À CRÉER",
        "TOOLKIT BONUS - CONTENU COMPLET DES FICHIERS À CRÉER",
        "INSTRUCTIONS DE PRODUCTION FINALES",
    ]

    upper = raw.upper()
    end_positions = []

    for marker in end_markers:
        pos = upper.find(marker.upper())
        if pos != -1:
            end_positions.append(pos)

    if end_positions:
        raw = raw[:min(end_positions)]

    return raw.strip()

def is_pagebreak(line: str) -> bool:
    """
    Détecte les sauts de page explicites du manuscrit.
    """
    stripped = line.strip().upper()
    return stripped in {
        "[PAGE_BREAK]",
        "[PAGEBREAK]",
        "<PAGE_BREAK>",
        "---PAGEBREAK---",
        "PAGE_BREAK",
    }


def parse_manuscript(raw: str) -> List[Chapter]:
    raw = filter_manuscript_content(raw)
    raw = clean_markdown_noise(raw)
    lines = [clean_line(line) for line in raw.split("\n")]

    chapters: List[Chapter] = []
    current = Chapter(title="Introduction", kind="introduction")
    paragraph_buffer: List[str] = []
    table_buffer: List[str] = []

    def flush_paragraph():
        nonlocal paragraph_buffer
        if paragraph_buffer:
            text = " ".join(x.strip() for x in paragraph_buffer if x.strip()).strip()
            if text:
                current.blocks.append(Block(type="paragraph", text=text))
            paragraph_buffer = []

    def flush_table():
        nonlocal table_buffer
        if table_buffer:
            cleaned = [
                line for line in table_buffer
                if line.strip() and not is_table_separator(line)
            ]
            if cleaned:
                current.blocks.append(Block(type="table", text="\n".join(cleaned)))
            table_buffer = []

    def start_new_chapter(title: str, number: Optional[str] = None, kind: str = "chapter"):
        nonlocal current
        flush_paragraph()
        flush_table()

        if current.title or current.blocks:
            chapters.append(current)

        current = Chapter(title=title.strip(), number=number, kind=kind)

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_table()
            continue

        if is_pagebreak(stripped):
            flush_paragraph()
            flush_table()
            current.blocks.append(Block(type="pagebreak"))
            continue

        if is_table_line(stripped):
            flush_paragraph()
            table_buffer.append(stripped)
            continue
        else:
            flush_table()

        image = parse_image(stripped)
        if image:
            flush_paragraph()
            filename, caption = image
            current.blocks.append(
                Block(
                    type="image",
                    text=filename,
                    meta={"caption": caption},
                )
            )
            continue

        callout = parse_callout(stripped)
        if callout:
            flush_paragraph()
            title, body = callout
            current.blocks.append(
                Block(
                    type="callout",
                    text=body,
                    meta={"title": title},
                )
            )
            continue

        quote = parse_quote(stripped)
        if quote:
            flush_paragraph()
            current.blocks.append(Block(type="quote", text=quote))
            continue

        list_item = parse_list_item(stripped)
        if list_item:
            flush_paragraph()
            current.blocks.append(Block(type="list_item", text=list_item))
            continue

        md_heading = parse_markdown_heading(stripped)
        if md_heading:
            flush_paragraph()
            level, title = md_heading

            # # Titre = chapitre réel.
            # ## et plus = intertitre interne.
            if level == 1:
                start_new_chapter(title=title, kind="chapter")
            else:
                current.blocks.append(
                    Block(type="heading", text=title, level=level)
                )
            continue

        chapter_title = parse_chapter_title(stripped)
        if chapter_title:
            start_new_chapter(
                title=chapter_title["title"],
                number=chapter_title["number"],
                kind=chapter_title["kind"],
            )
            continue

        numbered_title = parse_numbered_title(stripped)
        if numbered_title:
            flush_paragraph()

            level = numbered_title["level"]
            number = numbered_title["number"]
            title = numbered_title["title"]
            as_chapter = numbered_title["as_chapter"]

            if as_chapter:
                start_new_chapter(
                    title=f"{number}. {title}",
                    number=number,
                    kind="chapter",
                )
            else:
                current.blocks.append(
                    Block(
                        type="heading",
                        text=f"{number} {title}",
                        level=min(level + 1, 6),
                        meta={"number": number},
                    )
                )
            continue

        paragraph_buffer.append(stripped)

    flush_paragraph()
    flush_table()

    if current.title or current.blocks:
        chapters.append(current)

    # Supprime une introduction vide générée automatiquement si le manuscrit commence par un vrai titre.
    chapters = [
        ch for ch in chapters
        if ch.title.strip() or ch.blocks
    ]

    if chapters and chapters[0].title == "Introduction" and not chapters[0].blocks and len(chapters) > 1:
        chapters = chapters[1:]

    return chapters


def blocks_to_legacy_paragraphs(chapter: Chapter) -> List[str]:
    """
    Compatibilité avec le générateur actuel.

    Transforme les blocs structurés en anciens marqueurs :
    - heading -> ## titre
    - table -> [[TABLE_BLOCK]]
    - image -> [IMAGE: fichier | légende]
    - quote -> [QUOTE: texte]
    - callout -> [CALLOUT: titre | texte]
    """
    paragraphs: List[str] = []

    for block in chapter.blocks:
        if block.type == "paragraph":
            paragraphs.append(block.text)

        elif block.type == "heading":
            paragraphs.append("## " + block.text)

        elif block.type == "list_item":
            paragraphs.append("• " + block.text)

        elif block.type == "table":
            paragraphs.append("[[TABLE_BLOCK]]\n" + block.text)

        elif block.type == "image":
            caption = block.meta.get("caption", "")
            if caption:
                paragraphs.append(f"[IMAGE: {block.text} | {caption}]")
            else:
                paragraphs.append(f"[IMAGE: {block.text}]")

        elif block.type == "quote":
            paragraphs.append(f"[QUOTE: {block.text}]")

        elif block.type == "callout":
            title = block.meta.get("title", "À retenir")
            paragraphs.append(f"[CALLOUT: {title} | {block.text}]")

        elif block.type == "pagebreak":
            paragraphs.append("[PAGEBREAK]")

    return paragraphs