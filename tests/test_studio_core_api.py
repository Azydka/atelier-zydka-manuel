"""Contrat de l'API studio_core pour une future coque (pywebview) : appel direct, chemins renvoyés, aucune sortie console."""

import shutil
from pathlib import Path

import pytest

import studio_core
from studio_core.errors import CheckFailedError, ManuscriptNotFoundError

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"


@pytest.fixture
def workspace(tmp_path):
    shutil.copy(DEMO_DIR / "manuscrit_demo.txt", tmp_path / "manuscrit_beatmakers.txt")
    shutil.copy(DEMO_DIR / "config.demo.json", tmp_path / "config.json")
    (tmp_path / "images").mkdir()
    return studio_core.Workspace.legacy(tmp_path)


def test_build_archive_renvoie_les_chemins_produits(workspace, capsys):
    events = []
    results = studio_core.build_archive(workspace, on_progress=lambda message, step, total: events.append((step, total)))

    assert results["book_pdf"].is_file()
    assert results["teaser_pdf"].is_file()
    assert results["structure_report"].is_file()
    assert all(path.is_file() for path in results["quality_report"])
    assert results["visuals"] and all(path.is_file() for path in results["visuals"])
    assert results["release"].is_dir()
    assert results["zip"].is_file()

    assert events == [(i, 9) for i in range(1, 10)]
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == ""


def test_manuscrit_absent_leve_une_erreur(workspace):
    workspace.manuscript.unlink()
    with pytest.raises(ManuscriptNotFoundError):
        studio_core.build_all(workspace)


def test_check_bloquant_leve_une_erreur(workspace):
    workspace.manuscript.write_text("# Titre\n\n[IMAGE: absente.png | légende]\n", encoding="utf-8")
    with pytest.raises(CheckFailedError) as error:
        studio_core.run_check(workspace)
    assert error.value.issues


@pytest.mark.parametrize("forbidden", ["import streamlit", "print(", "sys.exit", "SystemExit", "subprocess"])
def test_le_moteur_reste_une_bibliotheque(forbidden):
    package = Path(studio_core.__file__).parent
    offenders = [p.name for p in package.glob("*.py") if forbidden in p.read_text(encoding="utf-8")]
    assert offenders == []
