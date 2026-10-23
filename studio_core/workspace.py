# -*- coding: utf-8 -*-
"""
Emplacements des fichiers d'entrée et de sortie d'une génération.

Le moteur ne calcule jamais un chemin lui-même : tout passe par un Workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# Dossier du package (ressources en lecture seule : polices, etc.).
PACKAGE_DIR = Path(__file__).resolve().parent
FONTS_DIR = PACKAGE_DIR / "fonts"


@dataclass(frozen=True)
class Workspace:
    manuscript: Path
    config: Path
    images_dir: Path
    book_pdf_dir: Path
    exports_dir: Path
    dist_dir: Path

    @property
    def teaser_dir(self) -> Path:
        return self.exports_dir / "pdf"

    @property
    def reports_dir(self) -> Path:
        return self.exports_dir / "rapports"

    @property
    def citations_file(self) -> Path:
        return self.exports_dir / "reseaux" / "citations" / "citations_extraites.md"

    @property
    def cards_dir(self) -> Path:
        return self.exports_dir / "reseaux" / "cartes"

    @classmethod
    def legacy(cls, root: Path) -> "Workspace":
        """Disposition historique : manuscrit, config et sorties à la racine du dépôt."""
        root = Path(root)
        return cls(
            manuscript=root / "manuscrit_beatmakers.txt",
            config=root / "config.json",
            images_dir=root / "images",
            book_pdf_dir=root / "manuelsortie",
            exports_dir=root / "exports",
            dist_dir=root / "dist",
        )
