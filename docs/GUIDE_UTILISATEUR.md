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
