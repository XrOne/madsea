# Définition des Séquences, Plans et Rôle des Styles Visuels dans Madsea

Ce document clarifie la terminologie et le workflow liés aux séquences et aux plans dans le projet Madsea, en particulier concernant l'influence des styles visuels.

## 1. Plan

*   Un **Plan** correspond à une unique image extraite d'un fichier PDF de storyboard. Chaque image individuelle du storyboard est considérée comme un plan distinct.

## 2. Séquence

*   Une **Séquence** est constituée d'un ensemble de plusieurs plans successifs.
*   La caractéristique principale qui définit et délimite une séquence est la **cohérence de son style visuel**.

## 3. Styles Visuels et Délimitation des Séquences (Exemple : Série "Déclic")

Pour la série "Déclic", deux styles visuels majeurs sont utilisés :

*   **Style "Ombres Chinoises"**:
    *   Généré par Intelligence Artificielle (IA) via ComfyUI, en utilisant des techniques comme les LoRA.
    *   C'est le style principal sur lequel se concentre l'outil Madsea pour la génération.
*   **Style "Labo"**:
    *   Créé par une équipe 3D de manière traditionnelle.
    *   Ces séquences ne sont pas générées par l'outil Madsea IA.

Une séquence dans un style donné (par exemple, "Ombres Chinoises") continue tant que les plans consécutifs partagent ce style. La séquence s'achève dès qu'un changement de style intervient. Ce changement marque le début d'une nouvelle séquence (qui pourrait être "Style Labo", ou une nouvelle séquence "Ombres Chinoises" après un interlude dans un autre style).

## 4. Workflow Utilisateur pour la Sélection et l'Identification des Séquences

*   **Sélection des Plans pour Séquences IA**: L'utilisateur (réalisateur, storyboarder) sélectionnera manuellement les plans extraits du PDF qui doivent composer une séquence à générer dans un style IA (par exemple, "Ombres Chinoises"). Toutes les images d'un PDF ne seront pas nécessairement utilisées pour une séquence IA.
*   **Identification des Séquences**: Pour éviter toute ambiguïté et perte d'information, l'utilisateur pourra, si nécessaire, indiquer le numéro de la séquence (par exemple, `SQ0010`, `SQ0020`) directement dans les textes ou annotations extraits associés aux plans lors de la phase de préparation ou de sélection. Cela permettra au système de regrouper correctement les plans, même s'ils ne sont pas tous traités par l'IA.

## 5. Implication pour la Nomenclature

La nomenclature `E{épisode}_SQ{séquence}-{plan}_{tâche}_v{version}.{ext}` reste valide.
*   `SQ{séquence}`: Sera déterminé par l'utilisateur en fonction de ces groupements par style.
*   `{plan}`: Correspondra toujours à une image individuelle du storyboard.
*   `{tâche}`: Indiquera le type de traitement (ex: `AI-concept-ombre-chinoise`, `extracted-raw`).

Cette approche permet une flexibilité où le contenu d'un seul PDF peut potentiellement être divisé en plusieurs séquences distinctes basées sur le style, ou à l'inverse, où seule une partie des plans d'un PDF est utilisée pour une séquence IA spécifique.
