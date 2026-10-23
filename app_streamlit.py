# -*- coding: utf-8 -*-
"""
Interface locale Streamlit — Manuscript Studio by Atelier Zydka

Interface au-dessus du moteur studio_core. Chaque livre est un projet
(un dossier) dans la racine des projets (Documents/Manuscript Studio par
défaut, ou la variable d'environnement MANUSCRIPT_STUDIO_HOME). Le moteur
lit et écrit uniquement dans le dossier du projet sélectionné.

Lancement :
python3 -m streamlit run app_streamlit.py
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

import studio_core
from studio_core.config import OUTPUT_NAME_KEYS, normalize_config
from studio_core.pdf_book import cover_text_defaults
from studio_core.project import DEMO_SLUG
from studio_core.report_quality import REPORT_NAME as QUALITY_REPORT_NAME, SCORE_NAME
from studio_core.report_structure import REPORT_NAME as STRUCTURE_REPORT_NAME


PROJECTS_ROOT = studio_core.default_projects_root()

CONFIG_FIELDS = [
    ("project_title", "Titre du projet"),
    ("book_title", "Titre du livre"),
    ("book_subtitle", "Sous-titre"),
    ("author_name", "Auteur"),
    ("brand_name", "Marque"),
    ("baseline", "Baseline"),
    ("year", "Année"),
]

OUTPUT_FIELDS = [
    ("output_pdf_name", "Nom du PDF principal"),
    ("teaser_pdf_name", "Nom du teaser PDF"),
    ("release_name", "Nom du dossier de release"),
    ("zip_name", "Nom du ZIP"),
]

COVER_FIELDS = [
    ("cover_kicker", "Accroche au-dessus du titre"),
    ("cover_footer_left", "Pied de couverture (gauche)"),
    ("cover_footer_right", "Pied de couverture (droite)"),
    ("back_cover_tagline", "Phrase de 4e de couverture"),
    ("back_cover_footer_left", "Pied de 4e de couverture (gauche)"),
    ("back_cover_footer_right", "Pied de 4e de couverture (droite)"),
]

THEME_FIELDS = [
    ("background", "Couleur de fond"),
    ("text", "Couleur du texte"),
    ("accent", "Couleur accent"),
    ("muted", "Couleur secondaire"),
]


st.set_page_config(
    page_title="Manuscript Studio by Atelier Zydka",
    page_icon="📚",
    layout="wide",
)


# ============================================================
# OUTILS
# ============================================================

def read_text(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8") if path.exists() else default


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_raw_config(project: studio_core.Project) -> dict:
    """config.json tel qu'écrit par l'utilisateur (sans les valeurs par défaut)."""
    try:
        return json.loads(read_text(project.config_file, "{}"))
    except json.JSONDecodeError:
        return {}


def save_config(project: studio_core.Project, config: dict) -> None:
    write_text(project.config_file, json.dumps(config, indent=2, ensure_ascii=False) + "\n")


def get_active_project() -> studio_core.Project | None:
    slug = st.session_state.get("active_project")
    if not slug:
        return None
    project = studio_core.Project(PROJECTS_ROOT / slug)
    return project if project.exists() else None


def load_config_or_default(project: studio_core.Project) -> dict:
    """Config du projet ; si config.json est invalide, affiche l'erreur et utilise les valeurs par défaut."""
    try:
        return project.load_config()
    except studio_core.ConfigError as error:
        st.error(f"config.json invalide ({error}). Corrigez-le dans l’onglet Configuration.")
        return normalize_config({})


def set_active_project(project: studio_core.Project | None) -> None:
    st.session_state["active_project"] = project.slug if project else None


def render_status_card(label: str, path: Path) -> None:
    icon = "✅" if path.exists() else "❌"
    st.write(f"{icon} **{label}**")
    st.caption(str(path))


def load_quality_score(project: studio_core.Project) -> dict | None:
    try:
        return json.loads(read_text(project.reports_dir / SCORE_NAME, "null"))
    except json.JSONDecodeError:
        return None


def run_with_progress(build, project: studio_core.Project) -> dict | None:
    """Lance une génération studio_core avec une barre de progression."""
    bar = st.progress(0.0, text="Préparation…")

    def on_progress(message: str, step: int, total: int) -> None:
        bar.progress(step / total, text=f"{step}/{total} — {message}")

    try:
        results = build(project, on_progress=on_progress)
    except studio_core.CheckFailedError as error:
        st.error("Le check a détecté une erreur bloquante.")
        st.code(str(error), language="text")
        return None
    except studio_core.StudioError as error:
        st.error(f"Erreur pendant la génération : {error}")
        return None

    bar.progress(1.0, text="Terminé")
    return results


# ============================================================
# EN-TÊTE
# ============================================================

st.title("Manuscript Studio by Atelier Zydka")
st.caption(f"Racine des projets : {PROJECTS_ROOT}")

project = get_active_project()

if project:
    st.success(f"Projet actif : {project.slug} — {project.root}")
else:
    st.info("Aucun projet chargé. Créez ou ouvrez un projet dans l’onglet Projets.")


tabs = st.tabs(
    [
        "Tableau de bord",
        "Projets",
        "Configuration",
        "Manuscrit",
        "Génération",
        "Exports",
        "Aide",
    ]
)


# ============================================================
# TABLEAU DE BORD
# ============================================================

with tabs[0]:
    st.header("Tableau de bord")

    if not project:
        st.info("Chargez un projet pour voir son état.")
    else:
        config = load_config_or_default(project)

        col1, col2, col3 = st.columns(3)

        with col1:
            render_status_card("Configuration", project.config_file)
            render_status_card("Manuscrit", project.manuscript)

        with col2:
            render_status_card("PDF principal", project.pdf_dir / config["output_pdf_name"])
            render_status_card("Teaser PDF", project.pdf_dir / config["teaser_pdf_name"])

        with col3:
            render_status_card("Visuels réseaux", project.cards_dir)
            render_status_card("Archive ZIP", project.exports_dir / config["zip_name"])

        st.divider()

        st.subheader("Projet actif")
        st.write("**Titre du livre :**", config["book_title"])
        st.write("**Auteur :**", config["author_name"])
        st.write("**Marque :**", config["brand_name"])
        st.write("**ZIP :**", config["zip_name"])

        st.divider()

        st.subheader("Score qualité éditorial")

        col_score, col_action = st.columns([2, 1])

        with col_action:
            if st.button("Rafraîchir le diagnostic qualité"):
                try:
                    with st.spinner("Diagnostic qualité en cours..."):
                        studio_core.build_quality(project)
                    st.success("Diagnostic qualité mis à jour.")
                    st.rerun()
                except studio_core.StudioError as error:
                    st.error(f"Erreur pendant le diagnostic qualité : {error}")

        with col_score:
            quality_score = load_quality_score(project)

            if quality_score:
                score = int(quality_score.get("score", 0))
                label = quality_score.get("label", "statut inconnu")

                st.metric("Score qualité", f"{score}/100", label)

                if score < 60:
                    st.error("Score bas. Consultez l’onglet Exports pour corriger le manuscrit.")
                elif score < 80:
                    st.warning("Score moyen. Des améliorations sont recommandées.")
                else:
                    st.success("Bon score. Le manuscrit semble exploitable pour une génération.")
            else:
                st.info("Aucun score qualité généré. Cliquez sur Rafraîchir le diagnostic qualité ou générez une archive.")


# ============================================================
# PROJETS
# ============================================================

with tabs[1]:
    st.header("Projets")

    st.write(
        "Chaque livre est un dossier indépendant : manuscrit, configuration, images "
        "et exports. Rien n’est écrit dans le dossier de l’application."
    )

    st.code(
        "<projet>/config.json\n"
        "<projet>/manuscrit.txt\n"
        "<projet>/citations.txt   (facultatif)\n"
        "<projet>/images/\n"
        "<projet>/exports/",
        language="text",
    )

    st.divider()

    st.subheader("Ouvrir un projet")

    projects = studio_core.list_projects(PROJECTS_ROOT)

    if not projects:
        st.info("Aucun projet pour le moment.")
    else:
        slugs = [p.slug for p in projects]
        selected = st.selectbox(
            "Projet disponible",
            slugs,
            index=slugs.index(project.slug) if project and project.slug in slugs else 0,
        )

        if st.button("Ouvrir ce projet"):
            set_active_project(studio_core.Project(PROJECTS_ROOT / selected))
            st.rerun()

    st.divider()

    st.subheader("Créer un projet")

    with st.form("create_project_form"):
        new_project_name = st.text_input("Titre du livre", placeholder="Exemple : Mon premier livre")
        create_submitted = st.form_submit_button("Créer le projet")

    if create_submitted:
        if not new_project_name.strip():
            st.error("Merci d’indiquer un titre.")
        else:
            try:
                created = studio_core.create_project(PROJECTS_ROOT, new_project_name.strip())
                set_active_project(created)
                st.rerun()
            except studio_core.StudioError as error:
                st.error(str(error))

    if not studio_core.Project(PROJECTS_ROOT / DEMO_SLUG).exists():
        if st.button("Créer le projet de démonstration"):
            set_active_project(studio_core.create_demo_project(PROJECTS_ROOT))
            st.rerun()


# ============================================================
# CONFIGURATION
# ============================================================

with tabs[2]:
    st.header("Configuration du projet")

    if not project:
        st.info("Chargez un projet pour modifier sa configuration.")
    else:
        raw_config = read_raw_config(project)
        try:
            config = normalize_config(raw_config)
        except studio_core.ConfigError as error:
            st.warning(f"{error} — valeurs par défaut proposées pour les noms de sortie.")
            config = normalize_config({k: v for k, v in raw_config.items() if k not in OUTPUT_NAME_KEYS})

        with st.form("config_form"):
            values = {key: st.text_input(label, value=config[key]) for key, label in CONFIG_FIELDS}

            st.subheader("Fichiers de sortie")
            values.update({key: st.text_input(label, value=config[key]) for key, label in OUTPUT_FIELDS})

            st.subheader("Couverture")
            st.caption("Un champ vide n’affiche rien sur la couverture.")
            cover_defaults = cover_text_defaults(config)
            values.update(
                {key: st.text_input(label, value=str(config.get(key, cover_defaults[key]))) for key, label in COVER_FIELDS}
            )

            st.subheader("Thème")
            theme = {key: st.color_picker(label, value=config["theme"][key]) for key, label in THEME_FIELDS}

            submitted = st.form_submit_button("Enregistrer config.json")

        if submitted:
            # Les clés non éditées ici (features, language…) sont conservées.
            new_config = {**raw_config, **values, "theme": {**raw_config.get("theme", {}), **theme}}
            # Un texte de couverture resté à sa valeur par défaut n'est pas figé dans config.json :
            # il continue de suivre baseline / book_subtitle.
            for key, _ in COVER_FIELDS:
                if key not in raw_config and new_config[key] == cover_defaults[key]:
                    del new_config[key]
            try:
                normalize_config(new_config)
            except studio_core.ConfigError as error:
                st.error(str(error))
            else:
                save_config(project, new_config)
                st.success(f"config.json enregistré : {project.config_file}")


# ============================================================
# MANUSCRIT
# ============================================================

with tabs[3]:
    st.header("Manuscrit")

    if not project:
        st.info("Chargez un projet pour éditer son manuscrit.")
    else:
        edited_manuscript = st.text_area(
            "Contenu du manuscrit",
            value=read_text(project.manuscript),
            height=520,
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Enregistrer le manuscrit"):
                write_text(project.manuscript, edited_manuscript)
                st.success(f"Manuscrit enregistré : {project.manuscript}")

        with col2:
            uploaded_file = st.file_uploader("Importer un fichier .txt ou .md", type=["txt", "md"])

            # Le fichier reste dans l'uploader entre deux exécutions : on ne l'importe qu'une fois.
            if uploaded_file is not None and st.session_state.get("imported_upload") != uploaded_file.file_id:
                write_text(project.manuscript, uploaded_file.read().decode("utf-8"))
                st.session_state["imported_upload"] = uploaded_file.file_id
                st.rerun()


# ============================================================
# GÉNÉRATION
# ============================================================

with tabs[4]:
    st.header("Génération")

    if not project:
        st.info("Chargez un projet pour lancer une génération.")
    else:
        st.write("Commande Terminal équivalente :")
        st.code(f'python3 make.py --project "{project.root}" archive', language="bash")

        if st.button("Générer l’archive ZIP", type="primary"):
            results = run_with_progress(studio_core.build_archive, project)
            if results:
                st.success(f"Archive générée : {results['zip']}")

        st.divider()

        zip_path = project.exports_dir / load_config_or_default(project)["zip_name"]

        if zip_path.exists():
            st.success(f"ZIP disponible : {zip_path.name}")

            with zip_path.open("rb") as file:
                st.download_button(
                    label="Télécharger le ZIP",
                    data=file,
                    file_name=zip_path.name,
                    mime="application/zip",
                )
        else:
            st.info("Aucune archive ZIP générée pour l’instant.")


# ============================================================
# EXPORTS
# ============================================================

with tabs[5]:
    st.header("Exports")

    if not project:
        st.info("Chargez un projet pour consulter ses exports.")
    else:
        for title, path in [
            ("Rapport éditorial", project.reports_dir / STRUCTURE_REPORT_NAME),
            ("Rapport qualité éditorial", project.reports_dir / QUALITY_REPORT_NAME),
            ("Citations marketing", project.citations_file),
        ]:
            st.subheader(title)
            if path.exists():
                st.markdown(read_text(path))
            else:
                st.info("Non généré.")

        st.subheader("Dossier des exports")
        st.code(str(project.exports_dir), language="text")


# ============================================================
# AIDE
# ============================================================

with tabs[6]:
    st.header("Aide")

    st.markdown(
        f"""
### Utilisation rapide

1. Ouvrez l’onglet **Projets** et créez ou ouvrez un projet.
2. Ouvrez l’onglet **Configuration** : titre, auteur, marque, couleurs.
3. Ouvrez l’onglet **Manuscrit** : collez ou importez le texte.
4. Ouvrez l’onglet **Génération** et cliquez sur **Générer l’archive ZIP**.
5. Téléchargez le ZIP.

### Où sont mes fichiers ?

Chaque projet est un dossier dans :

    {PROJECTS_ROOT}

Pour changer cette racine, définissez la variable d’environnement
`MANUSCRIPT_STUDIO_HOME` avant de lancer l’application.

### Citations marketing

Ajoutez un fichier `citations.txt` (une citation par ligne) dans le dossier
du projet. Sans ce fichier, les citations viennent des blocs `[QUOTE: …]`
et des lignes « À retenir : … » du manuscrit.

### Commande Terminal équivalente

    python3 make.py --project <projet> archive
        """
    )
