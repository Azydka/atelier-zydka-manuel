# -*- coding: utf-8 -*-
"""
Gestionnaire de projets privés — Manuscript Studio by Atelier Zydka

V3.2 :
- crée des projets privés dans private/projets/
- sauvegarde un manuscrit et une configuration par projet
- recharge un projet privé vers les fichiers actifs du moteur
- évite de versionner les vrais livres dans Git

Structure :

private/
└── projets/
    └── mon-projet/
        ├── config.json
        └── manuscrit.txt
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent

PRIVATE_DIR = ROOT / "private"
PROJECTS_DIR = PRIVATE_DIR / "projets"

ACTIVE_CONFIG = ROOT / "config.json"
ACTIVE_MANUSCRIPT = ROOT / "manuscrit_beatmakers.txt"


DEFAULT_PROJECT_CONFIG: dict[str, Any] = {
    "project_title": "Manuscript Studio by Atelier Zydka",
    "book_title": "Nouveau projet éditorial",
    "book_subtitle": "Transformer un manuscrit en pack éditorial complet",
    "author_name": "Auteur",
    "brand_name": "Marque",
    "baseline": "Créer · publier · diffuser",
    "year": "2026",
    "language": "fr",
    "output_pdf_name": "livre.pdf",
    "teaser_pdf_name": "teaser.pdf",
    "release_name": "release-livre",
    "zip_name": "release-livre.zip",
    "theme": {
        "background": "#090909",
        "text": "#F4F1EB",
        "accent": "#C79A3B",
        "muted": "#96928A"
    }
}


DEFAULT_MANUSCRIPT = """# Nouveau projet éditorial

## Sous-titre ou promesse

Ce fichier est un manuscrit privé de travail.

Il est stocké dans private/projets/ et ne doit pas être publié dans le dépôt GitHub.

---

# Introduction

Présentez ici l'objectif du livre, du guide ou du document.

---

# Partie 1 — Première idée

Développez ici le premier axe du manuscrit.

---

# Conclusion

Résumez l'intention du document.

Fin du document.
"""


def ensure_private_structure() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def slugify(name: str) -> str:
    value = name.strip().lower()
    value = value.replace("'", "-")
    value = value.replace("’", "-")
    value = re.sub(r"[^a-z0-9À-ÿ]+", "-", value)
    value = value.strip("-")
    value = re.sub(r"-+", "-", value)

    if not value:
        value = "nouveau-projet"

    return value


def list_projects() -> list[str]:
    ensure_private_structure()

    projects: list[str] = []

    for path in PROJECTS_DIR.iterdir():
        if path.is_dir():
            projects.append(path.name)

    return sorted(projects)


def project_path(project_slug: str) -> Path:
    ensure_private_structure()
    return PROJECTS_DIR / slugify(project_slug)


def create_project(project_name: str) -> Path:
    ensure_private_structure()

    slug = slugify(project_name)
    path = PROJECTS_DIR / slug

    path.mkdir(parents=True, exist_ok=True)

    config_path = path / "config.json"
    manuscript_path = path / "manuscrit.txt"

    if not config_path.exists():
        config = DEFAULT_PROJECT_CONFIG.copy()
        config["project_title"] = project_name
        config["book_title"] = project_name
        config["output_pdf_name"] = f"{slug}.pdf"
        config["teaser_pdf_name"] = f"teaser-{slug}.pdf"
        config["release_name"] = f"{slug}-release"
        config["zip_name"] = f"{slug}-release.zip"

        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    if not manuscript_path.exists():
        manuscript_path.write_text(DEFAULT_MANUSCRIPT, encoding="utf-8")

    return path


def read_project_config(project_slug: str) -> dict[str, Any]:
    path = project_path(project_slug)
    config_path = path / "config.json"

    if not config_path.exists():
        return DEFAULT_PROJECT_CONFIG.copy()

    return json.loads(config_path.read_text(encoding="utf-8"))


def read_project_manuscript(project_slug: str) -> str:
    path = project_path(project_slug)
    manuscript_path = path / "manuscrit.txt"

    if not manuscript_path.exists():
        return DEFAULT_MANUSCRIPT

    return manuscript_path.read_text(encoding="utf-8")


def save_project(
    project_slug: str,
    config: dict[str, Any],
    manuscript: str,
) -> None:
    path = project_path(project_slug)
    path.mkdir(parents=True, exist_ok=True)

    (path / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    (path / "manuscrit.txt").write_text(manuscript, encoding="utf-8")


def load_project_to_active_files(project_slug: str) -> None:
    """
    V3.7 — fonction conservée pour compatibilité.

    Sécurité :
    cette fonction ne copie plus les fichiers privés vers les fichiers publics actifs.
    Elle vérifie seulement que le projet privé est complet.

    La génération Streamlit utilise désormais une copie temporaire restaurée automatiquement.
    """
    path = project_path(project_slug)

    config_path = path / "config.json"
    manuscript_path = path / "manuscrit.txt"

    if not config_path.exists():
        raise FileNotFoundError(f"Config introuvable : {config_path}")

    if not manuscript_path.exists():
        raise FileNotFoundError(f"Manuscrit introuvable : {manuscript_path}")


def save_active_files_to_project(project_slug: str) -> None:
    path = project_path(project_slug)
    path.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ACTIVE_CONFIG, path / "config.json")
    shutil.copy2(ACTIVE_MANUSCRIPT, path / "manuscrit.txt")


def get_project_summary(project_slug: str) -> dict[str, str]:
    config = read_project_config(project_slug)

    return {
        "project": project_slug,
        "book_title": str(config.get("book_title", "")),
        "author_name": str(config.get("author_name", "")),
        "brand_name": str(config.get("brand_name", "")),
        "zip_name": str(config.get("zip_name", "")),
    }


def main() -> int:
    ensure_private_structure()

    print("Dossier projets privés :")
    print(PROJECTS_DIR)

    projects = list_projects()

    if not projects:
        print("Aucun projet privé pour le moment.")
    else:
        print("Projets privés :")
        for project in projects:
            print(f"- {project}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
