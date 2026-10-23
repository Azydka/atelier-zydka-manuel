# -*- coding: utf-8 -*-
"""
Générateur de teaser PDF — Manuscript Studio by Atelier Zydka

Version V2.2 :
- lit le titre depuis config.json ;
- lit le sous-titre depuis config.json ;
- lit l'auteur depuis config.json ;
- lit la marque depuis config.json ;
- lit l'année depuis config.json ;
- lit le nom du fichier teaser depuis config.json ;
- lit les couleurs principales depuis config.json.

Point d'entrée : build_teaser_pdf(texte, config, chemin_pdf).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from .parser import parse_manuscript
from .text import squash_spaces


PAGE_WIDTH, PAGE_HEIGHT = A5


@dataclass(frozen=True)
class TeaserStyle:
    project_title: str
    book_title: str
    book_subtitle: str
    author_name: str
    brand_name: str
    year: str
    background: HexColor
    text: HexColor
    accent: HexColor
    muted: HexColor

    @classmethod
    def from_config(cls, config: dict) -> "TeaserStyle":
        theme = config.get("theme", {})
        return cls(
            project_title=config.get("project_title", "Manuscript Studio by Atelier Zydka"),
            book_title=config.get("book_title", "Manuscrit de démonstration"),
            book_subtitle=config.get("book_subtitle", "Transformer un manuscrit brut en pack éditorial complet"),
            author_name=config.get("author_name", "Atelier Zydka"),
            brand_name=config.get("brand_name", "Atelier Zydka"),
            year=config.get("year", "2026"),
            background=HexColor(theme.get("background", "#090909")),
            text=HexColor(theme.get("text", "#F4F1EB")),
            accent=HexColor(theme.get("accent", "#C79A3B")),
            muted=HexColor(theme.get("muted", "#96928A")),
        )


def extract_headings_and_paragraphs(text: str) -> tuple[list[str], list[str]]:
    """Chapitres et paragraphes d'extrait, issus du parser commun (comme le PDF principal)."""
    chapters = parse_manuscript(text)

    headings = [squash_spaces(chapter.title) for chapter in chapters if chapter.title.strip()]
    paragraphs = [
        squash_spaces(block.text)
        for chapter in chapters
        for block in chapter.blocks
        if block.type == "paragraph" and len(squash_spaces(block.text)) >= 60
    ]

    return headings, paragraphs


def wrap_text(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = word if not current else f"{current} {word}"

        if stringWidth(test, font_name, font_size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_page_background(pdf: canvas.Canvas, style: TeaserStyle) -> None:
    pdf.setFillColor(style.background)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    pdf.setStrokeColor(style.accent)
    pdf.setLineWidth(1.2)
    pdf.rect(18, 18, PAGE_WIDTH - 36, PAGE_HEIGHT - 36, fill=0, stroke=1)

    pdf.setFillColor(style.accent)
    pdf.rect(28, PAGE_HEIGHT - 32, 90, 4, fill=1, stroke=0)


def draw_footer(pdf: canvas.Canvas, style: TeaserStyle, page_number: int) -> None:
    pdf.setFillColor(style.muted)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(28, 22, style.brand_name)
    pdf.drawRightString(PAGE_WIDTH - 28, 22, str(page_number))


def draw_cover_page(pdf: canvas.Canvas, style: TeaserStyle) -> None:
    draw_page_background(pdf, style)

    pdf.setFillColor(style.muted)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(28, PAGE_HEIGHT - 50, style.project_title.upper())

    pdf.setFillColor(style.text)
    pdf.setFont("Helvetica-Bold", 24)

    title_lines = wrap_text(style.book_title, "Helvetica-Bold", 24, PAGE_WIDTH - 56)
    y = PAGE_HEIGHT - 95

    for line in title_lines:
        pdf.drawString(28, y, line)
        y -= 28

    pdf.setFillColor(style.accent)
    pdf.rect(28, y - 6, 70, 3, fill=1, stroke=0)

    y -= 28

    pdf.setFillColor(style.text)
    pdf.setFont("Helvetica", 12)

    subtitle_lines = wrap_text(style.book_subtitle, "Helvetica", 12, PAGE_WIDTH - 56)
    for line in subtitle_lines:
        pdf.drawString(28, y, line)
        y -= 16

    pdf.setFillColor(style.muted)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(28, 72, f"Auteur : {style.author_name}")
    pdf.drawString(28, 56, f"Marque : {style.brand_name}")
    pdf.drawString(28, 40, f"Année : {style.year}")

    pdf.setFillColor(style.text)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawRightString(PAGE_WIDTH - 28, 40, "Teaser PDF")

    draw_footer(pdf, style, 1)
    pdf.showPage()


def draw_overview_page(pdf: canvas.Canvas, style: TeaserStyle, headings: list[str]) -> None:
    draw_page_background(pdf, style)

    pdf.setFillColor(style.text)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(28, PAGE_HEIGHT - 52, "Ce que contient cette démo")

    pdf.setFillColor(style.muted)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(28, PAGE_HEIGHT - 70, "Aperçu de la structure détectée dans le manuscrit.")

    y = PAGE_HEIGHT - 98

    pdf.setFont("Helvetica", 10)
    for index, heading in enumerate(headings[:8], start=1):
        if y < 50:
            break

        pdf.setFillColor(style.accent)
        pdf.drawString(28, y, f"{index:02d}")

        pdf.setFillColor(style.text)
        wrapped = wrap_text(heading, "Helvetica", 10, PAGE_WIDTH - 70)

        first_line = True
        for line in wrapped:
            x = 48 if first_line else 52
            pdf.drawString(x, y, line)
            y -= 14
            first_line = False

        y -= 6

    draw_footer(pdf, style, 2)
    pdf.showPage()


def draw_excerpt_page(pdf: canvas.Canvas, style: TeaserStyle, paragraphs: list[str]) -> None:
    draw_page_background(pdf, style)

    pdf.setFillColor(style.text)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(28, PAGE_HEIGHT - 52, "Extrait")

    pdf.setFillColor(style.muted)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(28, PAGE_HEIGHT - 70, "Quelques paragraphes issus du manuscrit de démonstration.")

    y = PAGE_HEIGHT - 100
    pdf.setFont("Helvetica", 9.5)

    for paragraph in paragraphs[:3]:
        wrapped = wrap_text(paragraph, "Helvetica", 9.5, PAGE_WIDTH - 56)

        for line in wrapped:
            if y < 45:
                break

            pdf.setFillColor(style.text)
            pdf.drawString(28, y, line)
            y -= 12

        y -= 10

        if y < 45:
            break

    draw_footer(pdf, style, 3)
    pdf.showPage()


def build_teaser_pdf(manuscript_text: str, config: dict, output_path: Path) -> Path:
    """Génère le teaser PDF (couverture, structure, extrait) et renvoie son chemin."""
    style = TeaserStyle.from_config(config)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    headings, paragraphs = extract_headings_and_paragraphs(manuscript_text)

    pdf = canvas.Canvas(str(output_path), pagesize=A5)
    pdf.setTitle(f"{style.book_title} — Teaser")
    pdf.setAuthor(style.author_name)
    pdf.setSubject(style.book_subtitle)
    pdf.setCreator(style.brand_name)

    draw_cover_page(pdf, style)
    draw_overview_page(pdf, style, headings)
    draw_excerpt_page(pdf, style, paragraphs)

    pdf.save()

    return output_path
