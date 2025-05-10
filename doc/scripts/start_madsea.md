# Guide du Script `start_madsea.bat`

## Objectif
Script principal pour démarrer tous les composants de l'application Madsea dans le bon ordre.

## Prérequis
- Tesseract OCR installé
- Python avec environnement virtuel configuré
- Node.js pour le frontend React

## Fonctionnement Détaillé

1. **Vérification des prérequis**
   - Vérifie l'existence de l'environnement virtuel Python
   - Vérifie que Tesseract est installé
   - Vérifie les dossiers essentiels (ocr, temp, uploads)

2. **Démarrage séquentiel des services**
   - ComfyUI en premier (port 8188, temps d'attente 10s)
   - Backend Flask ensuite (port 5000, temps d'attente 5s)
   - Frontend React en dernier (port 5173, temps d'attente 8s)

3. **Ouverture des interfaces**
   - Frontend React : http://localhost:5173 (interface principale)
   - ComfyUI : http://localhost:8188 (génération d'images)

## Exécution
```
i:\Madsea\start_madsea.bat
```

## Dépannage
- **Erreur Tesseract** : Vérifier l'installation avec `i:\Madsea\scripts\check_integrity.bat`
- **Backend Flask** : Vérifier les logs dans la fenêtre de terminal
- **Frontend React** : Vérifier la console du navigateur

## Bonnes Pratiques
- Toujours fermer proprement les services (fermer les fenêtres CMD)
- Relancer le script en cas de modification des fichiers de configuration
- Garder la console du backend ouverte pour surveiller les logs d'extraction