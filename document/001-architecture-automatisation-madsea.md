# 001-architecture-automatisation-madsea.md

## Résumé exécutif
Architecture automatisée pour la génération de plans IA à partir de storyboards PDF, pilotée par une interface créative, orchestrant ComfyUI (local/cloud) via Puppeteer/MCP, avec gestion stricte de la nomenclature et feedback visuel temps réel.

---

## 1. Schéma global du workflow

```mermaid
graph TD
    A[Utilisateur: Création Projet] --> B[Upload Storyboard PDF]
    B --> C[Extraction Images + Textes (Backend)]
    C --> D[Grille Sélection Plans (Frontend)]
    D --> E[Choix Style & Workflow IA]
    E --> F{Mode}
    F -- Auto --> G[Puppeteer contrôle ComfyUI]
    F -- Manuel --> H[ComfyUI Web UI]
    G --> I[Génération Images IA]
    H --> I
    I --> J[Renommage & Log Nomenclature]
    J --> K[Feedback Visuel Frontend]
    K --> L[Validation/Export]
```

---

## 2. Composants principaux

- **Frontend React/Tailwind**
  - Sélection visuelle des plans à générer
  - Choix du style (Ombres Chinoises, Labo, etc.)
  - Configuration du workflow IA (JSON, sliders)
  - Feedback progression, logs, relance en cas d’erreur

- **Backend FastAPI**
  - Extraction PDF (PyMuPDF, OCR)
  - API `/api/generate_ai_concept` orchestrant la génération IA
  - Service de nomenclature et log CSV
  - Appel du script Puppeteer (mode auto) ou gestion des uploads manuels

- **Automatisation ComfyUI (MCP Puppeteer)**
  - Contrôle l’UI ComfyUI (local/cloud)
  - Upload images, lance la génération, télécharge les résultats
  - Respecte la nomenclature Madsea
  - Loggue chaque étape pour le frontend

- **ComfyUI (local ou cloud)**
  - Exécute les workflows IA (Ombres Chinoises, Labo…)
  - Génère les images à partir des inputs reçus

---

## 3. Flux de données et interactions clés

1. **Utilisateur crée projet, importe PDF**
2. **Backend extrait images/textes, frontend affiche la grille**
3. **Utilisateur sélectionne les plans à générer, configure le style**
4. **Frontend envoie la sélection au backend (API)**
5. **Backend lance la génération IA (auto : Puppeteer, manuel : attends upload)**
6. **Les images générées sont renommées, loguées, et affichées dans la grille**
7. **Utilisateur valide, exporte ou relance selon besoin**

---

## 4. Points de vigilance
- Respect strict de la nomenclature Madsea
- Robustesse du batch (gestion erreurs, logs)
- Séparation claire auto/manuel
- Feedback utilisateur en temps réel
- Scalabilité local/cloud

---

**Validation ? Questions ? On passe à la spec d’API ?**
