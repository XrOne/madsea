"""
Script pour lancer automatiquement le serveur HTTP au bon dossier pour le front Madsea.
Usage : python serve_frontend.py
"""
import http.server
import socketserver
import os

# Chemin du dossier front (à adapter si besoin)
FRONT_DIR = os.path.join(os.path.dirname(__file__), '../front madsea')
PORT = 8888

os.chdir(FRONT_DIR)
print(f"[Madsea] Serveur HTTP lancé sur {PORT} dans le dossier : {os.path.abspath(FRONT_DIR)}")
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Accès : http://localhost:{PORT}/index.html")
    httpd.serve_forever()
