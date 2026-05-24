# Commencez ici — Atelier Zydka Manuel

Bienvenue dans Atelier Zydka Manuel.

Cet outil permet de transformer un manuscrit en pack éditorial complet :

- PDF principal ;
- teaser PDF ;
- citations marketing ;
- visuels réseaux sociaux ;
- rapport éditorial ;
- archive ZIP prête à diffuser.

---

## 1. Installation rapide

Installez les dépendances :

    python3 -m pip install -r requirements.txt

---

## 2. Lancer l'application

### Méthode recommandée

Sur Mac ou Linux :

    ./launch_app.sh

### Sur Mac

Vous pouvez aussi essayer de double-cliquer sur :

    launch_app.command

Si macOS bloque le fichier, utilisez la méthode Terminal :

    ./launch_app.sh

### Méthode directe

    python3 -m streamlit run app_streamlit.py

L'application s'ouvre dans le navigateur à l'adresse :

    http://localhost:8501

---

## 3. Utilisation simple

Dans l'interface :

1. Ouvrez l'onglet Configuration.
2. Modifiez le titre, l'auteur, la marque et les couleurs.
3. Ouvrez l'onglet Manuscrit.
4. Collez ou importez un manuscrit `.txt` ou `.md`.
5. Ouvrez l'onglet Génération.
6. Cliquez sur Générer l'archive ZIP.
7. Téléchargez le ZIP généré.

---

## 4. Fichier final

Le fichier final est généré ici :

    dist/atelier-zydka-manuel-release.zip

---

## 5. Important

Le dépôt public contient un manuscrit de démonstration.

Les vrais livres, manuscrits commerciaux ou contenus privés doivent rester dans un dossier local non versionné :

    private/

Ne publiez pas vos livres complets dans le dépôt public.

---

## 6. Documentation utile

À lire ensuite :

- README.md
- docs/GUIDE_UTILISATEUR.md
- docs/FAQ.md
- docs/BETA_TEST.md
- LICENSE.md

---

Fin du document.
