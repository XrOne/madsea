import React, { useState, useContext } from 'react';
import { AppContext } from '../../context/AppContext';

const SceneDisplay = ({ scene }) => {
  const { addNotification, updateScene } = useContext(AppContext);
  const [showDetails, setShowDetails] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [adjusting, setAdjusting] = useState(false);
  
  if (!scene) return null;
  
  // Fonction pour générer une image à partir de la vignette extraite
  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      addNotification('Génération en cours...', 'info');
      
      // Appel API réel pour générer l'image
      const response = await fetch(`/api/scenes/${scene.id}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          style: scene.selectedStyle || 'default', // Style sélectionné ou style par défaut
          strength: 0.75, // Force de l'IA pour respecter l'image d'origine
          seed: scene.seed || -1, // Graine pour la reproductibilité ou -1 pour aléatoire
        }),
      });
      
      if (!response.ok) {
        throw new Error('Erreur serveur: ' + (await response.text() || response.statusText));
      }
      
      const data = await response.json();
      
      // Mettre à jour la scène avec l'image générée
      updateScene(scene.id, {
        ...scene,
        generatedImageUrl: data.imageUrl,
        generationTimestamp: new Date().toISOString(),
        lastStyle: scene.selectedStyle || 'default',
      });
      
      addNotification('Image générée avec succès', 'success');
      
      // Déclencher une autosauvegarde après génération
      fetch('/api/project/' + scene.projectId + '/autosave', { method: 'POST' })
        .then(() => addNotification('Projet sauvegardé automatiquement', 'info'))
        .catch(err => console.error('Erreur autosauvegarde:', err));
        
    } catch (error) {
      addNotification('Erreur lors de la génération: ' + error.message, 'error');
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Fonction pour ajuster les limites de l'image extraite
  const handleAdjustBoundaries = async () => {
    try {
      setAdjusting(true);
      addNotification('Ajustement des limites de la vignette...', 'info');
      
      // Interface utilisateur pour ajuster l'image (serait implémentée avec un composant d'édition)
      // Pour l'instant, simulons un simple ajustement
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addNotification('Limites de la vignette ajustées', 'success');
    } catch (error) {
      addNotification('Erreur lors de l\'ajustement: ' + error.message, 'error');
    } finally {
      setAdjusting(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition">
      <div className="relative aspect-video bg-gray-100">
        {scene.imageUrl ? (
          <img 
            src={scene.imageUrl} 
            alt={`Scène ${scene.number}`} 
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <span className="ml-2">Aucune image</span>
          </div>
        )}
        
        {scene.generatedImageUrl && (
          <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
            Généré
          </div>
        )}
        
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
          <h3 className="text-white font-medium">Scène {scene.number}</h3>
          {scene.title && (
            <p className="text-white/80 text-sm">{scene.title}</p>
          )}
        </div>
      </div>
      
      <div className="p-3">
        <div className="flex justify-between items-center mb-2">
          <div className="text-sm text-gray-500">
            {scene.type && <span className="mr-2">{scene.type}</span>}
            {scene.duration && <span>{scene.duration}s</span>}
          </div>
          <button 
            onClick={() => setShowDetails(!showDetails)}
            className="text-blue-600 text-sm hover:text-blue-800"
          >
            {showDetails ? 'Masquer' : 'Détails'}
          </button>
        </div>
        
        {showDetails && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            {scene.description && (
              <div className="mb-2">
                <h4 className="text-xs font-medium text-gray-700 mb-1">Description</h4>
                <p className="text-sm text-gray-600">{scene.description}</p>
              </div>
            )}
            
            {scene.dialogue && (
              <div className="mb-2">
                <h4 className="text-xs font-medium text-gray-700 mb-1">Dialogue</h4>
                <p className="text-sm text-gray-600 italic">{scene.dialogue}</p>
              </div>
            )}
            
            {scene.cameraMovement && (
              <div className="mb-2">
                <h4 className="text-xs font-medium text-gray-700 mb-1">Mouvements de caméra</h4>
                <p className="text-sm text-gray-600">{scene.cameraMovement}</p>
              </div>
            )}
            
            {scene.extractedText && (
              <div>
                <h4 className="text-xs font-medium text-gray-700 mb-1">Texte extrait (OCR)</h4>
                <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">{scene.extractedText}</p>
              </div>
            )}
          </div>
        )}
        
        <div className="mt-3 flex justify-between space-x-2">
          <button 
            className={`px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50 ${adjusting ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={handleAdjustBoundaries}
            disabled={adjusting || isGenerating}
            title="Ajuster les limites de la vignette extraite"
          >
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
              </svg>
              {adjusting ? 'Ajustement...' : 'Ajuster'}
            </div>
          </button>
          
          <button 
            className="px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50"
            onClick={() => {
              // Ouvrir le panneau d'édition des métadonnées
              addNotification("\u00c9dition des m\u00e9tadonn\u00e9es - Ouverture du panneau", "info");
            }}
            disabled={adjusting || isGenerating}
          >
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
              Éditer
            </div>
          </button>
          
          <button 
            className={`px-3 py-1 rounded text-sm text-white flex-grow ${  
              isGenerating || adjusting
                ? 'bg-gray-400 cursor-not-allowed' 
                : scene.generatedImageUrl 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
            }`}
            onClick={handleGenerate}
            disabled={isGenerating || adjusting}
          >
            <div className="flex items-center justify-center">
              {isGenerating 
                ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Génération...
                  </>
                )
                : scene.generatedImageUrl 
                  ? (
                    <>
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                      </svg>
                      Régénérer
                    </>
                  )
                  : (
                    <>
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                      </svg>
                      Générer
                    </>
                  )
              }
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SceneDisplay;