# Installation — Manuscript Studio by Atelier Zydka

## Prérequis

Manuscript Studio by Atelier Zydka nécessite :

- Python 3 ;
- pip ;
- un ordinateur Mac, Linux ou Windows ;
- un navigateur web.

---

## Installer les dépendances

Depuis le dossier du projet :

    python3 -m pip install -r requirements.txt

Cette commande installe les bibliothèques nécessaires, notamment :

- Streamlit ;
- Pillow ;
- ReportLab.

---

## Lancer l'interface

Méthode principale :

    python3 -m streamlit run app_streamlit.py

Méthode avec script :

    ./launch_app.sh

Sur Mac, vous pouvez aussi essayer :

    launch_app.command

---

## Si Streamlit n'est pas reconnu

Essayez :

    python3 -m pip install streamlit

Puis relancez :

    python3 -m streamlit run app_streamlit.py

---

## Si macOS bloque launch_app.command

Utilisez plutôt :

    ./launch_app.sh

Ou lancez directement :

    python3 -m streamlit run app_streamlit.py

---

## Vérifier que tout fonctionne

Lancez :

    python3 make.py archive

Si tout fonctionne, une archive ZIP est créée ici :

    dist/atelier-zydka-manuel-release.zip

---

Fin du document.
