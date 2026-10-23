# -*- coding: utf-8 -*-
"""
Dossier de release et archive ZIP d'un projet — Manuscript Studio

build_release() rassemble les livrables déjà générés du projet dans
exports/release/<release_name>/ ; build_zip() compresse ce dossier dans
exports/<zip_name>. Seuls les livrables du livre sont inclus.
"""

from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path

from .project import Project
from .report_quality import REPORT_NAME as QUALITY_REPORT_NAME, SCORE_NAME
from .report_structure import REPORT_NAME as STRUCTURE_REPORT_NAME

log = logging.getLogger(__name__)

# Fichiers système jamais copiés ni archivés.
IGNORED_NAMES = (".DS_Store", "__pycache__")


def _copy(src: Path, dest: Path) -> None:
    if not src.exists():
        log.warning("Livrable absent, non copié : %s", src)
        return

    dest.parent.mkdir(parents=True, exist_ok=True)

    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*IGNORED_NAMES))
    else:
        shutil.copy2(src, dest)


def release_dir(project: Project, config: dict) -> Path:
    return project.releases_dir / config["release_name"]


def release_contents(project: Project, config: dict) -> list[tuple[Path, str]]:
    """(livrable du projet, chemin relatif dans la release)."""
    return [
        (project.pdf_dir / config["output_pdf_name"], f"pdf/{config['output_pdf_name']}"),
        (project.pdf_dir / config["teaser_pdf_name"], f"pdf/{config['teaser_pdf_name']}"),
        (project.reports_dir / STRUCTURE_REPORT_NAME, f"rapports/{STRUCTURE_REPORT_NAME}"),
        (project.reports_dir / QUALITY_REPORT_NAME, f"rapports/{QUALITY_REPORT_NAME}"),
        (project.reports_dir / SCORE_NAME, f"rapports/{SCORE_NAME}"),
        (project.citations_file, "reseaux/citations_extraites.md"),
        (project.cards_dir, "reseaux/cartes"),
    ]


def build_release(project: Project, config: dict) -> Path:
    """Crée le dossier de release à partir des livrables déjà générés et renvoie son chemin."""
    target = release_dir(project, config)

    if target.exists():
        shutil.rmtree(target)

    target.mkdir(parents=True, exist_ok=True)

    for src, relative in release_contents(project, config):
        _copy(src, target / relative)

    return target


def build_zip(project: Project, config: dict) -> Path:
    """Compresse le dossier de release. Renvoie le chemin du ZIP."""
    source = release_dir(project, config)
    zip_path = project.exports_dir / config["zip_name"]

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for path in sorted(source.rglob("*")):
            if any(name in path.parts for name in IGNORED_NAMES):
                continue

            if path.is_file():
                zipf.write(path, path.relative_to(project.releases_dir))

    return zip_path
