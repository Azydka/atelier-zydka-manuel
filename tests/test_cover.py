"""Couverture et 4e de couverture pilotées par config.json."""

import json

from pypdf import PdfReader
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

import studio_core
from studio_core.pdf_book import fit_font_size


def test_fit_font_size_garde_la_taille_max_si_ca_tient():
    assert fit_font_size("COURT", "Helvetica-Bold", 43, 24, 112 * mm, 3) == 43


def test_fit_font_size_reduit_un_mot_trop_large():
    size = fit_font_size("DÉMONSTRATION", "Helvetica-Bold", 43, 24, 112 * mm, 3)
    assert size < 43
    assert stringWidth("DÉMONSTRATION", "Helvetica-Bold", size) <= 112 * mm


def test_fit_font_size_respecte_le_minimum():
    assert fit_font_size("ANTICONSTITUTIONNELLEMENT " * 6, "Helvetica-Bold", 43, 24, 50 * mm, 3) == 24


def _pages_text(project):
    results = studio_core.build_all(project)
    reader = PdfReader(str(results["book_pdf"]))
    # Espaces et retours à la ligne normalisés : un titre peut être découpé sur plusieurs lignes.
    return tuple(" ".join(reader.pages[i].extract_text().split()) for i in (0, -1))


def _set_config(project, **values):
    config = json.loads(project.config_file.read_text(encoding="utf-8"))
    config.update(values)
    project.config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")


def test_couverture_utilise_book_title(tmp_path):
    project = studio_core.create_demo_project(tmp_path)
    _set_config(project, book_title="Les Jardins de Mars")

    first, last = _pages_text(project)

    assert "LES JARDINS DE MARS" in first
    assert "LE MANUEL" not in first
    assert "\\N" not in first and "\\N" not in last


def test_textes_de_couverture_configurables(tmp_path):
    project = studio_core.create_demo_project(tmp_path)
    _set_config(
        project,
        cover_kicker="Accroche test",
        cover_footer_left="Pied gauche",
        cover_footer_right="",
        back_cover_tagline="Phrase de dos",
        back_cover_footer_right="Pied dos",
    )

    first, last = _pages_text(project)

    assert "ACCROCHE TEST" in first and "PIED GAUCHE" in first
    assert "PHRASE DE DOS" in last and "PIED DOS" in last


def test_cle_vide_n_affiche_rien(tmp_path):
    project = studio_core.create_demo_project(tmp_path)
    _set_config(project, cover_kicker="")

    first, _ = _pages_text(project)

    assert "CULTURE · MÉTHODE" not in first
