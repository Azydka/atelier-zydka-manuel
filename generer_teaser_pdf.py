# -*- coding: utf-8 -*-
"""
Générateur de teaser PDF — Atelier Zydka Manuel

Version V2.2 :
- lit le titre depuis config.json ;
- lit le sous-titre depuis config.json ;
- lit l'auteur depuis config.json ;
- lit la marque depuis config.json ;
- lit l'année depuis config.json ;
- lit le nom du fichier teaser depuis config.json ;
- lit les couleurs principales depuis config.json.

Sortie :
exports/pdf/<teaser_pdf_name>
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from config_utils import load_config


ROOT = Path(__file__).resolve().parent
MANUSCRIPT_PATH = ROOT / "manuscrit_beatmakers.txt"
OUTPUT_DIR = ROOT / "exports" / "pdf"

CONFIG = load_config()

PROJECT_TITLE = CONFIG.get("project_title", "Atelier Zydka Manuel")
BOOK_TITLE = CONFIG.get("book_title", "Manuscrit de démonstration")
BOOK_SUBTITLE = CONFIG.get("book_subtitle", "Transformer un manuscrit brut en pack éditorial complet")
AUTHOR_NAME = CONFIG.get("author_name", "Atelier Zydka")
BRAND_NAME = CONFIG.get("brand_name", "Atelier Zydka")
YEAR = CONFIG.get("year", "2026")
TEASER_PDF_NAME = CONFIG.get("teaser_pdf_name", "teaser-manuel-presence.pdf")

THEME = CONFIG.get("theme", {})
BACKGROUND = HexColor(THEME.get("background", "#090909"))
TEXT = HexColor(THEME.get("text", "#F4F1EB"))
ACCENT = HexColor(THEME.get("accent", "#C79A3B"))
MUTED = HexColor(THEME.get("muted", "#96928A"))

PAGE_WIDTH, PAGE_HEIGHT = A5


def clean_line(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_headings_and_paragraphs(text: str) -> tuple[list[str], list[str]]:
    headings: list[str] = []
    paragraphs: list[str] = []

    for raw_line in text.splitlines():
        line = clean_line(raw_line)

        if not line:
            continue

        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            if heading:
                headings.append(heading)
            continue

        if line.startswith("- "):
            continue

        if line.startswith("```"):
            continue

        if len(line) >= 60:
            paragraphs.append(line)

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


def draw_page_background(pdf: canvas.Canvas) -> None:
    pdf.setFillColor(BACKGROUND)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    pdf.setStrokeColor(ACCENT)
    pdf.setLineWidth(1.2)
    pdf.rect(18, 18, PAGE_WIDTH - 36, PAGE_HEIGHT - 36, fill=0, stroke=1)

    pdf.setFillColor(ACCENT)
    pdf.rect(28, PAGE_HEIGHT - 32, 90, 4, fill=1, stroke=0)


def draw_footer(pdf: canvas.Canvas, page_number: int) -> None:
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(28, 22, BRAND_NAME)
    pdf.drawRightString(PAGE_WIDTH - 28, 22, str(page_number))


def draw_cover_page(pdf: canvas.Canvas) -> None:
    draw_page_background(pdf)

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(28, PAGE_HEIGHT - 50, PROJECT_TITLE.upper())

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 24)

    title_lines = wrap_text(BOOK_TITLE, "Helvetica-Bold", 24, PAGE_WIDTH - 56)
    y = PAGE_HEIGHT - 95

    for line in title_lines:
        pdf.drawString(28, y, line)
        y -= 28

    pdf.setFillColor(ACCENT)
    pdf.rect(28, y - 6, 70, 3, fill=1, stroke=0)

    y -= 28

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 12)

    subtitle_lines = wrap_text(BOOK_SUBTITLE, "Helvetica", 12, PAGE_WIDTH - 56)
    for line in subtitle_lines:
        pdf.drawString(28, y, line)
        y -= 16

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(28, 72, f"Auteur : {AUTHOR_NAME}")
    pdf.drawString(28, 56, f"Marque : {BRAND_NAME}")
    pdf.drawString(28, 40, f"Année : {YEAR}")

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawRightString(PAGE_WIDTH - 28, 40, "Teaser PDF")

    draw_footer(pdf, 1)
    pdf.showPage()


def draw_overview_page(pdf: canvas.Canvas, headings: list[str]) -> None:
    draw_page_background(pdf)

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(28, PAGE_HEIGHT - 52, "Ce que contient cette démo")

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(28, PAGE_HEIGHT - 70, "Aperçu de la structure détectée dans le manuscrit.")

    y = PAGE_HEIGHT - 98

    pdf.setFont("Helvetica", 10)
    for index, heading in enumerate(headings[:8], start=1):
        if y < 50:
            break

        pdf.setFillColor(ACCENT)
        pdf.drawString(28, y, f"{index:02d}")

        pdf.setFillColor(TEXT)
        wrapped = wrap_text(heading, "Helvetica", 10, PAGE_WIDTH - 70)

        first_line = True
        for line in wrapped:
            x = 48 if first_line else 52
            pdf.drawString(x, y, line)
            y -= 14
            first_line = False

        y -= 6

    draw_footer(pdf, 2)
    pdf.showPage()


def draw_excerpt_page(pdf: canvas.Canvas, paragraphs: list[str]) -> None:
    draw_page_background(pdf)

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(28, PAGE_HEIGHT - 52, "Extrait")

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(28, PAGE_HEIGHT - 70, "Quelques paragraphes issus du manuscrit de démonstration.")

    y = PAGE_HEIGHT - 100
    pdf.setFont("Helvetica", 9.5)

    for paragraph in paragraphs[:3]:
        wrapped = wrap_text(paragraph, "Helvetica", 9.5, PAGE_WIDTH - 56)

        for line in wrapped:
            if y < 45:
                break

            pdf.setFillColor(TEXT)
            pdf.drawString(28, y, line)
            y -= 12

        y -= 10

        if y < 45:
            break

    draw_footer(pdf, 3)
    pdf.showPage()


def main() -> int:
    if not MANUSCRIPT_PATH.exists():
        print(f"Manuscrit introuvable : {MANUSCRIPT_PATH}")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / TEASER_PDF_NAME

    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
    headings, paragraphs = extract_headings_and_paragraphs(manuscript)

    pdf = canvas.Canvas(str(output_path), pagesize=A5)
    pdf.setTitle(f"{BOOK_TITLE} — Teaser")
    pdf.setAuthor(AUTHOR_NAME)
    pdf.setSubject(BOOK_SUBTITLE)
    pdf.setCreator(BRAND_NAME)

    draw_cover_page(pdf)
    draw_overview_page(pdf, headings)
    draw_excerpt_page(pdf, paragraphs)

    pdf.save()

    print(f"Teaser PDF généré : {output_path.relative_to(ROOT)}")
    print("Version : teaser V2.2 configurable")
    print(f"Titre : {BOOK_TITLE}")
    print(f"Sous-titre : {BOOK_SUBTITLE}")
    print(f"Auteur : {AUTHOR_NAME}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
