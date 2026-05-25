# Quickstart — Manuscript Studio by Atelier Zydka

## Objectif

Générer rapidement un premier pack éditorial.

---

## Étape 1 — Installer

    python3 -m pip install -r requirements.txt

---

## Étape 2 — Lancer l'application

    ./launch_app.sh

Ou :

    python3 -m streamlit run app_streamlit.py

---

## Étape 3 — Configurer le projet

Dans l'interface :

- ouvrez l'onglet Configuration ;
- modifiez le titre ;
- modifiez l'auteur ;
- modifiez la marque ;
- choisissez les couleurs ;
- enregistrez.

---

## Étape 4 — Ajouter un manuscrit

Dans l'onglet Manuscrit :

- collez votre texte ;
- ou importez un fichier `.txt` ou `.md`.

Attention : pour un dépôt public, utilisez seulement un texte de démonstration.

---

## Étape 5 — Générer

Dans l'onglet Génération :

- cliquez sur Générer l'archive ZIP ;
- attendez la fin des logs ;
- téléchargez le ZIP.

---

## Étape 6 — Vérifier les exports

Le ZIP contient notamment :

- PDF principal ;
- teaser PDF ;
- citations marketing ;
- visuels réseaux sociaux ;
- rapport éditorial ;
- documentation.

---

## Commande alternative

Sans interface :

    python3 make.py archive

---

Fin du document.
