# -*- coding: utf-8 -*-
"""
Make script — Manuscript Studio by Atelier Zydka

Interface en ligne de commande au-dessus du moteur studio_core.
Chaque livre est un projet (un dossier) dans la racine des projets
(par défaut : Documents/Manuscript Studio).

Commandes :
python3 make.py list                   # liste les projets
python3 make.py new "Mon livre"        # crée un projet vide
python3 make.py init-demo              # crée le projet de démonstration
python3 make.py import-legacy          # copie les anciens private/projets/* dans la racine

python3 make.py [--project NOM] check      # vérifie le manuscrit
python3 make.py [--project NOM] pdf        # génère le PDF principal
python3 make.py [--project NOM] structure  # génère le rapport éditorial
python3 make.py [--project NOM] quality    # génère le rapport qualité éditorial
python3 make.py [--project NOM] marketing  # extrait les citations marketing
python3 make.py [--project NOM] teaser     # génère le teaser PDF
python3 make.py [--project NOM] visuals    # génère les visuels réseaux
python3 make.py [--project NOM] all        # lance tout le pipeline
python3 make.py [--project NOM] release    # crée le dossier de release du livre
python3 make.py [--project NOM] archive    # crée l'archive ZIP du livre

Options globales :
--projects-root DOSSIER   racine des projets (sinon MANUSCRIPT_STUDIO_HOME ou Documents/Manuscript Studio)
--project NOM|DOSSIER     projet à générer (défaut : le projet « demo », créé s'il n'existe pas)
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import studio_core
from studio_core.errors import CheckFailedError, StudioError
from studio_core.project import DEMO_SLUG, DEMO_TEMPLATE


ROOT = Path(__file__).resolve().parent
LEGACY_PRIVATE_DIR = ROOT / "private" / "projets"

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

PROJECT_COMMANDS = ["check", *SINGLE_STEPS, *PIPELINES]
ADMIN_COMMANDS = ["list", "new", "init-demo", "import-legacy"]


def print_progress(message: str, step: int, total: int) -> None:
    print(f"→ [{step}/{total}] {message}")


def print_outputs(results: dict) -> None:
    for value in results.values():
        paths = value if isinstance(value, (list, tuple)) else [value]
        paths = [p for p in paths if isinstance(p, Path)]
        if len(paths) > 4:
            print(f"  {len(paths)} fichiers dans : {paths[0].parent.parent}")
        else:
            for path in paths:
                print(f"  {path}")


def resolve_project(root: Path, name: str | None) -> studio_core.Project:
    if name:
        return studio_core.open_project(root, name)

    demo = studio_core.Project(root / DEMO_SLUG)
    if not demo.exists():
        demo = studio_core.create_demo_project(root)
        print(f"Projet de démonstration créé : {demo.root}")
    return demo


def run_admin(command: str, root: Path, args: argparse.Namespace) -> int:
    if command == "list":
        projects = studio_core.list_projects(root)
        print(f"Projets dans {root} :")
        for project in projects:
            print(f"  - {project.slug}")
        if not projects:
            print("  (aucun — essayez : python3 make.py init-demo)")
        return 0

    if command == "new":
        if not args.name:
            print('Indiquez le nom du livre : python3 make.py new "Mon livre"')
            return 1
        project = studio_core.create_project(root, " ".join(args.name))
        print(f"Projet créé : {project.root}")
        return 0

    if command == "init-demo":
        project = studio_core.create_demo_project(root)
        print(f"Projet de démonstration créé : {project.root}")
        return 0

    # import-legacy
    images = (ROOT / "images", DEMO_TEMPLATE / "images")
    results = studio_core.import_legacy_projects(LEGACY_PRIVATE_DIR, root, images)
    if not results:
        print(f"Aucun ancien projet trouvé dans {LEGACY_PRIVATE_DIR}")
    for source, target in results:
        if target is None:
            print(f"Ignoré (existe déjà dans la racine) : {source.name}")
        else:
            print(f"Copié : {source} → {target}")
    return 0


def run_project(command: str, project: studio_core.Project) -> int:
    print(f"Projet : {project.root}")

    if command == "check":
        result = studio_core.run_check(project)
        print(result.report)
        return 1 if result.has_errors else 0

    if command in SINGLE_STEPS:
        result = SINGLE_STEPS[command](project)
        print_outputs({command: result})
        return 0

    print_outputs(PIPELINES[command](project, on_progress=print_progress))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manuscript Studio — génération du pack éditorial.")
    parser.add_argument("--projects-root", type=Path, help="racine des projets")
    parser.add_argument("--project", help="nom (slug) ou dossier du projet")
    parser.add_argument("command", nargs="?", default="all", choices=ADMIN_COMMANDS + PROJECT_COMMANDS)
    parser.add_argument("name", nargs="*", help="nom du livre (commande new)")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="Attention : %(message)s")
    root = (args.projects_root or studio_core.default_projects_root()).expanduser().resolve()

    try:
        if args.command in ADMIN_COMMANDS:
            return run_admin(args.command, root, args)
        return run_project(args.command, resolve_project(root, args.project))

    except CheckFailedError as error:
        print(error)
        print("")
        print("Arrêt : le check a détecté une erreur bloquante.")
        return 1

    except StudioError as error:
        print(f"ERREUR : {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
