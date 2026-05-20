# -*- coding: utf-8 -*-
"""
Make script — Atelier Zydka Manuel

Commandes :
python3 make.py check   # vérifie le manuscrit
python3 make.py pdf     # génère le PDF
python3 make.py all     # vérifie puis génère
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> int:
    print("")
    print("→ " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    return result.returncode


def check() -> int:
    code = run([sys.executable, "-m", "py_compile", "verifier_manuscrit.py"])
    if code != 0:
        return code

    return run([sys.executable, "verifier_manuscrit.py"])


def pdf() -> int:
    code = run([sys.executable, "-m", "py_compile", "parser_manuscrit.py"])
    if code != 0:
        return code

    code = run([sys.executable, "-m", "py_compile", "generer_livre_manuel_presence.py"])
    if code != 0:
        return code

    return run([sys.executable, "generer_livre_manuel_presence.py"])


def all_steps() -> int:
    code = check()
    if code != 0:
        print("")
        print("Arrêt : le check a détecté une erreur bloquante.")
        return code

    return pdf()


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "check":
        return check()

    if command == "pdf":
        return pdf()

    if command == "all":
        return all_steps()

    print("Commande inconnue.")
    print("Commandes disponibles : check, pdf, all")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
