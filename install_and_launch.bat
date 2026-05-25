@echo off
cd /d "%~dp0"

echo ======================================
echo Manuscript Studio by Atelier Zydka
echo Installation + lancement
echo ======================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=py -3
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PYTHON_CMD=python
    ) else (
        echo Python n'est pas installe ou n'est pas accessible.
        echo Installez Python depuis :
        echo https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo Installation des dependances...
%PYTHON_CMD% -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Erreur pendant l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo Lancement de l'interface Manuscript Studio by Atelier Zydka...
%PYTHON_CMD% -m streamlit run app_streamlit.py

pause
