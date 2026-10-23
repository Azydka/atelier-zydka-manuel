# -*- coding: utf-8 -*-
"""
studio_core — moteur de Manuscript Studio by Atelier Zydka.

Transforme un manuscrit texte en pack éditorial (PDF A5, teaser, rapports,
citations, visuels, release, ZIP). Aucune dépendance à Streamlit ; aucune
sortie console : les avertissements passent par le module logging
(logger « studio_core »), la progression par un callback optionnel.
"""

from .config import DEFAULT_CONFIG, load_config
from .errors import (
    CheckFailedError,
    ConfigError,
    ManuscriptNotFoundError,
    StudioError,
)
from .parser import parse_manuscript
from .pipeline import (
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
from .workspace import Workspace

__all__ = [
    "DEFAULT_CONFIG",
    "CheckFailedError",
    "ConfigError",
    "ManuscriptNotFoundError",
    "StudioError",
    "Workspace",
    "build_all",
    "build_archive",
    "build_marketing",
    "build_pdf",
    "build_quality",
    "build_release_pack",
    "build_social_visuals",
    "build_structure",
    "build_teaser",
    "load_config",
    "parse_manuscript",
    "run_check",
]
