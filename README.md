# Atelier Zydka Manuel

**Générateur de livre premium, kit éditorial et système de publication créative pour artistes, beatmakers, auteurs, formateurs et studios indépendants.**

Ce dépôt contient le socle technique du projet **Atelier Zydka Manuel** : un générateur PDF éditorial capable de transformer un manuscrit texte enrichi en document A5 premium, avec couverture, chapitres, tableaux, images, citations, encadrés et pages d’ouverture.

L’ambition du projet dépasse le simple PDF : il doit évoluer vers un véritable **studio éditorial automatisé** capable de produire un livre, son teaser, ses visuels réseaux sociaux, ses déclinaisons de couverture, ses exports multi-formats et son système graphique personnalisable.

---

## Vision du projet

Le projet ne doit pas être vu uniquement comme un script qui transforme un manuscrit en PDF.

Il doit devenir un système complet permettant de produire, à partir d’un seul contenu source :

- un livre PDF premium ;
- un teaser PDF diffusable ;
- des cartes de citations pour les réseaux sociaux ;
- des couvertures adaptées à Instagram, LinkedIn, YouTube, Facebook et Pinterest ;
- une version HTML responsive ;
- un document DOCX modifiable ;
- un export EPUB / Kindle ;
- une version imprimable avec fond perdu ;
- un système de thèmes graphiques ;
- une personnalisation par logo, couleurs et polices ;
- une interface web locale ;
- un workflow de vérification, backup, preview et génération rapide.

La bonne ambition n’est pas de créer un simple générateur de PDF.

La bonne ambition est de créer un **studio éditorial automatisé, personnalisable, testable et versionné pour créateurs indépendants**.

---

## Statut actuel

Le dépôt contient actuellement la première base technique du moteur PDF.

### Déjà présent

- Génération PDF A5 avec ReportLab ;
- couverture premium ;
- pages fixes de présentation ;
- table des matières ;
- chapitres automatiques ;
- gestion des paragraphes ;
- intertitres ;
- tableaux Markdown ;
- images avec légendes ;
- citations éditoriales ;
- callouts / encadrés ;
- pages d’ouverture visuelle ;
- folios ;
- charte graphique Atelier Zydka ;
- fallback automatique des polices ;
- dossier de sortie ignoré par Git.

### En cours de structuration

- `README.md` complet ;
- `requirements.txt` ;
- `make.py` ;
- `verifier_manuscrit.py` ;
- `config.json` ;
- `design_config.py` ;
- dossier `exports/` structuré ;
- dossiers `themes/`, `assets/`, `tests/`, `docs/` ;
- tests unitaires du parsing ;
- génération du kit marketing.

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Azydka/atelier-zydka-manuel.git
cd atelier-zydka-manuel