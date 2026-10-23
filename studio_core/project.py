# -*- coding: utf-8 -*-
"""
Projet — l'unité de travail de Manuscript Studio.

Un livre = un dossier :

    <racine des projets>/<slug>/
        config.json        titre, auteur, couleurs, noms des fichiers
        manuscrit.txt      texte source
        citations.txt      (facultatif) citations marketing, une par ligne
        images/            images référencées par [IMAGE: …]
        exports/           tout ce que le moteur produit
            pdf/  rapports/  reseaux/  release/  <zip>

La racine par défaut est « Documents/Manuscript Studio » de l'utilisateur
(variable d'environnement MANUSCRIPT_STUDIO_HOME pour la changer). Le moteur
n'écrit jamais ailleurs que dans le dossier du projet.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT_CONFIG, load_config
from .errors import ManuscriptNotFoundError, StudioError
from .resources import TEMPLATES_DIR

MANUSCRIPT_NAME = "manuscrit.txt"
CONFIG_NAME = "config.json"
CITATIONS_NAME = "citations.txt"

ENV_PROJECTS_ROOT = "MANUSCRIPT_STUDIO_HOME"
DEMO_SLUG = "demo"
DEMO_TEMPLATE = TEMPLATES_DIR / "demo"


def default_projects_root() -> Path:
    override = os.environ.get(ENV_PROJECTS_ROOT)
    if override:
        return Path(override).expanduser()

    import platformdirs

    return Path(platformdirs.user_documents_dir()) / "Manuscript Studio"


def slugify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text or "projet"


@dataclass(frozen=True)
class Project:
    root: Path

    @property
    def slug(self) -> str:
        return self.root.name

    # Entrées
    @property
    def manuscript(self) -> Path:
        return self.root / MANUSCRIPT_NAME

    @property
    def config_file(self) -> Path:
        return self.root / CONFIG_NAME

    @property
    def citations_source(self) -> Path:
        return self.root / CITATIONS_NAME

    @property
    def images_dir(self) -> Path:
        return self.root / "images"

    # Sorties
    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def pdf_dir(self) -> Path:
        return self.exports_dir / "pdf"

    @property
    def reports_dir(self) -> Path:
        return self.exports_dir / "rapports"

    @property
    def citations_file(self) -> Path:
        return self.exports_dir / "reseaux" / "citations_extraites.md"

    @property
    def cards_dir(self) -> Path:
        return self.exports_dir / "reseaux" / "cartes"

    @property
    def releases_dir(self) -> Path:
        return self.exports_dir / "release"

    def exists(self) -> bool:
        return self.config_file.exists() or self.manuscript.exists()

    def load_config(self) -> dict:
        return load_config(self.config_file)

    def read_manuscript(self) -> str:
        if not self.manuscript.exists():
            raise ManuscriptNotFoundError(f"Manuscrit introuvable : {self.manuscript}")
        return self.manuscript.read_text(encoding="utf-8")


def list_projects(projects_root: Path) -> list[Project]:
    if not projects_root.exists():
        return []
    return [
        Project(path)
        for path in sorted(projects_root.iterdir())
        if path.is_dir() and Project(path).exists()
    ]


def open_project(projects_root: Path, name_or_path: str) -> Project:
    """Projet désigné par un chemin de dossier, par son nom de dossier ou par son slug dans la racine."""
    candidate = Path(name_or_path).expanduser()
    if candidate.is_dir() and Project(candidate).exists():
        return Project(candidate.resolve())

    for folder in (name_or_path, slugify(name_or_path)):
        project = Project(projects_root / folder)
        if project.exists():
            return project

    raise StudioError(f"Projet introuvable : {name_or_path} (racine : {projects_root})")


def _new_project_dir(projects_root: Path, slug: str) -> Path:
    target = projects_root / slug
    if target.exists():
        raise StudioError(f"Le dossier existe déjà : {target}")
    return target


def create_project(projects_root: Path, name: str) -> Project:
    """Crée un projet vide (config par défaut au nom du livre, manuscrit minimal)."""
    slug = slugify(name)
    target = _new_project_dir(projects_root, slug)
    project = Project(target)

    project.images_dir.mkdir(parents=True)
    config = {
        **{key: value for key, value in DEFAULT_CONFIG.items() if key != "features"},
        "book_title": name,
        "output_pdf_name": f"{slug}.pdf",
        "teaser_pdf_name": f"{slug}-teaser.pdf",
        "release_name": f"{slug}-release",
        "zip_name": f"{slug}-release.zip",
    }
    project.config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    project.manuscript.write_text(f"# {name}\n\n# Introduction\n\n", encoding="utf-8")
    return project


def create_demo_project(projects_root: Path, slug: str = DEMO_SLUG) -> Project:
    """Copie le projet de démonstration intégré dans la racine des projets."""
    target = _new_project_dir(projects_root, slug)
    shutil.copytree(DEMO_TEMPLATE, target)
    return Project(target)


def import_legacy_projects(
    legacy_dir: Path,
    projects_root: Path,
    legacy_images_dirs: tuple[Path, ...] = (),
) -> list[tuple[Path, Path | None]]:
    """
    Copie (sans rien supprimer ni écraser) les anciens projets
    <dépôt>/private/projets/<slug>/ vers la racine des projets.
    Les anciens projets partageaient le dossier images/ du dépôt : les images
    de legacy_images_dirs sont copiées dans images/ de chaque projet importé.
    Renvoie [(source, destination ou None si déjà présente)].
    """
    results: list[tuple[Path, Path | None]] = []
    if not legacy_dir.exists():
        return results

    for source in sorted(p for p in legacy_dir.iterdir() if p.is_dir()):
        target = projects_root / source.name
        if target.exists():
            results.append((source, None))
            continue
        shutil.copytree(source, target)
        images = target / "images"
        images.mkdir(exist_ok=True)
        for images_dir in legacy_images_dirs:
            for image in images_dir.glob("*") if images_dir.is_dir() else []:
                if image.is_file() and not (images / image.name).exists():
                    shutil.copy2(image, images / image.name)
        results.append((source, target))

    return results
