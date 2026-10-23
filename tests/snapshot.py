# -*- coding: utf-8 -*-
"""
Instantané du pack démo — Manuscript Studio by Atelier Zydka

Génère le pack démo dans une copie isolée du dépôt et résume ce qui est
produit (chapitres, pages et texte des PDF, fichiers de la release, ZIP).

Les tests comparent cet instantané à tests/reference/demo.json.
Pour régénérer la référence après un changement de rendu VOLONTAIRE :

    python -m tests.snapshot --update
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_PATH = Path(__file__).resolve().parent / "reference" / "demo.json"

# Dossiers jamais copiés dans l'espace de test : sorties, contenus privés, Git.
IGNORED = shutil.ignore_patterns(
    ".git", ".github", "__pycache__", ".pytest_cache", "tests",
    "exports", "manuelsortie", "dist", "private", "backups", "Archives dev",
)


def copy_repo(dest: Path) -> Path:
    shutil.copytree(REPO_ROOT, dest, ignore=IGNORED)
    return dest


def run_archive(workdir: Path) -> float:
    """Restaure la démo publique puis lance make.py archive. Renvoie la durée."""
    subprocess.run([sys.executable, "restore_demo.py"], cwd=workdir, check=True, capture_output=True)
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "make.py", "archive"],
        cwd=workdir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    duration = time.perf_counter() - start
    if result.returncode != 0:
        raise RuntimeError(f"make.py archive a échoué :\n{result.stdout}\n{result.stderr}")
    return duration


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


def pdf_summary(path: Path) -> dict:
    reader = PdfReader(str(path))
    return {
        "pages": len(reader.pages),
        "text": [normalize_text(page.extract_text() or "") for page in reader.pages],
    }


def report_count(path: Path, label: str) -> int:
    match = re.search(re.escape(label) + r"\s*:\s*\*\*(\d+)\*\*", path.read_text(encoding="utf-8"))
    if not match:
        raise AssertionError(f"« {label} » introuvable dans {path}")
    return int(match.group(1))


def toc_entries(toc_text: str) -> list[str]:
    """Entrées du sommaire PDF : une ligne « NN » suivie du titre."""
    lines = toc_text.split("\n")
    return [lines[i + 1] for i, line in enumerate(lines[:-1]) if re.fullmatch(r"\d{2}", line.strip())]


def parser_chapter_count(workdir: Path) -> int:
    code = (
        "import sys; sys.path.insert(0, '.');"
        "from parser_manuscrit import parse_manuscript;"
        "print(len(parse_manuscript(open('manuscrit_beatmakers.txt', encoding='utf-8').read())))"
    )
    out = subprocess.run([sys.executable, "-c", code], cwd=workdir, check=True, capture_output=True, text=True)
    return int(out.stdout.strip())


def files_under(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def collect(workdir: Path) -> dict:
    config = json.loads((workdir / "config.json").read_text(encoding="utf-8"))
    dist = workdir / "dist"
    release_dir = dist / config["release_name"]
    zip_path = dist / config["zip_name"]

    book = pdf_summary(workdir / "manuelsortie" / config["output_pdf_name"])
    teaser = pdf_summary(workdir / "exports" / "pdf" / config["teaser_pdf_name"])
    reports = workdir / "exports" / "rapports"

    with zipfile.ZipFile(zip_path) as zf:
        zip_names = sorted(name.replace("\\", "/") for name in zf.namelist())

    return {
        "chapters": {
            "parser_manuscrit": parser_chapter_count(workdir),
            "rapport_structure": report_count(reports / "rapport_structure.md", "Chapitres détectés"),
            "rapport_qualite": report_count(reports / "rapport_qualite.md", "Nombre de chapitres / sections détectés"),
            "sommaire_pdf": len(toc_entries(book["text"][1])),
            "teaser": len(toc_entries(teaser["text"][1])),
        },
        "book_pdf": book,
        "teaser_pdf": teaser,
        "release_files": files_under(release_dir),
        "zip_entries": zip_names,
    }


def build_snapshot(tmp_dir: Path) -> tuple[dict, float]:
    workdir = copy_repo(tmp_dir / "repo")
    duration = run_archive(workdir)
    return collect(workdir), duration


def main() -> int:
    import tempfile

    if "--update" not in sys.argv:
        print(__doc__)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        snapshot, duration = build_snapshot(Path(tmp))

    REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REFERENCE_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Référence mise à jour : {REFERENCE_PATH} (génération : {duration:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
