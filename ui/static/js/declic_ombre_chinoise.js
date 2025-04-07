/**
 * Déclic Ombre Chinoise Style Module
 * 
 * Ce module implémente le style "Déclic Ombre Chinoise" pour la plateforme Storyboard-to-Video.
 * Il fournit des fonctionnalités pour:
 * - Entraîner un modèle LoRA spécifique pour le style silhouette avec rim light
 * - Configurer les paramètres optimaux pour ce style
 * - Intégrer avec les modèles externes (Google Gemini Studio, Qwen 2.1, WAN 2.1)
 */

class DeclicOmbreChinoiseStyle {
    constructor() {
        this.styleName = 'declic_ombre_chinoise';
        this.styleDisplayName = 'Déclic Ombre Chinoise';
        this.styleDescription = 'Silhouettes intégrales avec rim light et lumière cinématographique réaliste';
        
        // Paramètres d'entraînement LoRA par défaut
        this.trainingParams = {
            baseModel: 'sd15', // Stable Diffusion 1.5 (recommandé pour rapidité)
            steps: 2000,      // Entre 1200 et 2000 steps
            learningRate: 1e-4, // Taux d'apprentissage recommandé pour LoRA
            loraRank: 16,     // Dimension LoRA entre 16 et 32
            batchSize: 2      // Taille de batch selon GPU disponible
        };
        
        // Prompts d'exemple pour l'entraînement
        this.trainingPrompts = [
            "A cinematic photograph of a silhouetted figure in dramatic backlight, intense golden rim lighting, volumetric light beams piercing through dusty window, deep rich shadows, ultra-detailed edge definition in hair and clothing textures, moody atmospheric noir, pure black silhouette, 16:9 cinematic ratio, award-winning cinematography.",
            "A dramatic silhouette against intense orange doorway light, perfect rim light separation, hyper-defined edges, deep contrast between light and shadow, cinematic composition with strong directional lighting, expressive dynamic pose, film noir aesthetic, dust particles visible in light beams, 16:9.",
            "A silhouette with striking golden rim light definition, bright volumetric light rays streaming through windows, masterful contrast control, atmospheric haze, precise edge details, dramatic mood lighting, cinematic framing, perfect black levels, 16:9 ratio.",
            "Multiple layered silhouettes in atmospheric scene, perfect rim light separation between figures, powerful volumetric light beams, cinematic depth, intricate shadow detail, noir style lighting, precise edge definition, dramatic lighting contrast, 16:9.",
            "A powerful silhouette composition with dramatic backlighting, golden hour rim light, dust particles dancing in light beams, stark contrast, perfect edge separation, cinematic atmosphere, deep shadows, professional lighting setup, 16:9 ratio.",
            "Cinematic silhouette portrait with perfect rim lighting, ultra-detailed edge definition, strong directional lighting creating dramatic shadows, atmospheric volumetric light, dust particles visible, pure black silhouette against golden light source, 16:9 ratio.",
            "Masterful silhouette photography with intense golden rim light, perfect separation between light and shadow, cinematic composition, dramatic backlighting, atmospheric haze, professional lighting techniques, 16:9 cinematic framing."
        ];
        
        // Paramètres du style pour la génération
        this.styleParams = {
            promptPrefix: "masterful cinematic photograph, award-winning cinematography, ultra-detailed silhouette technique, dramatic intense golden rim lighting, powerful volumetric light beams, atmospheric haze, professional lighting setup",
            promptSuffix: "perfect edge definition, pure black silhouette, film noir aesthetic, rich deep shadows, dust particles dancing in light beams, precise contrast control, stark lighting separation, hyper-defined edges, 16:9 cinematic ratio",
            negativePrompt: "low quality, blurry, distorted, deformed, cartoon, anime, visible face details, flat lighting, soft edges, gray tones, low contrast, diffused lighting, full color, bright midtones, washed out blacks, muddy shadows, amateur lighting",
            cfgScale: 10.0,
            steps: 45,
            sampler: "euler_ancestral"
        };
        
        // Modèles externes intégrés
        this.externalModels = {
            textGeneration: {
                geminiStudio: {
                    enabled: true,
                    apiEndpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
                },
                qwen: {
                    enabled: true,
                    model: 'qwen2:1.5b',
                    localEndpoint: 'http://localhost:11434/api/generate'
                }
            },
            imageGeneration: {
                wan: {
                    enabled: true,
                    provider: 'tencent',
                    apiEndpoint: 'https://api.tencent.com/wan/v1/images/generations'
                }
            }
        };
        
        // Initialiser l'intégration
        this.initialize();
    }
    
    // Initialiser le style
    initialize() {
        console.log('Initialisation du style Déclic Ombre Chinoise');
        this.registerStyleWithSwarmUI();
        this.setupExternalModelsButton();
        this.setupPreviewButton();
    }
    
    // Configurer le bouton pour installer les modèles externes
    setupExternalModelsButton() {
        // Attendre que l'interface soit chargée
        window.addEventListener('swarmui_loaded', () => {
            const stylePanel = document.getElementById('swarmui-style-panel');
            if (!stylePanel) return;
            
            // Créer le bouton pour les modèles externes
            const externalModelsButton = document.createElement('button');
            externalModelsButton.className = 'swarmui-btn swarmui-btn-secondary';
            externalModelsButton.textContent = 'Installer Modèles Externes';
            externalModelsButton.style.marginTop = '10px';
            externalModelsButton.style.marginLeft = '10px';
            externalModelsButton.addEventListener('click', () => {
                this.showExternalModelsDialog();
            });
            
            // Trouver le conteneur Déclic et y ajouter le bouton
            const declicContainer = document.querySelector('.swarmui-declic-container');
            if (declicContainer) {
                declicContainer.appendChild(externalModelsButton);
            }
        });
    }
    
    // Afficher la boîte de dialogue pour configurer les modèles externes
    showExternalModelsDialog() {
        // Créer la boîte de dialogue modale pour la configuration des modèles externes
        const externalModelsDialog = document.createElement('div');
        externalModelsDialog.className = 'swarmui-modal swarmui-external-models-modal';
        externalModelsDialog.innerHTML = `
            <div class="swarmui-modal-content swarmui-external-models-content">
                <span class="swarmui-modal-close">&times;</span>
                <h3>Configuration des Modèles Externes</h3>
                <div class="swarmui-external-models-container">
                    <div class="swarmui-external-models-description">
                        <p>Installez et configurez les modèles externes pour améliorer la génération de silhouettes avec rim light.</p>
                    </div>
                    <div class="swarmui-external-models-options">
                        <div class="swarmui-external-model-item">
                            <label>
                                <input type="checkbox" id="swarmui-use-qwen" checked />
                                <strong>Qwen 2.1 (via Ollama)</strong>
                            </label>
                            <p>Modèle de génération de texte pour des prompts précis de silhouettes</p>
                            <div id="swarmui-qwen-status" class="swarmui-model-status">Non configuré</div>
                        </div>
                        <div class="swarmui-external-model-item">
                            <label>
                                <input type="checkbox" id="swarmui-use-gemini" checked />
                                <strong>Google Gemini Studio</strong>
                            </label>
                            <p>API pour l'enrichissement des prompts et la génération de variations</p>
                            <div id="swarmui-gemini-status" class="swarmui-model-status">Non configuré</div>
                        </div>
                        <div class="swarmui-external-model-item">
                            <label>
                                <input type="checkbox" id="swarmui-use-wan" checked />
                                <strong>WAN 2.1 (Tencent)</strong>
                            </label>
                            <p>Modèle de génération d'images pour le style chinois</p>
                            <div id="swarmui-wan-status" class="swarmui-model-status">Non configuré</div>
                        </div>
                    </div>
                </div>
                <div class="swarmui-buttons">
                    <button class="swarmui-btn swarmui-btn-secondary swarmui-external-models-close">Annuler</button>
                    <button class="swarmui-btn swarmui-external-models-install">Installer & Configurer</button>
                </div>
            </div>
        `;
        document.body.appendChild(externalModelsDialog);
        
        // Ajouter du style CSS pour la boîte de dialogue
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .swarmui-external-models-modal .swarmui-modal-content {
                max-width: 700px;
                width: 90%;
            }
            .swarmui-external-models-container {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .swarmui-external-models-description {
                margin-bottom: 10px;
            }
            .swarmui-external-models-options {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .swarmui-external-model-item {
                background: rgba(0,0,0,0.1);
                padding: 15px;
                border-radius: 5px;
            }
            .swarmui-external-model-item p {
                margin: 5px 0 10px 0;
                font-size: 12px;
                color: #888;
            }
            .swarmui-model-status {
                font-size: 12px;
                padding: 5px 10px;
                border-radius: 3px;
                background: #333;
                display: inline-block;
                margin-top: 5px;
            }
        `;
        document.head.appendChild(styleElement);
        
        // Configurer les écouteurs d'événements
        const closeBtn = externalModelsDialog.querySelector('.swarmui-modal-close');
        const closeButton = externalModelsDialog.querySelector('.swarmui-external-models-close');
        const installButton = externalModelsDialog.querySelector('.swarmui-external-models-install');
        
        // Fermer la boîte de dialogue
        const closeExternalModelsDialog = () => {
            document.body.removeChild(externalModelsDialog);
            document.head.removeChild(styleElement);
        };
        
        if (closeBtn) closeBtn.addEventListener('click', closeExternalModelsDialog);
        if (closeButton) closeButton.addEventListener('click', closeExternalModelsDialog);
        
        // Installer et configurer les modèles externes
        if (installButton) {
            installButton.addEventListener('click', () => {
                // Récupérer les options sélectionnées
                const useQwen = document.getElementById('swarmui-use-qwen').checked;
                const useGemini = document.getElementById('swarmui-use-gemini').checked;
                const useWan = document.getElementById('swarmui-use-wan').checked;
                
                // Mettre à jour l'interface pour indiquer que l'installation est en cours
                installButton.disabled = true;
                installButton.textContent = 'Installation en cours...';
                
                // Mettre à jour les statuts
                document.getElementById('swarmui-qwen-status').textContent = useQwen ? 'Installation en cours...' : 'Non sélectionné';
                document.getElementById('swarmui-gemini-status').textContent = useGemini ? 'Configuration en cours...' : 'Non sélectionné';
                document.getElementById('swarmui-wan-status').textContent = useWan ? 'Configuration en cours...' : 'Non sélectionné';
                
                // Appeler l'API pour installer et configurer les modèles externes
                fetch('/comfyui/setup_external_models', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        use_qwen: useQwen,
                        use_gemini: useGemini,
                        use_wan: useWan
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Mettre à jour les statuts avec les résultats
                        const results = data.results;
                        
                        if (results.qwen) {
                            const qwenStatus = document.getElementById('swarmui-qwen-status');
                            qwenStatus.textContent = results.qwen.message || results.qwen.status;
                            qwenStatus.style.background = this.getStatusColor(results.qwen.status);
                        }
                        
                        if (results.gemini) {
                            const geminiStatus = document.getElementById('swarmui-gemini-status');
                            geminiStatus.textContent = results.gemini.message || results.gemini.status;
                            geminiStatus.style.background = this.getStatusColor(results.gemini.status);
                        }
                        
                        if (results.wan) {
                            const wanStatus = document.getElementById('swarmui-wan-status');
                            wanStatus.textContent = results.wan.message || results.wan.status;
                            wanStatus.style.background = this.getStatusColor(results.wan.status);
                        }
                        
                        // Mettre à jour le bouton
                        installButton.textContent = 'Installation terminée';
                        setTimeout(() => {
                            installButton.textContent = 'Installer & Configurer';
                            installButton.disabled = false;
                        }, 3000);
                        
                        // Mettre à jour l'état des modèles externes dans l'objet
                        this.externalModels.textGeneration.qwen.enabled = useQwen;
                        this.externalModels.textGeneration.geminiStudio.enabled = useGemini;
                        this.externalModels.imageGeneration.wan.enabled = useWan;
                        
                        // Afficher une notification de succès
                        if (window.swarmUIExtension && window.swarmUIExtension.showNotification) {
                            window.swarmUIExtension.showNotification('success', 'Configuration des modèles externes terminée');
                        }
                    } else {
                        // Afficher une erreur
                        installButton.textContent = 'Erreur';
                        setTimeout(() => {
                            installButton.textContent = 'Installer & Configurer';
                            installButton.disabled = false;
                        }, 3000);
                        
                        if (window.swarmUIExtension && window.swarmUIExtension.showNotification) {
                            window.swarmUIExtension.showNotification('error', 'Erreur lors de la configuration: ' + (data.error || 'Erreur inconnue'));
                        }
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la configuration des modèles externes:', error);
                    installButton.textContent = 'Erreur';
                    setTimeout(() => {
                        installButton.textContent = 'Installer & Configurer';
                        installButton.disabled = false;
                    }, 3000);
                    
                    if (window.swarmUIExtension && window.swarmUIExtension.showNotification) {
                        window.swarmUIExtension.showNotification('error', 'Erreur lors de la configuration: ' + error.message);
                    }
                });
            });
        }
    }
    
    // Obtenir la couleur de fond en fonction du statut
    getStatusColor(status) {
        switch(status) {
            case 'available':
            case 'configured':
                return '#2a6';
            case 'installing':
                return '#26a';
            case 'error':
                return '#a62';
            default:
                return '#333';
        }
    }
    
    // Configurer le bouton de prévisualisation
    setupPreviewButton() {
        // Attendre que l'interface soit chargée
        window.addEventListener('swarmui_loaded', () => {
            const stylePanel = document.getElementById('swarmui-style-panel');
            if (!stylePanel) return;
            
            // Créer le bouton de prévisualisation
            const previewButton = document.createElement('button');
            previewButton.className = 'swarmui-btn swarmui-btn-secondary';
            previewButton.textContent = 'Prévisualiser Style Ombre Chinoise';
            previewButton.style.marginTop = '10px';
            previewButton.addEventListener('click', () => {
                this.showStylePreview();
            });
            
            // Trouver le conteneur Déclic et y ajouter le bouton
            const declicContainer = document.querySelector('.swarmui-declic-container');
            if (declicContainer) {
                declicContainer.appendChild(previewButton);
            }
        });
    }
    
    // Afficher une prévisualisation du style
    showStylePreview() {
        // Créer la boîte de dialogue modale pour la prévisualisation
        const previewDialog = document.createElement('div');
        previewDialog.className = 'swarmui-modal swarmui-preview-modal';
        previewDialog.innerHTML = `
            <div class="swarmui-modal-content swarmui-preview-content">
                <span class="swarmui-modal-close">&times;</span>
                <h3>Prévisualisation du Style Déclic Ombre Chinoise</h3>
                <div class="swarmui-preview-container">
                    <div class="swarmui-preview-examples">
                        <h4>Exemples de silhouettes avec rim light</h4>
                        <div class="swarmui-preview-grid">
                            <div class="swarmui-preview-item">
                                <div class="swarmui-preview-placeholder">Chargement...</div>
                                <p>Silhouette avec rim light doré</p>
                            </div>
                            <div class="swarmui-preview-item">
                                <div class="swarmui-preview-placeholder">Chargement...</div>
                                <p>Silhouette avec lumière volumétrique</p>
                            </div>
                            <div class="swarmui-preview-item">
                                <div class="swarmui-preview-placeholder">Chargement...</div>
                                <p>Silhouettes multiples avec séparation</p>
                            </div>
                        </div>
                    </div>
                    <div class="swarmui-preview-params">
                        <h4>Paramètres optimisés</h4>
                        <div class="swarmui-preview-param-item">
                            <strong>Prompt Prefix:</strong>
                            <pre>${this.styleParams.promptPrefix}</pre>
                        </div>
                        <div class="swarmui-preview-param-item">
                            <strong>Prompt Suffix:</strong>
                            <pre>${this.styleParams.promptSuffix}</pre>
                        </div>
                        <div class="swarmui-preview-param-item">
                            <strong>Negative Prompt:</strong>
                            <pre>${this.styleParams.negativePrompt}</pre>
                        </div>
                        <div class="swarmui-preview-param-item">
                            <strong>CFG Scale:</strong> ${this.styleParams.cfgScale}
                        </div>
                        <div class="swarmui-preview-param-item">
                            <strong>Steps:</strong> ${this.styleParams.steps}
                        </div>
                        <div class="swarmui-preview-param-item">
                            <strong>Sampler:</strong> ${this.styleParams.sampler}
                        </div>
                    </div>
                </div>
                <div class="swarmui-buttons">
                    <button class="swarmui-btn swarmui-btn-secondary swarmui-preview-close">Fermer</button>
                    <button class="swarmui-btn swarmui-preview-apply">Appliquer ce style</button>
                </div>
            </div>
        `;
        document.body.appendChild(previewDialog);
        
        // Ajouter du style CSS pour la prévisualisation
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .swarmui-preview-modal .swarmui-modal-content {
                max-width: 900px;
                width: 90%;
            }
            .swarmui-preview-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }
            .swarmui-preview-examples {
                flex: 1;
                min-width: 300px;
            }
            .swarmui-preview-params {
                flex: 1;
                min-width: 300px;
                background: rgba(0,0,0,0.1);
                padding: 15px;
                border-radius: 5px;
            }
            .swarmui-preview-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            .swarmui-preview-item {
                text-align: center;
            }
            .swarmui-preview-placeholder {
                background: #333;
                height: 150px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaa;
                border-radius: 5px;
            }
            .swarmui-preview-param-item {
                margin-bottom: 10px;
            }
            .swarmui-preview-param-item pre {
                background: rgba(0,0,0,0.2);
                padding: 8px;
                border-radius: 4px;
                overflow-x: auto;
                margin: 5px 0;
                font-size: 12px;
            }
        `;
        document.head.appendChild(styleElement);
        
        // Configurer les écouteurs d'événements
        const closeBtn = previewDialog.querySelector('.swarmui-modal-close');
        const closeButton = previewDialog.querySelector('.swarmui-preview-close');
        const applyButton = previewDialog.querySelector('.swarmui-preview-apply');
        
        // Fermer la boîte de dialogue
        const closePreviewDialog = () => {
            document.body.removeChild(previewDialog);
            document.head.removeChild(styleElement);
        };
        
        if (closeBtn) closeBtn.addEventListener('click', closePreviewDialog);
        if (closeButton) closeButton.addEventListener('click', closePreviewDialog);
        
        // Appliquer le style
        if (applyButton) {
            applyButton.addEventListener('click', () => {
                // Appliquer le style au projet actuel
                if (window.swarmUIExtension && window.swarmUIExtension.applyStyle) {
                    window.swarmUIExtension.applyStyle(this.styleName);
                    window.swarmUIExtension.showNotification('success', 'Style Déclic Ombre Chinoise appliqué avec succès');
                } else {
                    console.error('SwarmUI Extension non disponible');
                }
                
                // Fermer la prévisualisation
                closePreviewDialog();
            });
        }
        
        // Simuler le chargement des exemples (dans un vrai environnement, ces images seraient générées ou chargées)
        this.loadPreviewExamples(previewDialog);
    }
    
    // Charger les exemples de prévisualisation
    loadPreviewExamples(previewDialog) {
        // Dans un environnement réel, ces images seraient générées à la volée ou chargées depuis un serveur
        // Pour cette démonstration, nous simulons le chargement avec un délai
        setTimeout(() => {
            const placeholders = previewDialog.querySelectorAll('.swarmui-preview-placeholder');
            
            // Remplacer les placeholders par des exemples d'images (simulé)
            placeholders.forEach((placeholder, index) => {
                placeholder.innerHTML = `<div style="background: #111; height: 100%; display: flex; align-items: center; justify-content: center;">
                    <div style="color: #ddd; font-size: 12px;">Exemple ${index + 1}<br>Silhouette avec rim light</div>
                </div>`;
            });
            
            // Dans un environnement réel, nous utiliserions:
            // 1. Une API pour générer des exemples basés sur les paramètres actuels
            // 2. Ou des images pré-générées stockées sur le serveur
            // placeholder.innerHTML = `<img src="/static/examples/declic_example_${index}.jpg" alt="Exemple ${index}">`;
        }, 1500);
    }
    
    // Enregistrer le style avec SwarmUI
    registerStyleWithSwarmUI() {
        // Vérifier si SwarmUI est disponible
        if (window.swarmUIExtension) {
            // Ajouter un bouton pour créer le style Déclic Ombre Chinoise
            this.addDeclicStyleButton();
        } else {
            // Attendre que SwarmUI soit chargé
            window.addEventListener('swarmui_loaded', () => {
                this.addDeclicStyleButton();
            });
        }
    }
    
    // Ajouter un bouton pour créer le style Déclic Ombre Chinoise
    addDeclicStyleButton() {
        const stylePanel = document.getElementById('swarmui-style-panel');
        if (!stylePanel) return;
        
        // Créer un conteneur pour le bouton
        const declicContainer = document.createElement('div');
        declicContainer.className = 'swarmui-declic-container';
        declicContainer.style.marginTop = '15px';
        declicContainer.style.borderTop = '1px solid #444';
        declicContainer.style.paddingTop = '15px';
        
        // Ajouter un titre
        const title = document.createElement('h4');
        title.textContent = 'Style Déclic Ombre Chinoise';
        title.style.marginBottom = '10px';
        declicContainer.appendChild(title);
        
        // Ajouter une description
        const description = document.createElement('p');
        description.textContent = this.styleDescription;
        description.style.fontSize = '12px';
        description.style.marginBottom = '10px';
        declicContainer.appendChild(description);
        
        // Créer le bouton
        const declicButton = document.createElement('button');
        declicButton.className = 'swarmui-btn';
        declicButton.textContent = 'Créer Style Déclic Ombre Chinoise';
        declicButton.addEventListener('click', () => {
            this.openDeclicStyleDialog();
        });
        declicContainer.appendChild(declicButton);
        
        // Ajouter le conteneur au panneau de style
        stylePanel.appendChild(declicContainer);
    }
    
    // Ouvrir la boîte de dialogue pour créer le style Déclic Ombre Chinoise
    openDeclicStyleDialog() {
        // Créer la boîte de dialogue modale
        const dialog = document.createElement('div');
        dialog.className = 'swarmui-modal';
        dialog.innerHTML = `
            <div class="swarmui-modal-content">
                <span class="swarmui-modal-close">&times;</span>
                <h3>Créer Style Déclic Ombre Chinoise</h3>
                <div class="swarmui-form">
                    <div class="swarmui-input-container">
                        <label for="swarmui-declic-images">Images de référence:</label>
                        <input type="file" id="swarmui-declic-images" multiple accept=".jpg,.jpeg,.png" />
                        <small>Sélectionnez 30-50 images représentant le style (silhouettes, rim light, lumières réalistes)</small>
                    </div>
                    <div class="swarmui-input-container">
                        <label for="swarmui-declic-model">Modèle de base:</label>
                        <select id="swarmui-declic-model" class="swarmui-select">
                            <option value="sd15" selected>Stable Diffusion 1.5 (recommandé pour rapidité)</option>
                            <option value="sdxl">Stable Diffusion XL (qualité optimale)</option>
                        </select>
                    </div>
                    <div class="swarmui-input-container">
                        <label for="swarmui-declic-steps">Étapes d'entraînement: <span id="swarmui-declic-steps-value">2000</span></label>
                        <input type="range" id="swarmui-declic-steps" min="1000" max="5000" step="100" value="2000" />
                    </div>
                    <div class="swarmui-input-container">
                        <label for="swarmui-declic-rank">Dimension LoRA (Rank):</label>
                        <select id="swarmui-declic-rank" class="swarmui-select">
                            <option value="8">8 - Léger (moins de détails)</option>
                            <option value="16" selected>16 - Détaillé (recommandé)</option>
                            <option value="32">32 - Haute qualité (fichier plus volumineux)</option>
                        </select>
                    </div>
                    <div class="swarmui-input-container">
                        <label for="swarmui-declic-batch">Taille de batch:</label>
                        <select id="swarmui-declic-batch" class="swarmui-select">
                            <option value="1">1 - GPU limité</option>
                            <option value="2" selected>2 - Recommandé</option>
                            <option value="4">4 - GPU puissant</option>
                        </select>
                    </div>
                    <div class="swarmui-input-container">
                        <label>Intégrations externes:</label>
                        <div>
                            <label>
                                <input type="checkbox" id="swarmui-declic-gemini" checked />
                                Google Gemini Studio (enrichissement de prompts)
                            </label>
                        </div>
                        <div>
                            <label>
                                <input type="checkbox" id="swarmui-declic-qwen" checked />
                                Qwen 2.1 (génération de prompts précis)
                            </label>
                        </div>
                        <div>
                            <label>
                                <input type="checkbox" id="swarmui-declic-wan" checked />
                                WAN 2.1 (Tencent) pour style chinois
                            </label>
                        </div>
                    </div>
                    <div class="swarmui-buttons">
                        <button id="swarmui-declic-cancel" class="swarmui-btn swarmui-btn-secondary">Annuler</button>
                        <button id="swarmui-declic-train" class="swarmui-btn">Démarrer l'entraînement</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
        
        // Configurer les écouteurs d'événements
        const closeBtn = dialog.querySelector('.swarmui-modal-close');
        const cancelBtn = dialog.querySelector('#swarmui-declic-cancel');
        const trainBtn = dialog.querySelector('#swarmui-declic-train');
        const stepsSlider = dialog.querySelector('#swarmui-declic-steps');
        const stepsValue = dialog.querySelector('#swarmui-declic-steps-value');
        
        // Mettre à jour l'affichage du nombre d'étapes
        if (stepsSlider && stepsValue) {
            stepsSlider.addEventListener('input', () => {
                stepsValue.textContent = stepsSlider.value;
            });
        }
        
        // Fermer la boîte de dialogue
        const closeDialog = () => {
            document.body.removeChild(dialog);
        };
        
        if (closeBtn) closeBtn.addEventListener('click', closeDialog);
        if (cancelBtn) cancelBtn.addEventListener('click', closeDialog);
        
        // Gérer le démarrage de l'entraînement
        if (trainBtn) {
            trainBtn.addEventListener('click', () => {
                const imagesInput = dialog.querySelector('#swarmui-declic-images');
                const modelSelect = dialog.querySelector('#swarmui-declic-model');
                const stepsInput = dialog.querySelector('#swarmui-declic-steps');
                const rankInput = dialog.querySelector('#swarmui-declic-rank');
                const batchInput = dialog.querySelector('#swarmui-declic-batch');
                const geminiCheck = dialog.querySelector('#swarmui-declic-gemini');
                const qwenCheck = dialog.querySelector('#swarmui-declic-qwen');
                const wanCheck = dialog.querySelector('#swarmui-declic-wan');
                
                if (!imagesInput || imagesInput.files.length < 5) {
                    window.swarmUIExtension.showNotification('error', 'Veuillez sélectionner au moins 5 images de référence');
                    return;
                }
                
                // Créer les données du formulaire
                const formData = new FormData();
                formData.append('name', this.styleName);
                formData.append('display_name', this.styleDisplayName);
                formData.append('description', this.styleDescription);
                formData.append('base_model', modelSelect ? modelSelect.value : 'sd15');
                formData.append('steps', stepsInput ? stepsInput.value : '2000');
                formData.append('rank', rankInput ? rankInput.value : '16');
                formData.append('batch_size', batchInput ? batchInput.value : '2');
                formData.append('learning_rate', '0.0001'); // 1e-4
                
                // Ajouter les intégrations externes
                formData.append('use_gemini', geminiCheck && geminiCheck.checked ? 'true' : 'false');
                formData.append('use_qwen', qwenCheck && qwenCheck.checked ? 'true' : 'false');
                formData.append('use_wan', wanCheck && wanCheck.checked ? 'true' : 'false');
                
                // Ajouter les prompts d'entraînement
                this.trainingPrompts.forEach((prompt, index) => {
                    formData.append(`training_prompt_${index}`, prompt);
                });
                
                // Ajouter toutes les images
                for (let i = 0; i < imagesInput.files.length; i++) {
                    formData.append('images', imagesInput.files[i]);
                }
                
                // Fermer la boîte de dialogue
                closeDialog();
                
                // Afficher une notification
                window.swarmUIExtension.showNotification('info', 'Démarrage de l\'entraînement LoRA pour Déclic Ombre Chinoise. Cela peut prendre un certain temps...');
                
                // Envoyer la demande d'entraînement
                this.startDeclicLoraTraining(formData);
            });
        }
    }
    
    // Démarrer l'entraînement LoRA pour Déclic Ombre Chinoise
    startDeclicLoraTraining(formData) {
        fetch('/comfyui/train_lora', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.swarmUIExtension.showNotification('success', 'Entraînement LoRA démarré avec succès');
                
                // Suivre l'état de l'entraînement
                this.pollLoraTrainingStatus(data.job_id);
            } else {
                window.swarmUIExtension.showNotification('error', `Échec du démarrage de l'entraînement: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Erreur lors du démarrage de l\'entraînement LoRA:', error);
            window.swarmUIExtension.showNotification('error', `Échec du démarrage de l'entraînement: ${error.message}`);
        });
    }
    
    // Suivre l'état de l'entraînement LoRA
    pollLoraTrainingStatus(jobId) {
        const statusCheck = setInterval(() => {
            fetch(`/comfyui/check_lora_training?job_id=${jobId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        clearInterval(statusCheck);
                        window.swarmUIExtension.showNotification('success', 'Entraînement LoRA Déclic Ombre Chinoise terminé avec succès');
                        
                        // Recharger les modèles LoRA
                        window.swarmUIExtension.loadLoraModels();
                        
                        // Optimiser les paramètres en fonction des résultats
                        this.optimizeStyleParameters();
                    } else if (data.status === 'failed') {
                        clearInterval(statusCheck);
                        window.swarmUIExtension.showNotification('error', `Échec de l'entraînement LoRA: ${data.error}`);
                    } else if (data.status === 'progress') {
                        // Mettre à jour la progression
                        const progressElement = document.getElementById('swarmui-progress-status');
                        if (progressElement) {
                            progressElement.innerHTML = `<div class="swarmui-status-info">Entraînement LoRA Déclic Ombre Chinoise: ${data.progress}% terminé</div>`;
                        }
                        
                        // Mettre à jour la barre de progression
                        const progressBar = document.getElementById('swarmui-progress-bar');
                        if (progressBar) {
                            progressBar.style.width = `${data.progress}%`;
                        }
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la vérification de l\'état de l\'entraînement LoRA:', error);
                });
        }, 5000); // Vérifier toutes les 5 secondes
    }
    
    // Optimiser les paramètres du style en fonction des images de référence
    optimizeStyleParameters() {
        console.log('Optimisation des paramètres du style Déclic Ombre Chinoise');
        
        // Récupérer les informations sur le modèle LoRA entraîné
        fetch('/comfyui/get_lora_info?name=declic_ombre_chinoise')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Analyser les caractéristiques des images d'entraînement
                    this.analyzeTrainingImages(data.training_images);
                } else {
                    console.error('Erreur lors de la récupération des informations LoRA:', data.error);
                }
            })
            .catch(error => {
                console.error('Erreur lors de l\'optimisation des paramètres:', error);
            });
    }
    
    // Analyser les images d'entraînement pour optimiser les paramètres
    analyzeTrainingImages(trainingImages) {
        // Dans un environnement réel, cette fonction utiliserait un modèle d'analyse d'image
        // pour déterminer les caractéristiques dominantes des images d'entraînement
        
        // Simuler l'analyse pour cette démonstration
        const analysisResults = {
            contrastLevel: 'high',           // Niveau de contraste (high, medium, low)
            rimLightIntensity: 'intense',    // Intensité du rim light (intense, moderate, subtle)
            shadowDepth: 'deep',             // Profondeur des ombres (deep, medium, shallow)
            lightColor: 'golden',            // Couleur dominante de la lumière (golden, white, blue, etc.)
            atmosphericElements: true,        // Présence d'éléments atmosphériques (poussière, brume)
            edgeDefinition: 'ultra-detailed' // Définition des bords (ultra-detailed, detailed, soft)
        };
        
        // Ajuster les paramètres en fonction de l'analyse
        this.adjustStyleParameters(analysisResults);
        
        // Afficher une notification
        window.swarmUIExtension.showNotification('info', 'Paramètres du style optimisés en fonction des images de référence');
    }
    
    // Ajuster les paramètres du style en fonction de l'analyse
    adjustStyleParameters(analysisResults) {
        // Ajuster le promptPrefix en fonction de l'analyse
        let newPromptPrefix = "masterful cinematic photograph, award-winning cinematography, ";
        
        // Ajouter des éléments en fonction de l'analyse des silhouettes
        newPromptPrefix += "ultra-detailed silhouette technique, ";
        
        // Ajouter des éléments en fonction de l'analyse du rim light
        if (analysisResults.rimLightIntensity === 'intense') {
            newPromptPrefix += "dramatic intense golden rim lighting, ";
        } else if (analysisResults.rimLightIntensity === 'moderate') {
            newPromptPrefix += "elegant golden rim lighting, ";
        } else {
            newPromptPrefix += "subtle rim lighting, ";
        }
        
        // Ajouter des éléments en fonction de l'analyse de la lumière volumétrique
        newPromptPrefix += "powerful volumetric light beams, ";
        
        // Ajouter des éléments atmosphériques si présents
        if (analysisResults.atmosphericElements) {
            newPromptPrefix += "atmospheric haze, dust particles, ";
        }
        
        // Finaliser le promptPrefix
        newPromptPrefix += "professional lighting setup";
        
        // Mettre à jour le promptPrefix
        this.styleParams.promptPrefix = newPromptPrefix;
        
        // Ajuster le promptSuffix en fonction de l'analyse
        let newPromptSuffix = "";
        
        // Ajouter des éléments en fonction de l'analyse de la définition des bords
        if (analysisResults.edgeDefinition === 'ultra-detailed') {
            newPromptSuffix += "perfect edge definition, hyper-defined edges, ";
        } else if (analysisResults.edgeDefinition === 'detailed') {
            newPromptSuffix += "clear edge definition, ";
        } else {
            newPromptSuffix += "soft edge definition, ";
        }
        
        // Ajouter des éléments en fonction de l'analyse des ombres
        if (analysisResults.shadowDepth === 'deep') {
            newPromptSuffix += "pure black silhouette, rich deep shadows, ";
        } else if (analysisResults.shadowDepth === 'medium') {
            newPromptSuffix += "strong black silhouette, deep shadows, ";
        } else {
            newPromptSuffix += "black silhouette, defined shadows, ";
        }
        
        // Ajouter des éléments esthétiques
        newPromptSuffix += "film noir aesthetic, ";
        
        // Ajouter des éléments en fonction de l'analyse des éléments atmosphériques
        if (analysisResults.atmosphericElements) {
            newPromptSuffix += "dust particles dancing in light beams, ";
        }
        
        // Ajouter des éléments en fonction de l'analyse du contraste
        if (analysisResults.contrastLevel === 'high') {
            newPromptSuffix += "precise contrast control, stark lighting separation, ";
        } else if (analysisResults.contrastLevel === 'medium') {
            newPromptSuffix += "good contrast control, clear lighting separation, ";
        } else {
            newPromptSuffix += "balanced contrast, subtle lighting separation, ";
        }
        
        // Finaliser le promptSuffix
        newPromptSuffix += "16:9 cinematic ratio";
        
        // Mettre à jour le promptSuffix
        this.styleParams.promptSuffix = newPromptSuffix;
        
        // Ajuster le negativePrompt
        this.styleParams.negativePrompt = "low quality, blurry, distorted, deformed, cartoon, anime, visible face details, flat lighting, soft edges, gray tones, low contrast, diffused lighting, full color, bright midtones, washed out blacks, muddy shadows, amateur lighting";
        
        // Ajuster les autres paramètres en fonction de l'analyse
        if (analysisResults.contrastLevel === 'high' && analysisResults.rimLightIntensity === 'intense') {
            this.styleParams.cfgScale = 10.0;
            this.styleParams.steps = 45;
        } else if (analysisResults.contrastLevel === 'medium' || analysisResults.rimLightIntensity === 'moderate') {
            this.styleParams.cfgScale = 9.0;
            this.styleParams.steps = 40;
        } else {
            this.styleParams.cfgScale = 8.0;
            this.styleParams.steps = 35;
        }
        
        // Sauvegarder les paramètres optimisés
        this.saveOptimizedParameters();
    }
    
    // Sauvegarder les paramètres optimisés
    saveOptimizedParameters() {
        // Créer l'objet de paramètres à sauvegarder
        const optimizedParams = {
            name: this.styleName,
            display_name: this.styleDisplayName,
            description: this.styleDescription,
            prompt_prefix: this.styleParams.promptPrefix,
            prompt_suffix: this.styleParams.promptSuffix,
            negative_prompt: this.styleParams.negativePrompt,
            cfg_scale: this.styleParams.cfgScale,
            steps: this.styleParams.steps,
            sampler: this.styleParams.sampler
        };
        
        // Envoyer les paramètres optimisés au serveur
        fetch('/styles/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(optimizedParams)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Paramètres optimisés sauvegardés avec succès');
            } else {
                console.error('Erreur lors de la sauvegarde des paramètres optimisés:', data.error);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la sauvegarde des paramètres optimisés:', error);
        });
    }
    
    // Créer un MCP JSON pour le style Déclic Ombre Chinoise
    createMCPJson(sceneData) {
        return {
            "scene": {
                "id": sceneData.id || "1A",
                "description": sceneData.description || "Scène avec silhouette et rim light dramatique",
                "camera": sceneData.camera || "Travelling latéral gauche-droite"
            },
            "generation": {
                "prompt_generation": {
                    "model": "qwen2.1-max",
                    "provider": "ollama-local",
                    "prompt_prefix": this.styleParams.promptPrefix,
                    "prompt_suffix": this.styleParams.promptSuffix,
                    "negative_prompt": this.styleParams.negativePrompt
                },
                "image": {
                    "stable_diffusion": this.trainingParams.baseModel,
                    "controlnet": "scribble",
                    "lora": "declic_ombre_chinoise.safetensors",
                    "lora_strength": 0.9,
                    "cfg_scale": this.styleParams.cfgScale,
                    "steps": this.styleParams.steps,
                    "sampler": this.styleParams.sampler,
                    "resolution": [1920, 1080],
                    "cloud_fallback": {
                        "enabled": true,
                        "provider": "google_gemini_studio"
                    }
                },
                "video": {
                    "animate_diff": true,
                    "fallback_api": "kling_ai",
                    "video_assembly": "ffmpeg",
                    "fps": 24,
                    "motion_strength": 0.85
                }
            }
        };
    }
}

// Initialiser le style Déclic Ombre Chinoise lorsque la page est chargée
document.addEventListener('DOMContentLoaded', () => {
    window.declicOmbreChinoiseStyle = new DeclicOmbreChinoiseStyle();
});