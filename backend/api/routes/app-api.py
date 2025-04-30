from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil
import uuid
import time
import json
from datetime import datetime
import zipfile
import tempfile

# Import des services
from services.extraction import StoryboardExtractor
from services.comfyui import ComfyUIService
from services.file_manager import FileManager

app = FastAPI(title="Madsea API", description="API pour transformer des storyboards en séquences visuelles")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour le développement - à restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des chemins
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
PROJECTS_FILE = os.path.join(os.getcwd(), "data", "projects.json")

# Créer les répertoires s'ils n'existent pas
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)

# Initialiser les services
file_manager = FileManager(UPLOAD_DIR, OUTPUT_DIR)
extractor = StoryboardExtractor(os.path.join(OUTPUT_DIR, "extracted"))
comfyui_service = ComfyUIService(comfyui_url="http://127.0.0.1:8188")

# Définition des modèles de données
class ProjectCreate(BaseModel):
    name: str
    type: str  # 'unitaire' ou 'serie'
    duration: Optional[str] = None
    season: Optional[str] = None
    episode: Optional[str] = None
    title: Optional[str] = None

class EpisodeCreate(BaseModel):
    number: str
    name: str

class GenerationRequest(BaseModel):
    scene_ids: List[str]
    style: str
    prompt_override: Optional[str] = None
    controlnet_weight: float = 1.0
    guidance_scale: float = 7.5
    steps: int = 40

class GenerationJob(BaseModel):
    job_id: str
    scene_ids: List[str]
    style: str
    status: str = "pending"
    progress: float = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    results: List[Dict[str, Any]] = []

# Gestionnaire d'états de génération
generation_jobs = {}

# Fonctions utilitaires
def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)

def find_project(project_id):
    projects = load_projects()
    for project in projects:
        if project['id'] == project_id:
            return project
    return None

def find_episode(project, episode_id):
    for episode in project.get('episodes', []):
        if episode['id'] == episode_id:
            return episode
    return None

def get_scenes_for_episode(episode_id):
    scenes_file = os.path.join(os.getcwd(), "data", "scenes", f"{episode_id}.json")
    if os.path.exists(scenes_file):
        with open(scenes_file, 'r') as f:
            return json.load(f)
    return []

def save_scenes_for_episode(episode_id, scenes):
    scenes_dir = os.path.join(os.getcwd(), "data", "scenes")
    os.makedirs(scenes_dir, exist_ok=True)
    
    scenes_file = os.path.join(scenes_dir, f"{episode_id}.json")
    with open(scenes_file, 'w') as f:
        json.dump(scenes, f, indent=2)

# Routes API
@app.get("/api/status")
async def get_status():
    """Vérifie le statut de l'API et de ComfyUI"""
    comfyui_status = comfyui_service.check_status()
    
    return {
        "api_status": "online",
        "version": "1.0.0",
        "comfyui_status": comfyui_status.get("status", "offline"),
        "timestamp": time.time()
    }

@app.get("/api/projects")
async def get_projects():
    """Récupère la liste des projets"""
    return load_projects()

@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    """Crée un nouveau projet"""
    projects = load_projects()
    
    # Générer un ID unique
    project_id = f"proj_{int(time.time())}"
    
    # Construire la nomenclature
    nomenclature = ""
    if project.type == "unitaire":
        if not project.title:
            raise HTTPException(status_code=400, detail="Le titre est requis pour un projet unitaire")
        nomenclature = f"{project.title.replace(' ', '_')}_v0001.jpg"
    else:
        if not all([project.season, project.episode]):
            raise HTTPException(status_code=400, detail="Saison et épisode requis pour une série")
        nomenclature = f"E{project.season}{project.episode}_SQ0001-0001_AI-Concept_v0001.jpg"
    
    # Créer l'objet projet
    new_project = {
        "id": project_id,
        "name": project.name,
        "type": project.type,
        "duration": project.duration,
        "season": project.season,
        "episode": project.episode,
        "title": project.title,
        "nomenclature": nomenclature,
        "episodes": [],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "isArchived": False
    }
    
    # Ajouter un premier épisode
    episode_id = f"ep_{int(time.time())}"
    first_episode = {
        "id": episode_id,
        "number": "1" if project.type == "unitaire" else f"{project.season}{project.episode}",
        "name": project.title if project.type == "unitaire" else f"Épisode {project.episode}",
        "scenes": []
    }
    
    new_project["episodes"].append(first_episode)
    projects.append(new_project)
    
    # Sauvegarder les projets
    save_projects(projects)
    
    return new_project

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Récupère les détails d'un projet"""
    project = find_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return project

@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, project_data: dict):
    """Met à jour un projet"""
    projects = load_projects()
    
    for i, project in enumerate(projects):
        if project["id"] == project_id:
            # Mettre à jour les champs modifiables
            for key in project_data:
                if key not in ["id", "createdAt"]:  # Champs non modifiables
                    project[key] = project_data[key]
            
            project["updatedAt"] = datetime.now().isoformat()
            projects[i] = project
            
            save_projects(projects)
            return project
    
    raise HTTPException(status_code=404, detail="Projet non trouvé")

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Supprime ou archive un projet"""
    projects = load_projects()
    
    for i, project in enumerate(projects):
        if project["id"] == project_id:
            # Archiver plutôt que supprimer définitivement
            project["isArchived"] = True
            project["updatedAt"] = datetime.now().isoformat()
            projects[i] = project
            
            save_projects(projects)
            return {"status": "success", "message": "Projet archivé avec succès"}
    
    raise HTTPException(status_code=404, detail="Projet non trouvé")

@app.post("/api/projects/{project_id}/episodes")
async def create_episode(project_id: str, episode: EpisodeCreate):
    """Crée un nouvel épisode dans un projet"""
    project = find_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    # Générer un ID unique
    episode_id = f"ep_{int(time.time())}"
    
    # Créer l'objet épisode
    new_episode = {
        "id": episode_id,
        "number": episode.number,
        "name": episode.name,
        "scenes": []
    }
    
    # Ajouter l'épisode au projet
    project["episodes"].append(new_episode)
    project["updatedAt"] = datetime.now().isoformat()
    
    # Sauvegarder les projets
    save_projects(load_projects())
    
    return new_episode

@app.post("/api/episodes/{episode_id}/import")
async def import_storyboard(
    background_tasks: BackgroundTasks,
    episode_id: str,
    project_id: str = Form(...),
    starting_sequence: int = Form(1),
    starting_plan: int = Form(1),
    file: UploadFile = File(...)
):
    """Importe et extrait un storyboard pour un épisode"""
    # Vérifier que le projet et l'épisode existent
    project = find_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    episode = find_episode(project, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Épisode non trouvé")
    
    # Déterminer le code du projet
    project_code = ""
    if project["type"] == "unitaire":
        project_code = project["title"].replace(" ", "_") if project["title"] else "UNIT"
    else:
        project_code = f"E{project['season']}{project['episode']}"
    
    # Créer un répertoire spécifique pour l'upload
    upload_path = os.path.join(UPLOAD_DIR, f"{project_id}_{episode_id}")
    os.makedirs(upload_path, exist_ok=True)
    
    # Sauvegarder le fichier
    file_path = os.path.join(upload_path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Configuration pour l'extraction
    project_info = {
        'project_code': project_code,
        'starting_sequence': starting_sequence,
        'starting_plan': starting_plan
    }
    
    # Initialiser le statut de l'extraction
    extraction_id = f"extract_{int(time.time())}"
    extraction_status = {
        "id": extraction_id,
        "status": "processing",
        "progress": 0,
        "message": "Début de l'extraction...",
        "file": file.filename,
        "project_id": project_id,
        "episode_id": episode_id
    }
    
    # Fonction d'extraction en arrière-plan
    def extract_storyboard():
        try:
            # Mise à jour du statut
            extraction_status["progress"] = 10
            extraction_status["message"] = "Analyse du fichier..."
            
            # Déterminer le type de fichier
            filename_lower = file.filename.lower()
            scenes = []
            
            extraction_status["progress"] = 30
            extraction_status["message"] = "Extraction des images..."
            
            # Traiter selon le type de fichier
            if filename_lower.endswith('.pdf'):
                # Extraction depuis PDF
                scenes = extractor.extract_from_pdf(file_path, project_info)
            elif filename_lower.endswith(('.zip', '.rar')):
                # Extraction depuis archive
                # Créer un répertoire temporaire pour l'extraction
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extraire l'archive
                    if filename_lower.endswith('.zip'):
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                    
                    # Trouver toutes les images dans le répertoire extrait
                    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
                    image_paths = []
                    
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in image_extensions):
                                image_paths.append(os.path.join(root, file))
                    
                    # Trier les images par nom
                    image_paths.sort()
                    
                    # Extraire les scènes depuis les images
                    scenes = extractor.extract_from_images(image_paths, project_info)
            else:
                # Traitement d'une seule image
                scenes = extractor.extract_from_images([file_path], project_info)
            
            extraction_status["progress"] = 70
            extraction_status["message"] = f"{len(scenes)} scènes détectées..."
            
            # Sauvegarder les scènes pour l'épisode
            save_scenes_for_episode(episode_id, scenes)
            
            # Mettre à jour l'épisode dans le projet
            projects = load_projects()
            for i, proj in enumerate(projects):
                if proj["id"] == project_id:
                    for j, ep in enumerate(proj["episodes"]):
                        if ep["id"] == episode_id:
                            projects[i]["episodes"][j]["scenes"] = [s["id"] for s in scenes]
                            break
            
            save_projects(projects)
            
            extraction_status["progress"] = 100
            extraction_status["status"] = "completed"
            extraction_status["message"] = f"Extraction terminée: {len(scenes)} scènes"
            extraction_status["scenes"] = scenes
            
        except Exception as e:
            extraction_status["status"] = "error"
            extraction_status["message"] = f"Erreur pendant l'extraction: {str(e)}"
    
    # Lancer l'extraction en arrière-plan
    background_tasks.add_task(extract_storyboard)
    
    return extraction_status

@app.get("/api/episodes/{episode_id}/scenes")
async def get_scenes(episode_id: str):
    """Récupère les scènes d'un épisode"""
    scenes = get_scenes_for_episode(episode_id)
    return scenes

@app.get("/api/extraction/{extraction_id}/status")
async def get_extraction_status(extraction_id: str):
    """Vérifie le statut d'une extraction en cours"""
    # Cette fonction devrait récupérer le statut actuel d'une extraction
    # Dans une implémentation réelle, on stockerait ces statuts dans une base de données
    # Pour simplifier, on renvoie un statut fictif
    return {
        "id": extraction_id,
        "status": "completed",
        "progress": 100,
        "message": "Extraction terminée avec succès"
    }

@app.post("/api/generate")
async def generate_images(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Lance une génération d'images pour les scènes sélectionnées"""
    # Vérifier que le style existe
    if request.style not in comfyui_service.available_styles:
        raise HTTPException(status_code=400, detail=f"Style non disponible. Styles valides: {list(comfyui_service.available_styles.keys())}")
    
    # Vérifier le statut de ComfyUI
    comfyui_status = comfyui_service.check_status()
    if comfyui_status.get("status") != "online":
        raise HTTPException(status_code=503, detail="ComfyUI n'est pas disponible")
    
    # Collecter les informations des scènes
    all_scenes = []
    scene_ids_set = set(request.scene_ids)
    
    # Pour une implémentation complète, on devrait chercher dans tous les épisodes
    # Ici on simplifie en parcourant les fichiers de scènes
    scenes_dir = os.path.join(os.getcwd(), "data", "scenes")
    if os.path.exists(scenes_dir):
        for scene_file in os.listdir(scenes_dir):
            if scene_file.endswith('.json'):
                with open(os.path.join(scenes_dir, scene_file), 'r') as f:
                    scenes = json.load(f)
                    for scene in scenes:
                        if scene["id"] in scene_ids_set:
                            all_scenes.append(scene)
    
    if not all_scenes:
        raise HTTPException(status_code=404, detail="Aucune scène trouvée avec les IDs fournis")
    
    # Créer un job de génération
    job_id = f"gen_{int(time.time())}"
    
    generation_job = GenerationJob(
        job_id=job_id,
        scene_ids=request.scene_ids,
        style=request.style
    )
    
    generation_jobs[job_id] = generation_job.dict()
    
    # Fonction de génération en arrière-plan
    def generate_images_task():
        try:
            job = generation_jobs[job_id]
            job["status"] = "processing"
            job["start_time"] = time.time()
            
            # Configurer le répertoire de sortie
            output_dir = os.path.join(OUTPUT_DIR, "generated", job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Préparer la liste des scènes pour la génération par lot
            scene_list = []
            for scene in all_scenes:
                # Si un prompt override est fourni, on l'utilise pour toutes les scènes
                prompt = request.prompt_override if request.prompt_override else extractor.auto_generate_prompt(scene)
                
                scene_list.append({
                    "id": scene["id"],
                    "image_path": scene["image_path"],
                    "prompt": prompt
                })
            
            # Lancer la génération par lot
            results = comfyui_service.batch_generate(
                scene_list=scene_list,
                style=request.style,
                output_dir=output_dir,
                controlnet_weight=request.controlnet_weight,
                guidance_scale=request.guidance_scale,
                steps=request.steps
            )
            
            # Mettre à jour le job avec les résultats
            job["results"] = results
            job["status"] = "completed"
            job["progress"] = 100
            job["end_time"] = time.time()
            
            # Mettre à jour les scènes avec les nouvelles images générées
            for result in results:
                if result["status"] == "success":
                    scene_id = result["scene_id"]
                    # Trouver l'épisode contenant cette scène
                    for scene_file in os.listdir(scenes_dir):
                        if scene_file.endswith('.json'):
                            with open(os.path.join(scenes_dir, scene_file), 'r') as f:
                                scenes = json.load(f)
                                updated = False
                                for i, scene in enumerate(scenes):
                                    if scene["id"] == scene_id:
                                        # Ajouter l'image générée à la scène
                                        if "generated_images" not in scene:
                                            scene["generated_images"] = []
                                        
                                        scene["generated_images"].append({
                                            "path": result["output_path"],
                                            "style": request.style,
                                            "timestamp": time.time(),
                                            "parameters": {
                                                "controlnet_weight": request.controlnet_weight,
                                                "guidance_scale": request.guidance_scale,
                                                "steps": request.steps,
                                                "seed": result.get("seed", -1)
                                            }
                                        })
                                        
                                        scenes[i] = scene
                                        updated = True
                                        break
                                
                                if updated:
                                    with open(os.path.join(scenes_dir, scene_file), 'w') as f:
                                        json.dump(scenes, f, indent=2)
        
        except Exception as e:
            job = generation_jobs.get(job_id, {})
            job["status"] = "error"
            job["message"] = str(e)
            job["end_time"] = time.time()
    
    # Lancer la génération en arrière-plan
    background_tasks.add_task(generate_images_task)
    
    return generation_job

@app.get("/api/generations/{job_id}")
async def get_generation_status(job_id: str):
    """Récupère le statut d'une génération"""
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job de génération non trouvé")
    
    job = generation_jobs[job_id]
    
    # Calculer le temps écoulé
    if job["status"] == "processing" and job.get("start_time"):
        elapsed = time.time() - job["start_time"]
        job["elapsed_time"] = elapsed
    
    return job

@app.get("/api/styles")
async def get_available_styles():
    """Récupère la liste des styles disponibles"""
    return {
        "styles": [
            {
                "id": "ombre_chinoise",
                "name": "Ombres chinoises",
                "description": "Silhouettes noires sur fond coloré",
                "icon": "🖤"
            },
            {
                "id": "laboratoire",
                "name": "Laboratoire",
                "description": "Style scientifique, rendu photoréaliste",
                "icon": "🔬"
            },
            {
                "id": "expressionniste",
                "name": "Expressionniste",
                "description": "Émotionnel, contrastes intenses, angles dramatiques",
                "icon": "🎨"
            },
            {
                "id": "custom",
                "name": "Custom",
                "description": "Personnalisé via paramètres avancés",
                "icon": "⚙️"
            }
        ]
    }

# Montage des fichiers statiques
@app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")

# Pour le développement, monter le frontend
@app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
