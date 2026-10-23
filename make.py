# -*- coding: utf-8 -*-
"""
Make script — Manuscript Studio by Atelier Zydka

Interface en ligne de commande au-dessus du moteur studio_core.

Commandes :
python3 make.py check      # vérifie le manuscrit
python3 make.py pdf        # génère le PDF principal
python3 make.py structure  # génère le rapport éditorial
python3 make.py quality    # génère le rapport qualité éditorial
python3 make.py marketing  # extrait les citations marketing
python3 make.py teaser     # génère le teaser PDF
python3 make.py visuals    # génère les visuels réseaux
python3 make.py all        # lance tout le pipeline
python3 make.py release    # crée un dossier de distribution propre
python3 make.py archive    # crée une archive ZIP transmissible
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import studio_core
from studio_core import check as check_module
from studio_core.errors import CheckFailedError, StudioError


ROOT = Path(__file__).resolve().parent

SINGLE_STEPS = {
    "pdf": studio_core.build_pdf,
    "structure": studio_core.build_structure,
    "quality": studio_core.build_quality,
    "marketing": studio_core.build_marketing,
    "teaser": studio_core.build_teaser,
    "visuals": studio_core.build_social_visuals,
}

PIPELINES = {
    "all": studio_core.build_all,
    "release": studio_core.build_release_pack,
    "archive": studio_core.build_archive,
}


def print_progress(message: str, step: int, total: int) -> None:
    print(f"→ [{step}/{total}] {message}")


def print_outputs(result) -> None:
    if isinstance(result, dict):
        for value in result.values():
            print_outputs(value)
    elif isinstance(result, (list, tuple)):
        if len(result) > 4:
            folders = sorted({str(Path(p).parent) for p in result})
            print(f"  {len(result)} fichiers dans : {', '.join(folders)}")
        else:
            for value in result:
                print_outputs(value)
    elif isinstance(result, Path):
        print(f"  {result}")


def check(workspace: studio_core.Workspace) -> int:
    raw = studio_core.pipeline.read_manuscript(workspace)
    issues = check_module.check_manuscript(raw, workspace.images_dir)
    print(check_module.format_report(workspace.manuscript, issues, raw))
    return 1 if check_module.has_errors(issues) else 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    command = argv[0] if argv else "all"

    logging.basicConfig(level=logging.WARNING, format="Attention : %(message)s")
    workspace = studio_core.Workspace.legacy(ROOT)

    try:
        if command == "check":
            return check(workspace)

        if command in SINGLE_STEPS:
            print_outputs(SINGLE_STEPS[command](workspace))
            return 0

        if command in PIPELINES:
            print_outputs(PIPELINES[command](workspace, on_progress=print_progress))
            return 0

    except CheckFailedError as error:
        print(error)
        print("")
        print("Arrêt : le check a détecté une erreur bloquante.")
        return 1

    except StudioError as error:
        print(f"ERREUR : {error}")
        return 1

    print("Commande inconnue.")
    print("Commandes disponibles : check, pdf, structure, quality, marketing, teaser, visuals, all, release, archive")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
