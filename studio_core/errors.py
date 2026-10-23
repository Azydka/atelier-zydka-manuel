# -*- coding: utf-8 -*-
"""Exceptions du moteur : il ne termine jamais le processus, il lève ces erreurs."""

from __future__ import annotations


class StudioError(Exception):
    """Erreur générique de Manuscript Studio."""


class ConfigError(StudioError):
    """config.json absent du format attendu ou illisible."""


class ManuscriptNotFoundError(StudioError):
    """Le manuscrit source est introuvable."""


class CheckFailedError(StudioError):
    """La vérification du manuscrit a détecté des erreurs bloquantes."""

    def __init__(self, message: str, issues: list) -> None:
        super().__init__(message)
        self.issues = issues
