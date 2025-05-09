import os
from PIL import Image
import cv2
import csv

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

def generate_nomenclature_files(base_dir, episode_id, sequence_id, nb_plans):
    extracted_raw_dir = os.path.join(base_dir, episode_id, 'extracted-raw')
    ai_concept_dir = os.path.join(base_dir, episode_id, 'AI-concept')
    animation_dir = os.path.join(base_dir, episode_id, 'Animation')
    ensure_dir(extracted_raw_dir)
    ensure_dir(ai_concept_dir)
    ensure_dir(animation_dir)
    log_rows = []
    for i in range(nb_plans):
        plan_num = (i+1) * 10
        plan_str = f"{plan_num:04d}"
        page_str = f"{(i//4)+1:04d}"
        img_idx_str = f"{(i%4)+1:04d}"
        # extracted-raw
        extracted_raw_name = f"E{episode_id}_P{page_str}-I{img_idx_str}_extracted-raw_v0001.png"
        extracted_raw_path = os.path.join(extracted_raw_dir, extracted_raw_name)
        create_placeholder_image(extracted_raw_path)
        # AI-concept
        ai_concept_name = f"E{episode_id}_SQ{sequence_id}-{plan_str}_AI-concept_v0001.png"
        ai_concept_path = os.path.join(ai_concept_dir, ai_concept_name)
        create_placeholder_image(ai_concept_path)
        # Animation
        animation_name = f"E{episode_id}_SQ{sequence_id}-{plan_str}_Animation_v0001.mp4"
        animation_path = os.path.join(animation_dir, animation_name)
        create_placeholder_video(animation_path)
        log_rows.append([extracted_raw_name, ai_concept_name, animation_name])
    return log_rows

def write_log_csv(log_path, rows):
    with open(log_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['extracted_raw', 'ai_concept', 'animation'])
        writer.writerows(rows)

if __name__ == "__main__":
    import numpy as np
    base_dir = r"i:\Madsea\outputs\nomenclature_test"
    episode_id = "202"
    sequence_id = "0010"
    nb_plans = 70
    rows = generate_nomenclature_files(base_dir, episode_id, sequence_id, nb_plans)
    write_log_csv(os.path.join(base_dir, episode_id, 'log-nomenclature.csv'), rows)
    print(f"Fichiers générés dans {base_dir} pour {nb_plans} plans.")
