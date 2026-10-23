"""
Tests de caractérisation du pack démo.

Ils figent le comportement actuel (tests/reference/demo.json) pour que les
refactors ne changent rien sans qu'on le voie. Un changement de rendu
volontaire se traite en régénérant la référence dans un commit dédié :
python -m tests.snapshot --update
"""

import pytest

MAX_ARCHIVE_SECONDS = 15


def test_archive_reste_rapide(demo_build):
    assert demo_build["duration"] < MAX_ARCHIVE_SECONDS


@pytest.mark.parametrize("source", ["parser_manuscrit", "rapport_structure", "rapport_qualite", "sommaire_pdf"])
def test_nombre_de_chapitres(demo_build, reference, source):
    assert demo_build["snapshot"]["chapters"][source] == reference["chapters"][source]


@pytest.mark.parametrize("pdf", ["book_pdf", "teaser_pdf"])
def test_nombre_de_pages(demo_build, reference, pdf):
    assert demo_build["snapshot"][pdf]["pages"] == reference[pdf]["pages"]


@pytest.mark.parametrize("pdf", ["book_pdf", "teaser_pdf"])
def test_texte_des_pdf(demo_build, reference, pdf):
    actual = demo_build["snapshot"][pdf]["text"]
    expected = reference[pdf]["text"]
    for page, (got, want) in enumerate(zip(actual, expected), start=1):
        assert got == want, f"{pdf} page {page} différente"
    assert len(actual) == len(expected)


def test_fichiers_de_la_release(demo_build, reference):
    assert demo_build["snapshot"]["release_files"] == reference["release_files"]


def test_contenu_du_zip(demo_build, reference):
    assert demo_build["snapshot"]["zip_entries"] == reference["zip_entries"]
    assert demo_build["snapshot"]["zip_entries"], "le ZIP ne doit pas être vide"
