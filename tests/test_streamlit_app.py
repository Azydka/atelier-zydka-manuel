"""Test de fumée de l'interface Streamlit : création du projet démo puis génération de l'archive."""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "app_streamlit.py")


def click(at, label_start):
    button = next(b for b in at.button if b.label.startswith(label_start))
    at = button.click().run()
    assert not at.exception, at.exception
    return at


def test_demo_puis_archive(tmp_path, monkeypatch):
    monkeypatch.setenv("MANUSCRIPT_STUDIO_HOME", str(tmp_path))

    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception, at.exception

    at = click(at, "Créer le projet de démonstration")
    at = click(at, "Générer")

    assert not at.error
    assert list((tmp_path / "demo" / "exports").glob("*.zip"))
