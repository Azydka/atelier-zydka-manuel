#!/bin/bash

cd "$(dirname "$0")" || exit 1

echo "Installation des dépendances..."
python3 -m pip install -r requirements.txt

echo "Lancement de l'interface Manuscript Studio by Atelier Zydka..."
python3 -m streamlit run app_streamlit.py
