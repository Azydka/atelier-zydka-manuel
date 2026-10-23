# Règles communes aux assistants (Codex/ChatGPT, Claude)

Ce dépôt est modifié par plusieurs assistants à tour de rôle. Ces règles évitent qu'un assistant écrase ou perde le travail de l'autre, et permettent de reprendre après une coupure. Le propriétaire du projet a le dernier mot sur tout.

## Avant de commencer (toujours)

1. Lire la passation en cours : `docs/passation-*.md` (la plus récente). Elle dit où en est le travail, ce qui est décidé et ce qui attend une décision.
2. Vérifier l'état du dépôt :
   ```
   git fetch
   git status -sb
   git stash list
   git worktree list
   git branch -vv
   git log --oneline -10
   ```
3. Comparer avec la passation : le dernier commit indiqué doit correspondre. S'il y a des modifications non commitées, un stash, un worktree ou une branche non fusionnée que vous n'avez pas créés : ne rien toucher et demander au propriétaire.
4. Lancer les tests (voir « Validation ») pour partir d'un état vert connu.

## Pendant le travail

- Travailler sur la branche indiquée dans la passation (phase 0 : `phase0/socle-moteur`). Jamais directement sur `main`.
- **Un commit par étape**, messages au format Conventional Commits (`fix(pdf): …`, `test: …`, `docs: …`).
- **Pousser la branche de travail après chaque commit** (`git push origin <branche>`), pour qu'une coupure ne fasse rien perdre. Ne jamais pousser `main` ni les tags sans accord du propriétaire. Pas de changement de visibilité du dépôt.
- Ne jamais supprimer, réécrire ou force-pousser le travail d'un autre assistant (branche, stash, commit) sans l'accord du propriétaire.
- Ne laisser aucune modification non commitée en fin de session : commiter (même un travail partiel, en le disant dans le message) ou annuler.

## Ce qui demande l'accord du propriétaire

- Tout changement du rendu du PDF ou du comportement visible (interface, contenu du ZIP, CLI) : montrer l'avant/après (PNG de la page concernée) et attendre le feu vert.
- Les couleurs de la charte (`theme` dans `config.json`, `#090909` / `#C79A3B`) : ne pas les modifier, la décision charte n'est pas prise. Elles doivent rester pilotées par la config.
- Toute suppression de fichier de manuscrit ou de projet privé : interdit. Pour sortir un fichier du suivi Git : `git rm --cached` (le fichier reste sur disque).

## Tests de référence (filet de non-régression)

- `tests/reference/demo.json` fige le pack démo : chapitres, pages et texte des PDF, fichiers de la release et du ZIP.
- Un changement de rendu volontaire et validé par le propriétaire se fait en **deux commits** : le code, puis la référence régénérée seule :
  ```
  python -m tests.snapshot --update
  ```
- Ne jamais régénérer la référence pour « faire passer » un test sans avoir compris et fait valider le changement.

## Validation avant chaque commit

```
pip install -r requirements-dev.txt
python -m pytest -q
python make.py --projects-root <dossier temporaire> archive
```

## Architecture en bref

- `studio_core/` : le moteur (bibliothèque, sans print, sys.exit ni Streamlit). Point d'entrée : `studio_core.build_archive(project, on_progress=None)`.
- Un livre = un projet = un dossier : `config.json`, `manuscrit.txt`, `citations.txt` (facultatif), `images/`, `exports/`. Racine par défaut : `Documents/Manuscript Studio` (variable `MANUSCRIPT_STUDIO_HOME` ou `--projects-root`).
- `make.py` : CLI mince. `app_streamlit.py` : interface au-dessus de `studio_core`.
- Le moteur n'écrit jamais dans le dossier du code (un test le vérifie).

## Fin de session ou de tâche (obligatoire, même en cas d'arrêt imprévu prévisible)

Mettre à jour `docs/passation-<sujet>.md` puis commiter et pousser :
- état du dépôt : branche, dernier commit, tests (nombre, vert/rouge) ;
- étapes faites (avec leurs commits), étape en cours et où elle s'est arrêtée ;
- décisions prises par le propriétaire ;
- questions en attente de décision ;
- pièges rencontrés.
