import json

import pytest

import studio_core
from studio_core.citations import collect_citations
from studio_core.errors import StudioError


def test_create_project(tmp_path):
    project = studio_core.create_project(tmp_path, "Mon Livre d'Été")

    assert project.slug == "mon-livre-d-ete"
    assert project.manuscript.exists() and project.images_dir.is_dir()
    config = json.loads(project.config_file.read_text(encoding="utf-8"))
    assert config["book_title"] == "Mon Livre d'Été"
    assert config["zip_name"] == "mon-livre-d-ete-release.zip"

    with pytest.raises(StudioError):
        studio_core.create_project(tmp_path, "Mon Livre d'Été")


def test_open_project_par_slug_ou_chemin(tmp_path):
    project = studio_core.create_demo_project(tmp_path)

    assert studio_core.open_project(tmp_path, "demo") == project
    assert studio_core.open_project(tmp_path, str(project.root)).root == project.root.resolve()
    assert [p.slug for p in studio_core.list_projects(tmp_path)] == ["demo"]

    with pytest.raises(StudioError):
        studio_core.open_project(tmp_path, "inconnu")


def test_default_projects_root_surchargeable(tmp_path, monkeypatch):
    monkeypatch.setenv("MANUSCRIPT_STUDIO_HOME", str(tmp_path))
    assert studio_core.default_projects_root() == tmp_path


def test_import_legacy_copie_sans_ecraser(tmp_path):
    legacy = tmp_path / "private" / "projets"
    (legacy / "livre-a").mkdir(parents=True)
    (legacy / "livre-a" / "manuscrit.txt").write_text("# A\n", encoding="utf-8")
    (legacy / "livre-b").mkdir()
    root = tmp_path / "racine"
    (root / "livre-b").mkdir(parents=True)

    results = dict(studio_core.import_legacy_projects(legacy, root))

    assert results[legacy / "livre-a"] == root / "livre-a"
    assert results[legacy / "livre-b"] is None
    assert (legacy / "livre-a" / "manuscrit.txt").exists(), "la source ne doit jamais être supprimée"
    assert (root / "livre-a" / "manuscrit.txt").read_text(encoding="utf-8") == "# A\n"


def test_citations_depuis_le_manuscrit(tmp_path):
    text = "# Chapitre\n\n[QUOTE: Une phrase forte.]\n\nÀ retenir : une idée clé.\n\nÀ retenir : une idée clé.\n"
    assert collect_citations(text) == (["Une phrase forte.", "une idée clé."], "le manuscrit")


def test_citations_txt_prioritaire(tmp_path):
    source = tmp_path / "citations.txt"
    source.write_text("# commentaire\nPremière.\n\n  Deuxième   citation. \n", encoding="utf-8")
    assert collect_citations("[QUOTE: ignorée]", source) == (["Première.", "Deuxième citation."], "citations.txt")


def test_noms_de_sortie_sans_chemin(tmp_path):
    from studio_core.config import normalize_config
    from studio_core.errors import ConfigError

    for bad in ["..", "../..", "", "/tmp/x.zip", "a/b.zip", "a\\b.zip"]:
        with pytest.raises(ConfigError):
            normalize_config({"release_name": bad})


def test_projet_sans_citation_genere_quand_meme(tmp_path):
    project = studio_core.create_project(tmp_path, "Livre vide")
    results = studio_core.build_archive(project)
    assert results["visuals"] == []
    assert results["zip"].is_file()


def test_citations_txt_vide_retombe_sur_le_manuscrit(tmp_path):
    source = tmp_path / "citations.txt"
    source.write_text("# seulement un commentaire\n", encoding="utf-8")
    assert collect_citations("[CALLOUT: Idée forte]", source) == (["Idée forte"], "le manuscrit")


def test_open_project_nom_accentue(tmp_path):
    (tmp_path / "livre-été").mkdir()
    (tmp_path / "livre-été" / "manuscrit.txt").write_text("# A\n", encoding="utf-8")
    assert studio_core.open_project(tmp_path, "livre-été").slug == "livre-été"
