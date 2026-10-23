# -*- coding: utf-8 -*-
"""
Instantané du pack démo — Manuscript Studio by Atelier Zydka

Génère le pack démo (make.py archive) depuis une copie isolée du dépôt,
avec une racine de projets temporaire, et résume ce qui est produit
(chapitres, pages et texte des PDF, fichiers de la release, ZIP).
Vérifie aussi que rien n'est écrit dans le dossier du code.

Les tests comparent cet instantané à tests/reference/demo.json.
Pour régénérer la référence après un changement de rendu VOLONTAIRE :

    python -m tests.snapshot --update
"""

from __future__ import annotations

import json
import os
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


def run_archive(workdir: Path, projects_root: Path) -> float:
    """Lance make.py archive (projet démo créé à la volée). Renvoie la durée."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "make.py", "--projects-root", str(projects_root), "archive"],
        cwd=workdir,
        env=env,
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


def parser_chapter_count(project_dir: Path) -> int:
    from studio_core.parser import parse_manuscript

    return len(parse_manuscript((project_dir / "manuscrit.txt").read_text(encoding="utf-8")))


def files_under(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def collect(project_dir: Path) -> dict:
    config = json.loads((project_dir / "config.json").read_text(encoding="utf-8"))
    exports = project_dir / "exports"
    release_dir = exports / "release" / config["release_name"]
    zip_path = exports / config["zip_name"]

    book = pdf_summary(exports / "pdf" / config["output_pdf_name"])
    teaser = pdf_summary(exports / "pdf" / config["teaser_pdf_name"])
    reports = exports / "rapports"

    with zipfile.ZipFile(zip_path) as zf:
        zip_names = sorted(name.replace("\\", "/") for name in zf.namelist())

    return {
        "chapters": {
            "parser_manuscrit": parser_chapter_count(project_dir),
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


def build_snapshot(tmp_dir: Path) -> tuple[dict, float, list[str]]:
    """Renvoie (instantané, durée, fichiers créés ou modifiés dans le dossier du code)."""
    workdir = copy_repo(tmp_dir / "repo")
    before = {p: p.stat().st_mtime_ns for p in workdir.rglob("*") if p.is_file()}
    duration = run_archive(workdir, tmp_dir / "projects")
    after = {p: p.stat().st_mtime_ns for p in workdir.rglob("*") if p.is_file()}
    written = sorted(str(p.relative_to(workdir)) for p in after if before.get(p) != after[p])
    return collect(tmp_dir / "projects" / "demo"), duration, written


def main() -> int:
    import tempfile

    if "--update" not in sys.argv:
        print(__doc__)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        snapshot, duration, _ = build_snapshot(Path(tmp))

    REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REFERENCE_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Référence mise à jour : {REFERENCE_PATH} (génération : {duration:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
