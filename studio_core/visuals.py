# -*- coding: utf-8 -*-
"""
Générateur de visuels réseaux — Manuscript Studio by Atelier Zydka

Point d'entrée : build_visuals(fichier_citations, dossier_sortie, config).
- lit la marque depuis config.json ;
- lit la baseline depuis config.json ;
- lit les couleurs depuis config.json ;
- génère des cartes carrées et story.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .errors import StudioError
from .text import clean_quote
from .workspace import FONTS_DIR


MAX_CITATIONS = 12


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


@dataclass(frozen=True)
class VisualStyle:
    brand_name: str
    baseline: str
    book_title: str
    colors: dict

    @classmethod
    def from_config(cls, config: dict) -> "VisualStyle":
        theme = config.get("theme", {})
        return cls(
            brand_name=config.get("brand_name", "Atelier Zydka").upper(),
            baseline=config.get("baseline", "Culture · méthode · indépendance"),
            book_title=config.get("book_title", "Manuscrit de démonstration").upper(),
            colors={
                "background": hex_to_rgb(theme.get("background", "#090909"), (9, 9, 9)),
                "text": hex_to_rgb(theme.get("text", "#F4F1EB"), (244, 241, 235)),
                "muted": hex_to_rgb(theme.get("muted", "#96928A"), (150, 146, 138)),
                "accent": hex_to_rgb(theme.get("accent", "#C79A3B"), (199, 154, 59)),
                "line": (55, 55, 55),
            },
        )


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
        str(FONTS_DIR / "Inter-Regular.ttf"),
        str(FONTS_DIR / "Helvetica.ttf"),
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    bold_candidates = [
        str(FONTS_DIR / "Inter-Bold.ttf"),
        str(FONTS_DIR / "Helvetica-Bold.ttf"),
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]

    quote_font = find_font(bold_candidates, size_quote)
    meta_font = find_font(regular_candidates, size_meta)
    brand_font = find_font(bold_candidates, size_brand)

    return quote_font, meta_font, brand_font


def extract_citations(markdown: str) -> list[str]:
    citations: list[str] = []

    for line in markdown.splitlines():
        line = line.strip()

        if not line.startswith(">"):
            continue

        citation = clean_quote(line.lstrip(">").strip())

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


def draw_background(draw: ImageDraw.ImageDraw, style: VisualStyle, width: int, height: int) -> None:
    draw.rectangle((0, 0, width, height), fill=style.colors["background"])

    draw.rectangle(
        (54, 54, width - 54, height - 54),
        outline=style.colors["line"],
        width=2,
    )

    draw.rectangle(
        (84, 84, 220, 91),
        fill=style.colors["accent"],
    )

    z_color = tuple(min(255, c + 15) for c in style.colors["background"])

    draw.line((width - 260, 120, width - 120, 120), fill=z_color, width=18)
    draw.line((width - 120, 120, width - 260, 260), fill=z_color, width=18)
    draw.line((width - 260, 260, width - 120, 260), fill=z_color, width=18)


def draw_card(quote: str, index: int, variant: str, settings: dict, style: VisualStyle) -> Image.Image:
    width, height = settings["size"]

    image = Image.new("RGB", (width, height), style.colors["background"])
    draw = ImageDraw.Draw(image)

    draw_background(draw, style, width, height)

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
            str(FONTS_DIR / "Inter-Bold.ttf"),
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ],
        110 if variant == "square" else 130,
    )

    draw.text(
        (quote_x, quote_y - 105),
        "“",
        fill=style.colors["accent"],
        font=mark_font,
    )

    y = quote_y

    for line in lines:
        draw.text(
            (quote_x, y),
            line,
            fill=style.colors["text"],
            font=quote_font,
        )
        y += text_height(draw, line, quote_font) + line_gap

    line_y = y + 46

    draw.rectangle(
        (quote_x, line_y, quote_x + 120, line_y + 4),
        fill=style.colors["accent"],
    )

    draw.text(
        (quote_x, line_y + 30),
        style.book_title,
        fill=style.colors["muted"],
        font=meta_font,
    )

    number = f"{index:02d}"
    number_width = text_width(draw, number, meta_font)

    draw.text(
        (width - settings["margin_x"] - number_width, line_y + 30),
        number,
        fill=style.colors["muted"],
        font=meta_font,
    )

    brand_width = text_width(draw, style.brand_name, brand_font)

    draw.text(
        ((width - brand_width) / 2, height - 125),
        style.brand_name,
        fill=style.colors["text"],
        font=brand_font,
    )

    baseline_width = text_width(draw, style.baseline, meta_font)

    draw.text(
        ((width - baseline_width) / 2, height - 78),
        style.baseline,
        fill=style.colors["muted"],
        font=meta_font,
    )

    return image


def generate_visuals(citations: list[str], output_dir: Path, style: VisualStyle) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []

    for variant, settings in FORMATS.items():
        folder = output_dir / settings["folder"]

        if folder.exists():
            for old_file in folder.glob("*.png"):
                old_file.unlink()

        folder.mkdir(parents=True, exist_ok=True)

        for index, quote in enumerate(citations, start=1):
            image = draw_card(quote, index, variant, settings, style)
            output = folder / f"citation_{index:02d}_{variant}.png"
            image.save(output, quality=95)
            produced.append(output)

    return produced


def build_visuals(citations_file: Path, output_dir: Path, config: dict) -> list[Path]:
    """Génère les cartes carrées et story à partir du fichier de citations."""
    citations_file = Path(citations_file)
    if not citations_file.exists():
        raise StudioError(f"Fichier de citations introuvable : {citations_file}")

    citations = extract_citations(citations_file.read_text(encoding="utf-8"))
    if not citations:
        raise StudioError("Aucune citation trouvée.")

    return generate_visuals(citations, output_dir, VisualStyle.from_config(config))
