# -*- coding: utf-8 -*-
"""
GÉNÉRATEUR PDF — LE MANUEL DE PRÉSENCE / ATELIER ZYDKA
=======================================================

Objectif
--------
Générer un PDF A5 portrait directement exploitable :
- mise en page vectorielle ReportLab ;
- charte Atelier Zydka respectée ;
- gabarits appliqués automatiquement ;
- contenu long importé depuis un fichier texte.

Installation
------------
pip install reportlab

Utilisation recommandée
-----------------------
1. Place ce script dans un dossier.
2. Crée un fichier texte : manuscrit_beatmakers.txt
3. Colle dedans le texte complet du livre.
4. Lance :

python generer_livre_manuel_presence.py

Sortie
------
manuelsortie/manuel-de-presence-atelier-zydka.pdf

Polices
-------
Place les fichiers suivants dans ./fonts si tu les as :
- Inter-Regular.ttf
- Inter-Bold.ttf
- Inter-Black.ttf
- IBMPlexMono-Regular.ttf
- SourceSerif4-Italic.ttf

Fallback automatique si les fontes ne sont pas présentes :
- Inter -> Helvetica
- Inter Bold / Black -> Helvetica-Bold
- IBM Plex Mono -> Courier
- Source Serif 4 Italic -> Times-Italic

Attention
---------
Canva peut importer le PDF, mais selon sa conversion il peut aplatir certains objets.
Pour un fichier Canva 100 % éditable, exporter aussi une version PPTX. Pour un PDF imprimable,
ce script est la source propre.
"""

from __future__ import annotations

import os
import re
import textwrap
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

from reportlab.lib import colors
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


# ============================================================
# PARAMÈTRES FICHIERS
# ============================================================

INPUT_MANUSCRIPT = "manuscrit_beatmakers.txt"
OUTPUT_DIR = "manuelsortie"
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "manuel-de-presence-atelier-zydka.pdf")
IMAGES_DIR = "images"


# ============================================================
# FORMAT ET CHARTE
# ============================================================

PAGE_W = 148 * mm
PAGE_H = 210 * mm
PAGE_SIZE = (PAGE_W, PAGE_H)

M_LEFT = 22 * mm
M_RIGHT = 16 * mm
M_TOP = 18 * mm
M_BOTTOM = 16 * mm

MAIN_COL = 88 * mm
NOTE_COL = 34 * mm
COL_GAP = 10 * mm
NOTE_X = M_LEFT + MAIN_COL + COL_GAP

CONTENT_TOP = 18 * mm
CONTENT_BOTTOM = 194 * mm

CARBON = HexColor("#0B0B0A")
PAPER = HexColor("#F6F6F4")
GRAPHITE = HexColor("#3A3A38")
STEEL = HexColor("#2A353F")
SIGNATURE = HexColor("#D8C9AE")
SOFT = HexColor("#8A8A88")
LINE = HexColor("#B9B9B5")
TABLE_ALT = HexColor("#EFEFEB")


# ============================================================
# POLICES
# ============================================================

@dataclass
class FontSet:
    inter: str
    inter_bold: str
    inter_black: str
    mono: str
    serif_italic: str
    using_fallbacks: bool


def register_font(name: str, path: str) -> bool:
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont(name, path))
        return True
    return False


def setup_fonts() -> FontSet:
    font_dir = "fonts"
    ok = {
        "inter": register_font("Inter", os.path.join(font_dir, "Inter-Regular.ttf")),
        "inter_bold": register_font("Inter-Bold", os.path.join(font_dir, "Inter-Bold.ttf")),
        "inter_black": register_font("Inter-Black", os.path.join(font_dir, "Inter-Black.ttf")),
        "mono": register_font("IBM-Plex-Mono", os.path.join(font_dir, "IBMPlexMono-Regular.ttf")),
        "serif": register_font("SourceSerif4-Italic", os.path.join(font_dir, "SourceSerif4-Italic.ttf")),
    }
    return FontSet(
        inter="Inter" if ok["inter"] else "Helvetica",
        inter_bold="Inter-Bold" if ok["inter_bold"] else "Helvetica-Bold",
        inter_black="Inter-Black" if ok["inter_black"] else "Helvetica-Bold",
        mono="IBM-Plex-Mono" if ok["mono"] else "Courier",
        serif_italic="SourceSerif4-Italic" if ok["serif"] else "Times-Italic",
        using_fallbacks=not all(ok.values()),
    )


FONTS = setup_fonts()


# ============================================================
# OUTILS COORDONNÉES ET TEXTE
# ============================================================

def ty(y_from_top: float) -> float:
    """Coordonnée Y depuis le haut de page vers ReportLab."""
    return PAGE_H - y_from_top


def clean_text(s: str) -> str:
    return (
        s.replace("•", "-")
        .replace("●", "-")
        .replace("○", "-")
        .replace("’", "’")
        .replace("\u00a0", " ")
        .strip()
    )


def draw_bg(c: canvas.Canvas, color=PAPER):
    c.setFillColor(color)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def draw_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y_top: float,
    w: float,
    font: str,
    size: float,
    leading: float,
    color=GRAPHITE,
    uppercase: bool = False,
    max_lines: Optional[int] = None,
) -> float:
    text = clean_text(text)
    if uppercase:
        text = text.upper()

    c.setFont(font, size)
    c.setFillColor(color)
    y = ty(y_top)
    lines: List[str] = []

    for raw in text.split("\n"):
        raw = raw.strip()
        if not raw:
            lines.append("")
        else:
            lines.extend(simpleSplit(raw, font, size, w))

    if max_lines:
        lines = lines[:max_lines]

    for line in lines:
        c.drawString(x, y, line)
        y -= leading

    return y_top + len(lines) * leading


def draw_h1(c, text, x, y_top, w, color=PAPER, size=43):
    return draw_text(c, text, x, y_top, w, FONTS.inter_black, size, size * 0.88, color, uppercase=True)


def draw_h2(c, text, x, y_top, w, color=CARBON, size=32):
    return draw_text(c, text, x, y_top, w, FONTS.inter_black, size, size * 0.94, color, uppercase=True)


def draw_h3(c, text, x, y_top, w, color=CARBON, size=13):
    return draw_text(c, text, x, y_top, w, FONTS.inter_black, size, size * 1.0, color, uppercase=True)


def draw_body(c, text, x, y_top, w=MAIN_COL, color=GRAPHITE, size=10, leading=14):
    return draw_text(c, text, x, y_top, w, FONTS.inter, size, leading, color)


def draw_lead(c, text, x, y_top, w=96 * mm, dark=False):
    return draw_text(c, text, x, y_top, w, FONTS.inter_bold, 14, 17, PAPER if dark else CARBON)


def draw_mono(c, text, x, y_top, w, dark=False, size=7, color=None):
    return draw_text(c, text, x, y_top, w, FONTS.mono, size, size * 1.3, color or (SIGNATURE if dark else STEEL), uppercase=True)


def draw_micro(c, text, x, y_top, w, dark=False, color=None):
    return draw_text(c, text, x, y_top, w, FONTS.mono, 6, 8, color or (SIGNATURE if dark else SOFT), uppercase=True)


def draw_serif(c, text, x, y_top, w, dark=True, size=14):
    return draw_text(c, text, x, y_top, w, FONTS.serif_italic, size, size * 1.18, PAPER if dark else CARBON)


def signature_line(c, x=M_LEFT, y_top=18 * mm, dark=False):
    c.setStrokeColor(SIGNATURE if dark else STEEL)
    c.setLineWidth(0.5)
    c.line(x, ty(y_top), x + 44 * mm, ty(y_top))


def folio(c, page_num: int, dark=False):
    draw_mono(c, f"{page_num:03d}", M_LEFT, 10 * mm, 18 * mm, dark=dark, size=7)


def z_block(c, page_num: int, force=False):
    if page_num % 2 == 0 and not force:
        return
    x = M_LEFT
    y = M_BOTTOM - 2 * mm
    c.setFillColor(SIGNATURE)
    c.rect(x, y, 10 * mm, 10 * mm, stroke=0, fill=1)
    c.setFillColor(CARBON)
    c.setFont(FONTS.inter_black, 8)
    c.drawCentredString(x + 5 * mm, y + 3.1 * mm, "Z")


def note(c, text: str, y_top=35 * mm, dark=False):
    draw_micro(c, text, NOTE_X, y_top, NOTE_COL, dark=dark)


def finish(c):
    c.showPage()


# ============================================================
# PARSING DU MANUSCRIT
# ============================================================

@dataclass
class Chapter:
    title: str
    paragraphs: List[str]


def default_manuscript() -> str:
    return """
Introduction
Le beatmaking est une discipline fascinante et dynamique qui a pris son essor grâce à l’évolution des technologies de production musicale et à l’impact des réseaux sociaux. En France, cette pratique est devenue de plus en plus accessible, permettant à un grand nombre d’artistes de se lancer dans la création musicale.

Cet ouvrage clarifie le métier de beatmaker, retrace son histoire et explique les différentes facettes de cette profession. Nous explorerons les outils nécessaires pour créer des beats, les techniques de production, ainsi que les stratégies pour monétiser son travail et protéger ses droits.

Chapitre 1 : Les Fondements du Beatmaking
Le beatmaking est une forme de production musicale qui repose sur l’utilisation d’outils numériques pour créer des rythmes et des compositions sans avoir recours à des instruments traditionnels.

Le terme beatmaking est apparu aux États-Unis à la fin des années 1970, en même temps que l’essor du rap. Le beatmaker crée une boucle rythmique à partir d’un sample et le transforme en une nouvelle composition instrumentale.

1.1 Qu’est-ce que le Beatmaking ?
Le beatmaking repose sur la relation entre les beatmakers et les artistes. Le beatmaker s’efforce de comprendre une vision pour produire des morceaux authentiques et percutants.

1.2 Les outils essentiels
Pour se lancer, il faut maîtriser son ordinateur, son DAW, ses plugins, ses samples, ses contrôleurs MIDI, son casque et ses moniteurs.

Chapitre 2 : Les Outils du Beatmaker
Le DAW est le cœur de toute configuration de production musicale. Il permet d’enregistrer, d’éditer, de mixer et de produire des pistes audio.

FL Studio, Ableton Live, Logic Pro X et Pro Tools offrent chacun une approche différente de la production. Le bon choix dépend du niveau, du budget et du flux de travail.

Chapitre 3 : Les Techniques de Production
Maîtriser les techniques de production permet de transformer des idées brutes en compositions polies et prêtes pour la diffusion.

La structure, le sampling, la programmation des rythmes, la mélodie, l’harmonie, l’arrangement, le mixage et le mastering forment la base d’un beat professionnel.

Conclusion
Le beatmaking est une discipline riche qui demande créativité, méthode et rigueur. Le système présenté dans ce livre aide à clarifier, produire, protéger et développer une carrière indépendante.
""".strip()


def load_manuscript() -> str:
    if os.path.exists(INPUT_MANUSCRIPT):
        with open(INPUT_MANUSCRIPT, "r", encoding="utf-8") as f:
            return f.read()
    return default_manuscript()



def is_markdown_table_line(line: str) -> bool:
    """Détecte une ligne de tableau Markdown."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def is_markdown_separator_line(line: str) -> bool:
    """Détecte la ligne séparatrice Markdown : | --- | --- |."""
    stripped = line.strip()
    if not is_markdown_table_line(stripped):
        return False
    cells = [c.strip() for c in stripped.strip("|").split("|")]
    cells = [c for c in cells if c]
    return bool(cells) and all(re.match(r"^:?-{3,}:?$", c) for c in cells)


def parse_markdown_table_row(line: str) -> List[str]:
    """Transforme une ligne Markdown en cellules."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_chapters(raw: str) -> List[Chapter]:
    """
    Parser intelligent externalisé.

    Accepte :
    - # Chapitre
    - ## Section
    - 1. Introduction
    - 1.1 Sous-section
    - Chapitre 1 : Titre
    - ANNEXE 1
    - Conclusion
    - tableaux Markdown
    - [IMAGE: fichier | légende]
    - [QUOTE: texte]
    - [CALLOUT: titre | texte]
    """
    from parser_manuscrit import parse_manuscript, blocks_to_legacy_paragraphs

    parsed = parse_manuscript(raw)

    return [
        Chapter(
            title=chapter.title,
            paragraphs=blocks_to_legacy_paragraphs(chapter),
        )
        for chapter in parsed
    ]

def table_rows_from_block(block: str) -> List[List[str]]:
    """
    Convertit un bloc [[TABLE_BLOCK]] en lignes.
    Supprime la ligne séparatrice Markdown.
    """
    raw_lines = block.replace("[[TABLE_BLOCK]]", "").strip().split("\n")
    rows: List[List[str]] = []

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        if is_markdown_separator_line(line):
            continue
        if is_markdown_table_line(line):
            rows.append(parse_markdown_table_row(line))

    return rows


def estimate_wrapped_height(text: str, width: float, font: str, size: float, leading: float, max_lines: int = 5) -> float:
    lines = simpleSplit(clean_text(text), font, size, width)
    lines = lines[:max_lines]
    return max(leading, len(lines) * leading)


def draw_cell_text(c, text: str, x: float, y_top: float, width: float, font: str, size: float, leading: float, color, max_lines: int = 5) -> None:
    c.setFont(font, size)
    c.setFillColor(color)
    lines = simpleSplit(clean_text(text), font, size, width)
    lines = lines[:max_lines]

    y = ty(y_top)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading


def draw_table_continuation_header(c, page_num: int) -> float:
    draw_bg(c, PAPER)
    folio(c, page_num)
    z_block(c, page_num)
    signature_line(c, M_LEFT, 27 * mm)
    draw_mono(c, "TABLEAU / SUITE", M_LEFT, 35 * mm, MAIN_COL)
    return 50 * mm


def draw_markdown_table(c, table_block: str, x: float, y_top: float, page_num: int):
    """
    Dessine un tableau Markdown en tableau vectoriel.
    Retourne : y_top, page_num.
    """
    rows = table_rows_from_block(table_block)

    if not rows or len(rows) < 2:
        return y_top, page_num

    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]

    # Largeur : on prend 106 mm pour les tableaux, car le A5 est étroit.
    table_w = 106 * mm if col_count >= 3 else MAIN_COL

    if col_count <= 2:
        font_size = 8.0
        leading = 9.3
    elif col_count == 3:
        font_size = 7.2
        leading = 8.4
    else:
        font_size = 6.3
        leading = 7.4

    padding_x = 2.0 * mm
    padding_y = 2.5 * mm

    # Répartition des colonnes.
    if col_count == 2:
        col_w = [table_w * 0.38, table_w * 0.62]
    elif col_count == 3:
        col_w = [table_w * 0.24, table_w * 0.38, table_w * 0.38]
    elif col_count == 4:
        col_w = [table_w * 0.20, table_w * 0.27, table_w * 0.28, table_w * 0.25]
    else:
        col_w = [table_w / col_count for _ in range(col_count)]

    y = y_top + 3 * mm

    for row_idx, row in enumerate(rows):
        row_heights = []

        for i, cell in enumerate(row):
            inner_w = max(8 * mm, col_w[i] - 2 * padding_x)
            if row_idx == 0:
                cell_font = FONTS.mono
                cell_size = 6.0
                cell_leading = 7.0
            else:
                cell_font = FONTS.inter_bold if i == 0 else FONTS.inter
                cell_size = font_size
                cell_leading = leading

            row_heights.append(
                estimate_wrapped_height(cell, inner_w, cell_font, cell_size, cell_leading, max_lines=5)
            )

        row_h = max(row_heights) + 2 * padding_y

        if y + row_h > CONTENT_BOTTOM:
            finish(c)
            page_num += 1
            y = draw_table_continuation_header(c, page_num)

            # Réimpression de l’en-tête si on coupe le tableau.
            header = rows[0]
            header_h = 10 * mm

            c.setFillColor(STEEL)
            c.rect(x, ty(y) - header_h + 3 * mm, table_w, header_h, stroke=0, fill=1)

            cx = x
            for i, cell in enumerate(header):
                draw_cell_text(
                    c,
                    cell.upper(),
                    cx + padding_x,
                    y + padding_y,
                    col_w[i] - 2 * padding_x,
                    FONTS.mono,
                    6.0,
                    7.0,
                    PAPER,
                    max_lines=3,
                )
                cx += col_w[i]

            y += header_h

        # Fond ligne.
        if row_idx == 0:
            c.setFillColor(STEEL)
        else:
            c.setFillColor(TABLE_ALT if row_idx % 2 == 1 else PAPER)

        c.rect(x, ty(y) - row_h + 3 * mm, table_w, row_h, stroke=0, fill=1)

        # Texte cellules.
        cx = x
        for i, cell in enumerate(row):
            if row_idx == 0:
                cell_font = FONTS.mono
                cell_size = 6.0
                cell_leading = 7.0
                cell_color = PAPER
                cell_text = cell.upper()
            else:
                cell_font = FONTS.inter_bold if i == 0 else FONTS.inter
                cell_size = font_size
                cell_leading = leading
                cell_color = GRAPHITE
                cell_text = cell

            draw_cell_text(
                c,
                cell_text,
                cx + padding_x,
                y + padding_y,
                col_w[i] - 2 * padding_x,
                cell_font,
                cell_size,
                cell_leading,
                cell_color,
                max_lines=5,
            )

            cx += col_w[i]

        # Filets.
        c.setStrokeColor(LINE)
        c.setLineWidth(0.35)

        top_line_y = ty(y)
        bottom_line_y = ty(y + row_h - 3 * mm)

        c.line(x, top_line_y, x + table_w, top_line_y)
        c.line(x, bottom_line_y, x + table_w, bottom_line_y)

        cx = x
        for cw in col_w:
            c.line(cx, top_line_y, cx, bottom_line_y)
            cx += cw
        c.line(x + table_w, top_line_y, x + table_w, bottom_line_y)

        y += row_h - 1 * mm

    return y + 5 * mm, page_num





def parse_image_block(text: str):
    """
    Parse une balise :
    [IMAGE: fichier.png | Légende]
    Retourne (filename, caption)
    """
    raw = text.strip()
    if not raw.startswith("[IMAGE:") or not raw.endswith("]"):
        return None, None

    content = raw[len("[IMAGE:"):-1].strip()

    if "|" in content:
        filename, caption = content.split("|", 1)
        return filename.strip(), caption.strip()

    return content.strip(), ""


def draw_image_placeholder(c, image_name: str, caption: str, x: float, y_top: float, w: float, h: float):
    """
    Dessine un placeholder si l’image est absente ou illisible.
    """
    c.setFillColor(TABLE_ALT)
    c.rect(x, ty(y_top) - h, w, h, stroke=0, fill=1)

    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.rect(x, ty(y_top) - h, w, h, stroke=1, fill=0)

    draw_mono(c, "IMAGE MANQUANTE", x + 4 * mm, y_top + 7 * mm, w - 8 * mm, size=6.5)
    draw_micro(c, image_name, x + 4 * mm, y_top + 16 * mm, w - 8 * mm)

    if caption:
        draw_micro(c, caption, x, y_top + (h / mm) * mm + 4 * mm, w)


def draw_image_block(c, image_name: str, caption: str, x: float, y_top: float, page_num: int):
    """
    Dessine une image dans la colonne principale.
    Règles :
    - largeur 88 mm
    - hauteur max 55 mm
    - légende mono 6 pt
    - nouvelle page si besoin
    - placeholder si image absente
    Retourne : y_top, page_num
    """
    img_w = MAIN_COL
    max_h = 55 * mm
    gap_before = 4 * mm
    gap_after = 7 * mm
    caption_h = 8 * mm if caption else 0

    y = y_top + gap_before

    image_path = os.path.join(IMAGES_DIR, image_name)

    # Hauteur prévue par défaut.
    display_w = img_w
    display_h = max_h

    # Calcul proportionnel si possible.
    if os.path.exists(image_path):
        try:
            from reportlab.lib.utils import ImageReader
            reader = ImageReader(image_path)
            iw, ih = reader.getSize()
            ratio = ih / float(iw)
            display_h = min(max_h, display_w * ratio)
        except Exception:
            display_h = max_h

    total_h = display_h + caption_h + gap_after

    if y + total_h > CONTENT_BOTTOM:
        finish(c)
        page_num += 1
        draw_bg(c, PAPER)
        folio(c, page_num)
        z_block(c, page_num)
        signature_line(c, M_LEFT, 27 * mm)
        draw_mono(c, "IMAGE / SUITE", M_LEFT, 35 * mm, MAIN_COL)
        y = 50 * mm

    if os.path.exists(image_path):
        try:
            c.drawImage(
                image_path,
                x,
                ty(y) - display_h,
                width=display_w,
                height=display_h,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            draw_image_placeholder(c, image_name, caption, x, y, display_w, display_h)
    else:
        draw_image_placeholder(c, image_name, caption, x, y, display_w, display_h)

    if caption:
        draw_micro(c, caption, x, y + (display_h / mm) * mm + 4 * mm, display_w)

    return y + total_h, page_num



def parse_callout_block(text: str):
    """
    Parse une balise :
    [CALLOUT: Titre | Texte]
    Retourne (title, body)
    """
    raw = text.strip()
    if not raw.startswith("[CALLOUT:") or not raw.endswith("]"):
        return None, None

    content = raw[len("[CALLOUT:"):-1].strip()

    if "|" in content:
        title, body = content.split("|", 1)
        return title.strip(), body.strip()

    return "À retenir", content.strip()


def draw_callout_block(c, title: str, body: str, x: float, y_top: float, page_num: int):
    """
    Dessine un encadré éditorial premium.
    Règles :
    - largeur colonne principale
    - fond blanc architectural / gris très léger
    - filet vertical gauche acier nuit
    - titre mono
    - texte Inter
    - nouvelle page si besoin
    Retourne : y_top, page_num
    """
    box_w = MAIN_COL
    padding = 5 * mm
    gap_before = 4 * mm
    gap_after = 7 * mm
    line_w = 1.2 * mm

    title_font = FONTS.mono
    title_size = 6.8
    title_leading = 8

    body_font = FONTS.inter
    body_size = 9.2
    body_leading = 12

    inner_w = box_w - (2 * padding) - line_w

    title_lines = simpleSplit(clean_text(title.upper()), title_font, title_size, inner_w)
    body_lines = simpleSplit(clean_text(body), body_font, body_size, inner_w)

    title_h = max(title_leading, len(title_lines) * title_leading)
    body_h = max(body_leading, len(body_lines) * body_leading)

    box_h = padding + title_h + 3 * mm + body_h + padding

    y = y_top + gap_before

    if y + box_h + gap_after > CONTENT_BOTTOM:
        finish(c)
        page_num += 1
        draw_bg(c, PAPER)
        folio(c, page_num)
        z_block(c, page_num)
        signature_line(c, M_LEFT, 27 * mm)
        draw_mono(c, "ENCADRÉ / SUITE", M_LEFT, 35 * mm, MAIN_COL)
        y = 50 * mm

    # Fond
    c.setFillColor(TABLE_ALT)
    c.rect(x, ty(y) - box_h, box_w, box_h, stroke=0, fill=1)

    # Filet vertical gauche
    c.setFillColor(STEEL)
    c.rect(x, ty(y) - box_h, line_w, box_h, stroke=0, fill=1)

    # Contour fin
    c.setStrokeColor(LINE)
    c.setLineWidth(0.35)
    c.rect(x, ty(y) - box_h, box_w, box_h, stroke=1, fill=0)

    # Titre
    text_x = x + padding + line_w
    text_y = y + padding

    c.setFillColor(STEEL)
    c.setFont(title_font, title_size)
    cursor = ty(text_y)
    for line in title_lines:
        c.drawString(text_x, cursor, line)
        cursor -= title_leading

    # Corps
    cursor -= 3 * mm
    c.setFillColor(GRAPHITE)
    c.setFont(body_font, body_size)
    for line in body_lines:
        c.drawString(text_x, cursor, line)
        cursor -= body_leading

    return y + box_h + gap_after, page_num



def parse_quote_block(text: str):
    """
    Parse une balise :
    [QUOTE: Texte de citation]
    Retourne le texte.
    """
    raw = text.strip()
    if not raw.startswith("[QUOTE:") or not raw.endswith("]"):
        return None

    return raw[len("[QUOTE:"):-1].strip()


def draw_quote_block(c, quote_text: str, x: float, y_top: float, page_num: int):
    """
    Dessine une citation premium.
    Règles :
    - bloc noir carbone
    - texte blanc architectural
    - serif italique si disponible
    - grande respiration
    - nouvelle page si besoin
    Retourne : y_top, page_num
    """
    box_w = MAIN_COL
    padding = 7 * mm
    gap_before = 6 * mm
    gap_after = 8 * mm

    quote_font = FONTS.serif_italic
    quote_size = 15
    quote_leading = 18

    inner_w = box_w - 2 * padding
    lines = simpleSplit(clean_text(quote_text), quote_font, quote_size, inner_w)

    box_h = padding + max(quote_leading, len(lines) * quote_leading) + padding

    y = y_top + gap_before

    if y + box_h + gap_after > CONTENT_BOTTOM:
        finish(c)
        page_num += 1
        draw_bg(c, PAPER)
        folio(c, page_num)
        z_block(c, page_num)
        signature_line(c, M_LEFT, 27 * mm)
        draw_mono(c, "CITATION / SUITE", M_LEFT, 35 * mm, MAIN_COL)
        y = 50 * mm

    # Bloc noir
    c.setFillColor(CARBON)
    c.rect(x, ty(y) - box_h, box_w, box_h, stroke=0, fill=1)

    # Petit signe graphique
    c.setFillColor(SIGNATURE)
    c.rect(x + padding, ty(y + padding) - 2 * mm, 14 * mm, 0.7 * mm, stroke=0, fill=1)

    # Citation
    c.setFillColor(PAPER)
    c.setFont(quote_font, quote_size)

    cursor = ty(y + padding + 8 * mm)
    for line in lines:
        c.drawString(x + padding, cursor, line)
        cursor -= quote_leading

    return y + box_h + gap_after, page_num



def parse_opening_image_block(text: str):
    """
    Parse une balise :
    [OPENING_IMAGE: fichier.png | Titre de partie]
    Retourne (filename, title)
    """
    raw = text.strip()
    if not raw.startswith("[OPENING_IMAGE:") or not raw.endswith("]"):
        return None, None

    content = raw[len("[OPENING_IMAGE:"):-1].strip()

    if "|" in content:
        filename, title = content.split("|", 1)
        return filename.strip(), title.strip()

    return content.strip(), "Ouverture"


def draw_opening_image_page(c, image_name: str, title: str, page_num: int):
    """
    Dessine une page d’ouverture sombre avec image.
    Retourne le nouveau numéro de page.
    """
    draw_bg(c, CARBON)

    # Folio clair
    c.setFillColor(SIGNATURE)
    c.setFont(FONTS.mono, 7)
    c.drawString(M_LEFT, ty(14 * mm), f"{page_num:03d}")

    image_path = os.path.join(IMAGES_DIR, image_name)

    # Zone visuelle
    img_x = M_LEFT
    img_y = 32 * mm
    img_w = 104 * mm
    img_h = 78 * mm

    if os.path.exists(image_path):
        try:
            c.drawImage(
                image_path,
                img_x,
                ty(img_y) - img_h,
                width=img_w,
                height=img_h,
                preserveAspectRatio=True,
                mask="auto",
            )

            # Voile noir léger pour garder la charte
            c.setFillColor(CARBON)
            try:
                c.setFillAlpha(0.18)
                c.rect(img_x, ty(img_y) - img_h, img_w, img_h, stroke=0, fill=1)
                c.setFillAlpha(1)
            except Exception:
                pass

        except Exception:
            c.setFillColor(STEEL)
            c.rect(img_x, ty(img_y) - img_h, img_w, img_h, stroke=0, fill=1)
            draw_micro(c, "IMAGE ILLISIBLE : " + image_name, img_x + 5 * mm, img_y + 8 * mm, img_w - 10 * mm, color=SIGNATURE)
    else:
        c.setFillColor(STEEL)
        c.rect(img_x, ty(img_y) - img_h, img_w, img_h, stroke=0, fill=1)
        draw_micro(c, "IMAGE MANQUANTE : " + image_name, img_x + 5 * mm, img_y + 8 * mm, img_w - 10 * mm, color=SIGNATURE)

    # Signature-line
    signature_line(c, M_LEFT, 122 * mm, dark=True)

    # Micro-label
    draw_micro(c, "PARTIE / OUVERTURE VISUELLE", M_LEFT, 132 * mm, 70 * mm, color=SIGNATURE)

    # Titre
    title_clean = clean_text(title)
    draw_h2(c, title_clean.upper(), M_LEFT, 145 * mm, 96 * mm, color=PAPER, size=27)

    # Sous-texte système
    draw_serif(
        c,
        "Studio nocturne. Matière urbaine. Présence construite.",
        M_LEFT,
        176 * mm,
        88 * mm,
        dark=True,
        size=13,
    )

    # Bloc Z
    c.setFillColor(SIGNATURE)
    c.rect(M_LEFT, ty(194 * mm) - 10 * mm, 10 * mm, 10 * mm, stroke=0, fill=1)
    c.setFillColor(CARBON)
    c.setFont(FONTS.inter_black, 8)
    c.drawCentredString(M_LEFT + 5 * mm, ty(194 * mm) - 6.8 * mm, "Z")

    finish(c)
    return page_num + 1


# ============================================================
# PAGES FIXES
# ============================================================

def cover(c, page_num):
    draw_bg(c, CARBON)
    draw_micro(c, "Version générée\nPDF éditorial premium\nAtelier Zydka", M_LEFT, 18 * mm, 55 * mm, color=SOFT)

    # Marque haut droite
    c.setFillColor(SIGNATURE)
    c.rect(122 * mm, ty(18 * mm) - 10 * mm, 10 * mm, 10 * mm, stroke=0, fill=1)
    c.setFillColor(CARBON)
    c.setFont(FONTS.inter_black, 8)
    c.drawCentredString(127 * mm, ty(18 * mm) - 6.8 * mm, "Z")

    draw_mono(c, "Studio · Présence · Système · Décision", M_LEFT, 91 * mm, 94 * mm, dark=True)
    signature_line(c, M_LEFT, 102 * mm, dark=True)
    draw_h1(c, "Le Manuel\nde Présence", M_LEFT, 110 * mm, 112 * mm, color=PAPER, size=43)
    draw_text(c, "Atelier Zydka", M_LEFT, 153 * mm, 92 * mm, FONTS.inter_bold, 10, 12, SIGNATURE, uppercase=True)
    draw_serif(c, "Livre pour beatmakers indépendants : stratégie, organisation et présence.", M_LEFT, 165 * mm, 90 * mm, dark=True, size=14)

    draw_micro(c, "Document de pilotage", M_LEFT, 190 * mm, 50 * mm, color=SOFT)
    draw_micro(c, "Référence studio", 100 * mm, 190 * mm, 36 * mm, color=SOFT)
    z_block(c, page_num, force=True)
    finish(c)


def charte_page(c, page_num):
    draw_bg(c, PAPER)
    folio(c, page_num)
    signature_line(c, M_LEFT, 27 * mm)
    draw_mono(c, "01 / Charte graphique", M_LEFT, 35 * mm, MAIN_COL)
    draw_h2(c, "Système visuel V3", M_LEFT, 43 * mm, MAIN_COL)
    draw_lead(c, "Minimalisme structurel, tension urbaine et précision de studio contemporain.", M_LEFT, 69 * mm)
    draw_body(c, "La maquette repose sur une base noire et blanche, une grille stricte et des interventions graphiques rares. Chaque signe doit aider à lire, décider ou mémoriser.", M_LEFT, 94 * mm)

    # Callout règle
    c.setFillColor(STEEL)
    c.rect(M_LEFT, ty(125 * mm) - 16 * mm, 1.2 * mm, 16 * mm, stroke=0, fill=1)
    draw_body(c, "Règle : aucun effet décoratif. Le premium vient du choix, du silence et de la hiérarchie.", M_LEFT + 5 * mm, 123 * mm, 80 * mm, size=9, leading=12)

    # Palette
    swatches = [
        (CARBON, PAPER, "Noir carbone\n#0B0B0A"),
        (PAPER, CARBON, "Blanc archi.\n#F6F6F4"),
        (GRAPHITE, PAPER, "Graphite\n#3A3A38"),
        (STEEL, PAPER, "Acier nuit\n#2A353F"),
        (SIGNATURE, CARBON, "Sable clair\n#D8C9AE"),
    ]
    x = M_LEFT
    for fill, txt_color, label in swatches:
        c.setFillColor(fill)
        c.rect(x, ty(147 * mm) - 23 * mm, 16 * mm, 23 * mm, stroke=0, fill=1)
        if fill == PAPER:
            c.setStrokeColor(LINE)
            c.rect(x, ty(147 * mm) - 23 * mm, 16 * mm, 23 * mm, stroke=1, fill=0)
        draw_micro(c, label, x + 1.5 * mm, 158 * mm, 13 * mm, color=txt_color)
        x += 18 * mm

    # Spécimens
    specs = [
        ("Titres", "Inter 800", "Titres massifs, serrés, souvent en deux lignes."),
        ("Corps", "Inter 400", "Lecture claire, sans effet, ligne courte et stable."),
        ("Citations", "Source Serif", "Usage rare pour phrases pivots et respirations."),
        ("Système", "IBM Plex Mono", "Versions, numéros, notes, catégories et repères."),
    ]
    positions = [(M_LEFT, 174 * mm), (M_LEFT + 48 * mm, 174 * mm), (M_LEFT, 194 * mm), (M_LEFT + 48 * mm, 194 * mm)]
    for (kicker, title, desc), (x, y) in zip(specs, positions):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(x, ty(y), x + 40 * mm, ty(y))
        draw_mono(c, kicker, x, y + 3 * mm, 42 * mm, size=6)
        draw_h3(c, title, x, y + 8 * mm, 42 * mm, size=11)
        draw_body(c, desc, x, y + 14 * mm, 42 * mm, size=7.5, leading=9)

    note(c, "Intentions : New York / Apple / Urbain. Grille A5. Marges larges. Accent clair limité.\n\nLe Bloc Z doit signer une page, pas l’habiller.", 34 * mm)
    finish(c)


def toc_page(c, page_num, chapters: List[Chapter]):
    draw_bg(c, PAPER)
    folio(c, page_num)
    z_block(c, page_num)
    signature_line(c, M_LEFT, 27 * mm)
    draw_mono(c, "02 / Navigation", M_LEFT, 35 * mm, MAIN_COL)
    draw_h2(c, "Table des matières", M_LEFT, 43 * mm, 96 * mm)

    y = 78 * mm
    max_rows = 7
    for i, ch in enumerate(chapters[:max_rows], start=1):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(M_LEFT, ty(y), M_LEFT + 106 * mm, ty(y))
        draw_mono(c, f"{i:02d}", M_LEFT, y + 4 * mm, 14 * mm)
        title = re.sub(r"^Chapitre\s+\d+\s*[:\-]\s*", "", ch.title, flags=re.I)
        draw_text(c, title, M_LEFT + 21 * mm, y + 3.5 * mm, 58 * mm, FONTS.inter_bold, 10.5, 12, CARBON, uppercase=True, max_lines=1)
        preview = " · ".join([p.replace("##", "").strip() for p in ch.paragraphs[:3]])[:90]
        draw_body(c, preview, M_LEFT + 21 * mm, y + 10 * mm, 58 * mm, color=SOFT, size=7.5, leading=9)
        draw_mono(c, "--", M_LEFT + 91 * mm, y + 4 * mm, 15 * mm)
        y += 20 * mm

    c.setStrokeColor(LINE)
    c.line(M_LEFT, ty(y), M_LEFT + 106 * mm, ty(y))
    finish(c)


def visual_opener(c, page_num, title="Fondations", subtitle="Signal, texture, rythme. Une présence qui se construit comme un son."):
    draw_bg(c, CARBON)
    folio(c, page_num, dark=True)
    z_block(c, page_num)

    # grille vectorielle
    c.setStrokeColor(Color(0.85, 0.79, 0.68, alpha=0.25))
    c.setLineWidth(0.35)
    for gx in range(22, 132, 8):
        c.line(gx * mm, ty(62 * mm), gx * mm, ty(136 * mm))
    for gy in range(62, 137, 8):
        c.line(22 * mm, ty(gy * mm), 132 * mm, ty(gy * mm))

    # orbites
    c.setStrokeColor(Color(0.85, 0.79, 0.68, alpha=0.35))
    for r in [42, 28, 14]:
        c.circle(112 * mm, ty(48 * mm), (r / 2) * mm, stroke=1, fill=0)

    # signal
    c.setFillColor(Color(0.85, 0.79, 0.68, alpha=0.55))
    heights = [12, 26, 18, 38, 14, 30, 21, 45, 17, 31, 22, 37, 15, 29, 20, 34]
    x = 18 * mm
    baseline = ty(136 * mm)
    for h in heights:
        c.rect(x, baseline, 2 * mm, h * mm, stroke=0, fill=1)
        x += 6 * mm

    # voile gauche
    c.setFillColor(Color(0.043, 0.043, 0.039, alpha=0.88))
    c.rect(0, 0, 62 * mm, PAGE_H, stroke=0, fill=1)

    signature_line(c, M_LEFT, 18 * mm, dark=True)
    draw_mono(c, "Partie / Ouverture", M_LEFT, 27 * mm, 80 * mm, dark=True)
    draw_h2(c, title, M_LEFT, 78 * mm, 94 * mm, color=PAPER, size=41)
    draw_serif(c, subtitle, M_LEFT, 112 * mm, 82 * mm, dark=True, size=14)
    draw_micro(c, "Direction visuelle\nConsole · onde · signal", 88 * mm, 180 * mm, 44 * mm, dark=True)
    finish(c)


def part_opener(c, page_num, title, subtitle):
    draw_bg(c, CARBON)
    folio(c, page_num, dark=True)
    z_block(c, page_num)
    signature_line(c, M_LEFT, 27 * mm, dark=True)
    draw_mono(c, "Ouverture de chapitre", M_LEFT, 35 * mm, 84 * mm, dark=True)
    draw_h2(c, title, M_LEFT, 101 * mm, 100 * mm, color=PAPER, size=38)
    draw_serif(c, subtitle, M_LEFT, 148 * mm, 84 * mm, dark=True, size=14)
    draw_micro(c, "Livre beatmakers indépendants", M_LEFT, 190 * mm, 80 * mm, color=SOFT)
    finish(c)


def callout_page(c, page_num):
    draw_bg(c, PAPER)
    folio(c, page_num)
    z_block(c, page_num)
    signature_line(c, M_LEFT, 27 * mm)
    draw_mono(c, "Module / Encadré", M_LEFT, 35 * mm, MAIN_COL)
    draw_h2(c, "Point critique", M_LEFT, 43 * mm, MAIN_COL)
    draw_lead(c, "Un encadré doit isoler une décision, une alerte ou une règle simple. Il ne sert pas à décorer la page.", M_LEFT, 72 * mm)

    x, y_top, w, h = M_LEFT, 106 * mm, MAIN_COL, 45 * mm
    c.setFillColor(PAPER)
    c.rect(x, ty(y_top) - h, w, h, stroke=0, fill=1)
    c.setStrokeColor(LINE)
    c.rect(x, ty(y_top) - h, w, h, stroke=1, fill=0)
    c.setFillColor(STEEL)
    c.rect(x, ty(y_top) - h, 1.4 * mm, h, stroke=0, fill=1)
    draw_mono(c, "À retenir", x + 5 * mm, y_top + 7 * mm, 60 * mm)
    draw_body(c, "Si tu publies tes beats sans contrat clair, tu crées un risque juridique dès la première vente.", x + 5 * mm, y_top + 18 * mm, 74 * mm)

    c.setFillColor(CARBON)
    c.rect(M_LEFT, ty(166 * mm) - 25 * mm, 96 * mm, 25 * mm, stroke=0, fill=1)
    draw_serif(c, "La clarté protège mieux qu’un effet de style.", M_LEFT + 7 * mm, 174 * mm, 80 * mm, dark=True, size=16)
    finish(c)


def table_page(c, page_num):
    draw_bg(c, PAPER)
    folio(c, page_num)
    z_block(c, page_num)
    signature_line(c, M_LEFT, 27 * mm)
    draw_mono(c, "Module / Tableau comparatif", M_LEFT, 35 * mm, MAIN_COL)
    draw_h2(c, "Comparer pour décider", M_LEFT, 43 * mm, 100 * mm, size=30)
    draw_lead(c, "Le tableau sert à choisir vite : outil, usage, limite, décision.", M_LEFT, 72 * mm)

    rows = [
        ("FL Studio", "Production rapide, séquenceur clair.", "Idéal démarrage."),
        ("Ableton Live", "Performance, boucles, expérimentation.", "Avancé / live."),
        ("Logic Pro", "Composition, mixage, écosystème Mac.", "Studio stable."),
        ("Pro Tools", "Édition précise, standard studio.", "Post-prod / mix."),
    ]
    headers = ["Outil", "Usage", "Décision"]
    x0, y0 = M_LEFT, 104 * mm
    col_w = [28 * mm, 46 * mm, 32 * mm]
    row_h = 18 * mm
    total_w = sum(col_w)

    c.setFillColor(STEEL)
    c.rect(x0, ty(y0) - row_h, total_w, row_h, stroke=0, fill=1)
    x = x0
    for i, h in enumerate(headers):
        draw_mono(c, h, x + 3 * mm, y0 + 6 * mm, col_w[i] - 6 * mm, color=PAPER, size=6.5)
        x += col_w[i]

    y = y0 + row_h
    for idx, row in enumerate(rows):
        c.setFillColor(TABLE_ALT if idx % 2 == 0 else PAPER)
        c.rect(x0, ty(y) - row_h, total_w, row_h, stroke=0, fill=1)
        c.setStrokeColor(LINE)
        c.line(x0, ty(y), x0 + total_w, ty(y))
        x = x0
        for i, cell in enumerate(row):
            draw_text(c, cell, x + 3 * mm, y + 5 * mm, col_w[i] - 6 * mm, FONTS.inter_bold if i == 0 else FONTS.inter, 8.3, 10, GRAPHITE)
            x += col_w[i]
        y += row_h
    c.setStrokeColor(LINE)
    c.rect(x0, ty(y0) - row_h * (len(rows) + 1), total_w, row_h * (len(rows) + 1), stroke=1, fill=0)
    finish(c)


def annex_page(c, page_num):
    draw_bg(c, PAPER)
    folio(c, page_num)
    signature_line(c, M_LEFT, 27 * mm)
    draw_mono(c, "Annexe A / Fiche outil", M_LEFT, 35 * mm, MAIN_COL)
    draw_h2(c, "Boîte à outils", M_LEFT, 43 * mm, 98 * mm)
    draw_lead(c, "Les annexes servent à exécuter. Elles ne doivent pas alourdir le corps principal.", M_LEFT, 72 * mm)

    blocks = [
        ("A", "Brief", "Questions de cadrage avant projet."),
        ("B", "Contrat", "Clauses, licences, droits."),
        ("C", "Split sheet", "Répartition des parts."),
        ("D", "Checklist", "Livraison et archivage."),
        ("E", "Calendrier", "Publication et relance."),
        ("F", "Audit", "État des lieux du système."),
    ]
    positions = [(M_LEFT, 106 * mm), (M_LEFT + 54 * mm, 106 * mm), (M_LEFT, 138 * mm), (M_LEFT + 54 * mm, 138 * mm), (M_LEFT, 170 * mm), (M_LEFT + 54 * mm, 170 * mm)]
    for (letter, title, desc), (x, y) in zip(blocks, positions):
        c.setStrokeColor(LINE)
        c.line(x, ty(y), x + 44 * mm, ty(y))
        draw_mono(c, letter, x, y + 4 * mm, 10 * mm)
        draw_h3(c, title, x, y + 11 * mm, 44 * mm, size=13)
        draw_body(c, desc, x, y + 22 * mm, 44 * mm, size=8.4, leading=10)
    finish(c)


def back_cover(c, page_num):
    draw_bg(c, CARBON)
    draw_micro(c, "Le Manuel de Présence\nAtelier Zydka", M_LEFT, 18 * mm, 55 * mm, color=SOFT)
    c.setFillColor(SIGNATURE)
    c.rect(122 * mm, ty(18 * mm) - 10 * mm, 10 * mm, 10 * mm, stroke=0, fill=1)
    c.setFillColor(CARBON)
    c.setFont(FONTS.inter_black, 8)
    c.drawCentredString(127 * mm, ty(18 * mm) - 6.8 * mm, "Z")
    signature_line(c, M_LEFT, 98 * mm, dark=True)
    draw_h2(c, "Construire moins.\nConstruire plus juste.", M_LEFT, 108 * mm, 98 * mm, color=PAPER, size=32)
    draw_serif(c, "Atelier Zydka — Construire la présence. Signer l’univers.", M_LEFT, 151 * mm, 82 * mm, dark=True, size=15)
    draw_micro(c, "Document de pilotage", M_LEFT, 190 * mm, 50 * mm, color=SOFT)
    draw_micro(c, "Accent clair · finition premium", 82 * mm, 190 * mm, 55 * mm, color=SOFT)
    finish(c)


# ============================================================
# FLUX CHAPITRES
# ============================================================

def draw_chapter_pages(c, start_page: int, chapter: Chapter, index: int) -> int:
    page = start_page
    title_clean = re.sub(r"^Chapitre\s+\d+\s*[:\-]\s*", "", chapter.title, flags=re.I)

    # Ouverture pour chaque grand chapitre.
    page += 1
    part_opener(c, page, title_clean[:80], "Lire, cadrer, construire : transformer une matière brute en système exploitable.")

    page += 1
    draw_bg(c, PAPER)
    folio(c, page)
    z_block(c, page)
    signature_line(c, M_LEFT, 27 * mm)
    draw_mono(c, f"Chapitre {index:02d} / Texte courant", M_LEFT, 35 * mm, MAIN_COL)
    y = draw_h2(c, title_clean, M_LEFT, 43 * mm, MAIN_COL, size=29)
    y += 7 * mm

    if chapter.paragraphs:
        first = chapter.paragraphs[0].replace("##", "").strip()
        y = draw_lead(c, first[:220], M_LEFT, y, MAIN_COL)
        y += 8 * mm
        remaining = chapter.paragraphs[1:]
    else:
        remaining = []

    note(c, "Note latérale : repères, définitions, erreurs fréquentes et décisions à retenir.", 35 * mm)

    for para in remaining:
        para = para.strip()
        if not para:
            continue

        if para.startswith("[[TABLE_BLOCK]]"):
            y, page = draw_markdown_table(c, para, M_LEFT, y, page)
            continue

        if para.startswith("[IMAGE:"):
            image_name, image_caption = parse_image_block(para)
            if image_name:
                y, page = draw_image_block(c, image_name, image_caption, M_LEFT, y, page)
            continue

        if para.startswith("[CALLOUT:"):
            callout_title, callout_body = parse_callout_block(para)
            if callout_body:
                y, page = draw_callout_block(c, callout_title, callout_body, M_LEFT, y, page)
            continue

        if para.startswith("[QUOTE:"):
            quote_text = parse_quote_block(para)
            if quote_text:
                y, page = draw_quote_block(c, quote_text, M_LEFT, y, page)
            continue

        if para.strip() == "[PAGE_BREAK]":
            finish(c)
            page += 1
            draw_bg(c, PAPER)
            folio(c, page)
            z_block(c, page)
            signature_line(c, M_LEFT, 27 * mm)
            draw_mono(c, f"Chapitre {index:02d} / Suite", M_LEFT, 35 * mm, MAIN_COL)
            draw_micro(c, "SUITE DU CHAPITRE. GARDER LES PARAGRAPHES COURTS ET LES INTERTITRES VISIBLES.", NOTE_X, 35 * mm, NOTE_COL)
            y = 50 * mm
            continue

        if para.startswith("[OPENING_IMAGE:"):
            opening_image_name, opening_title = parse_opening_image_block(para)
            if opening_image_name and FEATURES.get("include_visual_opening_pages", False):
                finish(c)
                page += 1
                page = draw_opening_image_page(c, opening_image_name, opening_title, page)
                draw_bg(c, PAPER)
                folio(c, page)
                z_block(c, page)
                signature_line(c, M_LEFT, 27 * mm)
                draw_mono(c, f"Chapitre {index:02d} / Suite", M_LEFT, 35 * mm, MAIN_COL)
                draw_micro(c, "SUITE DU CHAPITRE. GARDER LES PARAGRAPHES COURTS ET LES INTERTITRES VISIBLES.", NOTE_X, 35 * mm, NOTE_COL)
                y = 50 * mm
            continue

        is_intertitle = para.startswith("##")
        if is_intertitle:
            needed = 16 * mm
        else:
            lines = simpleSplit(para, FONTS.inter, 9.6, MAIN_COL)
            needed = len(lines) * 13 + 5 * mm

        if y + needed > CONTENT_BOTTOM:
            finish(c)
            page += 1
            draw_bg(c, PAPER)
            folio(c, page)
            z_block(c, page)
            signature_line(c, M_LEFT, 27 * mm)
            draw_mono(c, f"Chapitre {index:02d} / Suite", M_LEFT, 35 * mm, MAIN_COL)
            y = 50 * mm
            note(c, "Suite du chapitre. Garder les paragraphes courts et les intertitres visibles.", 35 * mm)

        if is_intertitle:
            y = draw_h3(c, para.replace("##", "").strip(), M_LEFT, y, MAIN_COL, size=12.5)
            y += 5 * mm
        elif para.startswith("•"):
            y = draw_body(c, para, M_LEFT + 3 * mm, y, MAIN_COL - 3 * mm, size=9.4, leading=12.5)
            y += 2.5 * mm
        else:
            y = draw_body(c, para, M_LEFT, y, MAIN_COL, size=9.6, leading=13)
            y += 3.2 * mm

    finish(c)
    return page


# ============================================================
# GÉNÉRATION PRINCIPALE
# ============================================================

def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw = load_manuscript()
    chapters = parse_chapters(raw)

    c = canvas.Canvas(OUTPUT_PDF, pagesize=PAGE_SIZE, pageCompression=0)
    c.setTitle("Le Manuel de présence — Atelier Zydka")
    c.setAuthor("Atelier Zydka")
    c.setSubject("Livre A5 pour beatmakers indépendants")
    c.setCreator("ReportLab — Atelier Source Éditoriale")

    page = 1
    cover(c, page)

    page += 1
    charte_page(c, page)

    page += 1
    toc_page(c, page, chapters)

    page += 1
    visual_opener(c, page, "Fondations", "Studio nocturne. Matière urbaine. Présence construite.")

    # Pages de démonstration des modules, conservées comme vraies pages utiles.
    page += 1
    callout_page(c, page)

    page += 1
    table_page(c, page)

    # Flux du manuscrit.
    for idx, ch in enumerate(chapters, start=1):
        page = draw_chapter_pages(c, page, ch, idx)

    page += 1
    annex_page(c, page)

    page += 1
    back_cover(c, page)

    c.save()

    print("PDF généré :", OUTPUT_PDF)
    print("Nombre de chapitres détectés :", len(chapters))
    if FONTS.using_fallbacks:
        print("Attention : polices fallback utilisées. Ajoute les .ttf dans ./fonts pour le rendu final fidèle.")
    if not os.path.exists(INPUT_MANUSCRIPT):
        print("Attention : aucun manuscrit_beatmakers.txt trouvé. Le PDF utilise un extrait de démonstration intégré.")


if __name__ == "__main__":
    generate()

