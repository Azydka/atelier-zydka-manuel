# FAQ — Manuscript Studio by Atelier Zydka

Version : V2.1  
Statut : Early Access  
Date : 23/05/2026

---

## Qu’est-ce qu’Manuscript Studio by Atelier Zydka ?

Manuscript Studio by Atelier Zydka est un système éditorial local qui transforme un manuscrit source en pack éditorial complet.

Il peut générer un PDF principal, un teaser PDF, un rapport éditorial, des citations marketing, des visuels réseaux sociaux, un dossier de release et une archive ZIP transmissible.

---

## Est-ce un SaaS ?

Non. La V2.1 est un outil local qui fonctionne sur ordinateur avec Python et le Terminal.

Une interface locale est envisagée pour une version future.

---

## Faut-il savoir coder ?

Il n’est pas nécessaire de savoir développer, mais il faut être à l’aise avec quelques commandes Terminal.

La commande principale est :

    python3 make.py archive

---

## Que génère l’outil ?

L’outil peut générer :

    manuelsortie/manuel-de-presence-atelier-zydka.pdf
    exports/pdf/teaser-manuel-presence.pdf
    exports/rapports/rapport_structure.md
    exports/reseaux/citations/citations_extraites.md
    exports/reseaux/cartes/
    dist/atelier-zydka-manuel-release/
    dist/atelier-zydka-manuel-release.zip

Le fichier final important est :

    dist/atelier-zydka-manuel-release.zip

---

## Puis-je utiliser mon propre manuscrit ?

Oui. Le manuscrit public de démonstration est :

    manuscrit_beatmakers.txt

Pour utiliser un autre contenu, il faut remplacer ou adapter ce fichier.

---

## Pourquoi le dépôt public contient-il seulement une démo ?

Parce que le moteur doit être testable et montrable, mais les contenus propriétaires doivent rester privés.

La bonne séparation est :

    moteur public = démonstration
    contenu privé = dossier private/ non versionné

---

## Puis-je vendre les PDF générés avec mes propres contenus ?

Oui, si vous possédez les droits sur vos contenus et si les documents générés ont été vérifiés.

En revanche, vous ne pouvez pas revendre l’outil lui-même, son code ou sa structure sans accord écrit.

---

## Puis-je revendre le code ?

Non. La licence V2.1 n’autorise pas la revente, la redistribution ou la transformation commerciale du code sans accord écrit d’Atelier Zydka.

---

## Quelle est la différence entre release et archive ?

La commande :

    python3 make.py release

génère un dossier propre :

    dist/atelier-zydka-manuel-release/

La commande :

    python3 make.py archive

génère ce dossier puis le compresse en ZIP :

    dist/atelier-zydka-manuel-release.zip

---

## Pourquoi y a-t-il des warnings ?

Le système peut détecter des points de vigilance : tableaux trop larges, balises inconnues, trop de chapitres ou risques de rendu A5.

Les warnings ne bloquent pas forcément la génération.

S’il y a :

    Erreurs : 0

le pipeline peut généralement continuer.

---

## Une interface graphique est-elle prévue ?

Oui. Une interface locale est envisagée pour la V2.5, probablement avec Streamlit.

---

## Quel est le prix recommandé en early access ?

Le prix recommandé pour une première version testable se situe entre 39 € et 49 €.

Ce prix reste cohérent tant que l’outil nécessite encore le Terminal et n’a pas d’interface graphique.

---

## Que faut-il tester en priorité ?

Lors d’un bêta-test, il faut vérifier :

- si le produit est compréhensible ;
- si le ZIP est clair ;
- si les exports donnent envie ;
- si le guide utilisateur suffit ;
- si les warnings inquiètent ou non ;
- si le prix paraît acceptable ;
- si l’absence d’interface graphique bloque l’utilisateur.

---

## Quelle est la prochaine étape ?

Les prochaines étapes logiques sont :

1. inclure la documentation dans la release ZIP ;
2. améliorer les premières pages PDF ;
3. enrichir config.json ;
4. préparer un bêta-test ;
5. lancer le parser intelligent V2.2.

---

Fin de la FAQ.
