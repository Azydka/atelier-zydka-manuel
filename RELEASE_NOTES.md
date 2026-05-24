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
