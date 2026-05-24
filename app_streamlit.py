# -*- coding: utf-8 -*-
"""
Interface locale Streamlit — Atelier Zydka Manuel

V3.0 MVP :
- afficher et modifier config.json ;
- afficher et modifier le manuscrit de démonstration ;
- lancer python3 make.py archive ;
- afficher les logs ;
- proposer le téléchargement du ZIP généré.

Lancement :
python3 -m streamlit run app_streamlit.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
MANUSCRIPT_PATH = ROOT / "manuscrit_beatmakers.txt"
ZIP_PATH = ROOT / "dist" / "atelier-zydka-manuel-release.zip"
REPORT_PATH = ROOT / "exports" / "rapports" / "rapport_structure.md"
CITATIONS_PATH = ROOT / "exports" / "reseaux" / "citations" / "citations_extraites.md"
PDF_DIR = ROOT / "manuelsortie"
TEASER_DIR = ROOT / "exports" / "pdf"
VISUALS_DIR = ROOT / "exports" / "reseaux" / "cartes"


st.set_page_config(
    page_title="Atelier Zydka Manuel",
    page_icon="📚",
    layout="wide",
)


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}

    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_config(config: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def run_command(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    output = ""

    if result.stdout:
        output += result.stdout

    if result.stderr:
        output += "\n--- STDERR ---\n"
        output += result.stderr

    return result.returncode, output


def render_status_card(label: str, path: Path) -> None:
    exists = path.exists()
    icon = "✅" if exists else "❌"
    st.write(f"{icon} **{label}**")
    st.caption(str(path.relative_to(ROOT)))


st.title("Atelier Zydka Manuel")
st.caption("Interface locale V3.0 MVP — générateur éditorial PDF / teaser / visuels / ZIP")

tabs = st.tabs(
    [
        "Tableau de bord",
        "Configuration",
        "Manuscrit",
        "Génération",
        "Exports",
        "Aide",
    ]
)


with tabs[0]:
    st.header("Tableau de bord")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_status_card("Configuration", CONFIG_PATH)
        render_status_card("Manuscrit", MANUSCRIPT_PATH)

    with col2:
        render_status_card("PDF principal", PDF_DIR)
        render_status_card("Teaser PDF", TEASER_DIR)

    with col3:
        render_status_card("Visuels réseaux", VISUALS_DIR)
        render_status_card("Archive ZIP", ZIP_PATH)

    st.divider()

    config = load_config()

    st.subheader("Projet actuel")

    st.write("**Titre du livre :**", config.get("book_title", "Non défini"))
    st.write("**Auteur :**", config.get("author_name", "Non défini"))
    st.write("**Marque :**", config.get("brand_name", "Non défini"))
    st.write("**ZIP :**", config.get("zip_name", "atelier-zydka-manuel-release.zip"))


with tabs[1]:
    st.header("Configuration du projet")

    config = load_config()

    with st.form("config_form"):
        project_title = st.text_input(
            "Titre du projet",
            value=config.get("project_title", "Atelier Zydka Manuel"),
        )

        book_title = st.text_input(
            "Titre du livre",
            value=config.get("book_title", "Manuscrit de démonstration"),
        )

        book_subtitle = st.text_area(
            "Sous-titre",
            value=config.get("book_subtitle", "Transformer un manuscrit brut en pack éditorial complet"),
            height=80,
        )

        author_name = st.text_input(
            "Auteur",
            value=config.get("author_name", "Atelier Zydka"),
        )

        brand_name = st.text_input(
            "Marque",
            value=config.get("brand_name", "Atelier Zydka"),
        )

        baseline = st.text_input(
            "Baseline",
            value=config.get("baseline", "Culture · méthode · indépendance"),
        )

        year = st.text_input(
            "Année",
            value=config.get("year", "2026"),
        )

        st.subheader("Fichiers de sortie")

        output_pdf_name = st.text_input(
            "Nom du PDF principal",
            value=config.get("output_pdf_name", "manuel-de-presence-atelier-zydka.pdf"),
        )

        teaser_pdf_name = st.text_input(
            "Nom du teaser PDF",
            value=config.get("teaser_pdf_name", "teaser-manuel-presence.pdf"),
        )

        release_name = st.text_input(
            "Nom du dossier de release",
            value=config.get("release_name", "atelier-zydka-manuel-release"),
        )

        zip_name = st.text_input(
            "Nom du ZIP",
            value=config.get("zip_name", "atelier-zydka-manuel-release.zip"),
        )

        st.subheader("Thème")

        theme = config.get("theme", {})

        background = st.color_picker(
            "Couleur de fond",
            value=theme.get("background", "#090909"),
        )

        text_color = st.color_picker(
            "Couleur du texte",
            value=theme.get("text", "#F4F1EB"),
        )

        accent = st.color_picker(
            "Couleur accent",
            value=theme.get("accent", "#C79A3B"),
        )

        muted = st.color_picker(
            "Couleur secondaire",
            value=theme.get("muted", "#96928A"),
        )

        submitted = st.form_submit_button("Enregistrer config.json")

    if submitted:
        new_config = {
            "project_title": project_title,
            "book_title": book_title,
            "book_subtitle": book_subtitle,
            "author_name": author_name,
            "brand_name": brand_name,
            "baseline": baseline,
            "year": year,
            "language": config.get("language", "fr"),
            "output_pdf_name": output_pdf_name,
            "teaser_pdf_name": teaser_pdf_name,
            "release_name": release_name,
            "zip_name": zip_name,
            "theme": {
                "background": background,
                "text": text_color,
                "accent": accent,
                "muted": muted,
            },
        }

        save_config(new_config)
        st.success("config.json enregistré.")


with tabs[2]:
    st.header("Manuscrit")

    st.warning(
        "Ne colle pas ici un livre complet si tu comptes pousser le dépôt public sur GitHub. "
        "Pour les livres commerciaux, travaille plutôt dans private/ ou sur une copie locale non publiée."
    )

    manuscript = read_text(MANUSCRIPT_PATH)

    edited_manuscript = st.text_area(
        "Contenu de manuscrit_beatmakers.txt",
        value=manuscript,
        height=520,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Enregistrer le manuscrit"):
            write_text(MANUSCRIPT_PATH, edited_manuscript)
            st.success("Manuscrit enregistré.")

    with col2:
        uploaded_file = st.file_uploader(
            "Importer un fichier .txt ou .md",
            type=["txt", "md"],
        )

        if uploaded_file is not None:
            content = uploaded_file.read().decode("utf-8")
            write_text(MANUSCRIPT_PATH, content)
            st.success("Fichier importé dans manuscrit_beatmakers.txt.")
            st.rerun()


with tabs[3]:
    st.header("Génération")

    st.write("Commande recommandée :")
    st.code("python3 make.py archive", language="bash")

    if st.button("Générer l’archive ZIP", type="primary"):
        with st.spinner("Génération en cours..."):
            code, output = run_command([sys.executable, "make.py", "archive"])

        if code == 0:
            st.success("Archive générée avec succès.")
        else:
            st.error(f"Erreur pendant la génération. Code : {code}")

        st.subheader("Logs")
        st.code(output, language="text")

    st.divider()

    if ZIP_PATH.exists():
        st.success("ZIP disponible")

        with ZIP_PATH.open("rb") as file:
            st.download_button(
                label="Télécharger le ZIP",
                data=file,
                file_name=ZIP_PATH.name,
                mime="application/zip",
            )
    else:
        st.info("Aucune archive ZIP générée pour l’instant.")


with tabs[4]:
    st.header("Exports")

    st.subheader("Rapport éditorial")

    if REPORT_PATH.exists():
        st.markdown(read_text(REPORT_PATH))
    else:
        st.info("Rapport non généré.")

    st.subheader("Citations marketing")

    if CITATIONS_PATH.exists():
        st.markdown(read_text(CITATIONS_PATH))
    else:
        st.info("Citations non générées.")

    st.subheader("Dossiers utiles")

    st.code(
        "\n".join(
            [
                "manuelsortie/",
                "exports/pdf/",
                "exports/reseaux/cartes/",
                "dist/",
            ]
        ),
        language="text",
    )


with tabs[5]:
    st.header("Aide")

    st.markdown(
        """
### Utilisation rapide

1. Ouvre l’onglet **Configuration**
2. Modifie le titre, l’auteur, la marque, les couleurs
3. Ouvre l’onglet **Manuscrit**
4. Colle ou importe un manuscrit de test
5. Ouvre l’onglet **Génération**
6. Clique sur **Générer l’archive ZIP**
7. Télécharge le ZIP

### Règle importante

Le dépôt public doit contenir une démo.

Les vrais livres ou contenus commerciaux doivent rester dans :

    private/

### Commande Terminal équivalente

    python3 make.py archive
        """
    )
