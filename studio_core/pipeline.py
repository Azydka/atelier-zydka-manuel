# -*- coding: utf-8 -*-
"""
Enchaînement des étapes — Manuscript Studio by Atelier Zydka

Chaque fonction est appelable directement (pas de sous-processus), renvoie
les chemins produits et lève une StudioError en cas d'échec. Les fonctions
longues acceptent un callback de progression optionnel :

    on_progress(message: str, step: int, total: int)
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from . import check as check_module
from .citations import build_citations
from .config import load_config
from .errors import CheckFailedError, ManuscriptNotFoundError
from .pdf_book import build_book_pdf
from .release import build_release, build_zip
from .report_quality import build_quality_report
from .report_structure import build_structure_report
from .teaser import build_teaser_pdf
from .visuals import build_visuals
from .workspace import Workspace

ProgressCallback = Callable[[str, int, int], None]


def read_manuscript(workspace: Workspace) -> str:
    if not workspace.manuscript.exists():
        raise ManuscriptNotFoundError(f"Manuscrit introuvable : {workspace.manuscript}")
    return workspace.manuscript.read_text(encoding="utf-8")


def run_check(workspace: Workspace) -> list:
    """Vérifie le manuscrit. Lève CheckFailedError si une erreur bloquante est trouvée."""
    raw = read_manuscript(workspace)
    issues = check_module.check_manuscript(raw, workspace.images_dir)
    if check_module.has_errors(issues):
        raise CheckFailedError(check_module.format_report(workspace.manuscript, issues, raw), issues)
    return issues


def build_pdf(workspace: Workspace) -> Path:
    config = load_config(workspace.config)
    text = workspace.manuscript.read_text(encoding="utf-8") if workspace.manuscript.exists() else None
    return build_book_pdf(text, config, workspace.book_pdf_dir / config["output_pdf_name"], workspace.images_dir)


def build_structure(workspace: Workspace) -> Path:
    return build_structure_report(read_manuscript(workspace), workspace.reports_dir)


def build_quality(workspace: Workspace) -> tuple[Path, Path]:
    return build_quality_report(read_manuscript(workspace), workspace.reports_dir)


def build_marketing(workspace: Workspace) -> Path:
    return build_citations(workspace.citations_file)


def build_teaser(workspace: Workspace) -> Path:
    config = load_config(workspace.config)
    return build_teaser_pdf(read_manuscript(workspace), config, workspace.teaser_dir / config["teaser_pdf_name"])


def build_social_visuals(workspace: Workspace) -> list[Path]:
    return build_visuals(workspace.citations_file, workspace.cards_dir, load_config(workspace.config))


STEPS: list[tuple[str, str, Callable[[Workspace], object]]] = [
    ("check", "Vérification du manuscrit", run_check),
    ("book_pdf", "PDF principal", build_pdf),
    ("structure_report", "Rapport de structure", build_structure),
    ("quality_report", "Rapport qualité", build_quality),
    ("citations", "Citations marketing", build_marketing),
    ("teaser_pdf", "Teaser PDF", build_teaser),
    ("visuals", "Visuels réseaux", build_social_visuals),
]


def _release(workspace: Workspace) -> Path:
    return build_release(workspace, load_config(workspace.config))


def _zip(workspace: Workspace) -> Path:
    return build_zip(workspace, load_config(workspace.config))


def _run(workspace: Workspace, steps: list, on_progress: Optional[ProgressCallback]) -> dict:
    results: dict = {}
    total = len(steps)

    for index, (name, label, step) in enumerate(steps, start=1):
        if on_progress is not None:
            on_progress(label, index, total)
        results[name] = step(workspace)

    return results


def build_all(workspace: Workspace, on_progress: Optional[ProgressCallback] = None) -> dict:
    """Vérifie puis génère tous les livrables. Renvoie {nom_étape: chemin(s) produit(s)}."""
    return _run(workspace, STEPS, on_progress)


def build_release_pack(workspace: Workspace, on_progress: Optional[ProgressCallback] = None) -> dict:
    """build_all puis dossier de release (clé « release »)."""
    return _run(workspace, STEPS + [("release", "Dossier de release", _release)], on_progress)


def build_archive(workspace: Workspace, on_progress: Optional[ProgressCallback] = None) -> dict:
    """Pack complet : livrables, dossier de release (« release ») et ZIP (« zip »)."""
    steps = STEPS + [("release", "Dossier de release", _release), ("zip", "Archive ZIP", _zip)]
    return _run(workspace, steps, on_progress)
