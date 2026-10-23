# Prompt de reprise — Étape 6 (polices embarquées)

À copier tel quel dans une nouvelle session (Claude Code ou ChatGPT/Codex).

---

Tu reprends la phase 0 « socle moteur » de Manuscript Studio, dépôt GitHub `Azydka/atelier-zydka-manuel`, branche `phase0/socle-moteur`. Ne travaille jamais sur `main`.

**Avant toute chose :**
1. Lis `AGENTS.md`, puis `docs/passation-phase0.md`.
2. Vérifie l'état du dépôt (`git fetch`, `git status -sb`, `git stash list`, `git log --oneline -5`). Le dernier commit doit correspondre à la passation. Si tu trouves quelque chose d'inattendu (modifications non commitées, stash, autre branche), arrête-toi et demande-moi.
3. `pip install -r requirements-dev.txt`, puis `python -m pytest -q` : tous les tests doivent passer avant de commencer.

**Mission : étape 6 uniquement, les polices embarquées.**
1. Rends les pages « avant » : `python tools/pack_demo_compare.py render avant --pages 1,2,4,9`. Suis la procédure de `.claude/skills/pack-demo-compare/SKILL.md`.
2. Ajoute dans `studio_core/fonts/` les fichiers officiels sous licence OFL, avec leur fichier de licence (`OFL.txt`, un par famille, nommé clairement) :
   - Inter : `Inter-Regular.ttf`, `Inter-Bold.ttf`, `Inter-Black.ttf` (dépôt officiel rsms/inter ou Google Fonts) ;
   - IBM Plex Mono : `IBMPlexMono-Regular.ttf` (dépôt officiel IBM/plex) ;
   - Source Serif 4 : `SourceSerif4-Italic.ttf` (dépôt officiel adobe-fonts/source-serif).

   Ce sont les noms attendus par `setup_fonts()` dans `studio_core/pdf_book.py`. Prends des TTF statiques, pas des polices variables. Si tu ne peux pas télécharger, dis-le et arrête-toi : n'invente pas de fichiers.
3. Enregistre ces polices dans ReportLab depuis `studio_core/fonts/` (`studio_core/resources.py::FONTS_DIR`). Supprime le fallback Helvetica/Courier/Times et le message « Polices fallback utilisées ». Une police manquante doit lever une `StudioError` claire. Les visuels Pillow (`studio_core/visuals.py`) doivent aussi utiliser Inter depuis ce dossier.
4. Le teaser (`studio_core/teaser.py`) utilise Helvetica en dur : signale-le-moi sans le changer (décision à prendre).
5. Rends les pages « après », fais le montage (`python tools/pack_demo_compare.py montage avant apres avant_apres.png`) et liste les écarts (`python tools/pack_demo_compare.py compare`). Le nombre de pages peut changer à cause des métriques : dis-le explicitement.
6. **Montre-moi le montage avant/après et attends mon feu vert avant tout commit.**
7. Après mon accord :
   - commit 1 `feat(pdf): polices Inter, IBM Plex Mono et Source Serif 4 embarquées`, push ;
   - commit 2, la référence seule (`python -m tests.snapshot --update`), message `test: référence PDF après polices embarquées`, push ;
   - `python -m pytest -q` doit être vert ;
   - mets à jour `docs/passation-phase0.md` (étape 6 faite, prochaine étape 7), commit, push.

**Règles à respecter :**
- Ne touche pas aux couleurs de la charte (`theme` dans config.json).
- Ne supprime aucun fichier de manuscrit ou de projet.
- Un commit par étape, push seulement sur `phase0/socle-moteur`, jamais de tag poussé.
- Arrête-toi et demande-moi dès qu'un choix change le rendu ou le comportement visible.
- Fais une passation (commit + push) avant de t'arrêter, même si l'étape n'est pas finie.

Termine par un récapitulatif : ce qui est fait, ce qui reste, et ce qui attend ma décision.
