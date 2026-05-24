# Atelier Zydka Manuel — Démarrage rapide

Bienvenue dans Atelier Zydka Manuel.

Ce dossier contient une application locale qui transforme un manuscrit en pack éditorial complet : PDF principal, teaser PDF, citations marketing, visuels réseaux sociaux, rapports éditoriaux et archive ZIP.

## Lancer l'application sur Mac

Double-cliquez sur :

    install_and_launch.command

La première fois, l'installation peut prendre quelques minutes.

Si macOS bloque le fichier :

1. faites clic droit sur install_and_launch.command ;
2. cliquez sur Ouvrir ;
3. confirmez l'ouverture.

## Lancer l'application sur Windows

Double-cliquez sur :

    install_and_launch.bat

Si Windows affiche une alerte :

1. cliquez sur Informations complémentaires ;
2. cliquez sur Exécuter quand même.

## Ce que fait le lanceur

Le lanceur :

1. vérifie que Python est disponible ;
2. installe les dépendances nécessaires ;
3. lance l'interface Atelier Zydka Manuel ;
4. affiche une adresse locale de type http://localhost:8501.

## Si l'interface ne s'ouvre pas

Copiez l'adresse affichée dans le terminal, par exemple :

    http://localhost:8501

Puis collez-la dans votre navigateur.

## Utilisation recommandée

Pour vos vrais livres, utilisez toujours l'onglet Projets privés.

Les vrais manuscrits doivent rester dans :

    private/projets/

Ne remplacez pas directement le fichier de démonstration public.

## En cas de problème

Sur Mac, ouvrez un terminal dans ce dossier et tapez :

    python3 -m pip install -r requirements.txt
    python3 -m streamlit run app_streamlit.py

Sur Windows, ouvrez PowerShell ou Invite de commandes dans ce dossier et tapez :

    python -m pip install -r requirements.txt
    python -m streamlit run app_streamlit.py

## Note

Cette version est encore une bêta locale.

Elle est pensée pour tester le workflow complet avant une future version plus simple avec installateur natif.
