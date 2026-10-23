# Passation — Phase 0 « socle moteur »

Document de reprise : à lire en premier par tout assistant (Claude, Codex/ChatGPT) qui reprend le travail. À mettre à jour à la fin de chaque étape (voir `AGENTS.md`).

## État du dépôt

- Branche de travail : `phase0/socle-moteur`, créée depuis `main` (`323ea87`), poussée sur `origin`.
- `main` n'a pas été modifiée. Aucun tag créé.
- Dernier commit de code : `836070b test: référence PDF après refonte de la couverture` (ce document est commité juste après).
- Tests : `python -m pytest -q` donne **42 tests verts** sous Linux (Python 3.13).
- `make.py archive` sur la démo : environ 1,5 s.

## Objectif de la phase 0

Préparer le moteur pour une future version PC Windows installable (pywebview + PyInstaller + Inno Setup) : moteur testé, importable, sans écriture à côté du code. **Hors périmètre** : la coque PC, EPUB/HTML, SaaS, éditeur visuel.

## Étapes

| # | Étape | État | Commits |
|---|-------|------|---------|
| 0 | Sécurité : exports/ et backups/ hors du suivi Git | ✅ | `c4f0aa0` |
| 1 | Filet de caractérisation (pytest + référence) | ✅ | `873e28f` |
| 2 | Parser unique (rapport qualité, teaser) | ✅ | `079d324`, `30cbfaa`, `18d4a50` |
| 3 | Package `studio_core` + make.py en CLI mince | ✅ | `073d384`, `22d1d3e` |
| 4 | Projet = dossier, plus d'écriture dans le code, Streamlit adapté | ✅ | `28d13b3`, `94c6045` |
| 5 | Couverture pilotée par la config | ✅ | `0227b5f`, `836070b` |
| 6 | Polices embarquées (Inter, IBM Plex Mono, Source Serif 4) | ⏳ | — |
| 7 | Nettoyage du code mort (liste à valider avant suppression) | ⏳ | — |
| 8 | CI GitHub Actions (pytest sous Windows et Linux) | ⏳ | — |
| 9 | Documentation (README, RELEASE_NOTES, docs/ARCHITECTURE.md) + note V4.0 et tag local `v4.0.0` | ⏳ | — |

## Décisions du propriétaire (ne pas remettre en cause)

- **Version** : la note de release s'appellera « V4.0 — socle moteur », avec un tag local `v4.0.0`. Les tags v3.7-beta à v3.9-beta existent déjà, et le README affiche encore V2.1.
- **Push** : uniquement sur `phase0/socle-moteur`. Ni `main` ni les tags.
- **Fichiers privés** : `backups/` et les anciens exports sont sortis du suivi avec `git rm --cached` (les fichiers sont conservés). Ils restent dans l'historique public : décision d'historique et de visibilité du dépôt laissée au propriétaire.
- **Chapitres** : on garde 6 chapitres sur la démo (le titre H1 du document compte comme chapitre 01). La règle « titre de document = page de titre » viendra plus tard.
- **Teaser** : il utilise le parser commun (6 entrées).
- **Release / ZIP d'un livre** : livrables seuls (PDF, teaser, rapports, citations, cartes), sans code ni lanceurs.
- **Citations** : `citations.txt` du projet, sinon `[QUOTE:]`, `[CALLOUT:]` « À retenir » et lignes « À retenir : » du manuscrit. La démo fournit un `citations.txt` générique.
- **Supprimés** : `restore_demo.py`, le bouton « Restaurer la démo », le garde-fou `SENSITIVE_RELEASE_PATTERNS`, `project_manager.py`.
- **Migration** : `make.py import-legacy` copie les anciens `private/projets/*` vers la racine des projets, sans rien supprimer.
- **Charte** : ne pas toucher aux couleurs de `config.json` (#090909 / #C79A3B). La décision charte V5 contre charte actuelle n'est pas prise.
- **Couverture (étape 5, rendu validé)** :
  - en haut à gauche : marque + année ;
  - titre = `book_title`, taille ajustée automatiquement (`fit_font_size`) ;
  - filet au-dessus du titre ;
  - clés optionnelles de config.json : `cover_kicker` (défaut `baseline`), `cover_footer_left/right` (défaut vide), `back_cover_tagline` (défaut `book_subtitle`), `back_cover_footer_left/right` (défaut vide). Clé absente = défaut ; chaîne vide = rien affiché ;
  - 4e de couverture signée par `author_name` ;
  - Streamlit n'écrit pas ces clés quand elles restent à leur valeur par défaut.

## Constats de l'audit (vérifiés dans le code)

- L'écart 7/6 chapitres venait de `rapport_qualite.py` (son propre découpage), pas du PDF. C'est corrigé.
- Couverture : titre en dur, `\n` littéraux, filet sur le titre et chevauchement du bloc Z sont corrigés à l'étape 5.
- `studio_core/text.py::clean_text` contient des expressions régulières aux antislashs doublés (`r"[ \\t…]"`), héritées de l'ancien code, qui ne font pas ce qu'elles semblent faire. Comportement conservé pour l'instant : à signaler à l'étape 7.
- `studio_core/parser.py::filter_manuscript_content` contient des marqueurs propres au livre privé (« Avertissement légal », « TOOLKIT BONUS… »). À signaler à l'étape 7.
- `check.py` avertit quand il y a moins de 10 chapitres : ce seuil est propre au livre privé.

## Prochaine étape : 6 (polices embarquées)

Prompt prêt à copier pour reprendre (Claude ou ChatGPT) : `docs/prompt-reprise-etape6.md`. Outil d'avant/après : `tools/pack_demo_compare.py`, procédure dans `.claude/skills/pack-demo-compare/SKILL.md`.

1. Télécharger les fichiers .ttf officiels sous licence OFL : Inter (Regular, Bold, Black), IBM Plex Mono (Regular) et Source Serif 4 (Italic), avec leurs fichiers de licence (`OFL.txt`), dans `studio_core/fonts/`. Les noms attendus par `setup_fonts()` dans `studio_core/pdf_book.py` sont `Inter-Regular.ttf`, `Inter-Bold.ttf`, `Inter-Black.ttf`, `IBMPlexMono-Regular.ttf` et `SourceSerif4-Italic.ttf`. Les visuels (`studio_core/visuals.py`) cherchent aussi `Inter-Regular.ttf` / `Inter-Bold.ttf` dans ce dossier.
2. Supprimer le fallback Helvetica/Courier/Times et son avertissement. Une police manquante doit devenir une erreur claire.
3. Le changement de polices modifie les métriques, donc éventuellement le nombre de pages. Faire un avant/après PNG de plusieurs pages (couverture, sommaire, une page de chapitre), **le montrer au propriétaire et attendre son accord**, puis commit du code et commit dédié de la référence.

## Questions en attente de décision

- Les images de la démo (6,5 Mo, inutilisées par le manuscrit démo) sont copiées dans chaque projet démo : faut-il les garder dans le modèle ?
- L'historique Git public contient le manuscrit privé (`backups/`) et des citations du livre : réécriture d'historique ou passage du dépôt en privé, décision du propriétaire.

## Pièges

- La documentation utilisateur (README, `docs/GUIDE_UTILISATEUR.md`, `docs/FAQ.md`, `INSTALLATION.md`) décrit encore l'ancien fonctionnement (`restore_demo.py`, `manuelsortie/`, `dist/`). C'est normal jusqu'à l'étape 9.
- `interface_web_manuel_presence.py` est du code mort, qui pointe vers un script renommé. Il sera supprimé à l'étape 7.
- Les tests de génération passent par `make.py` dans une copie du dépôt, avec `PYTHONDONTWRITEBYTECODE=1`, pour vérifier qu'aucun fichier n'est écrit dans le dossier du code.
- Les visuels utilisent des polices système (absentes sous Linux, donc police bitmap par défaut). Seuls les noms de fichiers des cartes sont comparés, pas leur contenu.
