# -*- coding: utf-8 -*-
"""
Dossier de release et archive ZIP — Manuscript Studio by Atelier Zydka

build_release() rassemble la documentation et les livrables déjà générés
dans <dist>/<release_name>/ ; build_zip() compresse ce dossier.
"""

from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path

from .errors import StudioError
from .report_quality import REPORT_NAME as QUALITY_REPORT_NAME, SCORE_NAME
from .report_structure import REPORT_NAME as STRUCTURE_REPORT_NAME
from .workspace import PACKAGE_DIR, Workspace

log = logging.getLogger(__name__)

# Racine de l'application (documentation, lanceurs) : en lecture seule.
APP_ROOT = PACKAGE_DIR.parent

# Fichiers système jamais copiés ni archivés.
IGNORED_NAMES = (".DS_Store", "__pycache__")

DOCUMENTATION_FILES = [
    "README.md",
    "RELEASE_NOTES.md",
    "LICENSE.md",
    "START_HERE.md",
    "INSTALLATION.md",
    "QUICKSTART.md",
    "requirements.txt",
    "app_streamlit.py",
    "project_manager.py",
    "restore_demo.py",
    "demo",
    "launch_app.sh",
    "launch_app.command",
    "install_and_launch.command",
    "install_and_launch.sh",
    "install_and_launch.bat",
    "docs/GUIDE_UTILISATEUR.md",
    "docs/FAQ.md",
    "docs/PAGE_VENTE.md",
    "docs/BETA_TEST.md",
]


SENSITIVE_RELEASE_PATTERNS = [
    "BEATMAKER INDÉPENDANT",
    "BEATMAKER INDEPENDANT",
    "ÉDITION V13",
    "EDITION V13",
    "Beatmaker_Toolkit",
    "beatmaker-indépendant-2027",
    "beatmaker_independant_2027",
    "manuscrit_beatmakers_v13",
]


def assert_no_sensitive_content(path: Path) -> None:
    """
    Bloque la génération d'une release publique si un contenu privé
    ou un mot-clé de manuscrit réel est détecté dans le dossier de release.
    """
    matches: list[str] = []

    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue

        if any(name in file_path.parts for name in IGNORED_NAMES):
            continue

        # On évite de lire les binaires lourds, mais on contrôle les noms.
        for pattern in SENSITIVE_RELEASE_PATTERNS:
            if pattern in str(file_path):
                relative = file_path.relative_to(path)
                matches.append(f"{relative} -> {pattern}")

        if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf", ".zip", ".ico"}:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern in SENSITIVE_RELEASE_PATTERNS:
            if pattern in content:
                relative = file_path.relative_to(path)
                matches.append(f"{relative} -> {pattern}")

    if matches:
        details = "\n".join(f"- {item}" for item in matches)
        raise StudioError(
            "Contenu sensible détecté dans la release publique.\n"
            "Génération ZIP bloquée.\n\n"
            f"{details}\n\n"
            "Nettoyez les fichiers publics avant de relancer make.py archive."
        )


def copy_file(src: Path, dest: Path) -> None:
    if not src.exists():
        log.warning("Fichier absent, non copié : %s", src)
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    log.debug("Copié : %s → %s", src, dest)


def copy_dir(src: Path, dest: Path) -> None:
    if not src.exists():
        log.warning("Dossier absent, non copié : %s", src)
        return

    if dest.exists():
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns(*IGNORED_NAMES),
    )

    log.debug("Copié : %s → %s", src, dest)


def copy_any(src: Path, dest: Path) -> None:
    if src.is_dir():
        copy_dir(src, dest)
    else:
        copy_file(src, dest)


def release_dir(workspace: Workspace, config: dict) -> Path:
    return workspace.dist_dir / config["release_name"]


def build_release(workspace: Workspace, config: dict, app_root: Path = APP_ROOT) -> Path:
    """Crée le dossier de release à partir des livrables déjà générés et renvoie son chemin."""
    target = release_dir(workspace, config)

    if target.exists():
        shutil.rmtree(target)

    target.mkdir(parents=True, exist_ok=True)

    for relative in DOCUMENTATION_FILES:
        copy_any(Path(app_root) / relative, target / relative)

    outputs = [
        (workspace.book_pdf_dir / config["output_pdf_name"], target / "pdf" / config["output_pdf_name"]),
        (workspace.teaser_dir / config["teaser_pdf_name"], target / "pdf" / config["teaser_pdf_name"]),
        (workspace.reports_dir / STRUCTURE_REPORT_NAME, target / "rapports" / STRUCTURE_REPORT_NAME),
        (workspace.reports_dir / QUALITY_REPORT_NAME, target / "rapports" / QUALITY_REPORT_NAME),
        (workspace.reports_dir / SCORE_NAME, target / "rapports" / SCORE_NAME),
        (workspace.citations_file, target / "reseaux" / "citations_extraites.md"),
        (workspace.cards_dir, target / "reseaux" / "cartes"),
    ]

    for src, dest in outputs:
        copy_any(src, dest)

    return target


def build_zip(workspace: Workspace, config: dict) -> Path:
    """Vérifie le dossier de release puis le compresse. Renvoie le chemin du ZIP."""
    source = release_dir(workspace, config)
    zip_path = workspace.dist_dir / config["zip_name"]

    if zip_path.exists():
        zip_path.unlink()

    assert_no_sensitive_content(source)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for path in source.rglob("*"):
            if any(name in path.parts for name in IGNORED_NAMES):
                continue

            if path.is_file():
                zipf.write(path, path.relative_to(workspace.dist_dir))

    return zip_path
