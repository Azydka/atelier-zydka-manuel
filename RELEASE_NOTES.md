# Release Notes — Atelier Zydka Manuel

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