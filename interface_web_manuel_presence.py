#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface web premium — Atelier Zydka
Lancement :
python3 interface_web_manuel_presence.py

Puis ouvrir :
http://127.0.0.1:8765
"""

import os
import re
import json
import shutil
import subprocess
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
GENERATOR = BASE_DIR / "generer_livre_manuel_presence.py"
MANUSCRIPT = BASE_DIR / "manuscrit_beatmakers.txt"
OUTPUT_DIR = BASE_DIR / "manuelsortie"
OUTPUT_PDF = OUTPUT_DIR / "manuel-de-presence-atelier-zydka.pdf"
IMAGES_DIR = BASE_DIR / "images"
PORT = 8765

# ============================================================
# HTML + CSS + JS (intégrés)
# ============================================================

HTML_PREMIUM = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Atelier Zydka — Studio de présence</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0B0B0A;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.5;
            color: #F6F6F4;
            padding: 32px 40px;
        }

        /* Grille principale */
        .container {
            max-width: 1480px;
            margin: 0 auto;
        }

        /* En-tête */
        .header {
            border-bottom: 1px solid rgba(216,201,174,0.2);
            padding-bottom: 24px;
            margin-bottom: 32px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            flex-wrap: wrap;
        }
        .header h1 {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.03em;
            text-transform: uppercase;
            color: #F6F6F4;
        }
        .header .sub {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            text-transform: uppercase;
            color: #D8C9AE;
            letter-spacing: 0.08em;
        }
        .header .status {
            font-size: 13px;
            color: #8A8A88;
        }

        /* Deux colonnes */
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 32px;
        }

        /* Colonne principale */
        .editor-panel {
            background: #1A1A18;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #2A2A28;
        }
        .panel-header {
            background: #0F0F0E;
            padding: 16px 24px;
            border-bottom: 1px solid #2A2A28;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .panel-header h2 {
            font-size: 16px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #D8C9AE;
        }
        .badge {
            background: #2A353F;
            padding: 4px 12px;
            border-radius: 40px;
            font-size: 12px;
            font-family: monospace;
        }
        textarea {
            width: 100%;
            background: #121210;
            color: #F6F6F4;
            border: none;
            padding: 24px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 13px;
            line-height: 1.6;
            resize: vertical;
            outline: none;
        }
        .toolbar {
            padding: 12px 24px;
            background: #0F0F0E;
            border-top: 1px solid #2A2A28;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .tool-btn {
            background: #2A353F;
            border: none;
            color: #F6F6F4;
            padding: 6px 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tool-btn:hover {
            background: #D8C9AE;
            color: #0B0B0A;
        }

        /* Colonne latérale */
        .tools-panel {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        .card {
            background: #1A1A18;
            border-radius: 12px;
            border: 1px solid #2A2A28;
            overflow: hidden;
        }
        .card-header {
            background: #0F0F0E;
            padding: 16px 20px;
            border-bottom: 1px solid #2A2A28;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 13px;
        }
        .card-content {
            padding: 20px;
        }
        .btn {
            background: #D8C9AE;
            color: #0B0B0A;
            border: none;
            padding: 10px 20px;
            font-weight: 700;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: 0.15s;
            display: inline-block;
            text-align: center;
            text-decoration: none;
        }
        .btn-secondary {
            background: #2A353F;
            color: #F6F6F4;
        }
        .btn-block {
            display: block;
            width: 100%;
            margin-top: 12px;
        }
        .file-input {
            margin-bottom: 16px;
        }
        .file-input label {
            display: block;
            font-size: 12px;
            margin-bottom: 6px;
            color: #D8C9AE;
        }
        .file-input input {
            width: 100%;
            background: #0F0F0E;
            border: 1px solid #2A2A28;
            padding: 10px;
            border-radius: 6px;
            color: #F6F6F4;
        }
        .log-area {
            background: #0F0F0E;
            border-radius: 8px;
            padding: 16px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: #B0B0A8;
        }
        .preview {
            background: #0B0B0A;
            border-radius: 8px;
            margin-top: 16px;
            border: 1px solid #2A2A28;
            min-height: 280px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        iframe {
            width: 100%;
            border: none;
            border-radius: 8px;
            background: white;
        }
        .status-ok { color: #7A9F7A; }
        .status-warn { color: #D8C9AE; }
        .status-err { color: #C96A6A; }
        hr {
            border-color: #2A2A28;
            margin: 16px 0;
        }
        @media (max-width: 900px) {
            body { padding: 20px; }
            .dashboard { grid-template-columns: 1fr; }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <h1>LE MANUEL DE PRÉSENCE</h1>
            <div class="sub">Atelier Zydka — Studio de présence</div>
        </div>
        <div class="status" id="statusIndicator">✔️ Serveur actif</div>
    </div>

    <div class="dashboard">
        <!-- Colonne gauche : éditeur -->
        <div class="editor-panel">
            <div class="panel-header">
                <h2>📄 Manuscrit enrichi</h2>
                <div class="badge" id="manuscritStatus">–</div>
            </div>
            <textarea id="manuscritEditor" rows="18" placeholder="Charge ou crée ton manuscrit ici..."></textarea>
            <div class="toolbar">
                <button class="tool-btn" data-tag="[QUOTE: ]">📌 Citation</button>
                <button class="tool-btn" data-tag="[IMAGE:  | Légende]">🖼️ Image</button>
                <button class="tool-btn" data-tag="[CALLOUT: Titre | Texte]">📦 Callout</button>
                <button class="tool-btn" data-tag="[OPENING_IMAGE:  | Titre]">🌄 Ouverture visuelle</button>
                <button class="tool-btn" data-tag="[PAGE_BREAK]">⤵️ Saut de page</button>
                <button class="tool-btn" data-help>❓ Balises</button>
            </div>
        </div>

        <!-- Colonne droite : outils -->
        <div class="tools-panel">
            <div class="card">
                <div class="card-header">🔧 Actions</div>
                <div class="card-content">
                    <div class="file-input">
                        <label>Importer un manuscrit (.txt)</label>
                        <input type="file" id="manuscritFile" accept=".txt">
                    </div>
                    <button id="saveBtn" class="btn btn-block">💾 Sauvegarder le manuscrit</button>
                    <button id="generateBtn" class="btn btn-block btn-secondary">⚙️ Générer le PDF</button>
                    <button id="checkImagesBtn" class="btn btn-block">🖼️ Vérifier les images</button>
                    <button id="openFolderBtn" class="btn btn-block">📂 Ouvrir dossier manuelsortie</button>
                    <hr>
                    <a id="pdfLink" href="#" target="_blank" style="display:none;" class="btn btn-block">📖 Ouvrir le PDF</a>
                </div>
            </div>

            <div class="card">
                <div class="card-header">📋 Journal</div>
                <div class="card-content">
                    <div id="logArea" class="log-area">Prêt. Charge un manuscrit ou écris directement dans l’éditeur.</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">👁️ Aperçu PDF (après génération)</div>
                <div class="card-content">
                    <div id="previewContainer" class="preview">
                        <span style="color:#8A8A88;">Aucun PDF généré</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // Récupérer les éléments
    const editor = document.getElementById('manuscritEditor');
    const manuscritFile = document.getElementById('manuscritFile');
    const saveBtn = document.getElementById('saveBtn');
    const generateBtn = document.getElementById('generateBtn');
    const checkImagesBtn = document.getElementById('checkImagesBtn');
    const openFolderBtn = document.getElementById('openFolderBtn');
    const logArea = document.getElementById('logArea');
    const pdfLink = document.getElementById('pdfLink');
    const previewContainer = document.getElementById('previewContainer');
    const manuscritStatus = document.getElementById('manuscritStatus');

    // Charger le manuscrit existant au démarrage
    async function loadManuscript() {
        const res = await fetch('/api/manuscript');
        const data = await res.json();
        if (data.content !== undefined) {
            editor.value = data.content;
            manuscritStatus.innerText = data.exists ? '✅ Chargé' : '📝 Nouveau fichier';
            log('Manuscrit chargé depuis le serveur.');
        } else {
            log('Erreur : impossible de charger le manuscrit.');
        }
    }
    loadManuscript();

    // Sauvegarder le manuscrit
    async function saveManuscript() {
        const content = editor.value;
        const res = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });
        const data = await res.json();
        if (data.ok) {
            log('✅ Manuscrit sauvegardé avec succès.');
            manuscritStatus.innerText = '✅ Sauvegardé';
        } else {
            log('❌ Erreur lors de la sauvegarde : ' + data.error);
        }
    }

    // Générer le PDF
    async function generatePDF() {
        log('⚙️ Lancement de la génération du PDF...');
        // D'abord sauvegarder le manuscrit actuel
        await saveManuscript();
        const res = await fetch('/api/generate', { method: 'POST' });
        const data = await res.json();
        if (data.ok) {
            log('✅ PDF généré avec succès.');
            log(data.output || '');
            // Afficher le lien et l'aperçu
            pdfLink.style.display = 'block';
            pdfLink.href = '/pdf';
            // Charger l'aperçu (iframe)
            previewContainer.innerHTML = '<iframe src="/pdf" style="width:100%; height:280px;" title="Aperçu PDF"></iframe>';
            // Vérifier le statut des polices etc.
            if (data.warning) log('⚠️ ' + data.warning);
        } else {
            log('❌ Échec de génération : ' + data.error);
            if (data.stderr) log(data.stderr);
        }
    }

    // Vérifier les images
    async function checkImages() {
        const res = await fetch('/api/check-images');
        const data = await res.json();
        if (data.ok) {
            log(data.result);
        } else {
            log('Erreur : ' + data.error);
        }
    }

    // Ouvrir le dossier de sortie
    async function openFolder() {
        const res = await fetch('/api/open-folder');
        const data = await res.json();
        if (data.ok) {
            log('📂 Dossier manuelsortie ouvert.');
        } else {
            log('❌ Impossible d\'ouvrir le dossier.');
        }
    }

    // Ajouter une balise à l'éditeur à la position du curseur
    function insertTag(tag) {
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        const text = editor.value;
        const before = text.substring(0, start);
        const after = text.substring(end);
        editor.value = before + tag + after;
        editor.focus();
        editor.selectionStart = editor.selectionEnd = start + tag.length;
        log(`Balise insérée : ${tag}`);
    }

    // Helper pour les logs
    function log(msg) {
        logArea.innerText += msg + '\n';
        logArea.scrollTop = logArea.scrollHeight;
    }

    // Events
    saveBtn.addEventListener('click', saveManuscript);
    generateBtn.addEventListener('click', generatePDF);
    checkImagesBtn.addEventListener('click', checkImages);
    openFolderBtn.addEventListener('click', openFolder);

    // Importation d'un fichier manuscrit
    manuscritFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            editor.value = ev.target.result;
            log(`Fichier importé : ${file.name}`);
            manuscritStatus.innerText = '📄 Importé (non sauvegardé)';
        };
        reader.readAsText(file, 'UTF-8');
    });

    // Assistant balises
    document.querySelectorAll('.tool-btn[data-tag]').forEach(btn => {
        btn.addEventListener('click', () => {
            insertTag(btn.getAttribute('data-tag'));
        });
    });
    document.querySelector('.tool-btn[data-help]').addEventListener('click', () => {
        log('Balises disponibles :\n[QUOTE: Texte]\n[IMAGE: fichier.jpg | Légende]\n[CALLOUT: Titre | Texte]\n[OPENING_IMAGE: fichier.jpg | Titre]\n[PAGE_BREAK]\nTableaux Markdown : | Col1 | Col2 |\\n| --- | --- |\\n| val1 | val2 |');
    });

    // Nettoyer le log (optionnel)
    window.log = log;
</script>
</body>
</html>
"""

# ============================================================
# SERVEUR HTTP AVEC API JSON
# ============================================================

class PremiumHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PREMIUM.encode("utf-8"))
            return

        if path == "/api/manuscript":
            self.send_json_manuscript()
            return

        if path == "/api/check-images":
            self.send_json_check_images()
            return

        if path == "/pdf":
            self.send_pdf()
            return

        self.send_error(404, "Page non trouvée")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/save":
            self.save_manuscript()
            return

        if path == "/api/generate":
            self.generate_pdf()
            return

        if path == "/api/open-folder":
            self.open_folder()
            return

        self.send_error(404, "Endpoint inconnu")

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def send_json_manuscript(self):
        exists = MANUSCRIPT.exists()
        content = ""
        if exists:
            content = MANUSCRIPT.read_text(encoding="utf-8")
        self.send_json({"exists": exists, "content": content})

    def save_manuscript(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(body)
            content = data.get("content", "")
            MANUSCRIPT.write_text(content, encoding="utf-8")
            self.send_json({"ok": True})
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)}, code=500)

    def generate_pdf(self):
        if not GENERATOR.exists():
            self.send_json({"ok": False, "error": "Générateur introuvable"})
            return
        try:
            result = subprocess.run(
                [sys.executable, str(GENERATOR)],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=120
            )
            output_text = result.stdout.strip()
            stderr_text = result.stderr.strip()
            ok = result.returncode == 0 and OUTPUT_PDF.exists()
            warning = None
            if "polices fallback" in output_text or "fallback" in stderr_text:
                warning = "Polices fallback utilisées (rendu moins fidèle)"
            self.send_json({
                "ok": ok,
                "output": output_text,
                "stderr": stderr_text,
                "warning": warning
            })
        except subprocess.TimeoutExpired:
            self.send_json({"ok": False, "error": "Génération trop longue (>120s)"}, code=500)
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)}, code=500)

    def send_json_check_images(self):
        if not MANUSCRIPT.exists():
            self.send_json({"ok": True, "result": "⚠️ manuscrit_beatmakers.txt introuvable"})
            return
        if not IMAGES_DIR.exists():
            self.send_json({"ok": True, "result": "⚠️ dossier images/ introuvable"})
            return
        text = MANUSCRIPT.read_text(encoding="utf-8")
        names = []
        for pattern in [r"\[IMAGE:\s*([^|\]]+)", r"\[OPENING_IMAGE:\s*([^|\]]+)"]:
            for m in re.findall(pattern, text):
                names.append(m.strip())
        if not names:
            self.send_json({"ok": True, "result": "Aucune image déclarée dans le manuscrit."})
            return
        lines = []
        missing = []
        for name in names:
            path = IMAGES_DIR / name
            if path.exists():
                lines.append(f"✅ {name}")
            else:
                lines.append(f"❌ {name} introuvable")
                missing.append(name)
        if missing:
            lines.append("⚠️ Corrige les noms avant export final.")
        self.send_json({"ok": True, "result": "\n".join(lines)})

    def open_folder(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        subprocess.run(["open", str(OUTPUT_DIR)])
        self.send_json({"ok": True})

    def send_pdf(self):
        if not OUTPUT_PDF.exists():
            self.send_error(404, "PDF non généré encore")
            return
        data = OUTPUT_PDF.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    print(f"Interface web premium Atelier Zydka : http://127.0.0.1:{PORT}")
    print("Laisse ce terminal ouvert pendant l’utilisation.")
    server = HTTPServer(("127.0.0.1", PORT), PremiumHandler)
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        server.shutdown()


if __name__ == "__main__":
    main()