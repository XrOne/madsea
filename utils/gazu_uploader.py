import gazu
import json
import logging
from pathlib import Path

def upload_proposals_to_gazu(project_name, shots_json_path, email, password, task_type="Concept Art"):
    """
    Envoie les propositions d'images à l'API Gazu (CGWire) pour validation prestataire.
    Args:
        project_name (str): Nom du projet CGWire
        shots_json_path (str or Path): Chemin vers le JSON d'indexation des plans/propositions
        email (str): Email utilisateur CGWire
        password (str): Mot de passe utilisateur CGWire
        task_type (str): Type de tâche (ex: "Concept Art")
    Returns:
        list: Résultats d'upload pour chaque proposition
    """
    logging.info(f"Connexion à Gazu pour le projet {project_name}...")
    gazu.log_in(email, password)
    project = gazu.project.get_project_by_name(project_name)
    with open(shots_json_path, 'r', encoding='utf-8') as f:
        shots = json.load(f)
    results = []
    for shot_info in shots:
        shot_id = shot_info["shot_id"]
        try:
            shot = gazu.shot.get_shot_by_name(project, shot_id.split("_")[0] + "_" + shot_id.split("_")[1] + "_" + shot_id.split("_")[2])
            for proposal_path in shot_info.get("proposals", []):
                task = gazu.task.get_task_by_name(shot, task_type)
                version_name = Path(proposal_path).stem
                try:
                    version = gazu.task.add_task_output(
                        task,
                        comment=f"Proposition restylisée {shot_info.get('style','')}, version {shot_info.get('version',1)}",
                        output_file=proposal_path,
                        version_name=version_name
                    )
                    results.append({"shot_id": shot_id, "proposal": proposal_path, "status": "success"})
                except Exception as e:
                    logging.error(f"Erreur upload {proposal_path} pour {shot_id}: {e}")
                    results.append({"shot_id": shot_id, "proposal": proposal_path, "status": "error", "error": str(e)})
        except Exception as e:
            logging.error(f"Shot {shot_id} introuvable: {e}")
            results.append({"shot_id": shot_id, "status": "error", "error": str(e)})
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Uploader des images de plans/propositions sur Gazu (CGWire)")
    parser.add_argument('--project', required=True, help='Nom du projet CGWire')
    parser.add_argument('--json', required=True, help='Chemin vers le fichier JSON d\'indexation')
    parser.add_argument('--email', required=True, help='Email utilisateur CGWire')
    parser.add_argument('--password', required=True, help='Mot de passe utilisateur CGWire')
    parser.add_argument('--task', default="Concept Art", help='Type de tâche (par défaut: Concept Art)')
    args = parser.parse_args()
    results = upload_proposals_to_gazu(args.project, args.json, args.email, args.password, args.task)
    print(json.dumps(results, indent=2, ensure_ascii=False))
