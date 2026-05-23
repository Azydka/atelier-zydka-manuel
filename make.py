# -*- coding: utf-8 -*-
"""
Make script — Atelier Zydka Manuel

Commandes :
python3 make.py check      # vérifie le manuscrit
python3 make.py pdf        # génère le PDF principal
python3 make.py structure  # génère le rapport éditorial
python3 make.py marketing  # extrait les citations marketing
python3 make.py teaser     # génère le teaser PDF
python3 make.py visuals    # génère les visuels réseaux
python3 make.py all        # lance tout le pipeline
python3 make.py release    # crée un dossier de distribution propre
python3 make.py archive    # crée une archive ZIP transmissible
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST_ROOT = ROOT / "dist"
RELEASE_DIR = DIST_ROOT / "atelier-zydka-manuel-release"
ZIP_PATH = DIST_ROOT / "atelier-zydka-manuel-release.zip"


def run(command: list[str]) -> int:
    print("")
    print("→ " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    return result.returncode


def copy_file(src: Path, dest: Path) -> None:
    if not src.exists():
        print(f"Attention : fichier absent, non copié : {src}")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"Copié : {src.relative_to(ROOT)} → {dest.relative_to(ROOT)}")


def copy_dir(src: Path, dest: Path) -> None:
    if not src.exists():
        print(f"Attention : dossier absent, non copié : {src}")
        return

    if dest.exists():
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"),
    )

    print(f"Copié : {src.relative_to(ROOT)} → {dest.relative_to(ROOT)}")


def check() -> int:
    code = run([sys.executable, "-m", "py_compile", "verifier_manuscrit.py"])
    if code != 0:
        return code

    return run([sys.executable, "verifier_manuscrit.py"])


def pdf() -> int:
    code = run([sys.executable, "-m", "py_compile", "parser_manuscrit.py"])
    if code != 0:
        return code

    code = run([sys.executable, "-m", "py_compile", "generer_livre_manuel_presence.py"])
    if code != 0:
        return code

    return run([sys.executable, "generer_livre_manuel_presence.py"])


def structure() -> int:
    code = run([sys.executable, "-m", "py_compile", "rapport_structure.py"])
    if code != 0:
        return code

    return run([sys.executable, "rapport_structure.py"])


def marketing() -> int:
    code = run([sys.executable, "-m", "py_compile", "generer_exports_marketing.py"])
    if code != 0:
        return code

    return run([sys.executable, "generer_exports_marketing.py"])


def teaser() -> int:
    code = run([sys.executable, "-m", "py_compile", "generer_teaser_pdf.py"])
    if code != 0:
        return code

    return run([sys.executable, "generer_teaser_pdf.py"])


def visuals() -> int:
    code = run([sys.executable, "-m", "py_compile", "generer_visuels_reseaux.py"])
    if code != 0:
        return code

    return run([sys.executable, "generer_visuels_reseaux.py"])


def all_steps() -> int:
    code = check()
    if code != 0:
        print("")
        print("Arrêt : le check a détecté une erreur bloquante.")
        return code

    for step in (pdf, structure, marketing, teaser, visuals):
        code = step()
        if code != 0:
            return code

    return 0


def release() -> int:
    code = all_steps()
    if code != 0:
        return code

    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    copy_file(ROOT / "README.md", RELEASE_DIR / "README.md")
    copy_file(ROOT / "RELEASE_NOTES.md", RELEASE_DIR / "RELEASE_NOTES.md")

    copy_file(
        ROOT / "manuelsortie" / "manuel-de-presence-atelier-zydka.pdf",
        RELEASE_DIR / "pdf" / "manuel-de-presence-atelier-zydka.pdf",
    )

    copy_file(
        ROOT / "exports" / "pdf" / "teaser-manuel-presence.pdf",
        RELEASE_DIR / "pdf" / "teaser-manuel-presence.pdf",
    )

    copy_file(
        ROOT / "exports" / "rapports" / "rapport_structure.md",
        RELEASE_DIR / "rapports" / "rapport_structure.md",
    )

    copy_file(
        ROOT / "exports" / "reseaux" / "citations" / "citations_extraites.md",
        RELEASE_DIR / "reseaux" / "citations_extraites.md",
    )

    copy_dir(
        ROOT / "exports" / "reseaux" / "cartes",
        RELEASE_DIR / "reseaux" / "cartes",
    )

    print("")
    print("Release générée :")
    print(RELEASE_DIR)

    return 0


def archive() -> int:
    code = release()
    if code != 0:
        return code

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for path in RELEASE_DIR.rglob("*"):
            if ".DS_Store" in path.parts:
                continue

            if "__pycache__" in path.parts:
                continue

            if path.is_file():
                zipf.write(path, path.relative_to(DIST_ROOT))

    print("")
    print("Archive ZIP générée :")
    print(ZIP_PATH)

    return 0


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "check":
        return check()

    if command == "pdf":
        return pdf()

    if command == "structure":
        return structure()

    if command == "marketing":
        return marketing()

    if command == "teaser":
        return teaser()

    if command == "visuals":
        return visuals()

    if command == "all":
        return all_steps()

    if command == "release":
        return release()

    if command == "archive":
        return archive()

    print("Commande inconnue.")
    print("Commandes disponibles : check, pdf, structure, marketing, teaser, visuals, all, release, archive")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
