# PROTOCOL MADSEA

## Workflows utilisateur
1. Importer PDF → Extraire pages automatiquement
2. Vérifier extraction → Ajuster OCR si nécessaire
3. Sélectionner style → Générer images pour tous les plans
4. Prévisualiser/Comparer → Exporter résultats finaux

## Workflows développeur
1. Développer services indépendamment (extraction, génération, UI)
2. Tester extraction PDF en priorité (multi-pages, OCR)
3. Configurer ComfyUI avec workflows ControlNet
4. Respecter nomenclature pour tous les fichiers générés

## Standards de code
- Python: docstrings Google format, typing hints
- Frontend: React fonctionnel, Tailwind pour UI
- Tests: unitaires avant intégration
- Documentation: Markdown dans docs/

## Gestion des versions
- Incrémentation automatique des versions de fichiers
- Conservation des archives pour comparaison
- Nomenclature stricte E202_SQ0010-0010_AI-concept_v0001.png
