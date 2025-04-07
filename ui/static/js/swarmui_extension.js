/**
 * SwarmUI Extension for Storyboard-to-Video Platform
 * 
 * This module extends the ComfyUI interface (SwarmUI) with custom functionality for:
 * - Storyboard PDF/image upload and parsing
 * - Workflow management and generation buttons
 * - LoRA style selection and management
 * - Generation progress display
 * - MCP (Model-Context-Protocol) implementation
 */

// Main SwarmUI extension class
class SwarmUIExtension {
    constructor() {
        this.initialized = false;
        this.uploadedStoryboardPath = null;
        this.selectedStyle = 'default';
        this.selectedLoraModel = '';
        this.loraStrength = 0.8;
        this.isGenerating = false;
        this.useAnimation = false;
        
        // Model selection properties
        this.selectedSDModel = 'sd15'; // Default to SD 1.5
        this.selectedControlNetModel = 'scribble'; // Default to Scribble
        
        // Animation properties
        this.useAnimationDiff = true;
        this.useRunwayFallback = false;
        this.useKlingAI = false;
        
        // Cloud fallback properties
        this.useCloudFallback = false;
        this.selectedCloudProvider = '';
        
        // Initialize MCP protocol handler
        this.mcpProtocol = new MCPProtocol();
        
        // Initialize when ComfyUI is ready
        document.addEventListener('DOMContentLoaded', () => {
            // Wait for ComfyUI to initialize
            this.waitForComfyUI().then(() => {
                this.initialize();
            });
        });
    }

    // Wait for ComfyUI to be fully loaded
    waitForComfyUI() {
        return new Promise((resolve) => {
            const checkComfyUI = () => {
                // Check if ComfyUI's app object is available
                if (window.app && window.app.canvas && window.app.graph) {
                    resolve();
                } else {
                    setTimeout(checkComfyUI, 100);
                }
            };
            checkComfyUI();
        });
    }

    // Initialize the extension
    initialize() {
        if (this.initialized) return;
        
        console.log('Initializing SwarmUI Extension for Storyboard-to-Video');
        
        // Add CSS styles
        this.addStyles();
        
        // Initialize UI
        this.initUI();
        
        // Load available styles
        this.loadStyles();
        
        // Load available LoRA models
        this.loadLoraModels();
        
        // Check ComfyUI availability
        this.checkComfyUIAvailability();
        
        this.initialized = true;
    }

    // Add CSS styles
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .swarmui-panel {
                background-color: #1f1f1f;
                border-radius: 8px;
                margin: 10px;
                padding: 15px;
                color: #e0e0e0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .swarmui-panel h3 {
                margin-top: 0;
                margin-bottom: 15px;
                border-bottom: 1px solid #444;
                padding-bottom: 8px;
            }
            
            .swarmui-input-container {
                margin-bottom: 12px;
            }
            
            .swarmui-input-container label {
                display: block;
                margin-bottom: 5px;
            }
            
            .swarmui-btn {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 8px;
                margin-bottom: 8px;
            }
            
            .swarmui-btn:hover {
                background-color: #2980b9;
            }
            
            .swarmui-btn:disabled {
                background-color: #95a5a6;
                cursor: not-allowed;
            }
            
            .swarmui-btn-secondary {
                background-color: #7f8c8d;
            }
            
            .swarmui-btn-secondary:hover {
                background-color: #6c7a7a;
            }
            
            .swarmui-select {
                width: 100%;
                padding: 8px;
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 4px;
            }
            
            .swarmui-progress-bar-container {
                width: 100%;
                height: 20px;
                background-color: #2c2c2c;
                border-radius: 10px;
                margin-bottom: 10px;
                overflow: hidden;
            }
            
            .swarmui-progress-bar {
                height: 100%;
                background-color: #2ecc71;
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .swarmui-progress-status {
                margin-bottom: 15px;
            }
            
            .swarmui-status-info {
                color: #3498db;
            }
            
            .swarmui-status-success {
                color: #2ecc71;
            }
            
            .swarmui-status-error {
                color: #e74c3c;
            }
            
            .swarmui-preview-container {
                margin-top: 15px;
            }
            
            .swarmui-preview-container img, 
            .swarmui-preview-container video {
                max-width: 100%;
                border-radius: 4px;
            }
            
            .swarmui-thumbnails {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 15px;
            }
            
            .swarmui-thumbnail {
                width: 120px;
                height: 120px;
                border-radius: 4px;
                overflow: hidden;
                position: relative;
                cursor: pointer;
                border: 2px solid #444;
            }
            
            .swarmui-thumbnail:hover {
                border-color: #3498db;
            }
            
            .swarmui-thumbnail img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            .swarmui-thumbnail-placeholder {
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #2c2c2c;
                color: #e0e0e0;
                font-size: 14px;
                text-align: center;
                padding: 5px;
            }
            
            .swarmui-thumbnail-text {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 5px;
                font-size: 12px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .swarmui-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            
            .swarmui-modal-content {
                background-color: #2c2c2c;
                padding: 20px;
                border-radius: 8px;
                max-width: 500px;
                width: 100%;
                position: relative;
            }
            
            .swarmui-modal-close {
                position: absolute;
                top: 10px;
                right: 15px;
                font-size: 24px;
                cursor: pointer;
                color: #e0e0e0;
            }
            
            .swarmui-modal-close:hover {
                color: #e74c3c;
            }
            
            .swarmui-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .swarmui-buttons {
                display: flex;
                justify-content: flex-end;
                gap: 10px;
            }
            
            .swarmui-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px;
                border-radius: 5px;
                color: white;
                z-index: 1001;
                max-width: 300px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                animation: fadeIn 0.3s, fadeOut 0.3s 2.7s;
                opacity: 0;
                animation-fill-mode: forwards;
            }
            
            .swarmui-notification.success {
                background-color: #2ecc71;
            }
            
            .swarmui-notification.error {
                background-color: #e74c3c;
            }
            
            .swarmui-notification.warning {
                background-color: #f39c12;
            }
            
            .swarmui-notification.info {
                background-color: #3498db;
            }
            
            .swarmui-panels-container {
                position: fixed;
                top: 60px;
                right: 20px;
                width: 300px;
                max-height: calc(100vh - 80px);
                overflow-y: auto;
                z-index: 900;
                display: flex;
                flex-direction: column;
                gap: 10px;
                transition: transform 0.3s ease;
            }
            
            .swarmui-panels-container.collapsed {
                transform: translateX(310px);
            }
            
            .swarmui-panel-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 40px;
                height: 40px;
                background-color: #3498db;
                border: none;
                border-radius: 50%;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                z-index: 901;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }
            
            .swarmui-panel-toggle:hover {
                background-color: #2980b9;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    // Initialize UI
    initUI() {
        // Create panels container
        const panelsContainer = document.createElement('div');
        panelsContainer.className = 'swarmui-panels-container';
        panelsContainer.id = 'swarmui-panels-container';
        document.body.appendChild(panelsContainer);
        
        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'swarmui-panel-toggle';
        toggleButton.id = 'swarmui-panel-toggle';
        toggleButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
        `;
        document.body.appendChild(toggleButton);
        
        // Setup toggle functionality
        toggleButton.addEventListener('click', () => {
            panelsContainer.classList.toggle('collapsed');
        });
        
        // Create storyboard panel
        this.createStoryboardPanel(panelsContainer);
        
        // Create style panel
        this.createStylePanel(panelsContainer);
        
        // Create models panel
        this.createModelsPanel(panelsContainer);
        
        // Create workflow panel
        this.createWorkflowPanel(panelsContainer);
        
        // Create animation panel
        this.createAnimationPanel(panelsContainer);
        
        // Create cloud fallback panel
        this.createCloudFallbackPanel(panelsContainer);
        
        // Create progress panel
        this.createProgressPanel(panelsContainer);
        
        // Setup event listeners
        this.setupEventListeners();
    }

    // Create storyboard panel
    createStoryboardPanel(container) {
        const panel = document.createElement('div');
        panel.className = 'swarmui-panel';
        panel.id = 'swarmui-storyboard-panel';
        panel.innerHTML = `
            <h3>Storyboard Upload</h3>
            <div class="swarmui-upload-container">
                <form id="swarmui-storyboard-form" enctype="multipart/form-data">
                    <div class="swarmui-input-container">
                        <label for="swarmui-storyboard-file">Select PDF or Images:</label>
                        <input type="file" id="swarmui-storyboard-file" name="storyboard" accept=".pdf,.jpg,.jpeg,.png" class="swarmui-file-input" />
                    </div>
                    <button type="submit" class="swarmui-btn">Upload Storyboard</button>
                </form>
                <div id="swarmui-storyboard-status"></div>
                <div id="swarmui-storyboard-thumbnails" class="swarmui-thumbnails"></div>
            </div>
        `;
        container.appendChild(panel);
    }

    // Create style panel
    createStylePanel(container) {
        const panel = document.createElement('div');
        panel.className = 'swarmui-panel';
        panel.id = 'swarmui-style-panel';
        panel.innerHTML = `
            <h3>Style Selection</h3>
            <div class="swarmui-style-container">
                <div class="swarmui-input-container">
                    <label for="swarmui-style-select">Select Style:</label>
                    <select id="swarmui-style-select" class="swarmui-select"></select>
                </div>
                <div class="swarmui-input-container">
                    <label for="swarmui-lora-select">Select LoRA Model:</label>
                    <select id="swarmui-lora-select" class="swarmui-select"></select>
                </div>
                <div class="swarmui-input-container">
                    <label for="swarmui-lora-strength">LoRA Strength: <span id="swarmui-lora-strength-value">0.8</span></label>
                    <input type="range" id="swarmui-lora-strength" min="0" max="1" step="0.05" value="0.8" />
                </div>
                <button id="swarmui-train-lora-btn" class="swarmui-btn">Train New Style</button>
            </div>
        `;
        container.appendChild(panel);
    }
    
    // Create models panel for Stable Diffusion and ControlNet
    createModelsPanel(container) {
        const panel = document.createElement('div');
        panel.className = 'swarmui-panel';
        panel.id = 'swarmui-models-panel';
        panel.innerHTML = `
            <h3>AI Models</h3>
            <div class="swarmui-models-container">
                <div class="swarmui-input-container">
                    <label for="swarmui-sd-model-select">Stable Diffusion Model:</label>
                    <select id="swarmui-sd-model-select" class="swarmui-select">
                        <option value="sd15">Stable Diffusion 1.5</option>
                        <option value="sdxl">Stable Diffusion XL</option>
                    </select>
                </div>
                <div class="swarmui-input-container">
                    <label for="swarmui-controlnet-model-select">ControlNet Model:</label>
                    <select id="swarmui-controlnet-model-select" class="swarmui-select">
                        <option value="scribble">Scribble</option>
                        <option value="lineart">Lineart</option>
                    </select>
                </div>
            </div>
        `;
        container.appendChild(panel);
    }
    
    // Create animation panel
    createAnimationPanel(container) {
        const panel = document.createElement('div');
        panel.className = 'swarmui-panel';
        panel.id = 'swarmui-animation-panel';
        panel.innerHTML = `
            <h3>Animation Options</h3>
            <div class="swarmui-animation-container">
                <div class="swarmui-input-container">
                    <label>
                        <input type="checkbox" id="swarmui-use-animation-diff" checked />
                        Use AnimateDiff (Local)
                    </label>
                </div>
                <div class="swarmui-input-container">
                    <label>
                        <input type="checkbox" id="swarmui-use-runway" />
                        Use RunwayML Gen-2 (Cloud)
                    </label>
                </div>
                <div class="swarmui-input-container">
                    <label>
                        <input type="checkbox" id="swarmui-use-kling" />
                        Use Kling AI / Veo2 (Cloud)
                    </label>
                </div>
                <div class="swarmui-input-container">
                    <label for="swarmui-transition-select">Transition Type:</label>
                    <select id="swarmui-transition-select" class="swarmui-select">
                        <option value="crossfade">Crossfade</option>
                        <option value="fade">Fade</option>
                        <option value="wipe">Wipe</option>
                        <option value="zoom">Zoom</option>
                    </select>
                </div>
            </div>
        `;
        container.appendChild(panel);
    }
    
    // Create cloud fallback panel
    createCloudFallbackPanel(container) {
        const panel = document.createElement('div');
        panel.className = 'swarmui-panel';
        panel.id = 'swarmui-cloud-panel';
        panel.innerHTML = `
            <h3>Cloud Fallback</h3>
            <div class="swarmui-cloud-container">
                <div class="swarmui-input-container">
                    <label>
                        <input type="checkbox" id="swarmui-use-cloud-fallback" />
                        Enable Cloud Fallback
                    </label>
                </div>
                <div class="swarmui-input-container">
                    <label for="swarmui-cloud-provider-select">Cloud Provider:</label>
                    <select id="swarmui-cloud-provider-select" class="swarmui-select" disabled>
                        <option value="midjourney">Midjourney API</option>
                        <option value="dalle">DALL-E API</option>
                        <option value="tencent">Tencent API</option>
                        <option value="alibaba">Alibaba API</option>
                        <option value="google">Google Studio API</option>
                    </select>
                </div>
                <div class="swarmui-input-container">
                    <label for="swarmui-api-key">API Key:</label>
                    <input type="password" id="swarmui-api-key" class="swarmui-input" disabled />
                </div>
            </div>
        `;
        container.appendChild(panel);
    }

    // Create workflow panel
    createWorkflowPanel(container) {
        const panel = document.createElement('div');
        panel.className = 'swarmui-panel';
        panel.id = 'swarmui-workflow-panel';
        panel.innerHTML = `
            <h3>Generation Controls</h3>
            <div class="swarmui-workflow-container">
                <button id="swarmui-load-workflow-btn" class="swarmui-btn">Load Workflow</button>
                <button id="swarmui-generate-btn" class="swarmui-btn" disabled>Generate Images</button>
                <button id="swarmui-create-video-btn" class="swarmui-btn" disabled>Create Video</button>
                <div class="swarmui-input-container">
                    <label>
                        <input type="checkbox" id="swarmui-use-animation" />
                        Use Animation Effects
                    </label>
                </div>
            </div>
        `;
        container.appendChild(panel);
    }

    // Create progress panel
    createProgressPanel(container) {
        const panel = document.createElement('div');
        panel.className = 'swarmui-panel';
        panel.id = 'swarmui-progress-panel';
        panel.innerHTML = `
            <h3>Generation Progress</h3>
            <div class="swarmui-progress-container">
                <div class="swarmui-progress-bar-container">
                    <div id="swarmui-progress-bar" class="swarmui-progress-bar"></div>
                </div>
                <div id="swarmui-progress-status" class="swarmui-progress-status">Ready to start generation</div>
                <div id="swarmui-preview-container" class="swarmui-preview-container"></div>
            </div>
        `;
        container.appendChild(panel);
    }

    // Setup event listeners
    setupEventListeners() {
        // Storyboard upload form
        const uploadForm = document.getElementById('swarmui-storyboard-form');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.uploadStoryboard(new FormData(uploadForm));
            });
        }
        
        // Style selection
        const styleSelect = document.getElementById('swarmui-style-select');
        if (styleSelect) {
            styleSelect.addEventListener('change', (e) => {
                this.selectedStyle = e.target.value;
                this.updateSceneStyles();
            });
        }
        
        // LoRA model selection
        const loraSelect = document.getElementById('swarmui-lora-select');
        if (loraSelect) {
            loraSelect.addEventListener('change', (e) => {
                this.selectedLoraModel = e.target.value;
                this.updateSceneStyles();
            });
        }
        
        // LoRA strength slider
        const loraStrength = document.getElementById('swarmui-lora-strength');
        if (loraStrength) {
            loraStrength.addEventListener('input', (e) => {
                this.loraStrength = parseFloat(e.target.value);
                const strengthValue = document.getElementById('swarmui-lora-strength-value');
                if (strengthValue) {
                    strengthValue.textContent = this.loraStrength.toFixed(2);
                }
                this.updateSceneStyles();
            });
        }
        
        // Train new style button
        const trainLoraBtn = document.getElementById('swarmui-train-lora-btn');
        if (trainLoraBtn) {
            trainLoraBtn.addEventListener('click', () => {
                this.openTrainStyleDialog();
            });
        }
        
        // Stable Diffusion model selection
        const sdModelSelect = document.getElementById('swarmui-sd-model-select');
        if (sdModelSelect) {
            sdModelSelect.addEventListener('change', (e) => {
                this.selectedSDModel = e.target.value;
                this.updateSceneModels();
            });
        }
        
        // ControlNet model selection
        const controlNetModelSelect = document.getElementById('swarmui-controlnet-model-select');
        if (controlNetModelSelect) {
            controlNetModelSelect.addEventListener('change', (e) => {
                this.selectedControlNetModel = e.target.value;
                this.updateSceneModels();
            });
        }
        
        // Animation options
        const useAnimationDiff = document.getElementById('swarmui-use-animation-diff');
        if (useAnimationDiff) {
            useAnimationDiff.addEventListener('change', (e) => {
                this.useAnimationDiff = e.target.checked;
                this.updateAnimationSettings();
            });
        }
        
        const useRunway = document.getElementById('swarmui-use-runway');
        if (useRunway) {
            useRunway.addEventListener('change', (e) => {
                this.useRunwayFallback = e.target.checked;
                this.updateAnimationSettings();
            });
        }
        
        const useKling = document.getElementById('swarmui-use-kling');
        if (useKling) {
            useKling.addEventListener('change', (e) => {
                this.useKlingAI = e.target.checked;
                this.updateAnimationSettings();
            });
        }
        
        const transitionSelect = document.getElementById('swarmui-transition-select');
        if (transitionSelect) {
            transitionSelect.addEventListener('change', (e) => {
                this.transitionType = e.target.value;
                this.updateAnimationSettings();
            });
        }
        
        // Cloud fallback options
        const useCloudFallback = document.getElementById('swarmui-use-cloud-fallback');
        if (useCloudFallback) {
            useCloudFallback.addEventListener('change', (e) => {
                this.useCloudFallback = e.target.checked;
                
                // Enable/disable cloud provider select and API key input
                const cloudProviderSelect = document.getElementById('swarmui-cloud-provider-select');
                const apiKeyInput = document.getElementById('swarmui-api-key');
                
                if (cloudProviderSelect) {
                    cloudProviderSelect.disabled = !this.useCloudFallback;
                }
                
                if (apiKeyInput) {
                    apiKeyInput.disabled = !this.useCloudFallback;
                }
                
                this.updateCloudFallbackSettings();
            });
        }
        
        const cloudProviderSelect = document.getElementById('swarmui-cloud-provider-select');
        if (cloudProviderSelect) {
            cloudProviderSelect.addEventListener('change', (e) => {
                this.selectedCloudProvider = e.target.value;
                this.updateCloudFallbackSettings();
            });
        }
        
        // Load workflow button
        const loadWorkflowBtn = document.getElementById('swarmui-load-workflow-btn');
        if (loadWorkflowBtn) {
            loadWorkflowBtn.addEventListener('click', () => {
                this.loadWorkflow();
            });
        }
        
        // Generate button
        const generateBtn = document.getElementById('swarmui-generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.startGeneration();
            });
        }
        
        // Create video button
        const createVideoBtn = document.getElementById('swarmui-create-video-btn');
        if (createVideoBtn) {
            createVideoBtn.addEventListener('click', () => {
                this.createVideo();
            });
        }
        
        // Animation checkbox
        const useAnimation = document.getElementById('swarmui-use-animation');
        if (useAnimation) {
            useAnimation.addEventListener('change', (e) => {
                this.useAnimation = e.target.checked;
            });
        }
    }

    // Check ComfyUI availability
    checkComfyUIAvailability() {
        fetch('/comfyui/check_comfyui')
            .then(response => response.json())
            .then(data => {
                if (!data.available) {
                    this.showNotification('warning', `ComfyUI not available: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Error checking ComfyUI availability:', error);
                this.showNotification('error', 'Could not connect to ComfyUI');
            });
    }

    // Load available styles
    loadStyles() {
        fetch('/comfyui/styles')
            .then(response => response.json())
            .then(styles => {
                const styleSelect = document.getElementById('swarmui-style-select');
                if (!styleSelect) return;
                
                styleSelect.innerHTML = '';
                
                styles.forEach(style => {
                    const option = document.createElement('option');
                    option.value = style.name;
                    option.textContent = style.name;
                    option.title = style.description || '';
                    styleSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error loading styles:', error);
                this.showNotification('error', 'Failed to load styles');
            });
    }

    // Load available LoRA models
    loadLoraModels() {
        fetch('/comfyui/lora_models')
            .then(response => response.json())
            .then(models => {
                const loraSelect = document.getElementById('swarmui-lora-select');
                if (!loraSelect) return;
                
                loraSelect.innerHTML = '';
                
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.display_name || model.name;
                    loraSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error loading LoRA models:', error);
                this.showNotification('error', 'Failed to load LoRA models');
            });
    }

    // Upload storyboard
    uploadStoryboard(formData) {
        const statusElement = document.getElementById('swarmui-storyboard-status');
        if (statusElement) {
            statusElement.innerHTML = '<div class="swarmui-status-info">Uploading...</div>';
        }
        
        fetch('/comfyui/upload_storyboard', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.uploadedStoryboardPath = data.path;
                
                if (statusElement) {
                    statusElement.innerHTML = `<div class="swarmui-status-success">Uploaded successfully: ${data.filename}</div>`;
                }
                
                // Parse storyboard
                this.parseStoryboard(data.path);
            } else {
                if (statusElement) {
                    statusElement.innerHTML = `<div class="swarmui-status-error">Error: ${data.error}</div>`;
                }
                this.showNotification('error', `Upload failed: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error uploading storyboard:', error);
            
            if (statusElement) {
                statusElement.innerHTML = `<div class="swarmui-status-error">Error: ${error.message}</div>`;
            }
            this.showNotification('error', `Upload failed: ${error.message}`);
        });
    }

    // Parse storyboard
    parseStoryboard(storyboardPath) {
        const statusElement = document.getElementById('swarmui-storyboard-status');
        if (statusElement) {
            statusElement.innerHTML = '<div class="swarmui-status-info">Parsing storyboard...</div>';
        }
        
        // Initialize storyboard in MCP protocol
        this.mcpProtocol.initializeStoryboard(storyboardPath)
            .then(result => {
                if (result.success) {
                    if (statusElement) {
                        statusElement.innerHTML = `<div class="swarmui-status-success">Parsed ${result.totalScenes} scenes</div>`;
                    }
                    
                    // Display thumbnails
                    this.displaySceneThumbnails(result.scenes);
                    
                    // Update scene styles
                    this.updateSceneStyles();
                    
                    // Enable generation button
                    const generateBtn = document.getElementById('swarmui-generate-btn');
                    if (generateBtn) {
                        generateBtn.disabled = false;
                    }
                    
                    this.showNotification('success', `Parsed ${result.totalScenes} scenes successfully`);
                } else {
                    if (statusElement) {
                        statusElement.innerHTML = `<div class="swarmui-status-error">Error: ${result.error}</div>`;
                    }
                    this.showNotification('error', `Parsing failed: ${result.error}`);
                }
            })
            .catch(error => {
                console.error('Error parsing storyboard:', error);
                
                if (statusElement) {
                    statusElement.innerHTML = `<div class="swarmui-status-error">Error: ${error.message}</div>`;
                }
                this.showNotification('error', `Parsing failed: ${error.message}`);
            });
    }

    // Display scene thumbnails
    displaySceneThumbnails(scenes) {
        const thumbnailsContainer = document.getElementById('swarmui-storyboard-thumbnails');
        if (!thumbnailsContainer) return;
        
        thumbnailsContainer.innerHTML = '';
        
        scenes.forEach(scene => {
            const thumbnail = document.createElement('div');
            thumbnail.className = 'swarmui-thumbnail';
            thumbnail.dataset.sceneId = scene.scene_id;
            
            // Create thumbnail image if reference image exists
            if (scene.input.reference_image) {
                const img = document.createElement('img');
                img.src = `/comfyui/uploads/${scene.input.reference_image.split('/').pop()}`;
                img.alt = `Scene ${scene.scene_id}`;
                thumbnail.appendChild(img);
            } else {
                // Placeholder if no image
                thumbnail.innerHTML = `<div class="swarmui-thumbnail-placeholder">Scene ${scene.scene_id}</div>`;
            }
            
            // Add scene text
            const text = document.createElement('div');
            text.className = 'swarmui-thumbnail-text';
            text.textContent = scene.input.prompt_text.substring(0, 50) + (scene.input.prompt_text.length > 50 ? '...' : '');
            thumbnail.appendChild(text);
            
            // Add click handler to edit scene
            thumbnail.addEventListener('click', () => {
                this.openSceneEditor(scene);
            });
            
            thumbnailsContainer.appendChild(thumbnail);
        });
    }

    // Update scene styles
    updateSceneStyles() {
        // Update all scenes with current style settings
        if (this.mcpProtocol.scenes) {
            this.mcpProtocol.scenes.forEach(scene => {
                this.mcpProtocol.updateSceneParams(scene.scene_id, {
                    generation: {
                        style: {
                            lora_model: this.selectedLoraModel,
                            strength: this.loraStrength
                        }
                    }
                });
            });
        }
    }
    
    // Update scene models
    updateSceneModels() {
        // Update all scenes with current model settings
        if (this.mcpProtocol.scenes) {
            this.mcpProtocol.scenes.forEach(scene => {
                this.mcpProtocol.updateSceneParams(scene.scene_id, {
                    generation: {
                        model: this.selectedSDModel,
                        controlnet: {
                            model: this.selectedControlNetModel
                        }
                    }
                });
            });
        }
    }
    
    // Update cloud fallback settings
    updateCloudFallbackSettings() {
        // Update all scenes with current cloud fallback settings
        if (this.mcpProtocol.scenes) {
            this.mcpProtocol.scenes.forEach(scene => {
                this.mcpProtocol.updateSceneParams(scene.scene_id, {
                    generation: {
                        fallback_cloud: {
                            enabled: this.useCloudFallback,
                            provider: this.selectedCloudProvider
                        }
                    }
                });
            });
        }
    }
    
    // Update animation settings
    updateAnimationSettings() {
        // Update all scenes with current animation settings
        if (this.mcpProtocol.scenes) {
            this.mcpProtocol.scenes.forEach(scene => {
                this.mcpProtocol.updateSceneParams(scene.scene_id, {
                    animation: {
                        animate_diff: this.useAnimationDiff,
                        runway_api_fallback: {
                            enabled: this.useRunwayFallback
                        },
                        kling_api: {
                            enabled: this.useKlingAI
                        }
                    }
                });
            });
        }
    }

    // Open scene editor
    openSceneEditor(scene) {
        // Create modal dialog
        const dialog = document.createElement('div');
        dialog.className = 'swarmui-modal';
        dialog.innerHTML = `
            <div class="swarmui-modal-content">
                <span class="swarmui-modal-close">&times;</span>
                <h3>Edit Scene ${scene.scene_id}</h3>
                <div class="swarmui-form">
                    <div class="swarmui-input-container">
                        <label for="swarmui-scene-prompt">Prompt Text:</label>
                        <textarea id="swarmui-scene-prompt" rows="4">${scene.input.prompt_text}</textarea>
                    </div>
                    <div class="swarmui-input-container">
                        <label for="swarmui-scene-camera">Camera Movement:</label>
                        <select id="swarmui-scene-camera" class="swarmui-select">
                            <option value="static" ${scene.input.camera_movement === 'static' ? 'selected' : ''}>Static</option>
                            <option value="pan-left" ${scene.input.camera_movement === 'pan-left' ? 'selected' : ''}>Pan Left</option>
                            <option value="pan-right" ${scene.input.camera_movement === 'pan-right' ? 'selected' : ''}>Pan Right</option>