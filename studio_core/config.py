# -*- coding: utf-8 -*-
"""
Configuration d'un projet — Manuscript Studio by Atelier Zydka

Une seule fonction de lecture : load_config(path). Les valeurs absentes
de config.json sont complétées par DEFAULT_CONFIG (fusion récursive).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .errors import ConfigError


DEFAULT_CONFIG: dict[str, Any] = {
    "project_title": "Manuscript Studio by Atelier Zydka",
    "book_title": "Manuscrit de démonstration",
    "book_subtitle": "Transformer un manuscrit brut en pack éditorial complet",
    "author_name": "Atelier Zydka",
    "brand_name": "Atelier Zydka",
    "baseline": "Culture · méthode · indépendance",
    "year": "2026",
    "language": "fr",
    "output_pdf_name": "manuel-de-presence-atelier-zydka.pdf",
    "teaser_pdf_name": "teaser-manuel-presence.pdf",
    "release_name": "atelier-zydka-manuel-release",
    "zip_name": "atelier-zydka-manuel-release.zip",
    "theme": {
        "background": "#090909",
        "text": "#F4F1EB",
        "accent": "#C79A3B",
        "muted": "#96928A"
    },
    # Pages optionnelles du PDF principal.
    "features": {
        "include_cover": True,
        "include_back_cover": True,
        "include_annex_page": False,
        "include_demo_pages": False,
        "include_fixed_intro_pages": False,
        "include_visual_opening_pages": False,
        "include_table_of_contents": True,
        "strict_missing_images": False,
    },
}


def deep_merge(default: dict[str, Any], custom: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(default)

    for key, value in custom.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    """Complète une configuration (éventuellement partielle) avec DEFAULT_CONFIG."""
    return deep_merge(DEFAULT_CONFIG, config)


def load_config(path: Path | str | None) -> dict[str, Any]:
    """Lit config.json et le complète avec les valeurs par défaut."""
    if path is None or not Path(path).exists():
        return copy.deepcopy(DEFAULT_CONFIG)

    path = Path(path)

    try:
        custom_config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ConfigError(f"Erreur dans {path.name} : {error}") from error

    if not isinstance(custom_config, dict):
        raise ConfigError(f"Erreur : {path.name} doit contenir un objet JSON.")

    return normalize_config(custom_config)
