# -*- coding: utf-8 -*-
"""
Enchaînement des étapes — Manuscript Studio by Atelier Zydka

Chaque fonction prend un Project, est appelable directement (pas de
sous-processus), renvoie les chemins produits et lève une StudioError en
cas d'échec. Une génération lit config.json et le manuscrit une seule fois
(BuildContext) puis les passe à toutes les étapes. Les fonctions longues
acceptent un callback de progression optionnel :

    on_progress(message: str, step: int, total: int)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from . import check as check_module
from .citations import build_citations
from .errors import CheckFailedError
from .pdf_book import build_book_pdf
from .project import Project
from .release import build_release, build_zip
from .report_quality import build_quality_report
from .report_structure import build_structure_report
from .teaser import build_teaser_pdf
from .visuals import build_visuals

ProgressCallback = Callable[[str, int, int], None]


@dataclass(frozen=True)
class BuildContext:
    """Entrées d'une génération, lues une seule fois."""

    project: Project
    config: dict
    manuscript: str

    @classmethod
    def load(cls, project: Project) -> "BuildContext":
        return cls(project, project.load_config(), project.read_manuscript())


@dataclass(frozen=True)
class CheckResult:
    issues: list
    report: str

    @property
    def has_errors(self) -> bool:
        return check_module.has_errors(self.issues)


def _check(ctx: BuildContext) -> CheckResult:
    issues = check_module.check_manuscript(ctx.manuscript, ctx.project.images_dir)
    return CheckResult(issues, check_module.format_report(ctx.project.manuscript, issues, ctx.manuscript))


def _check_or_fail(ctx: BuildContext) -> CheckResult:
    result = _check(ctx)
    if result.has_errors:
        raise CheckFailedError(result.report, result.issues)
    return result


def _pdf(ctx: BuildContext) -> Path:
    p = ctx.project
    return build_book_pdf(ctx.manuscript, ctx.config, p.pdf_dir / ctx.config["output_pdf_name"], p.images_dir)


def _structure(ctx: BuildContext) -> Path:
    return build_structure_report(ctx.manuscript, ctx.project.reports_dir)


def _quality(ctx: BuildContext) -> tuple[Path, Path]:
    return build_quality_report(ctx.manuscript, ctx.project.reports_dir)


def _citations(ctx: BuildContext) -> Path:
    p = ctx.project
    return build_citations(ctx.manuscript, p.citations_file, p.citations_source)


def _teaser(ctx: BuildContext) -> Path:
    return build_teaser_pdf(ctx.manuscript, ctx.config, ctx.project.pdf_dir / ctx.config["teaser_pdf_name"])


def _visuals(ctx: BuildContext) -> list[Path]:
    return build_visuals(ctx.project.citations_file, ctx.project.cards_dir, ctx.config)


def _release(ctx: BuildContext) -> Path:
    return build_release(ctx.project, ctx.config)


def _zip(ctx: BuildContext) -> Path:
    return build_zip(ctx.project, ctx.config)


Step = tuple[str, str, Callable[[BuildContext], object]]

STEPS: list[Step] = [
    ("check", "Vérification du manuscrit", _check_or_fail),
    ("book_pdf", "PDF principal", _pdf),
    ("structure_report", "Rapport de structure", _structure),
    ("quality_report", "Rapport qualité", _quality),
    ("citations", "Citations marketing", _citations),
    ("teaser_pdf", "Teaser PDF", _teaser),
    ("visuals", "Visuels réseaux", _visuals),
]
RELEASE_STEPS: list[Step] = STEPS + [("release", "Dossier de release", _release)]
ARCHIVE_STEPS: list[Step] = RELEASE_STEPS + [("zip", "Archive ZIP", _zip)]


def _run(project: Project, steps: list[Step], on_progress: Optional[ProgressCallback]) -> dict:
    ctx = BuildContext.load(project)
    results: dict = {}

    for index, (name, label, step) in enumerate(steps, start=1):
        if on_progress is not None:
            on_progress(label, index, len(steps))
        results[name] = step(ctx)

    return results


# Étapes isolées
def run_check(project: Project) -> CheckResult:
    """Vérifie le manuscrit et renvoie le résultat (sans lever d'erreur si le check échoue)."""
    return _check(BuildContext.load(project))


def build_pdf(project: Project) -> Path:
    return _pdf(BuildContext.load(project))


def build_structure(project: Project) -> Path:
    return _structure(BuildContext.load(project))


def build_quality(project: Project) -> tuple[Path, Path]:
    return _quality(BuildContext.load(project))


def build_marketing(project: Project) -> Path:
    return _citations(BuildContext.load(project))


def build_teaser(project: Project) -> Path:
    return _teaser(BuildContext.load(project))


def build_social_visuals(project: Project) -> list[Path]:
    return _visuals(BuildContext.load(project))


# Enchaînements
def build_all(project: Project, on_progress: Optional[ProgressCallback] = None) -> dict:
    """Vérifie puis génère tous les livrables. Renvoie {nom_étape: chemin(s) produit(s)}."""
    return _run(project, STEPS, on_progress)


def build_release_pack(project: Project, on_progress: Optional[ProgressCallback] = None) -> dict:
    """build_all puis dossier de release (clé « release »)."""
    return _run(project, RELEASE_STEPS, on_progress)


def build_archive(project: Project, on_progress: Optional[ProgressCallback] = None) -> dict:
    """Pack complet : livrables, dossier de release (« release ») et ZIP (« zip »)."""
    return _run(project, ARCHIVE_STEPS, on_progress)
