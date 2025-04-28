import requests
import json
import os

# Configuration
API_URL = "http://localhost:5000/api/upload_storyboard"
PDF_PATH = r"d:\madsea\pdf storyboard\E202_nanoTech 2024-04-09 11.25.08.pdf"
OUTPUT_JSON = "api_test_results.json"

# Vérifier que le fichier PDF existe
if not os.path.exists(PDF_PATH):
    print(f"ERREUR: Le fichier PDF {PDF_PATH} n'existe pas.")
    exit(1)

print(f"Test d'extraction OCR améliorée via API")
print(f"PDF de test: {PDF_PATH}")
print(f"API endpoint: {API_URL}")
print("-" * 80)

# Préparer les données pour l'API
files = {
    'storyboard_file': open(PDF_PATH, 'rb')
}

# Dans un cas réel, ces IDs seraient fournis par l'interface, mais ici nous utilisons des valeurs factices
form_data = {
    'project_id': 'test_project_001',
    'episode_id': 'test_episode_001',
    'options': json.dumps({
        'detectPanels': True,
        'extractText': True,
        'enhanceQuality': True,
        'extractCaptions': True
    })
}

try:
    print("Envoi de la requête API...")
    response = requests.post(API_URL, files=files, data=form_data)
    
    # Fermer le fichier après utilisation
    files['storyboard_file'].close()
    
    print(f"Statut de la réponse: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        
        # Sauvegarder la réponse complète dans un fichier JSON
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        print(f"Résultats enregistrés dans {OUTPUT_JSON}")
        
        # Afficher un résumé des résultats
        print("\nRésumé des résultats:")
        print(f"- Message: {result.get('message', 'Non fourni')}")
        
        # Afficher les statistiques sur les données extraites
        if 'extracted_images' in result:
            print(f"- Images extraites: {len(result['extracted_images'])}")
        
        if 'pages' in result:
            print(f"- Pages traitées: {len(result['pages'])}")
            
            # Compter les textes extraits par OCR
            ocr_texts_count = 0
            for page in result.get('pages', []):
                ocr_texts_count += len(page.get('texts', []))
            
            print(f"- Blocs de texte extraits: {ocr_texts_count}")
            
            # Afficher un échantillon de texte extrait (première page si disponible)
            if result['pages'] and 'texts' in result['pages'][0]:
                print("\nÉchantillon de texte extrait (première page):")
                for i, text in enumerate(result['pages'][0]['texts']):
                    if i < 3:  # Limiter à 3 exemples
                        print(f"  Texte {i+1}: {text.get('content', '')[:100]}...")
                    else:
                        break
        
    else:
        print(f"ERREUR: L'API a retourné une erreur {response.status_code}")
        print(f"Détails: {response.text}")

except Exception as e:
    print(f"ERREUR: {str(e)}")
    if 'response' in locals() and hasattr(response, 'text'):
        print(f"Détails de la réponse: {response.text}")

print("-" * 80)
print("Test terminé")
