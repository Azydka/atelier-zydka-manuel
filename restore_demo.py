# -*- coding: utf-8 -*-
"""
Restauration de la démo publique — Atelier Zydka Manuel

Objectif :
- restaurer config.json depuis demo/config.demo.json ;
- restaurer manuscrit_beatmakers.txt depuis demo/manuscrit_demo.txt ;
- éviter de laisser un manuscrit privé dans les fichiers actifs du dépôt.

Usage :
python3 restore_demo.py
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent

DEMO_CONFIG = ROOT / "demo" / "config.demo.json"
DEMO_MANUSCRIPT = ROOT / "demo" / "manuscrit_demo.txt"

ACTIVE_CONFIG = ROOT / "config.json"
ACTIVE_MANUSCRIPT = ROOT / "manuscrit_beatmakers.txt"


def restore_file(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Fichier de démo introuvable : {source}")

    shutil.copy2(source, destination)
    print(f"Restauré : {source.relative_to(ROOT)} → {destination.relative_to(ROOT)}")


def main() -> int:
    print("Restauration de la démo publique...")
    print("")

    restore_file(DEMO_CONFIG, ACTIVE_CONFIG)
    restore_file(DEMO_MANUSCRIPT, ACTIVE_MANUSCRIPT)

    print("")
    print("Démo publique restaurée.")
    print("Vous pouvez maintenant vérifier avec : git status")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
