# Définition des Séquences, Plans et Styles dans Madsea

## Concepts fondamentaux

### Plan

Un **plan** est une image unique extraite d'un PDF de storyboard. C'est l'unité élémentaire visuelle du projet, représentant une composition spécifique à transformer en style "Ombres Chinoises" ou autre.

Chaque plan est identifié par un numéro incrémental (généralement par pas de 10) au sein d'une séquence, par exemple : `0010`, `0020`, etc.

### Séquence

Une **séquence** est un ensemble de plans successifs définis par une cohérence de style visuel. Pour la série "Déclic", les styles principaux sont :

1. **Ombres Chinoises** : Style silhouette noir sur fond contrasté, généré par IA
2. **Style Labo** : Rendu 3D pour les scènes se déroulant en laboratoire

Une séquence est identifiée par un préfixe "SQ" suivi d'un numéro à 4 chiffres, par exemple : `SQ0010`.

Important : Un changement de style marque le début d'une nouvelle séquence.

### Style visuel

Le **style visuel** détermine l'apparence finale des plans générés. Pour "Ombres Chinoises", ce style se caractérise par :

- Silhouettes noires ou très sombres
- Contraste élevé
- Détails limités mais suffisants pour reconnaître les personnages et objets
- Ambiance cinématographique
- Éclairage dramatique avec parfois des effets de contre-jour

## Workflow Utilisateur

1. **Extraction du PDF** : L'utilisateur upload un PDF de storyboard qui est automatiquement décomposé en plans individuels.

2. **Attribution des numéros de séquence** : L'utilisateur peut spécifier le numéro de séquence (SQxxxx) pour chaque plan extrait. Ceci est particulièrement important car toutes les images d'un PDF ne seront pas nécessairement utilisées dans une séquence "Ombres Chinoises".

3. **Sélection des plans** : L'utilisateur sélectionne les plans qui doivent être transformés en style "Ombres Chinoises".

4. **Génération par IA** : Les plans sélectionnés sont envoyés à ComfyUI qui applique le style "Ombres Chinoises" tout en préservant la composition originale.

5. **Validation** : L'utilisateur valide ou rejette les plans générés, avec possibilité de régénérer si nécessaire.

## Nomenclature des fichiers

La nomenclature `E{saison_episode}_SQ{sequence}-{plan}_{tache}_v{version}.{extension}` est strictement appliquée à chaque étape :

- **Pour les plans extraits** : `E202_SQ0010-0010_extracted-raw_v0001.png`
- **Pour les plans générés** : `E202_SQ0010-0010_AI-concept_v0001.png`

Cette nomenclature assure la traçabilité et l'organisation cohérente du projet, particulièrement important pour gérer les 70 plans prévus en 10 jours.

## Style "Ombres Chinoises" - Spécifications techniques

Le style "Ombres Chinoises" pour la série "Déclic" est généré à l'aide de :

1. **Modèle de base** : SDE-LCM 3.2
2. **ControlNet** : UHD v2.5 (Canny, Depth, Pose) pour préserver la composition
3. **LoRA spécifique** : ShadowCraft XL v2.1 pour l'effet silhouette
4. **IP-Adapter** : Utilisant des références du dossier `declics/ombre chinoise/`
5. **Prompts optimisés** : Intégrant des mentions explicites du style cinématographique silhouette

Ce workflow technique produit des images qui respectent fidèlement la composition du storyboard original tout en y appliquant l'esthétique "Ombres Chinoises" caractéristique de la série "Déclic".

## Exemples visuels

Le dossier `i:\Madsea\declics\ombre chinoise\` contient 65+ exemples du style recherché. Ces images servent à la fois de :

1. Références pour les humains évaluant la qualité des générations
2. Données d'apprentissage pour l'IP-Adapter
3. Guide visuel pour ajuster les paramètres du workflow