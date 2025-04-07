/**
 * MCP (Model-Context-Protocol) Protocol Handler for Storyboard-to-Video Platform
 * 
 * This module implements the MCP protocol for communication between the UI and backend.
 * It handles the structured data exchange format for scenes, generation parameters, and outputs.
 * 
 * Enhanced version with support for:
 * - Multiple Stable Diffusion models (SD 1.5, SDXL)
 * - ControlNet models (Scribble, Lineart)
 * - LoRA style models
 * - Animation models (AnimateDiff, RunwayML, Kling AI)
 * - Cloud API fallbacks (Midjourney, DALL-E, etc.)
 */

class MCPProtocol {
    constructor() {
        this.scenes = [];
        this.currentSceneIndex = 0;
        this.generationInProgress = false;
        
        // Available models configuration
        this.availableModels = {
            // Image generation models
            stableDiffusion: [
                { id: 'sd15', name: 'Stable Diffusion 1.5', default: true },
                { id: 'sdxl', name: 'Stable Diffusion XL', default: false }
            ],
            // ControlNet models
            controlNet: [
                { id: 'scribble', name: 'Scribble', default: true },
                { id: 'lineart', name: 'Lineart', default: false }
            ],
            // Animation models
            animation: [
                { id: 'animatediff', name: 'AnimateDiff', local: true, default: true },
                { id: 'runway', name: 'RunwayML Gen-2', local: false, default: false },
                { id: 'kling', name: 'Kling AI', local: false, default: false },
                { id: 'veo2', name: 'Veo2', local: false, default: false }
            ],
            // Cloud API fallbacks
            cloudApi: [
                { id: 'midjourney', name: 'Midjourney API', type: 'image' },
                { id: 'dalle', name: 'DALL-E API', type: 'image' },
                { id: 'tencent', name: 'Tencent API', type: 'image' },
                { id: 'alibaba', name: 'Alibaba API', type: 'image' },
                { id: 'google', name: 'Google Studio API', type: 'image' }
            ]
        };
    }

    /**
     * Initialize a new storyboard processing session
     * @param {string} storyboardPath - Path to the uploaded storyboard
     * @returns {Promise} - Promise that resolves when scenes are parsed
     */
    async initializeStoryboard(storyboardPath) {
        try {
            const response = await fetch('/comfyui/parse_storyboard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    storyboard_path: storyboardPath
                })
            });

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to parse storyboard');
            }

            // Initialize scenes with default model settings
            this.scenes = data.scenes.map(scene => {
                // Ensure generation object exists with default values
                if (!scene.generation) {
                    scene.generation = {};
                }
                
                // Set default model values if not present
                scene.generation.model = scene.generation.model || this.getDefaultModel('stableDiffusion').id;
                scene.generation.controlnet = scene.generation.controlnet || {
                    model: this.getDefaultModel('controlNet').id,
                    reference_image: scene.input.reference_sketch_image || ''
                };
                
                // Set default style values if not present
                if (!scene.generation.style) {
                    scene.generation.style = {
                        lora_model: '',
                        strength: 0.8
                    };
                }
                
                // Set default fallback cloud settings if not present
                if (!scene.generation.fallback_cloud) {
                    scene.generation.fallback_cloud = {
                        enabled: false,
                        provider: '',
                        api_key: ''
                    };
                }
                
                // Set default animation settings if not present
                if (!scene.animation) {
                    scene.animation = {
                        animate_diff: true,
                        runway_api_fallback: {
                            enabled: false,
                            api_key: ''
                        },
                        kling_api: {
                            enabled: false,
                            action: ''
                        },
                        video_assembly: {
                            ffmpeg: true,
                            transition: 'crossfade',
                            clip_duration: scene.input.duration_seconds || 5
                        }
                    };
                }
                
                return scene;
            });
            
            this.currentSceneIndex = 0;
            
            return {
                success: true,
                totalScenes: data.total_scenes,
                scenes: this.scenes
            };
        } catch (error) {
            console.error('Error initializing storyboard:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get default model for a specific category
     * @param {string} category - Model category (stableDiffusion, controlNet, etc.)
     * @returns {Object} - Default model object
     */
    getDefaultModel(category) {
        const models = this.availableModels[category];
        if (!models || models.length === 0) {
            throw new Error(`No models available for category: ${category}`);
        }
        
        const defaultModel = models.find(model => model.default) || models[0];
        return defaultModel;
    }

    /**
     * Update scene parameters
     * @param {string} sceneId - ID of the scene to update
     * @param {Object} params - Parameters to update
     */
    updateSceneParams(sceneId, params) {
        const sceneIndex = this.scenes.findIndex(scene => scene.scene_id === sceneId);
        
        if (sceneIndex === -1) {
            console.error(`Scene with ID ${sceneId} not found`);
            return false;
        }

        // Update scene parameters
        const scene = this.scenes[sceneIndex];
        
        if (params.input) {
            scene.input = { ...scene.input, ...params.input };
        }
        
        if (params.generation) {
            // Handle nested objects properly
            if (!scene.generation) scene.generation = {};
            
            // Update style object if provided
            if (params.generation.style) {
                scene.generation.style = { 
                    ...scene.generation.style || {}, 
                    ...params.generation.style 
                };
            }
            
            // Update controlnet object if provided
            if (params.generation.controlnet) {
                scene.generation.controlnet = { 
                    ...scene.generation.controlnet || {}, 
                    ...params.generation.controlnet 
                };
            }
            
            // Update fallback_cloud object if provided
            if (params.generation.fallback_cloud) {
                scene.generation.fallback_cloud = { 
                    ...scene.generation.fallback_cloud || {}, 
                    ...params.generation.fallback_cloud 
                };
            }
            
            // Update other generation parameters
            Object.keys(params.generation).forEach(key => {
                if (key !== 'style' && key !== 'controlnet' && key !== 'fallback_cloud') {
                    scene.generation[key] = params.generation[key];
                }
            });
        }
        
        if (params.animation) {
            // Handle nested objects properly
            if (!scene.animation) scene.animation = {};
            
            // Update runway_api_fallback object if provided
            if (params.animation.runway_api_fallback) {
                scene.animation.runway_api_fallback = { 
                    ...scene.animation.runway_api_fallback || {}, 
                    ...params.animation.runway_api_fallback 
                };
            }
            
            // Update kling_api object if provided
            if (params.animation.kling_api) {
                scene.animation.kling_api = { 
                    ...scene.animation.kling_api || {}, 
                    ...params.animation.kling_api 
                };
            }
            
            // Update video_assembly object if provided
            if (params.animation.video_assembly) {
                scene.animation.video_assembly = { 
                    ...scene.animation.video_assembly || {}, 
                    ...params.animation.video_assembly 
                };
            }
            
            // Update other animation parameters
            Object.keys(params.animation).forEach(key => {
                if (key !== 'runway_api_fallback' && key !== 'kling_api' && key !== 'video_assembly') {
                    scene.animation[key] = params.animation[key];
                }
            });
        }
        
        if (params.output) {
            scene.output = { ...scene.output || {}, ...params.output };
        }
        
        return true;
    }

    /**
     * Generate image for a specific scene
     * @param {number} sceneId - ID of the scene to generate
     * @returns {Promise} - Promise that resolves when generation is complete
     */
    async generateScene(sceneId) {
        if (this.generationInProgress) {
            return {
                success: false,
                error: 'Generation already in progress'
            };
        }

        const sceneIndex = this.scenes.findIndex(scene => scene.scene_id === sceneId);
        
        if (sceneIndex === -1) {
            return {
                success: false,
                error: `Scene with ID ${sceneId} not found`
            };
        }

        try {
            this.generationInProgress = true;
            
            // Send generation request
            const response = await fetch('/comfyui/generate_scene', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scene: this.scenes[sceneIndex]
                })
            });

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to start generation');
            }

            // Poll for generation status
            const promptId = data.prompt_id;
            let isCompleted = false;
            let result = null;
            
            while (!isCompleted) {
                // Wait for 1 second before checking status
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                const statusResponse = await fetch(`/comfyui/check_generation_status?prompt_id=${promptId}`);
                const statusData = await statusResponse.json();
                
                if (statusData.status === 'completed') {
                    isCompleted = true;
                    result = statusData;
                } else if (statusData.error) {
                    throw new Error(statusData.error);
                }
            }

            // Update scene with generated image
            if (result && result.images && result.images.length > 0) {
                this.scenes[sceneIndex].output.final_image = result.images[0].url;
                this.scenes[sceneIndex].output.image_url = result.images[0].url;
            }

            this.generationInProgress = false;
            
            return {
                success: true,
                scene: this.scenes[sceneIndex],
                images: result ? result.images : []
            };
        } catch (error) {
            console.error('Error generating scene:', error);
            this.generationInProgress = false;
            
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Generate all scenes sequentially
     * @returns {Promise} - Promise that resolves when all generations are complete
     */
    async generateAllScenes(progressCallback) {
        if (this.generationInProgress) {
            return {
                success: false,
                error: 'Generation already in progress'
            };
        }

        if (this.scenes.length === 0) {
            return {
                success: false,
                error: 'No scenes to generate'
            };
        }

        try {
            this.generationInProgress = true;
            
            const results = [];
            
            for (let i = 0; i < this.scenes.length; i++) {
                const scene = this.scenes[i];
                
                // Update progress
                if (progressCallback) {
                    progressCallback({
                        currentScene: i + 1,
                        totalScenes: this.scenes.length,
                        progress: Math.round(((i + 1) / this.scenes.length) * 100),
                        scene: scene
                    });
                }
                
                // Generate scene
                const result = await this.generateScene(scene.scene_id);
                results.push(result);
                
                if (!result.success) {
                    console.error(`Error generating scene ${scene.scene_id}:`, result.error);
                }
            }

            this.generationInProgress = false;
            
            return {
                success: true,
                results: results
            };
        } catch (error) {
            console.error('Error generating all scenes:', error);
            this.generationInProgress = false;
            
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Create video from generated scenes
     * @param {boolean} useAnimation - Whether to use animation effects
     * @returns {Promise} - Promise that resolves when video creation is complete
     */
    async createVideo(useAnimation = false) {
        if (this.scenes.length === 0) {
            return {
                success: false,
                error: 'No scenes to create video from'
            };
        }

        // Check if all scenes have generated images
        const missingImages = this.scenes.filter(scene => !scene.output || !scene.output.final_image);
        if (missingImages.length > 0) {
            return {
                success: false,
                error: `Missing generated images for scenes: ${missingImages.map(s => s.scene_id).join(', ')}`
            };
        }

        try {
            // Send video creation request
            const response = await fetch('/comfyui/create_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scenes: this.scenes,
                    use_animation: useAnimation
                })
            });

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to create video');
            }

            // Update scenes with video clip paths
            const videoPath = data.video_path;
            const videoUrl = data.video_url;
            
            // Set the video path for all scenes
            this.scenes.forEach(scene => {
                scene.output.video_clip = videoUrl;
            });
            
            return {
                success: true,
                videoPath: videoPath,
                videoUrl: videoUrl
            };
        } catch (error) {
            console.error('Error creating video:', error);
            
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get available models for a specific category
     * @param {string} category - Model category (stableDiffusion, controlNet, etc.)
     * @returns {Array} - Array of available models
     */
    getAvailableModels(category) {
        return this.availableModels[category] || [];
    }

    /**
     * Get current generation progress
     * @returns {Object} - Current generation progress
     */
    getProgress() {
        return {
            currentScene: this.currentSceneIndex,
            totalScenes: this.scenes.length,
            isGenerating: this.generationInProgress,
            progress: this.scenes.length > 0 ? (this.currentSceneIndex + 1) / this.scenes.length : 0
        };
    }

    /**
     * Export the current state as JSON
     * @returns {Object} - JSON representation of the current state
     */
    exportToJson() {
        return {
            scenes: this.scenes,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Import state from JSON
     * @param {Object} json - JSON representation of the state
     */
    importFromJson(json) {
        if (json && json.scenes) {
            this.scenes = json.scenes;
            return true;
        }
        return false;
    }
}

// Export the class for use in other modules
window.MCPProtocol = MCPProtocol;