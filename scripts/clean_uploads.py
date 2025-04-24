#!/usr/bin/env python3
"""
Nettoyage sécurisé du dossier uploads/ pour Madsea.
- Supprime tous les dossiers/fichiers générés (sessions, images, pdf, zip)
- Ne supprime JAMAIS .gitkeep, ni la structure uploads/ elle-même
- Mode dry-run par défaut (affiche ce qui serait supprimé)
- Mode suppression réelle avec --force
"""
import os
import sys
import shutil

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
PROTECTED_FILES = {'.gitkeep'}

def clean_uploads(force=False):
    if not os.path.isdir(UPLOADS_DIR):
        print(f"[clean_uploads] Dossier introuvable: {UPLOADS_DIR}")
        return
    for name in os.listdir(UPLOADS_DIR):
        path = os.path.join(UPLOADS_DIR, name)
        if name in PROTECTED_FILES:
            print(f"[clean_uploads] Protégé: {name}")
            continue
        if os.path.isdir(path):
            print(f"[clean_uploads] {'SUPPRESSION' if force else 'Dry-run'} dossier: {path}")
            if force:
                shutil.rmtree(path)
        else:
            print(f"[clean_uploads] {'SUPPRESSION' if force else 'Dry-run'} fichier: {path}")
            if force:
                os.remove(path)
    print("[clean_uploads] Nettoyage terminé.")

if __name__ == '__main__':
    force = '--force' in sys.argv
    print(f"[clean_uploads] Nettoyage uploads/ ({'SUPPRESSION RÉELLE' if force else 'DRY-RUN'})")
    clean_uploads(force=force)
