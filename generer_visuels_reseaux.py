# -*- coding: utf-8 -*-
"""
Générateur de visuels réseaux — Atelier Zydka Manuel

Génère des cartes PNG à partir des citations marketing.

Sorties :
- exports/reseaux/cartes/carre/
- exports/reseaux/cartes/story/
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CITATIONS_FILE = Path("exports/reseaux/citations/citations_extraites.md")
OUTPUT_BASE = Path("exports/reseaux/cartes")

CARBON = "#111111"
PAPER = "#F4F1EA"
STEEL = "#8A8A8A"
SIGNATURE = "#B59A5B"
WHITE = "#FFFFFF"


FORMATS = {
    "carre": (1080, 1080),
    "story": (1080, 1920),
}


def clean(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("##", "")
    text = text.replace("#", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -–—:;,. ")


def load_font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass

    return ImageFont.load_default()


def load_quotes(limit: int = 12) -> list[str]:
    if not CITATIONS_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {CITATIONS_FILE}")

    raw = CITATIONS_FILE.read_text(encoding="utf-8")
    quotes = []

    banned = [
        "ce livre n’est pas",
        "ce livre n'est pas",
        "important — structure",
        "livre principal",
    ]

    for line in raw.splitlines():
        if not line.strip().startswith("> "):
            continue

        quote = clean(line.strip()[2:])
        low = quote.lower()

        if not quote:
            continue

        if any(b in low for b in banned):
            continue

        if 65 <= len(quote) <= 210:
            quotes.append(quote)

    fallback = [
        "Avant de chercher plus de visibilité, rendez votre catalogue exploitable.",
        "Un beat prêt à vendre est un beat prêt à livrer.",
        "Votre catalogue doit devenir consultable en moins de deux minutes.",
        "La protection commence par la traçabilité.",
        "L’international peut multiplier les opportunités, mais aussi les malentendus.",
    ]

    final = []
    seen = set()

    for quote in quotes + fallback:
        if quote not in seen:
            seen.add(quote)
            final.append(quote)

    return final[:limit]


def draw_wrapped_text(draw, text, box, font, fill, line_spacing=14):
    x, y, w, h = box

    avg_chars = max(18, int(w / (font.size * 0.48)))
    lines = []

    for paragraph in text.split("\n"):
        lines.extend(textwrap.wrap(paragraph, width=avg_chars))

    line_heights = []
    total_h = 0

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        total_h += lh + line_spacing

    total_h -= line_spacing
    cursor_y = y + max(0, (h - total_h) / 2)

    for line, lh in zip(lines, line_heights):
        draw.text((x, cursor_y), line, font=font, fill=fill)
        cursor_y += lh + line_spacing


def make_card(quote: str, index: int, fmt_name: str, size: tuple[int, int]):
    w, h = size
    img = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(img)

    title_font = load_font(42, bold=True)
    quote_font = load_font(56 if fmt_name == "carre" else 64, bold=True)
    small_font = load_font(28, bold=False)
    mono_font = load_font(24, bold=False)

    margin = 86 if fmt_name == "carre" else 92

    # Bloc fond haut
    draw.rectangle((0, 0, w, 190), fill=CARBON)

    # Signature
    draw.text((margin, 58), "ATELIER ZYDKA", font=mono_font, fill=SIGNATURE)
    draw.text((margin, 105), "LE MANUEL DE PRÉSENCE", font=title_font, fill=WHITE)

    # Bloc Z
    z_size = 72
    draw.rectangle((w - margin - z_size, 58, w - margin, 58 + z_size), fill=SIGNATURE)
    draw.text((w - margin - z_size + 23, 72), "Z", font=title_font, fill=CARBON)

    # Numéro
    draw.text((margin, 240), f"{index:02d}", font=small_font, fill=SIGNATURE)

    # Citation
    quote_box = (
        margin,
        300 if fmt_name == "carre" else 430,
        w - margin * 2,
        470 if fmt_name == "carre" else 820,
    )
    draw_wrapped_text(draw, quote, quote_box, quote_font, CARBON)

    # Ligne signature
    line_y = h - 180
    draw.line((margin, line_y, margin + 260, line_y), fill=SIGNATURE, width=4)

    draw.text((margin, line_y + 34), "Beatmaker indépendant 2027", font=small_font, fill=CARBON)
    draw.text((margin, line_y + 78), "Organiser. Protéger. Vendre. Être visible.", font=small_font, fill=STEEL)

    return img


def main() -> int:
    quotes = load_quotes(limit=12)

    for fmt_name, size in FORMATS.items():
        out_dir = OUTPUT_BASE / fmt_name
        out_dir.mkdir(parents=True, exist_ok=True)

        for i, quote in enumerate(quotes, start=1):
            img = make_card(quote, i, fmt_name, size)
            out_file = out_dir / f"citation_{i:02d}_{fmt_name}.png"
            img.save(out_file, "PNG")

    print(f"Visuels générés dans : {OUTPUT_BASE}")
    print(f"Citations utilisées : {len(quotes)}")
    print("Formats : carré + story")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
