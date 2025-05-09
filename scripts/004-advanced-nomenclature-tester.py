import os
from PIL import Image
import cv2
import csv
import numpy as np

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def create_placeholder_image(path, size=(1920, 1080)):
    img = Image.new('RGB', size, color=(255, 255, 255))
    img.save(path)

def create_placeholder_video(path, size=(1920, 1080), duration=1, fps=1):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    frame = 255 * np.ones((size[1], size[0], 3), dtype=np.uint8)
    for _ in range(int(duration * fps)):
        out.write(frame)
    out.release()

def generate_nomenclature_files_alternating_sequences(base_dir, episode_id, sequences_data, total_plans):
    """
    Génère des fichiers respectant la nomenclature Madsea pour des séquences alternées.
    
    Args:
        base_dir: Dossier de base
        episode_id: ID de l'épisode (ex: "666")
        sequences_data: Liste de tuples (sequence_id, nb_plans) pour chaque séquence "Ombres Chinoises"
        total_plans: Nombre total de plans à générer (pour uniformiser la numérotation des fichiers extracted-raw)
    """
    # Créer les répertoires nécessaires
    extracted_raw_dir = os.path.join(base_dir, episode_id, 'extracted-raw')
    ai_concept_dir = os.path.join(base_dir, episode_id, 'AI-concept')
    animation_dir = os.path.join(base_dir, episode_id, 'Animation')
    ensure_dir(extracted_raw_dir)
    ensure_dir(ai_concept_dir)
    ensure_dir(animation_dir)
    
    log_rows = []
    global_plan_index = 0  # Index global pour l'extraction des pages
    
    # Créer un fichier d'information sur les séquences
    sequences_info = []
    
    for sequence_id, nb_plans in sequences_data:
        # Pour chaque séquence d'Ombres Chinoises
        sequence_info = {
            "sequence_id": sequence_id,
            "style": "Ombres Chinoises",
            "nb_plans": nb_plans,
            "plans": []
        }
        
        for i in range(nb_plans):
            # Numérotation du plan dans la séquence
            plan_num = (i+1) * 10
            plan_str = f"{plan_num:04d}"
            
            # Pour les images extraites, on garde une numérotation globale
            page_str = f"{(global_plan_index//4)+1:04d}"
            img_idx_str = f"{(global_plan_index%4)+1:04d}"
            
            # Fichier extracted-raw (image extraite du PDF)
            extracted_raw_name = f"E{episode_id}_P{page_str}-I{img_idx_str}_extracted-raw_v0001.png"
            extracted_raw_path = os.path.join(extracted_raw_dir, extracted_raw_name)
            create_placeholder_image(extracted_raw_path)
            
            # AI-concept (image générée par IA pour Ombres Chinoises)
            ai_concept_name = f"E{episode_id}_SQ{sequence_id}-{plan_str}_AI-concept_v0001.png"
            ai_concept_path = os.path.join(ai_concept_dir, ai_concept_name)
            create_placeholder_image(ai_concept_path)
            
            # Animation (vidéo générée)
            animation_name = f"E{episode_id}_SQ{sequence_id}-{plan_str}_Animation_v0001.mp4"
            animation_path = os.path.join(animation_dir, animation_name)
            create_placeholder_video(animation_path)
            
            # Ajouter à la liste des plans de cette séquence
            sequence_info["plans"].append({
                "extracted_raw": extracted_raw_name,
                "ai_concept": ai_concept_name,
                "animation": animation_name,
                "plan_num": plan_str
            })
            
            log_rows.append([extracted_raw_name, ai_concept_name, animation_name])
            global_plan_index += 1
        
        sequences_info.append(sequence_info)
    
    # Compléter jusqu'au total de plans demandés (pour les plans Labo non générés)
    while global_plan_index < total_plans:
        page_str = f"{(global_plan_index//4)+1:04d}"
        img_idx_str = f"{(global_plan_index%4)+1:04d}"
        
        # Seulement l'image extraite pour ces plans (style Labo)
        extracted_raw_name = f"E{episode_id}_P{page_str}-I{img_idx_str}_extracted-raw_v0001.png"
        extracted_raw_path = os.path.join(extracted_raw_dir, extracted_raw_name)
        create_placeholder_image(extracted_raw_path)
        
        log_rows.append([extracted_raw_name, "Style Labo (non généré)", "Style Labo (non généré)"])
        global_plan_index += 1
    
    # Générer le CSV de log
    write_log_csv(os.path.join(base_dir, episode_id, 'log-nomenclature.csv'), log_rows)
    
    # Générer un fichier JSON/CSV de description des séquences
    write_sequences_info(os.path.join(base_dir, episode_id, 'sequences-info.csv'), sequences_info)
    
    return log_rows, sequences_info

def write_log_csv(log_path, rows):
    with open(log_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['extracted_raw', 'ai_concept', 'animation'])
        writer.writerows(rows)

def write_sequences_info(info_path, sequences_info):
    with open(info_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['sequence_id', 'style', 'nb_plans', 'first_plan', 'last_plan'])
        for seq in sequences_info:
            first_plan = seq["plans"][0]["plan_num"] if seq["plans"] else "N/A"
            last_plan = seq["plans"][-1]["plan_num"] if seq["plans"] else "N/A"
            writer.writerow([
                seq["sequence_id"], 
                seq["style"], 
                seq["nb_plans"],
                first_plan,
                last_plan
            ])

if __name__ == "__main__":
    base_dir = r"i:\Madsea\outputs\nomenclature_test"
    episode_id = "666"
    
    # Liste des séquences "Ombres Chinoises" avec leur nombre de plans
    # Format: [(sequence_id, nb_plans), ...]
    sequences_data = [
        ("0010", 10),  # SQ0010: 10 plans
        ("0030", 15),  # SQ0030: 15 plans
        ("0050", 20),  # SQ0050: 20 plans
        ("0070", 25),  # SQ0070: 25 plans
    ]
    
    # Nombre total de plans (y compris ceux qui ne sont pas à générer)
    total_plans = 100  # 70 plans Ombres Chinoises + 30 plans Labo
    
    log_rows, sequences_info = generate_nomenclature_files_alternating_sequences(
        base_dir, episode_id, sequences_data, total_plans
    )
    
    print(f"Fichiers générés dans {base_dir} pour {len(log_rows)} plans total.")
    print(f"Dont {sum(seq['nb_plans'] for seq in sequences_info)} plans 'Ombres Chinoises' à générer par IA.")
    print(f"Répartis sur {len(sequences_info)} séquences : {', '.join([f'SQ{seq['sequence_id']}' for seq in sequences_info])}")
