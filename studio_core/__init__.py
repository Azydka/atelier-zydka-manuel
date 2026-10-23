# -*- coding: utf-8 -*-
"""
studio_core — moteur de Manuscript Studio by Atelier Zydka.

Transforme le manuscrit d'un projet (un dossier par livre) en pack éditorial :
PDF A5, teaser, rapports, citations, visuels, release, ZIP. Aucune dépendance
à Streamlit ; aucune sortie console : les avertissements passent par le module
logging (logger « studio_core »), la progression par un callback optionnel.
Le moteur n'écrit que dans le dossier exports/ du projet.
"""

from .errors import (
    CheckFailedError,
    ConfigError,
    ManuscriptNotFoundError,
    StudioError,
)
from .pipeline import (
    CheckResult,
    build_all,
    build_archive,
    build_marketing,
    build_pdf,
    build_quality,
    build_release_pack,
    build_social_visuals,
    build_structure,
    build_teaser,
    run_check,
)
from .project import (
    Project,
    create_demo_project,
    create_project,
    default_projects_root,
    import_legacy_projects,
    list_projects,
    open_project,
)

__all__ = [
    "CheckFailedError",
    "CheckResult",
    "ConfigError",
    "ManuscriptNotFoundError",
    "Project",
    "StudioError",
    "build_all",
    "build_archive",
    "build_marketing",
    "build_pdf",
    "build_quality",
    "build_release_pack",
    "build_social_visuals",
    "build_structure",
    "build_teaser",
    "create_demo_project",
    "create_project",
    "default_projects_root",
    "import_legacy_projects",
    "list_projects",
    "open_project",
    "run_check",
]
