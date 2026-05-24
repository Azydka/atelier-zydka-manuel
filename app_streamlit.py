# -*- coding: utf-8 -*-
"""
Interface locale Streamlit — Atelier Zydka Manuel

V3.2 :
- tableau de bord ;
- édition de config.json ;
- édition / import de manuscrit ;
- génération de l'archive ZIP ;
- téléchargement du ZIP ;
- consultation des exports ;
- gestion de projets privés dans private/projets/.

Lancement :
python3 -m streamlit run app_streamlit.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import streamlit as st

from project_manager import (
    create_project,
    get_project_summary,
    list_projects,
    load_project_to_active_files,
    read_project_config,
    read_project_manuscript,
    save_active_files_to_project,
    save_project,
)

from restore_demo import main as restore_public_demo


ROOT = Path(__file__).resolve().parent

CONFIG_PATH = ROOT / "config.json"
MANUSCRIPT_PATH = ROOT / "manuscrit_beatmakers.txt"

ZIP_PATH = ROOT / "dist" / "atelier-zydka-manuel-release.zip"
REPORT_PATH = ROOT / "exports" / "rapports" / "rapport_structure.md"
QUALITY_REPORT_PATH = ROOT / "exports" / "rapports" / "rapport_qualite.md"
CITATIONS_PATH = ROOT / "exports" / "reseaux" / "citations" / "citations_extraites.md"

PDF_DIR = ROOT / "manuelsortie"
TEASER_DIR = ROOT / "exports" / "pdf"
VISUALS_DIR = ROOT / "exports" / "reseaux" / "cartes"


st.set_page_config(
    page_title="Atelier Zydka Manuel",
    page_icon="📚",
    layout="wide",
)


# ============================================================
# OUTILS FICHIERS
# ============================================================

def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default

    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_active_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}

    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_active_config(config: dict) -> None:
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


def get_active_project() -> str | None:
    return st.session_state.get("active_private_project")


def set_active_project(project_slug: str | None) -> None:
    st.session_state["active_private_project"] = project_slug


# ============================================================
# HEADER
# ============================================================

st.title("Atelier Zydka Manuel")
st.caption("Interface locale V3.2 — générateur éditorial avec projets privés")

active_project = get_active_project()

if active_project:
    st.success(f"Projet privé actif : {active_project}")
else:
    st.info("Aucun projet privé chargé. Le moteur utilise les fichiers actifs du dépôt.")


tabs = st.tabs(
    [
        "Tableau de bord",
        "Projets privés",
        "Configuration",
        "Manuscrit",
        "Génération",
        "Exports",
        "Sécurité",
        "Aide",
    ]
)


# ============================================================
# TABLEAU DE BORD
# ============================================================

with tabs[0]:
    st.header("Tableau de bord")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_status_card("Configuration active", CONFIG_PATH)
        render_status_card("Manuscrit actif", MANUSCRIPT_PATH)

    with col2:
        render_status_card("PDF principal", PDF_DIR)
        render_status_card("Teaser PDF", TEASER_DIR)

    with col3:
        render_status_card("Visuels réseaux", VISUALS_DIR)
        render_status_card("Archive ZIP", ZIP_PATH)

    st.divider()

    config = load_active_config()

    st.subheader("Projet actif")

    st.write("**Projet privé chargé :**", active_project or "Aucun")
    st.write("**Titre du livre :**", config.get("book_title", "Non défini"))
    st.write("**Auteur :**", config.get("author_name", "Non défini"))
    st.write("**Marque :**", config.get("brand_name", "Non défini"))
    st.write("**ZIP :**", config.get("zip_name", "atelier-zydka-manuel-release.zip"))

    st.divider()

    st.subheader("Règle de sécurité")

    st.warning(
        "Les vrais manuscrits commerciaux doivent être stockés dans private/projets/. "
        "Le dépôt public doit conserver uniquement un manuscrit de démonstration."
    )


# ============================================================
# PROJETS PRIVÉS
# ============================================================

with tabs[1]:
    st.header("Projets privés")

    st.write(
        "Les projets privés permettent de travailler sur plusieurs livres sans publier "
        "les manuscrits commerciaux dans le dépôt GitHub."
    )

    st.code(
        "private/projets/nom-du-projet/config.json\n"
        "private/projets/nom-du-projet/manuscrit.txt",
        language="text",
    )

    st.divider()

    st.subheader("Créer un nouveau projet privé")

    with st.form("create_private_project_form"):
        new_project_name = st.text_input(
            "Nom du projet",
            placeholder="Exemple : Beatmaker Indépendant 2027",
        )

        create_submitted = st.form_submit_button("Créer le projet privé")

    if create_submitted:
        if not new_project_name.strip():
            st.error("Merci d’indiquer un nom de projet.")
        else:
            path = create_project(new_project_name)
            set_active_project(path.name)
            load_project_to_active_files(path.name)
            st.success(f"Projet créé et chargé : {path.name}")
            st.rerun()

    st.divider()

    st.subheader("Charger un projet privé existant")

    projects = list_projects()

    if not projects:
        st.info("Aucun projet privé pour le moment.")
    else:
        selected_project = st.selectbox(
            "Projet disponible",
            projects,
            index=projects.index(active_project) if active_project in projects else 0,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Charger ce projet"):
                load_project_to_active_files(selected_project)
                set_active_project(selected_project)
                st.success(f"Projet chargé : {selected_project}")
                st.rerun()

        with col2:
            if st.button("Sauvegarder les fichiers actifs dans ce projet"):
                save_active_files_to_project(selected_project)
                set_active_project(selected_project)
                st.success(f"Fichiers actifs sauvegardés dans : {selected_project}")

        with col3:
            if st.button("Afficher le résumé"):
                summary = get_project_summary(selected_project)
                st.json(summary)

    st.divider()

    st.subheader("Sauvegarde rapide")

    if active_project:
        if st.button("Sauvegarder config + manuscrit dans le projet actif"):
            config = load_active_config()
            manuscript = read_text(MANUSCRIPT_PATH)
            save_project(active_project, config, manuscript)
            st.success(f"Projet sauvegardé : {active_project}")
    else:
        st.info("Chargez ou créez un projet privé pour activer la sauvegarde rapide.")


# ============================================================
# CONFIGURATION
# ============================================================

with tabs[2]:
    st.header("Configuration du projet")

    config = load_active_config()

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
            value=config.get(
                "book_subtitle",
                "Transformer un manuscrit brut en pack éditorial complet",
            ),
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

        save_active_config(new_config)

        if active_project:
            manuscript = read_text(MANUSCRIPT_PATH)
            save_project(active_project, new_config, manuscript)
            st.success(f"config.json enregistré et projet privé sauvegardé : {active_project}")
        else:
            st.success("config.json enregistré.")


# ============================================================
# MANUSCRIT
# ============================================================

with tabs[3]:
    st.header("Manuscrit")

    st.warning(
        "Pour les livres commerciaux, utilisez un projet privé. "
        "Ne poussez jamais un livre complet dans le dépôt public."
    )

    manuscript = read_text(MANUSCRIPT_PATH)

    edited_manuscript = st.text_area(
        "Contenu du manuscrit actif",
        value=manuscript,
        height=520,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Enregistrer le manuscrit"):
            write_text(MANUSCRIPT_PATH, edited_manuscript)

            if active_project:
                config = load_active_config()
                save_project(active_project, config, edited_manuscript)
                st.success(f"Manuscrit enregistré et projet privé sauvegardé : {active_project}")
            else:
                st.success("Manuscrit enregistré dans manuscrit_beatmakers.txt.")

    with col2:
        uploaded_file = st.file_uploader(
            "Importer un fichier .txt ou .md",
            type=["txt", "md"],
        )

        if uploaded_file is not None:
            content = uploaded_file.read().decode("utf-8")
            write_text(MANUSCRIPT_PATH, content)

            if active_project:
                config = load_active_config()
                save_project(active_project, config, content)

            st.success("Fichier importé dans le manuscrit actif.")
            st.rerun()


# ============================================================
# GÉNÉRATION
# ============================================================

with tabs[4]:
    st.header("Génération")

    st.write("Commande utilisée :")
    st.code("python3 make.py archive", language="bash")

    if active_project:
        st.info(
            f"Projet privé actif : {active_project}. "
            "La génération utilise les fichiers actifs chargés depuis ce projet."
        )

    if st.button("Générer l’archive ZIP", type="primary"):
        if active_project:
            config = load_active_config()
            manuscript = read_text(MANUSCRIPT_PATH)
            save_project(active_project, config, manuscript)

        with st.spinner("Génération en cours..."):
            code, output = run_command([sys.executable, "make.py", "archive"])

        if code == 0:
            st.success("Archive générée avec succès.")
        else:
            st.error(f"Erreur pendant la génération. Code : {code}")

        st.subheader("Logs")
        st.code(output, language="text")

    st.divider()

    config = load_active_config()
    zip_name = config.get("zip_name", "atelier-zydka-manuel-release.zip")
    configured_zip_path = ROOT / "dist" / zip_name

    if configured_zip_path.exists():
        st.success(f"ZIP disponible : {configured_zip_path.name}")

        with configured_zip_path.open("rb") as file:
            st.download_button(
                label="Télécharger le ZIP",
                data=file,
                file_name=configured_zip_path.name,
                mime="application/zip",
            )
    elif ZIP_PATH.exists():
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


# ============================================================
# EXPORTS
# ============================================================

with tabs[5]:
    st.header("Exports")

    st.subheader("Rapport éditorial")

    if REPORT_PATH.exists():
        st.markdown(read_text(REPORT_PATH))
    else:
        st.info("Rapport non généré.")

    st.subheader("Rapport qualité éditorial")

    if QUALITY_REPORT_PATH.exists():
        st.markdown(read_text(QUALITY_REPORT_PATH))
    else:
        st.info("Rapport qualité non généré.")

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
                "private/projets/",
            ]
        ),
        language="text",
    )


# ============================================================
# SÉCURITÉ
# ============================================================

with tabs[6]:
    st.header("Sécurité")

    st.warning(
        "Cette section permet de restaurer la démo publique avant un commit ou un push GitHub. "
        "Elle remplace config.json et manuscrit_beatmakers.txt par les fichiers de démonstration."
    )

    st.subheader("Restaurer la démo publique")

    st.write(
        "À utiliser après avoir travaillé sur un projet privé, afin d’éviter de laisser "
        "un vrai manuscrit commercial dans les fichiers actifs du dépôt."
    )

    st.code(
        "demo/config.demo.json → config.json\n"
        "demo/manuscrit_demo.txt → manuscrit_beatmakers.txt",
        language="text",
    )

    confirm_restore = st.checkbox(
        "Je confirme vouloir restaurer la démo publique dans les fichiers actifs."
    )

    if st.button("Restaurer la démo publique", type="primary"):
        if not confirm_restore:
            st.error("Cochez la confirmation avant de restaurer la démo.")
        else:
            try:
                restore_public_demo()
                set_active_project(None)
                st.success("Démo publique restaurée. Aucun projet privé n’est désormais chargé.")
                st.info("Avant de pousser sur GitHub, vérifiez quand même le Terminal avec : git status")
            except Exception as error:
                st.error(f"Erreur pendant la restauration : {error}")

    st.divider()

    st.subheader("Rappel important")

    st.markdown(
        """
- `private/projets/` contient vos vrais projets.
- `config.json` et `manuscrit_beatmakers.txt` sont les fichiers actifs du moteur.
- Avant un `git add` ou un `git push`, restaurez la démo publique si vous avez chargé un projet privé.
- Vérifiez toujours avec :

        git status
        """
    )


# ============================================================
# AIDE
# ============================================================

with tabs[7]:
    st.header("Aide")

    st.markdown(
        """
### Utilisation rapide

1. Ouvrez l’onglet **Projets privés**.
2. Créez ou chargez un projet privé.
3. Ouvrez l’onglet **Configuration**.
4. Modifiez le titre, l’auteur, la marque, les couleurs.
5. Ouvrez l’onglet **Manuscrit**.
6. Collez ou importez un manuscrit.
7. Ouvrez l’onglet **Génération**.
8. Cliquez sur **Générer l’archive ZIP**.
9. Téléchargez le ZIP.

### Règle importante

Le dépôt public doit contenir une démo.

Les vrais livres ou contenus commerciaux doivent rester dans :

    private/projets/

### Commande Terminal équivalente

    python3 make.py archive
        """
    )
