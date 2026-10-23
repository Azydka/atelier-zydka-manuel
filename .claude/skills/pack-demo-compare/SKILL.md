---
name: pack-demo-compare
description: Avant/après du pack démo de Manuscript Studio pour tout changement qui touche le rendu du PDF (couverture, polices, mise en page, pages) — génère la démo, rend des pages en PNG avant et après, assemble un montage côte à côte, liste les écarts avec tests/reference/demo.json, puis guide la validation par le propriétaire et la mise à jour de la référence en commit dédié. À utiliser dès qu'une modification de studio_core peut changer le PDF, le teaser ou le contenu du ZIP.
---

# Avant/après du pack démo

Outil : `tools/pack_demo_compare.py` (Python pur, Windows/macOS/Linux, nécessite `pip install -r requirements-dev.txt`). Il n'écrit rien dans le dépôt : tout va dans le dossier temporaire du système (`<tmp>/manuscript-studio-compare/`).

## Procédure

1. **Avant toute modification** du code, rendre les pages concernées :
   ```
   python tools/pack_demo_compare.py render avant --pages 1,2,4,9
   ```
   Choisir les pages selon le changement : 1 = couverture, 2 = sommaire, 3-8 = chapitres, 9 = 4e de couverture (démo à 9 pages).
2. Faire la modification.
3. Rendre les mêmes pages et assembler le montage :
   ```
   python tools/pack_demo_compare.py render apres --pages 1,2,4,9
   python tools/pack_demo_compare.py montage avant apres avant_apres.png
   ```
4. Lister les écarts avec la référence de test :
   ```
   python tools/pack_demo_compare.py compare
   ```
   Chaque écart doit être attendu et expliqué. Un écart inattendu (autre page, nombre de pages, fichiers du ZIP, écriture dans le dossier du code) se corrige avant d'aller plus loin.
5. **Montrer le montage au propriétaire et attendre son accord explicite** (règle AGENTS.md). Ne rien commiter avant.
6. Après accord :
   - commit 1 : le code (`fix(pdf): …` / `feat(pdf): …`), puis push de la branche de travail ;
   - commit 2 : la référence seule (`python -m tests.snapshot --update`, puis `test: référence … après …`), puis push ;
   - `python -m pytest -q` doit être vert ;
   - mettre à jour `docs/passation-phase0.md`, commiter et pousser.

## Notes

- Les visuels réseaux (PNG des cartes) ne sont comparés que par leurs noms de fichiers.
- Le montage est une image : l'envoyer au propriétaire (pièce jointe ou fichier) plutôt que la décrire.
