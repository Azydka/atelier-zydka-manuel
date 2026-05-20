# -*- coding: utf-8 -*-
"""
Générateur Teaser PDF — Atelier Zydka Manuel

Génère un teaser court à partir du manuscrit et des citations marketing.

Sortie :
exports/pdf/teaser-manuel-presence.pdf
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


OUTPUT = Path("exports/pdf/teaser-manuel-presence.pdf")
CITATIONS_FILE = Path("exports/reseaux/citations/citations_extraites.md")
MANUSCRIPT = Path("manuscrit_beatmakers.txt")


PAGE_W, PAGE_H = A5

CARBON = HexColor("#111111")
PAPER = HexColor("#F4F1EA")
STEEL = HexColor("#8A8A8A")
SIGNATURE = HexColor("#B59A5B")
WHITE = HexColor("#FFFFFF")


def ty(y_mm: float) -> float:
    return PAGE_H - y_mm * mm


def clean(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def draw_page_base(c: canvas.Canvas, page_num: int, dark: bool = False):
    c.setFillColor(CARBON if dark else PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    c.setFillColor(SIGNATURE if dark else CARBON)
    c.setFont("Courier", 7)
    c.drawString(16 * mm, 10 * mm, f"{page_num:03d}")

    c.setFillColor(SIGNATURE)
    c.rect(16 * mm, 16 * mm, 9 * mm, 9 * mm, stroke=0, fill=1)

    c.setFillColor(CARBON if not dark else PAPER)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(20.5 * mm, 18.8 * mm, "Z")


def draw_wrapped(c, text: str, x_mm: float, y_mm: float, w_mm: float, font: str, size: float, leading: float, color) -> float:
    c.setFillColor(color)
    c.setFont(font, size)

    lines = simpleSplit(clean(text), font, size, w_mm * mm)
    y = y_mm

    for line in lines:
        c.drawString(x_mm * mm, ty(y), line)
        y += leading

    return y


def load_citations(limit: int = 5) -> list[str]:
    if not CITATIONS_FILE.exists():
        return []

    raw = CITATIONS_FILE.read_text(encoding="utf-8")
    quotes = []

    for line in raw.splitlines():
        if line.strip().startswith("> "):
            quote = clean(line.strip()[2:])
            if 55 <= len(quote) <= 210:
                quotes.append(quote)

    return quotes[:limit]


def get_chapters(limit: int = 9) -> list[str]:
    if not MANUSCRIPT.exists():
        return []

    raw = MANUSCRIPT.read_text(encoding="utf-8")
    chapters = []

    for line in raw.splitlines():
        line = clean(line)
        if line.startswith("# "):
            title = line[2:].strip()
            if title.lower() != "table des matières":
                chapters.append(title)

    # Fallback si les titres ne sont pas tous en markdown strict
    if len(chapters) < 5:
        possible = [
            "Le métier en 2026",
            "S’équiper sans se disperser",
            "Créer des beats vendables",
            "Organiser son catalogue comme un pro",
            "Vendre ses beats proprement",
            "Protéger ses droits sans devenir juriste",
            "Se rendre visible et trouver des clients",
            "S’ouvrir aux marchés globaux sans se perdre",
            "Plan d’action 90 jours",
        ]
        return possible[:limit]

    return chapters[:limit]


def cover(c: canvas.Canvas):
    draw_page_base(c, 1, dark=True)

    c.setFillColor(SIGNATURE)
    c.setFont("Courier", 8)
    c.drawString(16 * mm, ty(30), "TEASER PDF / ATELIER ZYDKA")

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 27)
    c.drawString(16 * mm, ty(62), "LE MANUEL")
    c.drawString(16 * mm, ty(75), "DE PRÉSENCE")

    c.setFillColor(SIGNATURE)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(16 * mm, ty(95), "Beatmaker indépendant 2027")

    draw_wrapped(
        c,
        "Un extrait court pour comprendre l’approche : organiser, protéger, vendre et rendre visible son travail sans se disperser.",
        16, 122, 105, "Helvetica", 10.5, 5.8, WHITE
    )

    c.showPage()


def promise_page(c: canvas.Canvas):
    draw_page_base(c, 2)

    c.setFillColor(SIGNATURE)
    c.setFont("Courier", 8)
    c.drawString(16 * mm, ty(28), "PROMESSE")

    draw_wrapped(
        c,
        "Ce manuel aide les beatmakers indépendants à passer d’un disque dur rempli de fichiers à un catalogue clair, vendable et défendable.",
        16, 55, 105, "Helvetica-Bold", 17, 9, CARBON
    )

    draw_wrapped(
        c,
        "L’objectif n’est pas de produire plus dans le désordre. L’objectif est de construire un système simple : fichiers propres, offres claires, droits compris, prospection suivie, visibilité régulière.",
        16, 112, 105, "Helvetica", 10.5, 6.2, CARBON
    )

    c.showPage()


def audience_page(c: canvas.Canvas):
    draw_page_base(c, 3)

    c.setFillColor(SIGNATURE)
    c.setFont("Courier", 8)
    c.drawString(16 * mm, ty(28), "POUR QUI ?")

    items = [
        "Beatmakers qui veulent vendre proprement.",
        "Producteurs qui ont trop de fichiers et pas assez de système.",
        "Artistes-producteurs qui veulent clarifier leurs droits.",
        "Créateurs qui veulent structurer leur catalogue avant de chercher plus de visibilité.",
    ]

    y = 55
    for item in items:
        c.setFillColor(SIGNATURE)
        c.rect(16 * mm, ty(y + 1) - 4 * mm, 4 * mm, 4 * mm, stroke=0, fill=1)
        y = draw_wrapped(c, item, 25, y, 95, "Helvetica-Bold", 12.5, 7.2, CARBON)
        y += 5

    c.showPage()


def quotes_page(c: canvas.Canvas):
    quotes = load_citations(5)

    draw_page_base(c, 4)

    c.setFillColor(SIGNATURE)
    c.setFont("Courier", 8)
    c.drawString(16 * mm, ty(28), "EXTRAITS")

    y = 48

    if not quotes:
        quotes = [
            "Avant de chercher plus de visibilité, rendez votre catalogue exploitable.",
            "Un beat prêt à vendre est un beat prêt à livrer.",
            "La protection commence par la traçabilité.",
        ]

    for i, quote in enumerate(quotes, start=1):
        c.setFillColor(CARBON)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(16 * mm, ty(y), f"{i:02d}")

        y = draw_wrapped(c, quote, 27, y, 92, "Helvetica", 10, 5.6, CARBON)
        y += 7

    c.showPage()


def summary_page(c: canvas.Canvas):
    chapters = get_chapters(9)

    draw_page_base(c, 5)

    c.setFillColor(SIGNATURE)
    c.setFont("Courier", 8)
    c.drawString(16 * mm, ty(28), "MINI SOMMAIRE")

    y = 48

    for i, title in enumerate(chapters, start=1):
        c.setFillColor(SIGNATURE)
        c.setFont("Courier", 8)
        c.drawString(16 * mm, ty(y), f"{i:02d}")

        y = draw_wrapped(c, title, 28, y, 92, "Helvetica-Bold", 10.8, 6.2, CARBON)
        y += 2.5

        if y > 178:
            break

    c.showPage()


def final_page(c: canvas.Canvas):
    draw_page_base(c, 6, dark=True)

    c.setFillColor(SIGNATURE)
    c.setFont("Courier", 8)
    c.drawString(16 * mm, ty(30), "APPEL À L’ACTION")

    draw_wrapped(
        c,
        "Ne cherchez pas seulement à faire plus de beats. Construisez un système qui rend vos beats trouvables, vendables et exploitables.",
        16, 62, 105, "Helvetica-Bold", 19, 9.5, WHITE
    )

    draw_wrapped(
        c,
        "Le manuel complet développe la méthode, les modèles, les checklists et les fichiers bonus pour passer à l’action.",
        16, 132, 105, "Helvetica", 10.5, 6.2, WHITE
    )

    c.setFillColor(SIGNATURE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(16 * mm, ty(178), "Atelier Zydka")

    c.showPage()


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(OUTPUT), pagesize=A5, pageCompression=0)
    c.setTitle("Teaser — Le Manuel de Présence")
    c.setAuthor("Atelier Zydka")
    c.setSubject("Teaser PDF du manuel pour beatmakers indépendants")

    cover(c)
    promise_page(c)
    audience_page(c)
    quotes_page(c)
    summary_page(c)
    final_page(c)

    c.save()

    print(f"Teaser PDF généré : {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
