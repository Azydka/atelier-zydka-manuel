#!/bin/bash

cd "$(dirname "$0")"

echo "Lancement de l'application Atelier Zydka Manuel..."
echo ""

python3 -m streamlit run app_streamlit.py
