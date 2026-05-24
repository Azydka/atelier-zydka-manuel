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
