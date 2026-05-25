# -*- coding: utf-8 -*-
"""
Générateur de visuels réseaux — Manuscript Studio by Atelier Zydka

Version V2.2 :
- lit la marque depuis config.json ;
- lit la baseline depuis config.json ;
- lit les couleurs depuis config.json ;
- génère des cartes carrées et story.
"""

from __future__ import annotations

import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from config_utils import load_config


CONFIG = load_config()

INPUT_FILE = Path("exports/reseaux/citations/citations_extraites.md")
OUTPUT_DIR = Path("exports/reseaux/cartes")

MAX_CITATIONS = 12

BRAND_NAME = CONFIG.get("brand_name", "Atelier Zydka").upper()
BASELINE = CONFIG.get("baseline", "Culture · méthode · indépendance")
BOOK_TITLE = CONFIG.get("book_title", "Manuscrit de démonstration").upper()
THEME = CONFIG.get("theme", {})


def hex_to_rgb(value: str, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    if not isinstance(value, str):
        return fallback

    value = value.strip().lstrip("#")

    if len(value) != 6:
        return fallback

    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return fallback


COLORS = {
    "background": hex_to_rgb(THEME.get("background", "#090909"), (9, 9, 9)),
    "text": hex_to_rgb(THEME.get("text", "#F4F1EB"), (244, 241, 235)),
    "muted": hex_to_rgb(THEME.get("muted", "#96928A"), (150, 146, 138)),
    "accent": hex_to_rgb(THEME.get("accent", "#C79A3B"), (199, 154, 59)),
    "line": (55, 55, 55),
}


FORMATS = {
    "square": {
        "size": (1080, 1080),
        "folder": "square",
        "font_quote": 58,
        "font_quote_small": 48,
        "font_meta": 30,
        "font_brand": 34,
        "margin_x": 110,
        "quote_box_height": 620,
    },
    "story": {
        "size": (1080, 1920),
        "folder": "story",
        "font_quote": 70,
        "font_quote_small": 58,
        "font_meta": 34,
        "font_brand": 38,
        "margin_x": 105,
        "quote_box_height": 900,
    },
}


def find_font(candidates: list[str], size: int):
    for path in candidates:
        font_path = Path(path)
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)

    return ImageFont.load_default()


def get_fonts(size_quote: int, size_meta: int, size_brand: int):
    regular_candidates = [
        "fonts/Inter-Regular.ttf",
        "fonts/Helvetica.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    bold_candidates = [
        "fonts/Inter-Bold.ttf",
        "fonts/Helvetica-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]

    quote_font = find_font(bold_candidates, size_quote)
    meta_font = find_font(regular_candidates, size_meta)
    brand_font = find_font(bold_candidates, size_brand)

    return quote_font, meta_font, brand_font


def clean_text(text: str) -> str:
    text = text.replace("“", "«")
    text = text.replace("”", "»")
    text = text.strip()
    return re.sub(r"\s+", " ", text)


def extract_citations(markdown: str) -> list[str]:
    citations: list[str] = []

    for line in markdown.splitlines():
        line = line.strip()

        if not line.startswith(">"):
            continue

        citation = clean_text(line.lstrip(">").strip())

        if citation:
            citations.append(citation)

    return citations[:MAX_CITATIONS]


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = word if not current else f"{current} {word}"

        if text_width(draw, test, font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def fit_quote(draw, quote: str, max_width: int, max_height: int, base_size: int, small_size: int):
    quote_font, _, _ = get_fonts(base_size, 30, 34)
    lines = wrap_text(draw, quote, quote_font, max_width)
    line_gap = int(base_size * 0.26)
    total_height = sum(text_height(draw, line, quote_font) for line in lines) + line_gap * (len(lines) - 1)

    if total_height <= max_height and len(lines) <= 8:
        return quote_font, lines, line_gap

    quote_font, _, _ = get_fonts(small_size, 30, 34)
    lines = wrap_text(draw, quote, quote_font, max_width)
    line_gap = int(small_size * 0.26)

    return quote_font, lines, line_gap


def draw_background(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    draw.rectangle((0, 0, width, height), fill=COLORS["background"])

    draw.rectangle(
        (54, 54, width - 54, height - 54),
        outline=COLORS["line"],
        width=2,
    )

    draw.rectangle(
        (84, 84, 220, 91),
        fill=COLORS["accent"],
    )

    z_color = tuple(min(255, c + 15) for c in COLORS["background"])

    draw.line((width - 260, 120, width - 120, 120), fill=z_color, width=18)
    draw.line((width - 120, 120, width - 260, 260), fill=z_color, width=18)
    draw.line((width - 260, 260, width - 120, 260), fill=z_color, width=18)


def draw_card(quote: str, index: int, variant: str, settings: dict) -> Image.Image:
    width, height = settings["size"]

    image = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(image)

    draw_background(draw, width, height)

    _, meta_font, brand_font = get_fonts(
        settings["font_quote"],
        settings["font_meta"],
        settings["font_brand"],
    )

    max_width = width - (settings["margin_x"] * 2)
    max_height = settings["quote_box_height"]

    quote_font, lines, line_gap = fit_quote(
        draw,
        quote,
        max_width=max_width,
        max_height=max_height,
        base_size=settings["font_quote"],
        small_size=settings["font_quote_small"],
    )

    total_height = sum(text_height(draw, line, quote_font) for line in lines) + line_gap * (len(lines) - 1)

    if variant == "square":
        quote_y = int((height - total_height) / 2) - 20
    else:
        quote_y = int((height - total_height) / 2) - 70

    quote_x = settings["margin_x"]

    mark_font = find_font(
        [
            "fonts/Inter-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ],
        110 if variant == "square" else 130,
    )

    draw.text(
        (quote_x, quote_y - 105),
        "“",
        fill=COLORS["accent"],
        font=mark_font,
    )

    y = quote_y

    for line in lines:
        draw.text(
            (quote_x, y),
            line,
            fill=COLORS["text"],
            font=quote_font,
        )
        y += text_height(draw, line, quote_font) + line_gap

    line_y = y + 46

    draw.rectangle(
        (quote_x, line_y, quote_x + 120, line_y + 4),
        fill=COLORS["accent"],
    )

    draw.text(
        (quote_x, line_y + 30),
        BOOK_TITLE,
        fill=COLORS["muted"],
        font=meta_font,
    )

    number = f"{index:02d}"
    number_width = text_width(draw, number, meta_font)

    draw.text(
        (width - settings["margin_x"] - number_width, line_y + 30),
        number,
        fill=COLORS["muted"],
        font=meta_font,
    )

    brand_width = text_width(draw, BRAND_NAME, brand_font)

    draw.text(
        ((width - brand_width) / 2, height - 125),
        BRAND_NAME,
        fill=COLORS["text"],
        font=brand_font,
    )

    baseline_width = text_width(draw, BASELINE, meta_font)

    draw.text(
        ((width - baseline_width) / 2, height - 78),
        BASELINE,
        fill=COLORS["muted"],
        font=meta_font,
    )

    return image


def generate_visuals(citations: list[str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for variant, settings in FORMATS.items():
        folder = OUTPUT_DIR / settings["folder"]

        if folder.exists():
            for old_file in folder.glob("*.png"):
                old_file.unlink()

        folder.mkdir(parents=True, exist_ok=True)

        for index, quote in enumerate(citations, start=1):
            image = draw_card(quote, index, variant, settings)
            output = folder / f"citation_{index:02d}_{variant}.png"
            image.save(output, quality=95)


def main() -> int:
    if not INPUT_FILE.exists():
        print(f"Fichier introuvable : {INPUT_FILE}")
        return 1

    markdown = INPUT_FILE.read_text(encoding="utf-8")
    citations = extract_citations(markdown)

    if not citations:
        print("Aucune citation trouvée.")
        return 1

    generate_visuals(citations)

    print(f"Visuels générés dans : {OUTPUT_DIR}")
    print(f"Citations utilisées : {min(len(citations), MAX_CITATIONS)}")
    print("Formats : carré + story")
    print(f"Marque : {BRAND_NAME}")
    print(f"Baseline : {BASELINE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
