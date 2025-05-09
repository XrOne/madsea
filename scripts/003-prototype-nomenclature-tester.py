import os
from PIL import Image
import cv2
import csv
import numpy as np
import logging
import pytest
from unittest.mock import patch

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Répertoire vérifié/créé : {path}")
    except Exception as e:
        logging.error(f"Erreur création répertoire {path} : {e}")

def create_placeholder_image(path, size=(1920, 1080)):
    try:
        img = Image.new('RGB', size, color=(255, 255, 255))
        img.save(path)
        logging.info(f"Image créée : {path}")
    except Exception as e:
        logging.error(f"Erreur création image {path} : {e}")

def create_placeholder_video(path, size=(1920, 1080), duration=1, fps=1):
    try:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, fps, size)
        frame = 255 * np.ones((size[1], size[0], 3), dtype=np.uint8)
        for _ in range(int(duration * fps)):
            out.write(frame)
        out.release()
        logging.info(f"Vidéo créée : {path}")
    except Exception as e:
        logging.error(f"Erreur création vidéo {path} : {e}")

def generate_nomenclature_files(base_dir, episode_id, sequence_id, nb_plans):
    try:
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
    except Exception as e:
        logging.error(f"Erreur dans la génération des fichiers de nomenclature : {e}")
        return []

def write_log_csv(log_path, rows):
    try:
        with open(log_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['extracted_raw', 'ai_concept', 'animation'])
            writer.writerows(rows)
        logging.info(f"Log CSV écrit : {log_path}")
    except Exception as e:
        logging.error(f"Erreur écriture log CSV {log_path} : {e}")

def main_nomenclature(base_dir, episode_id, sequence_id, nb_plans):
    rows = generate_nomenclature_files(base_dir, episode_id, sequence_id, nb_plans)
    log_path = os.path.join(base_dir, episode_id, 'log-nomenclature.csv')
    write_log_csv(log_path, rows)
    logging.info(f"Fichiers générés dans {base_dir} pour {nb_plans} plans.")
    return rows

def test_invalid_input():
    with pytest.raises(ValueError):
        generate_nomenclature_files(None, None, None, -1)

@patch('os.makedirs')
def test_ensure_dir(mock_makedirs):
    ensure_dir('test_dir')
    mock_makedirs.assert_called_once_with('test_dir', exist_ok=True)

def test_create_placeholder_image():
    create_placeholder_image('test_image.png')
    assert os.path.exists('test_image.png')

def test_create_placeholder_video():
    create_placeholder_video('test_video.mp4')
    assert os.path.exists('test_video.mp4')

def test_generate_nomenclature_files():
    rows = generate_nomenclature_files('test_dir', 'E20', 'SQ001', 5)
    assert len(rows) == 5

def test_write_log_csv():
    rows = [['test1', 'test2', 'test3']]
    write_log_csv('test_log.csv', rows)
    assert os.path.exists('test_log.csv')

if __name__ == "__main__":
    base_dir = r"i:\Madsea\outputs\nomenclature_test"
    episode_id = "666"
    sequence_id = "0010"
    nb_plans = 70
    main_nomenclature(base_dir, episode_id, sequence_id, nb_plans)
