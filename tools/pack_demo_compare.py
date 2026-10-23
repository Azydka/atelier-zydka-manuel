# -*- coding: utf-8 -*-
"""
Avant/après du pack démo — Manuscript Studio by Atelier Zydka

Outil de travail pour les changements de rendu (utilisable par Claude,
Codex/ChatGPT ou à la main). Fonctionne sous Windows, macOS et Linux.

1. AVANT de modifier le code :
       python tools/pack_demo_compare.py render avant --pages 1,2,4,9
2. APRÈS la modification :
       python tools/pack_demo_compare.py render apres --pages 1,2,4,9
       python tools/pack_demo_compare.py montage avant apres avant_apres.png
3. Écarts avec la référence de test (tests/reference/demo.json) :
       python tools/pack_demo_compare.py compare

Les dossiers sont créés dans le dossier temporaire du système, sauf si on
donne un chemin absolu. Rien n'est écrit dans le dépôt.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

WORK_DIR = Path(tempfile.gettempdir()) / "manuscript-studio-compare"


def resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else WORK_DIR / p


def build_demo(target: Path) -> Path:
    """Génère le pack démo dans target/projects et renvoie le dossier du projet."""
    import studio_core

    projects = target / "projects"
    if projects.exists():
        import shutil

        shutil.rmtree(projects)
    project = studio_core.create_demo_project(projects)
    studio_core.build_archive(project)
    return project.root


def render(name: str, pages: list[int], scale: float) -> None:
    import pypdfium2 as pdfium

    target = resolve(name)
    project_dir = build_demo(target)
    config = json.loads((project_dir / "config.json").read_text(encoding="utf-8"))
    pdf_path = project_dir / "exports" / "pdf" / config["output_pdf_name"]

    pdf = pdfium.PdfDocument(str(pdf_path))
    print(f"PDF : {pdf_path} ({len(pdf)} pages)")
    for number in pages:
        if number < 1 or number > len(pdf):
            print(f"  page {number} absente, ignorée")
            continue
        image = pdf[number - 1].render(scale=scale).to_pil()
        out = target / f"page_{number:02d}.png"
        image.save(out)
        print(f"  {out}")


def montage(before: str, after: str, output: str) -> None:
    from PIL import Image, ImageDraw

    before_dir, after_dir = resolve(before), resolve(after)
    names = sorted(p.name for p in before_dir.glob("page_*.png") if (after_dir / p.name).exists())
    if not names:
        raise SystemExit("Aucune page commune entre les deux dossiers.")

    pairs = [(Image.open(before_dir / n), Image.open(after_dir / n)) for n in names]
    w, h = pairs[0][0].size
    pad, header = 20, 40
    out = Image.new("RGB", (2 * w + 3 * pad, header + len(pairs) * (h + pad) + pad), "white")
    draw = ImageDraw.Draw(out)
    draw.text((pad, 12), "AVANT", fill="black")
    draw.text((2 * pad + w, 12), "APRÈS", fill="black")
    for row, (a, b) in enumerate(pairs):
        y = header + row * (h + pad)
        out.paste(a, (pad, y))
        out.paste(b, (2 * pad + w, y))
        draw.text((pad, y - 14), names[row], fill="gray")

    output_path = resolve(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path)
    print(f"Montage : {output_path}")


def compare() -> int:
    from tests.snapshot import REFERENCE_PATH, build_snapshot

    reference = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        snapshot, duration, written = build_snapshot(Path(tmp))

    print(f"Génération : {duration:.1f} s")
    differences = 0
    if written:
        differences += 1
        print(f"ÉCRITURES DANS LE DOSSIER DU CODE : {written}")
    for key, expected in reference.items():
        actual = snapshot.get(key)
        if key in ("book_pdf", "teaser_pdf"):
            if actual["pages"] != expected["pages"]:
                differences += 1
                print(f"{key} : {expected['pages']} → {actual['pages']} pages")
            for i, (a, b) in enumerate(zip(expected["text"], actual["text"]), start=1):
                if a != b:
                    differences += 1
                    print(f"{key} page {i} changée")
        elif actual != expected:
            differences += 1
            print(f"{key} : {expected} → {actual}")

    print("Identique à la référence." if not differences else f"{differences} écart(s) avec la référence.")
    return 1 if differences else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_render = sub.add_parser("render", help="génère la démo et rend des pages du PDF en PNG")
    p_render.add_argument("name")
    p_render.add_argument("--pages", default="1,2,9")
    p_render.add_argument("--scale", type=float, default=1.2)

    p_montage = sub.add_parser("montage", help="assemble avant/après côte à côte")
    p_montage.add_argument("before")
    p_montage.add_argument("after")
    p_montage.add_argument("output")

    sub.add_parser("compare", help="écarts entre la démo actuelle et tests/reference/demo.json")

    args = parser.parse_args()
    if args.command == "render":
        render(args.name, [int(p) for p in args.pages.split(",")], args.scale)
        return 0
    if args.command == "montage":
        montage(args.before, args.after, args.output)
        return 0
    return compare()


if __name__ == "__main__":
    raise SystemExit(main())
