import React, { useState, useContext, useEffect } from 'react';
import { AppContext } from '../context/AppContext';
import SceneGrid from '../components/scene/SceneGrid';
import StyleSelector from '../components/scene/StyleSelector';
import AutosaveTimeline from '../components/project/AutosaveTimeline';
import SceneToolbar from '../components/SceneToolbar';
import LoRATrainer from '../components/LoRATrainer';

const SceneGenerationView = () => {
  const { activeProject, activeEpisode, addNotification } = useContext(AppContext);
  const [showTimeline, setShowTimeline] = useState(false);
  const [showStyleSelector, setShowStyleSelector] = useState(false);
  const [currentStyle, setCurrentStyle] = useState(null);
  const [generationStatus, setGenerationStatus] = useState({
    isGenerating: false,
    progress: 0,
    scenesCompleted: 0,
    totalScenes: 0
  });

  // Mettre à jour le statut de génération quand l'épisode actif change
  useEffect(() => {
    if (activeEpisode && activeEpisode.scenes) {
      setGenerationStatus(prev => ({
        ...prev,
        totalScenes: activeEpisode.scenes.length,
        scenesCompleted: activeEpisode.scenes.filter(s => s.generatedImageUrl).length
      }));
    }
  }, [activeEpisode]);

  const handleStyleChange = (styleId) => {
    setCurrentStyle(styleId);
    addNotification(`Style sélectionné pour la génération`, 'info');
  };

  const handleGenerateAll = async () => {
    try {
      if (!activeEpisode || !activeEpisode.scenes || activeEpisode.scenes.length === 0) {
        addNotification('Aucune scène disponible pour la génération', 'warning');
        return;
      }

      if (!currentStyle) {
        addNotification('Veuillez sélectionner un style avant de générer', 'warning');
        setShowStyleSelector(true);
        return;
      }

      setGenerationStatus({
        isGenerating: true,
        progress: 0,
        scenesCompleted: 0,
        totalScenes: activeEpisode.scenes.length
      });

      console.log('Tentative de génération de toutes les scènes...');
      
      // Appel API pour générer toutes les scènes
      const response = await fetch(`/api/episodes/${activeEpisode.id}/generate-all`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          style: currentStyle,
          // Autres options de génération
          strength: 0.75,
          seed: -1,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Erreur backend:', errorData);
        addNotification(errorData.error || 'Erreur lors de la génération', 'error');
        setGenerationStatus({
          isGenerating: false,
          progress: 0,
          scenesCompleted: 0,
          totalScenes: activeEpisode.scenes.length
        });
        return;
      }
      
      const { taskId } = await response.json();
      
      console.log('Génération en cours...');
      
      // Suivre la progression de la tâche de génération
      const progressInterval = setInterval(async () => {
        try {
          const statusResponse = await fetch(`/api/tasks/${taskId}/status`);
          const statusData = await statusResponse.json();
          
          if (statusData.status === 'completed') {
            clearInterval(progressInterval);
            setGenerationStatus({
              isGenerating: false,
              progress: 100,
              scenesCompleted: activeEpisode.scenes.length,
              totalScenes: activeEpisode.scenes.length
            });
            addNotification('Génération de toutes les scènes terminée avec succès', 'success');
            
            // Déclencher une autosauvegarde
            fetch(`/api/project/${activeProject.id}/autosave`, { 
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                description: 'Autosauvegarde après génération de toutes les scènes',
                trigger: 'generation_complete',
                changes: ['Génération de toutes les scènes']
              })
            });
            
          } else if (statusData.status === 'failed') {
            clearInterval(progressInterval);
            setGenerationStatus({
              isGenerating: false,
              progress: 0,
              scenesCompleted: statusData.completedScenes || 0,
              totalScenes: activeEpisode.scenes.length
            });
            addNotification(`Erreur lors de la génération: ${statusData.error || 'Erreur inconnue'}`, 'error');
          } else {
            // En cours
            setGenerationStatus({
              isGenerating: true,
              progress: statusData.progress || 0,
              scenesCompleted: statusData.completedScenes || 0,
              totalScenes: activeEpisode.scenes.length
            });
          }
        } catch (error) {
          console.error('Erreur lors de la vérification du statut:', error);
        }
      }, 2000); // Vérifier toutes les 2 secondes
      
    } catch (err) {
      console.error('Erreur:', err);
      addNotification('Erreur de communication avec le serveur', 'error');
      setGenerationStatus({
        isGenerating: false,
        progress: 0,
        scenesCompleted: 0,
        totalScenes: activeEpisode.scenes.length
      });
    }
  };

  const handleGenerateVideo = async () => {
    try {
      addNotification('Préparation de la génération de séquence vidéo...', 'info');
      
      // Vérifier que suffisamment de scènes sont générées
      const generatedScenes = activeEpisode.scenes.filter(s => s.generatedImageUrl);
      if (generatedScenes.length < activeEpisode.scenes.length) {
        if (!confirm(`Seulement ${generatedScenes.length} scènes sur ${activeEpisode.scenes.length} ont été générées. Voulez-vous quand même créer une vidéo ?`)) {
          return;
        }
      }
      
      console.log('Tentative de génération de la vidéo...');
      
      // Appel API pour générer la vidéo
      const response = await fetch(`/api/episodes/${activeEpisode.id}/generate-video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          // Options de génération vidéo
          framerate: 24,
          resolution: '1080p',
          transitionType: 'dissolve',
          transitionDuration: 1.0,
          audioEnabled: false
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Erreur backend:', errorData);
        addNotification(errorData.error || 'Erreur lors de la génération vidéo', 'error');
        return;
      }
      
      const { taskId, estimatedTime } = await response.json();
      
      addNotification(`Génération de vidéo en cours (temps estimé: ${estimatedTime}s)`, 'info');
      
    } catch (err) {
      console.error('Erreur:', err);
      addNotification('Erreur de communication avec le serveur', 'error');
    }
  };

  const handleRestoreVersion = () => {
    // Recharger les données après restauration
    window.location.reload();
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Génération de séquence</h1>
          <p className="text-gray-500">
            {activeProject && activeEpisode ? (
              <>
                {activeProject.name} / Épisode {activeEpisode.number}: {activeEpisode.name}
              </>
            ) : (
              'Sélectionnez un projet et un épisode'
            )}
          </p>
        </div>
        
        <div className="flex space-x-3">
          <button
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            onClick={() => setShowTimeline(true)}
          >
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Historique
            </div>
          </button>
          
          <button
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            onClick={() => setShowStyleSelector(!showStyleSelector)}
          >
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"></path>
              </svg>
              {showStyleSelector ? 'Masquer les styles' : 'Styles'}
            </div>
          </button>
          
          <button
            className={`px-4 py-2 rounded-md shadow-sm text-sm font-medium text-white ${
              generationStatus.isGenerating 
                ? 'bg-gray-500 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
            onClick={handleGenerateAll}
            disabled={generationStatus.isGenerating}
          >
            <div className="flex items-center">
              {generationStatus.isGenerating ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </>
              ) : (
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              )}
              Générer toutes les scènes
            </div>
          </button>
          
          <button
            className="px-4 py-2 rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
            onClick={handleGenerateVideo}
          >
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
              Créer la séquence
            </div>
          </button>
        </div>
      </div>
      
      {generationStatus.isGenerating && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-medium text-blue-800">Génération en cours...</h3>
            <span className="text-sm text-blue-800">
              {generationStatus.scenesCompleted} / {generationStatus.totalScenes} scènes
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2.5">
            <div 
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${generationStatus.progress}%` }}
            ></div>
          </div>
          <p className="mt-2 text-xs text-blue-600">
            La génération peut prendre plusieurs minutes selon le nombre de scènes et la complexité.
          </p>
        </div>
      )}
      
      {showStyleSelector && (
        <div className="mb-6">
          <StyleSelector 
            sceneId={null} // null pour le mode global
            currentStyle={currentStyle}
            onStyleChange={handleStyleChange}
          />
        </div>
      )}
      
      <SceneToolbar />
      <LoRATrainer />
      
      <div>
        <SceneGrid />
      </div>
      
      {showTimeline && activeProject && (
        <AutosaveTimeline 
          projectId={activeProject.id}
          onRestore={handleRestoreVersion}
          onClose={() => setShowTimeline(false)}
        />
      )}
    </div>
  );
};

export default SceneGenerationView;