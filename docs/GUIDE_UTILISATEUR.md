# Guide utilisateur — Atelier Zydka Manuel

Version : V2.1  
Projet : Atelier Zydka Manuel  
Statut : Packaging éditorial propre  
Dernière mise à jour : 23/05/2026

---

## 1. Présentation

**Atelier Zydka Manuel** est un système éditorial local qui transforme un manuscrit source en pack éditorial complet.

À partir d’un fichier texte principal, l’outil peut générer :

- un PDF principal ;
- un teaser PDF ;
- un rapport éditorial ;
- des citations marketing ;
- des visuels réseaux sociaux ;
- un dossier de release ;
- une archive ZIP transmissible.

L’objectif est de transformer une matière brute en produit éditorial complet, diffusable et testable.

---

## 2. À qui s’adresse cet outil ?

Atelier Zydka Manuel s’adresse à :

- un auteur indépendant ;
- un créateur de guide pratique ;
- un beatmaker ou producteur musical ;
- un formateur ;
- un studio créatif ;
- une agence éditoriale ;
- un entrepreneur qui veut transformer un contenu long en produit PDF.

Dans sa version actuelle, le projet est encore un outil local. Il s’utilise depuis le Terminal avec des commandes Python.

---

## 3. Ce que le projet génère

Après génération complète, le projet peut produire :

```text
manuelsortie/manuel-de-presence-atelier-zydka.pdf
exports/pdf/teaser-manuel-presence.pdf
exports/rapports/rapport_structure.md
exports/reseaux/citations/citations_extraites.md
exports/reseaux/cartes/
dist/atelier-zydka-manuel-release/
dist/atelier-zydka-manuel-release.zip

---

## Personnaliser le projet avec config.json

Depuis la V2.2, le fichier suivant permet de personnaliser une partie du projet :

    config.json

Ce fichier permet notamment de modifier :

- le titre du projet ;
- le titre du livre ;
- le sous-titre ;
- le nom de l’auteur ;
- le nom de marque ;
- la baseline ;
- l’année ;
- le nom du PDF principal ;
- le nom du teaser PDF ;
- le nom du dossier de release ;
- le nom du ZIP ;
- les couleurs principales.

Exemple de champs utiles :

    "book_title": "Mon guide",
    "book_subtitle": "Transformer une idée en produit éditorial",
    "author_name": "Nom de l’auteur",
    "brand_name": "Ma marque",
    "baseline": "Créer · publier · diffuser",
    "zip_name": "mon-guide-release.zip"

Après modification de config.json, relancez :

    python3 make.py archive

Les changements seront appliqués aux éléments déjà connectés à la configuration :

- archive ZIP ;
- dossier de release ;
- visuels réseaux ;
- teaser PDF ;
- métadonnées du PDF principal ;
- nom du PDF principal.

---

## V2.3 — Personnalisation du PDF principal

Depuis la V2.3, le PDF principal est davantage piloté par `config.json`.

Les éléments suivants peuvent être personnalisés :

- titre affiché sur la couverture ;
- sous-titre ;
- auteur ;
- marque ;
- baseline ;
- année ;
- couleurs principales ;
- nom du fichier PDF.

Exemple :

    {
      "book_title": "Mon guide professionnel",
      "book_subtitle": "Méthode, structure et diffusion",
      "author_name": "Nom de l’auteur",
      "brand_name": "Ma marque",
      "baseline": "Créer · publier · diffuser",
      "year": "2026",
      "output_pdf_name": "mon-guide.pdf"
    }

Après modification, relancez :

    python3 make.py archive

Le PDF principal sera régénéré avec les nouvelles informations.

---

## V3.0 — Utiliser l’interface locale

Depuis la V3.0, il est possible d’utiliser une interface locale Streamlit.

Pour la lancer :

    python3 -m streamlit run app_streamlit.py

L’interface permet de :

- modifier la configuration du projet ;
- modifier le manuscrit ;
- importer un fichier `.txt` ou `.md` ;
- générer l’archive ZIP ;
- télécharger le ZIP ;
- consulter le rapport éditorial ;
- consulter les citations marketing.

### Onglets disponibles

- Tableau de bord ;
- Configuration ;
- Manuscrit ;
- Génération ;
- Exports ;
- Aide.

### Règle importante

Ne collez pas un livre complet dans le manuscrit public si vous comptez pousser le dépôt sur GitHub.

Pour les projets commerciaux, utilisez un dossier local privé non versionné :

    private/

---

## V3.1 — Lancement simplifié

La V3.1 ajoute des fichiers pour lancer plus facilement l’interface locale.

### Installer les dépendances

Avant de lancer l’application, installez les dépendances :

    python3 -m pip install -r requirements.txt

### Méthode 1 — Lancement classique

    python3 -m streamlit run app_streamlit.py

### Méthode 2 — Script de lancement

    ./launch_app.sh

### Méthode 3 — Fichier macOS

Sur Mac, vous pouvez essayer de double-cliquer sur :

    launch_app.command

Si macOS bloque le fichier, utilisez plutôt :

    ./launch_app.sh

### Remarque

L’application reste locale. Elle s’ouvre dans le navigateur, généralement à l’adresse :

    http://localhost:8501

---

## V3.1 — Lancement simplifié

La V3.1 ajoute des fichiers pour lancer plus facilement l’interface locale.

### Installer les dépendances

Avant de lancer l’application, installez les dépendances :

    python3 -m pip install -r requirements.txt

### Méthode 1 — Lancement classique

    python3 -m streamlit run app_streamlit.py

### Méthode 2 — Script de lancement

    ./launch_app.sh

### Méthode 3 — Fichier macOS

Sur Mac, vous pouvez essayer de double-cliquer sur :

    launch_app.command

Si macOS bloque le fichier, utilisez plutôt :

    ./launch_app.sh

### Remarque

L’application reste locale. Elle s’ouvre dans le navigateur, généralement à l’adresse :

    http://localhost:8501

---

## V3.2 — Utiliser les projets privés

La V3.2 ajoute un mode projets privés.

Ce mode permet de travailler sur plusieurs livres sans remplacer définitivement le manuscrit public du dépôt.

### Créer un projet privé

Dans l’interface :

1. Ouvrez l’onglet Projets privés.
2. Entrez le nom du projet.
3. Cliquez sur Créer le projet privé.

Un dossier est créé ici :

    private/projets/nom-du-projet/

Il contient :

    config.json
    manuscrit.txt

### Charger un projet privé

Dans l’onglet Projets privés :

1. Sélectionnez un projet existant.
2. Cliquez sur Charger ce projet.

Le projet devient actif dans l’application.

### Sauvegarder un projet privé

Après modification de la configuration ou du manuscrit, utilisez :

    Sauvegarder config + manuscrit dans le projet actif

### Règle importante

Ne publiez jamais vos vrais manuscrits dans le dépôt public.

Utilisez les projets privés pour les livres commerciaux :

    private/projets/

---

## V3.3 — Restaurer la démo publique

La V3.3 ajoute une sécurité importante avant les commits ou les publications GitHub.

Quand vous chargez un projet privé, ses fichiers peuvent devenir les fichiers actifs du moteur.

Avant de pousser le dépôt public, restaurez la démo publique.

### Méthode interface

Dans l’application Streamlit :

1. ouvrez l’onglet Sécurité ;
2. cochez la case de confirmation ;
3. cliquez sur Restaurer la démo publique ;
4. ouvrez le Terminal ;
5. vérifiez :

        git status

### Méthode Terminal

    python3 restore_demo.py

### Fichiers restaurés

    demo/config.demo.json → config.json
    demo/manuscrit_demo.txt → manuscrit_beatmakers.txt

### Règle importante

Les projets privés restent dans :

    private/projets/

Le dépôt public doit rester une démo.

---

## V3.4 — Rapport qualité éditorial

La V3.4 ajoute un rapport qualité éditorial avancé.

Ce rapport analyse le manuscrit actif et donne une vue claire sur son état de préparation.

### Générer le rapport qualité

Commande :

    python3 make.py quality

Le fichier généré se trouve ici :

    exports/rapports/rapport_qualite.md

### Générer avec tout le pack

Le rapport est aussi généré automatiquement avec :

    python3 make.py archive

### Ce que le rapport analyse

- nombre de chapitres ou sections ;
- nombre de mots ;
- nombre de paragraphes ;
- densité des sections ;
- titres trop longs ;
- sections vides ;
- sections trop longues ;
- notes internes ;
- statuts éditoriaux ;
- score global ;
- recommandations.

### Dans l’interface Streamlit

Ouvrez l’onglet Exports pour consulter :

- le rapport éditorial ;
- le rapport qualité éditorial ;
- les citations marketing.

### Interprétation rapide

- 🟢 prêt ou confortable ;
- 🟡 à surveiller ;
- 🟠 correction recommandée ;
- 🔴 problème prioritaire ;
- ⚫ section vide ou structurelle.

---

## V3.5 — Lire le score qualité

La V3.5 ajoute un score qualité visible directement dans le tableau de bord.

### Générer le score

Vous pouvez lancer :

    python3 make.py quality

Ou générer tout le pack :

    python3 make.py archive

### Fichiers générés

    exports/rapports/rapport_qualite.md
    exports/rapports/score_qualite.json

### Dans l’interface

Ouvrez le tableau de bord Streamlit.

Le score qualité indique rapidement si le manuscrit semble :

- prêt ;
- améliorable ;
- à corriger en priorité.

Pour lire le détail, ouvrez l’onglet Exports et consultez le rapport qualité éditorial.
