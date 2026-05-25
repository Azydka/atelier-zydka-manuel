#!/bin/bash

cd "$(dirname "$0")"

echo "Lancement de l'application Manuscript Studio by Atelier Zydka..."
echo ""

python3 -m streamlit run app_streamlit.py
