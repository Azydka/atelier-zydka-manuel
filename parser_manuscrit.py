# -*- coding: utf-8 -*-
"""
PARSER MANUSCRIT — MANUSCRIPT STUDIO BY ATELIER ZYDKA
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
    - démarrer directement au vrai contenu publiable ;
    - exclure le toolkit complet et les instructions de production finales.
    """
    raw = text.replace("\r\n", "\n").replace("\r", "\n")

    # Démarrage propre : on ignore l'en-tête technique du fichier source.
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

    # Coupure avant les blocs non publiables de fin.
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


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def is_table_separator(line: str) -> bool:
    if not is_table_line(line):
        return False
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    cells = [c for c in cells if c]
    return bool(cells) and all(re.match(r"^:?-{3,}:?$", c) for c in cells)


def parse_markdown_heading(line: str):
    """
    Détecte :
    # Titre
    ## Titre
    ### Titre
    """
    match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
    if not match:
        return None

    level = len(match.group(1))
    title = match.group(2).strip()
    return level, title


def parse_numbered_title(line: str):
    """
    Détecte les titres numérotés sans transformer les listes courtes
    ou les étapes d'exercice en faux chapitres.

    Exemples acceptés :
    - 1. Introduction
    - 1. Les bases du beatmaking
    - 1.1 Sous-section
    - 2.3.1 Détail

    Exemples rejetés comme chapitres :
    - 1. ---
    - 1. Hook.
    - 2. Erreur 1 : pas de structure.
    - 1. Ordinateur principal ;
    """
    stripped = line.strip()

    match = re.match(r"^(\d+(?:\.\d+)*)(?:\.|\s)?\s+(.+)$", stripped)
    if not match:
        return None

    number = match.group(1)
    title = match.group(2).strip()
    level = number.count(".") + 1

    # Nettoyage Markdown léger pour l'analyse.
    clean_title = re.sub(r"[*_`]", "", title).strip()
    clean_title = clean_title.strip("-–—:;,. ")

    if not clean_title:
        return None

    # Rejette les placeholders ou séparateurs.
    if clean_title in {"---", "--", "…", "..."}:
        return None

    # Rejette les micro-étapes trop courtes au niveau chapitre.
    # Exemple : 1. Hook. / 2. Cloud sécurisé.
    words = clean_title.split()
    if level == 1 and len(words) <= 3:
        return {
            "level": level,
            "number": number,
            "title": title,
            "as_chapter": False,
        }

    # Rejette les titres qui ressemblent à des items de liste terminés par ;
    if level == 1 and title.rstrip().endswith(";"):
        return {
            "level": level,
            "number": number,
            "title": title,
            "as_chapter": False,
        }

    # Les sous-sections 1.1, 2.3, etc. sont toujours des intertitres.
    if level > 1:
        return {
            "level": level,
            "number": number,
            "title": title,
            "as_chapter": False,
        }

    # Niveau 1 : vrai chapitre seulement si le titre ressemble vraiment
    # à un chapitre structurant, pas à une étape ou une réponse d'exercice.
    chapter_keywords = (
        "partie",
        "chapitre",
        "introduction",
        "conclusion",
        "annexe",
        "livre",
        "avertissement",
        "table des matières",
    )

    normalized = clean_title.lower()

    if not normalized.startswith(chapter_keywords):
        return {
            "level": level,
            "number": number,
            "title": title,
            "as_chapter": False,
        }

    return {
        "level": level,
        "number": number,
        "title": title,
        "as_chapter": True,
    }


def parse_chapter_title(line: str):
    """
    Détecte :
    Chapitre 1 : Titre
    CHAPITRE 1 - Titre
    Partie 1 : Titre
    ANNEXE 1
    Conclusion
    Introduction
    Ressources
    Finalisation
    """
    stripped = line.strip()

    patterns = [
        r"^(chapitre)\s+([0-9IVXLCDM]+)\s*[:\-–—]?\s*(.*)$",
        r"^(partie)\s+([0-9IVXLCDM]+)\s*[:\-–—]?\s*(.*)$",
        r"^(annexe)\s+([0-9A-ZIVXLCDM]+)\s*[:\-–—]?\s*(.*)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, stripped, flags=re.IGNORECASE)
        if match:
            kind = match.group(1).lower()
            number = match.group(2)
            title_rest = match.group(3).strip()
            title = stripped if not title_rest else f"{match.group(1).capitalize()} {number} : {title_rest}"
            return {
                "title": title,
                "number": number,
                "kind": kind,
            }

    simple_titles = {
        "introduction": "Introduction",
        "conclusion": "Conclusion",
        "ressources": "Ressources",
        "bibliographie": "Bibliographie",
        "glossaire": "Glossaire",
        "finalisation": "Finalisation",
        "annexes": "Annexes",
    }

    key = stripped.lower()
    if key in simple_titles:
        return {
            "title": simple_titles[key],
            "number": None,
            "kind": key,
        }

    return None


def parse_image(line: str):
    """
    [IMAGE: fichier.png | Légende]
    """
    match = re.match(r"^\[IMAGE:\s*(.+?)\s*\]$", line.strip(), flags=re.IGNORECASE)
    if not match:
        return None

    content = match.group(1).strip()
    if "|" in content:
        filename, caption = content.split("|", 1)
        return filename.strip(), caption.strip()

    return content.strip(), ""


def parse_callout(line: str):
    """
    [CALLOUT: Titre | Texte]
    """
    match = re.match(r"^\[CALLOUT:\s*(.+?)\s*\]$", line.strip(), flags=re.IGNORECASE)
    if not match:
        return None

    content = match.group(1).strip()
    if "|" in content:
        title, body = content.split("|", 1)
        return title.strip(), body.strip()

    return "À retenir", content


def parse_quote(line: str):
    """
    [QUOTE: Texte]
    > Citation Markdown
    """
    match = re.match(r"^\[QUOTE:\s*(.+?)\s*\]$", line.strip(), flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()

    if line.strip().startswith(">"):
        return line.strip().lstrip(">").strip()

    return None


def parse_list_item(line: str):
    """
    - Item
    * Item
    • Item
    """
    match = re.match(r"^\s*[-*•]\s+(.+)$", line)
    if not match:
        return None

    return match.group(1).strip()


def is_pagebreak(line: str) -> bool:
    return line.strip().upper() in {
        "[PAGEBREAK]",
        "[PAGE BREAK]",
        "---PAGE---",
        "<PAGEBREAK>",
    }


# ============================================================
# PARSER PRINCIPAL
# ============================================================

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