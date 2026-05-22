# Atelier Zydka Manuel

**Générateur éditorial automatisé pour produire un livre PDF premium, ses rapports de contrôle, son teaser et ses visuels marketing à partir d’un manuscrit source.**

Atelier Zydka Manuel transforme un manuscrit texte enrichi en système de publication complet :

- PDF principal au format A5 ;
- vérification du manuscrit ;
- rapport de structure éditoriale ;
- diagnostic éditorial avec score ;
- exports de citations marketing ;
- teaser PDF ;
- visuels réseaux sociaux au format carré et story.

Le projet sert de socle à un studio éditorial automatisé pour créateurs, beatmakers, artistes, formateurs et indépendants.

---

## Vision du projet

Le projet ne doit pas être vu comme un simple script qui génère un PDF.

Il doit devenir un système éditorial capable de transformer une source unique en plusieurs livrables cohérents :

- un livre ;
- un teaser ;
- des visuels ;
- des citations ;
- des rapports de contrôle ;
- des supports de diffusion ;
- une base réutilisable pour d’autres produits éditoriaux.

La logique centrale est simple :

> un contenu bien structuré doit pouvoir devenir un produit complet.

---

## État actuel

Le pipeline complet est opérationnel.

Commande principale :

```bash
python3 make.py all
```

Cette commande lance automatiquement :

```text
check
pdf
structure
marketing
teaser
visuals
```

Dernière validation connue :

```text
check OK
pdf OK
structure OK
marketing OK
teaser OK
visuals OK
```

---

## Fonctionnalités disponibles

### 1. Génération du PDF principal

Le projet génère un livre PDF A5 avec ReportLab.

Sortie :

```text
manuelsortie/manuel-de-presence-atelier-zydka.pdf
```

Commande :

```bash
python3 make.py pdf
```

Fonctions prises en charge :

- couverture ;
- table des matières ;
- chapitres automatiques ;
- titres et sous-titres ;
- paragraphes ;
- listes ;
- citations ;
- encadrés ;
- tableaux Markdown ;
- images ;
- folios ;
- charte graphique Atelier Zydka ;
- fallback automatique des polices.

---

### 2. Vérification du manuscrit

Le linter vérifie la structure du manuscrit et signale les problèmes utiles.

Commande :

```bash
python3 make.py check
```

Contrôles actuels :

- présence du manuscrit ;
- détection des chapitres ;
- faux chapitres potentiels ;
- tableaux trop larges ;
- images manquantes ;
- erreurs structurelles majeures.

Le linter a été nettoyé pour éviter le bruit :

- le Markdown gras `**` n’est plus signalé inutilement ;
- les checklists `[ ]` sont considérées comme du contenu normal ;
- les tableaux larges restent signalés car ils peuvent poser problème en A5.

---

### 3. Rapport de structure éditoriale

Le projet génère un rapport Markdown qui analyse la structure du manuscrit.

Commande :

```bash
python3 make.py structure
```

Sortie :

```text
exports/rapports/rapport_structure.md
```

Le rapport contient :

- synthèse du manuscrit ;
- nombre de chapitres ;
- nombre total de blocs ;
- paragraphes ;
- titres internes ;
- listes ;
- tableaux ;
- images ;
- citations ;
- encadrés ;
- score éditorial moyen ;
- lecture stratégique ;
- plan d’action recommandé ;
- diagnostic par chapitre ;
- priorités de correction ;
- détail des blocs.

État actuel du manuscrit :

```text
18 chapitres
900 blocs
score éditorial moyen : 87.4/100
```

---

### 4. Exports marketing

Le projet extrait des citations exploitables pour la communication.

Commande :

```bash
python3 make.py marketing
```

Sortie :

```text
exports/reseaux/citations/citations_extraites.md
```

État actuel :

```text
54 citations extraites
```

---

### 5. Teaser PDF

Le projet génère un teaser PDF court et diffusable.

Commande :

```bash
python3 make.py teaser
```

Sortie :

```text
exports/pdf/teaser-manuel-presence.pdf
```

Version actuelle :

```text
teaser V2 propre
```

---

### 6. Visuels réseaux sociaux

Le projet génère des cartes visuelles à partir des citations sélectionnées.

Commande :

```bash
python3 make.py visuals
```

Sortie :

```text
exports/reseaux/cartes
```

Formats générés :

```text
carré
story
```

État actuel :

```text
12 citations utilisées
formats carré + story
```

---

## Commandes disponibles

```bash
python3 make.py check
python3 make.py pdf
python3 make.py structure
python3 make.py marketing
python3 make.py teaser
python3 make.py visuals
python3 make.py all
```

Commande recommandée avant chaque commit important :

```bash
python3 make.py all
```

---

## Structure du projet

```text
atelier-zydka-manuel/
├── manuscrit_beatmakers.txt
├── parser_manuscrit.py
├── verifier_manuscrit.py
├── rapport_structure.py
├── generer_livre_manuel_presence.py
├── generer_exports_marketing.py
├── generer_teaser_pdf.py
├── generer_visuels_reseaux.py
├── make.py
├── config.json
├── requirements.txt
├── images/
├── exports/
│   ├── pdf/
│   ├── rapports/
│   └── reseaux/
│       ├── citations/
│       └── cartes/
└── manuelsortie/
```

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Azydka/atelier-zydka-manuel.git
cd atelier-zydka-manuel
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

Ou, au minimum :

```bash
pip install reportlab
```

### 3. Lancer le pipeline complet

```bash
python3 make.py all
```

---

## Configuration

Le fichier principal de configuration est :

```text
config.json
```

Il permet notamment d’activer ou désactiver certaines pages ou comportements.

Exemple :

```json
{
  "features": {
    "include_cover": true,
    "include_back_cover": true,
    "include_annex_page": false,
    "include_demo_pages": false,
    "include_fixed_intro_pages": false,
    "include_visual_opening_pages": false,
    "include_chapter_openers": false,
    "include_table_of_contents": true,
    "strict_missing_images": false
  }
}
```

---

## Manuscrit source

Le manuscrit principal est :

```text
manuscrit_beatmakers.txt
```

Le parser reconnaît notamment :

- titres Markdown ;
- chapitres ;
- parties ;
- annexes ;
- paragraphes ;
- listes ;
- tableaux Markdown ;
- images ;
- citations ;
- encadrés ;
- sauts de page.

---

## Philosophie

Atelier Zydka Manuel part d’une idée simple :

> Un manuscrit bien structuré peut devenir plus qu’un livre.

Il peut devenir un PDF premium, un teaser, des visuels, des citations, des rapports de contrôle et un système complet de diffusion.

Le but n’est pas seulement de produire un fichier.

Le but est de transformer une matière brute en présence éditoriale complète.

---

## Roadmap courte

Prochaines améliorations possibles :

1. améliorer le rendu des tableaux larges en A5 ;
2. exporter le rapport éditorial en PDF ;
3. générer une note de release automatique ;
4. créer un dossier de distribution propre ;
5. ajouter des tests unitaires sur le parser ;
6. préparer une version HTML ou EPUB ;
7. créer une interface locale de prévisualisation.

---

## État de release

Branche de préparation :

```text
release-produit-v1
```

Dernier socle validé sur `main` :

```text
5f503d9 — Affine les recommandations du rapport éditorial
```