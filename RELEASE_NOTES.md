# Release Notes — Atelier Zydka Manuel

## V2.1 — Packaging éditorial propre

### Ajouté

- Ajout de la commande `python3 make.py archive`.
- Génération automatique d’une archive ZIP transmissible.
- Création du fichier `dist/atelier-zydka-manuel-release.zip`.
- Intégration du manuscrit **Beatmaker Indépendant 2027 — Édition V13 Ultime**.
- Mise en place d’une sélection éditoriale contrôlée pour les citations marketing.
- Génération de visuels réseaux sociaux plus propres à partir de citations validées.
- Amélioration du positionnement produit autour d’un mini-studio éditorial local.

### Modifié

- Mise à jour du manuscrit principal `manuscrit_beatmakers.txt`.
- Réécriture de `generer_exports_marketing.py` pour éviter les extractions parasites.
- Mise à jour du fichier `exports/reseaux/citations/citations_extraites.md`.
- Clarification du workflow de génération complet.
- Consolidation de la logique de release.

### Corrigé

- Suppression des titres d’annexes dans les citations marketing.
- Suppression des fragments Markdown dans les visuels sociaux.
- Suppression des symboles parasites issus d’emojis non rendus.
- Réduction du risque de cartes sociales inutilisables.
- Séparation plus propre entre contenu éditorial, exports et livrable final.

### Commandes principales

```bash
python3 make.py all
python3 make.py release
python3 make.py archive# Release Notes — Atelier Zydka Manuel

## Version produit — 22/05/2026

Cette release stabilise **Atelier Zydka Manuel** comme générateur éditorial complet.

Le projet ne se limite plus à produire un PDF. Il génère désormais un ensemble cohérent de livrables éditoriaux, marketing et de contrôle qualité à partir d’un manuscrit source.

---

## État Git

Branche source :

`main`

Dernier commit validé :

`c908ca5 — Met à jour le README pour la release produit`

État confirmé :

`working tree clean`

---

## Pipeline validé

Commande de validation :

`python3 make.py all`

Résultat validé :

- check OK
- pdf OK
- structure OK
- marketing OK
- teaser OK
- visuals OK

---

## Livrables générés

### PDF principal

`manuelsortie/manuel-de-presence-atelier-zydka.pdf`

### Rapport de structure éditoriale

`exports/rapports/rapport_structure.md`

État du rapport :

- 18 chapitres
- 900 blocs
- score éditorial moyen : 87.4/100

### Citations marketing

`exports/reseaux/citations/citations_extraites.md`

État :

- 54 citations extraites

### Teaser PDF

`exports/pdf/teaser-manuel-presence.pdf`

État :

- teaser V2 propre

### Visuels réseaux sociaux

`exports/reseaux/cartes`

Formats générés :

- carré
- story

État :

- 12 citations utilisées

---

## Fonctionnalités stabilisées

- Parser intelligent du manuscrit
- Détection propre des chapitres
- Nettoyage des artefacts Markdown au rendu PDF
- Désactivation des pages de démonstration
- Désactivation des pages d’ouverture visuelle
- Désactivation des ouvertures de chapitre via configuration
- Génération PDF A5
- Linter manuscrit
- Rapport de structure éditoriale
- Diagnostic éditorial avec score
- Export marketing des citations
- Teaser PDF
- Visuels réseaux sociaux
- README remis à jour

---

## Points d’attention connus

### Polices

Le générateur fonctionne avec des polices fallback.

Message actuel :

`Attention : polices fallback utilisées. Ajoute les .ttf dans ./fonts pour le rendu final fidèle.`

Action future :

- ajouter les polices dans `./fonts`
- ou documenter explicitement le fallback

### Tableaux larges

Les tableaux larges restent le principal point à améliorer pour un rendu A5 parfait.

Action future :

- améliorer le rendu A5 des grands tableaux
- ou prévoir une version annexe / paysage

### Distribution

Les exports sont générés localement.

Action future :

- créer un dossier de distribution propre
- livrer uniquement les fichiers utiles

---

## Prochaines évolutions recommandées

1. Créer un dossier de distribution propre
2. Ajouter une commande `make release`
3. Exporter le rapport éditorial en PDF
4. Améliorer les tableaux larges en A5
5. Ajouter des tests unitaires sur le parser
6. Préparer une version HTML ou EPUB
7. Documenter l’installation des polices
8. Créer une archive finale livrable

---

## Conclusion

Cette version marque le passage du projet d’un simple générateur PDF à un véritable système éditorial automatisé.

Le socle actuel est propre, versionné, testé et exploitable.

---

## V2.2 — Configuration personnalisable

### Ajouté

- Ajout de `config_utils.py`.
- Centralisation de la lecture de `config.json`.
- Enrichissement de `config.json` avec les champs projet, livre, auteur, marque, baseline, année, fichiers de sortie et thème.
- Personnalisation du nom du dossier de release via `release_name`.
- Personnalisation du nom de l’archive ZIP via `zip_name`.
- Personnalisation du nom du PDF principal via `output_pdf_name`.
- Personnalisation du nom du teaser PDF via `teaser_pdf_name`.
- Connexion des visuels réseaux à `brand_name`, `baseline` et `theme`.
- Connexion du teaser PDF à `book_title`, `book_subtitle`, `author_name`, `brand_name`, `year` et `theme`.
- Connexion partielle du PDF principal à `book_title`, `book_subtitle`, `author_name`, `brand_name` et `output_pdf_name`.

### Objectif

La V2.2 transforme Atelier Zydka Manuel en moteur éditorial personnalisable à partir d’un fichier `config.json`.

Le projet passe de :

    générateur lié à un projet précis

à :

    moteur éditorial adaptable à plusieurs projets.

### Commande à utiliser après personnalisation

    python3 make.py archive

---

## V2.3 — PDF principal configurable

### Ajouté

- Connexion visuelle de la couverture PDF principale à `config.json`.
- Utilisation de `book_title` pour le titre de couverture.
- Utilisation de `book_subtitle` pour le sous-titre.
- Utilisation de `author_name` pour l’auteur.
- Utilisation de `brand_name` pour la marque.
- Utilisation de `baseline` pour la ligne éditoriale.
- Utilisation de `year` pour l’année.
- Connexion des couleurs principales du PDF au thème défini dans `config.json`.
- Connexion de la quatrième de couverture à `book_title`, `book_subtitle` et `brand_name`.

### Objectif

La V2.3 renforce la promesse de personnalisation du moteur éditorial.

Le PDF principal n’est plus seulement généré techniquement : il commence à refléter les paramètres du projet défini dans `config.json`.

---

## V3.0 — Interface locale Streamlit

### Ajouté

- Ajout de `app_streamlit.py`.
- Création d’une interface locale Streamlit.
- Ajout d’un tableau de bord projet.
- Ajout d’un formulaire de modification de `config.json`.
- Ajout d’un éditeur de manuscrit.
- Ajout d’un import de fichier `.txt` ou `.md`.
- Ajout d’un bouton pour générer l’archive ZIP.
- Ajout d’un affichage des logs de génération.
- Ajout d’un bouton de téléchargement du ZIP généré.
- Ajout d’un onglet Exports pour consulter le rapport éditorial et les citations.

### Commande de lancement

    python3 -m streamlit run app_streamlit.py

### Objectif

La V3.0 transforme Atelier Zydka Manuel en application locale utilisable sans lancer manuellement chaque commande du pipeline.

---

## V3.1 — Lancement simplifié

### Ajouté

- Ajout de `requirements.txt`.
- Ajout de `launch_app.sh`.
- Ajout de `launch_app.command`.
- Simplification du lancement de l’interface locale Streamlit.
- Documentation des commandes d’installation et de lancement.

### Commandes utiles

Installer les dépendances :

    python3 -m pip install -r requirements.txt

Lancer l’application :

    python3 -m streamlit run app_streamlit.py

Ou :

    ./launch_app.sh

### Objectif

La V3.1 réduit la friction d’installation et de lancement pour les utilisateurs non techniques.

---

## V3.1 — Lancement simplifié

### Ajouté

- Ajout de `requirements.txt`.
- Ajout de `launch_app.sh`.
- Ajout de `launch_app.command`.
- Inclusion de `app_streamlit.py` dans la release ZIP.
- Inclusion des fichiers de lancement dans la release ZIP.
- Simplification du lancement de l’interface locale Streamlit.
- Documentation des commandes d’installation et de lancement.

### Commandes utiles

Installer les dépendances :

    python3 -m pip install -r requirements.txt

Lancer l’application :

    python3 -m streamlit run app_streamlit.py

Ou :

    ./launch_app.sh

### Objectif

La V3.1 réduit la friction d’installation et de lancement pour les utilisateurs non techniques.

---

## V3.1.1 — Pack d’onboarding

### Ajouté

- Ajout de `START_HERE.md`.
- Ajout de `INSTALLATION.md`.
- Ajout de `QUICKSTART.md`.
- Inclusion des documents d’onboarding dans la release ZIP.
- Amélioration du premier contact utilisateur après téléchargement.

### Objectif

La V3.1.1 facilite la prise en main immédiate du projet après décompression du ZIP.

L’utilisateur sait désormais par où commencer, comment installer les dépendances, comment lancer l’application et comment générer son premier pack éditorial.

---

## V3.2 — Mode projets privés

### Ajouté

- Ajout de `project_manager.py`.
- Création d’une structure de projets privés dans `private/projets/`.
- Ajout d’un onglet Projets privés dans l’interface Streamlit.
- Possibilité de créer un projet privé.
- Possibilité de charger un projet privé.
- Possibilité de sauvegarder `config.json` et le manuscrit dans un projet privé.
- Possibilité de générer un pack depuis un projet privé chargé.
- Inclusion de `project_manager.py` dans la release ZIP.

### Objectif

La V3.2 permet d’utiliser Atelier Zydka Manuel avec de vrais livres sans exposer les contenus commerciaux dans GitHub.

Le dépôt public reste un moteur avec manuscrit de démonstration.

Les contenus sensibles ou commerciaux restent dans :

    private/projets/

---

## V3.3 — Restauration de la démo publique

### Ajouté

- Ajout du dossier `demo/`.
- Ajout de `demo/config.demo.json`.
- Ajout de `demo/manuscrit_demo.txt`.
- Ajout de `restore_demo.py`.
- Inclusion de `restore_demo.py` et du dossier `demo/` dans la release ZIP.
- Ajout d’un onglet Sécurité dans l’interface Streamlit.
- Ajout d’un bouton **Restaurer la démo publique**.
- Ajout d’une confirmation obligatoire avant restauration.

### Objectif

La V3.3 réduit le risque de publier accidentellement un manuscrit privé dans le dépôt GitHub.

Elle permet de restaurer rapidement les fichiers publics :

    config.json
    manuscrit_beatmakers.txt

à partir de la démo officielle :

    demo/config.demo.json
    demo/manuscrit_demo.txt

---

## V3.4 — Rapport qualité éditorial avancé

### Ajouté

- Ajout de `rapport_qualite.py`.
- Ajout de la commande `python3 make.py quality`.
- Génération de `exports/rapports/rapport_qualite.md`.
- Inclusion du rapport qualité dans le pipeline `make.py archive`.
- Inclusion du rapport qualité dans le ZIP de release.
- Affichage du rapport qualité dans l’onglet Exports de Streamlit.

### Analyse effectuée

Le rapport qualité détecte :

- chapitres ou sections trop courts ;
- chapitres ou sections trop longs ;
- titres trop longs ;
- notes internes ;
- mentions TODO, FIXME, À RELIRE ;
- statuts éditoriaux ;
- densité des sections ;
- score qualité global ;
- recommandations éditoriales.

### Objectif

La V3.4 ajoute une couche de contrôle éditorial avancé avant publication.

Elle rapproche Atelier Zydka Manuel d’un véritable studio éditorial local capable de diagnostiquer un manuscrit avant génération du pack final.

---

## V3.5 — Score qualité dans le tableau de bord

### Ajouté

- Génération de `exports/rapports/score_qualite.json`.
- Inclusion de `score_qualite.json` dans la release ZIP.
- Lecture du score qualité par l’interface Streamlit.
- Affichage du score qualité dans le tableau de bord.
- Ajout d’alertes selon le niveau du score.
- Maintien du rapport complet dans l’onglet Exports.

### Objectif

La V3.5 transforme le rapport qualité en indicateur produit immédiatement visible.

L’utilisateur n’a plus besoin d’ouvrir le rapport complet pour savoir si le manuscrit mérite une correction avant publication.

---

## V3.6 — Rafraîchissement du diagnostic qualité

### Ajouté

- Ajout d’un bouton Rafraîchir le diagnostic qualité dans le tableau de bord Streamlit.
- Exécution de `python3 make.py quality` depuis l’interface.
- Mise à jour du score qualité sans générer toute l’archive ZIP.
- Amélioration de l’expérience de contrôle éditorial.

### Objectif

La V3.6 rend le diagnostic qualité plus rapide, plus interactif et plus intégré au flux de travail.
