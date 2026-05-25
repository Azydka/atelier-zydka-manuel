# -*- coding: utf-8 -*-
"""
Utilitaires de configuration — Manuscript Studio by Atelier Zydka

Ce module centralise la lecture de config.json pour éviter de dupliquer
la logique dans chaque script.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"


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
    }
}


def deep_merge(default: dict[str, Any], custom: dict[str, Any]) -> dict[str, Any]:
    result = default.copy()

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


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    try:
        custom_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"Erreur dans config.json : {error}") from error

    if not isinstance(custom_config, dict):
        raise SystemExit("Erreur : config.json doit contenir un objet JSON.")

    return deep_merge(DEFAULT_CONFIG, custom_config)


def get_config_value(key: str, default: Any = None) -> Any:
    config = load_config()
    return config.get(key, default)
