#!/bin/bash

cd "$(dirname "$0")" || exit 1
clear

echo "======================================"
echo " Manuscript Studio by Atelier Zydka"
echo " Installation + lancement"
echo "======================================"
echo ""

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Python n'est pas installé ou n'est pas accessible."
    echo ""
    echo "Installez Python depuis :"
    echo "https://www.python.org/downloads/"
    echo ""
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo "Python détecté : $PYTHON_CMD"
echo ""

echo "Installation des dépendances..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Erreur pendant l'installation des dépendances."
    echo "Vérifiez votre connexion internet ou votre installation Python."
    echo ""
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo ""
echo "Lancement de l'interface Manuscript Studio by Atelier Zydka..."
echo ""
echo "Si le navigateur ne s'ouvre pas automatiquement, copiez l'adresse affichée dans le terminal."
echo ""

$PYTHON_CMD -m streamlit run app_streamlit.py

echo ""
read -p "Appuyez sur Entrée pour fermer..."
