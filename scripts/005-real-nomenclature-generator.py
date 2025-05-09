import os
import csv
import numpy as np
from PIL import Image
import cv2
import shutil

def ensure_dir(path):
    """Créer un répertoire s'il n'existe pas."""
    os.makedirs(path, exist_ok=True)

def create_placeholder_image(path, size=(1920, 1080)):
    """Créer une image placeholder blanche."""
    img = Image.new('RGB', size, color=(255, 255, 255))
    img.save(path)

def create_placeholder_video(path, size=(1920, 1080), duration=1, fps=1):
    """Créer une vidéo placeholder blanche."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    frame = 255 * np.ones((size[1], size[0], 3), dtype=np.uint8)
    for _ in range(int(duration * fps)):
        out.write(frame)
    out.release()

def load_shots_from_csv(csv_path):
    """Charger les données du CSV du réalisateur."""
    shots = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Ignorer l'en-tête
        for row in reader:
            if len(row) >= 6:
                shot = {
                    'episode': row[0],
                    'sequence': row[1],
                    'plan': row[2],
                    'description': row[3],
                    'frame_in': row[4],
                    'frame_out': row[5],
                    'storyboard': row[6] if len(row) > 6 else "unknown",
                    'ai_concept': row[8] if len(row) > 8 else "todo"
                }
                shots.append(shot)
    return shots

def generate_nomenclature_files(base_dir, shots, source_storyboard_path=None):
    """
    Génère les fichiers selon la nomenclature Madsea en utilisant les données du CSV.
    
    Args:
        base_dir: Répertoire de base pour la sortie
        shots: Liste des plans extraits du CSV
        source_storyboard_path: Chemin optionnel vers les storyboards source
    """
    # Déterminer l'identifiant d'épisode (tous les plans devraient avoir le même)
    if not shots:
        print("Aucun plan trouvé dans le CSV.")
        return []
    
    episode_id = shots[0]['episode'].replace('E', '')
    
    # Créer les répertoires principaux
    episode_dir = os.path.join(base_dir, episode_id)
    extracted_raw_dir = os.path.join(episode_dir, 'extracted-raw')
    ai_concept_dir = os.path.join(episode_dir, 'AI-concept')
    animation_dir = os.path.join(episode_dir, 'Animation')
    ensure_dir(extracted_raw_dir)
    ensure_dir(ai_concept_dir)
    ensure_dir(animation_dir)
    
    # Créer les répertoires de séquence pour AI-concept et Animation
    sequences = {shot['sequence'] for shot in shots}
    for seq in sequences:
        ensure_dir(os.path.join(ai_concept_dir, seq))
        ensure_dir(os.path.join(animation_dir, seq))
    
    log_rows = []
    sequence_stats = {}
    
    # Initialiser les statistiques de séquence
    for seq in sequences:
        sequence_stats[seq] = {
            'count': 0,
            'plans': []
        }
    
    # Générer les fichiers pour chaque plan
    for i, shot in enumerate(shots):
        seq_id = shot['sequence']
        plan_id = shot['plan']
        
        # Compteur pour extracted-raw (P-I)
        page_str = f"{(i//4)+1:04d}"
        img_idx_str = f"{(i%4)+1:04d}"
        
        # Générer le nom du fichier extracted-raw
        extracted_raw_name = f"E{episode_id}_P{page_str}-I{img_idx_str}_extracted-raw_v0001.png"
        extracted_raw_path = os.path.join(extracted_raw_dir, extracted_raw_name)
        
        # Si chemin source fourni, copier l'image storyboard, sinon créer placeholder
        if source_storyboard_path:
            # TODO: Logique pour trouver et copier l'image storyboard source
            # Cette partie dépendrait de la structure des fichiers source
            # Pour l'instant, on crée des placeholders
            create_placeholder_image(extracted_raw_path)
        else:
            create_placeholder_image(extracted_raw_path)
        
        # Générer le nom du fichier AI-concept
        ai_concept_name = f"E{episode_id}_{seq_id}-{plan_id}_AI-concept_v0001.png"
        ai_concept_path = os.path.join(ai_concept_dir, seq_id, ai_concept_name)
        create_placeholder_image(ai_concept_path)
        
        # Générer le nom du fichier Animation
        animation_name = f"E{episode_id}_{seq_id}-{plan_id}_Animation_v0001.mp4"
        animation_path = os.path.join(animation_dir, seq_id, animation_name)
        create_placeholder_video(animation_path)
        
        # Mettre à jour les statistiques de séquence
        sequence_stats[seq_id]['count'] += 1
        sequence_stats[seq_id]['plans'].append(plan_id)
        
        # Ajouter au log
        log_rows.append([
            extracted_raw_name, 
            os.path.join(seq_id, ai_concept_name),
            os.path.join(seq_id, animation_name)
        ])
    
    # Générer le CSV de log
    log_path = os.path.join(episode_dir, 'log-nomenclature.csv')
    with open(log_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['extracted_raw', 'ai_concept', 'animation'])
        writer.writerows(log_rows)
    
    # Générer le CSV des statistiques de séquence
    sequence_path = os.path.join(episode_dir, 'sequences-stats.csv')
    with open(sequence_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['sequence_id', 'nb_plans', 'plan_ids'])
        for seq_id, stats in sequence_stats.items():
            writer.writerow([
                seq_id,
                stats['count'],
                ', '.join(stats['plans'])
            ])
    
    return log_rows, sequence_stats

if __name__ == "__main__":
    # Chemins de fichiers
    csv_path = r"i:\Madsea\ComfyUI\2025_05_09_kitsu_declics_s02_e202_shots.csv"
    base_dir = r"i:\Madsea\outputs\nomenclature_test"
    
    # Charger les données du CSV
    shots = load_shots_from_csv(csv_path)
    
    # Générer les fichiers selon la nomenclature
    log_rows, sequence_stats = generate_nomenclature_files(base_dir, shots)
    
    # Afficher les statistiques
    print(f"Fichiers générés dans {base_dir} pour l'épisode {shots[0]['episode']}.")
    print(f"Total de {len(shots)} plans répartis sur {len(sequence_stats)} séquences.")
    
    # Afficher les détails des séquences
    for seq_id, stats in sequence_stats.items():
        print(f"  - {seq_id}: {stats['count']} plans")
