"""Contrat de l'API studio_core pour une future coque (pywebview) : appel direct, chemins renvoyés, aucune sortie console."""

from pathlib import Path

import pytest

import studio_core
from studio_core.errors import CheckFailedError, ManuscriptNotFoundError


@pytest.fixture
def project(tmp_path):
    return studio_core.create_demo_project(tmp_path / "projets")


def test_build_archive_renvoie_les_chemins_produits(project, capsys):
    events = []
    results = studio_core.build_archive(project, on_progress=lambda message, step, total: events.append((step, total)))

    assert results["book_pdf"].is_file()
    assert results["teaser_pdf"].is_file()
    assert results["structure_report"].is_file()
    assert all(path.is_file() for path in results["quality_report"])
    assert results["visuals"] and all(path.is_file() for path in results["visuals"])
    assert results["release"].is_dir()
    assert results["zip"].is_file()

    produced = [results["book_pdf"], results["zip"], results["release"], *results["visuals"]]
    assert all(project.exports_dir in path.parents for path in produced)

    assert events == [(i, 9) for i in range(1, 10)]
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == ""


def test_manuscrit_absent_leve_une_erreur(project):
    project.manuscript.unlink()
    with pytest.raises(ManuscriptNotFoundError):
        studio_core.build_all(project)


def test_check_bloquant(project):
    project.manuscript.write_text("# Titre\n\n[IMAGE: absente.png | légende]\n", encoding="utf-8")

    result = studio_core.run_check(project)
    assert result.has_errors and "absente.png" in result.report

    with pytest.raises(CheckFailedError) as error:
        studio_core.build_all(project)
    assert error.value.issues


@pytest.mark.parametrize("forbidden", ["import streamlit", "print(", "sys.exit", "SystemExit", "subprocess"])
def test_le_moteur_reste_une_bibliotheque(forbidden):
    package = Path(studio_core.__file__).parent
    offenders = [p.name for p in package.glob("*.py") if forbidden in p.read_text(encoding="utf-8")]
    assert offenders == []
