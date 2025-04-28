import React, { useContext, useState, useEffect } from 'react';
import { AppContext } from '../context/AppContext';
import EpisodeSelector from '../components/project/EpisodeSelector';
import UploadStoryboard from '../components/project/UploadStoryboard';
import SceneGrid from '../components/scene/SceneGrid';

const ProjectView = () => {
  const { activeProject, activeEpisode, scenes: contextScenes } = useContext(AppContext);
  const [currentScenes, setCurrentScenes] = useState([]);

  useEffect(() => {
    if (activeProject && activeEpisode) {
      const scenesForEpisode = contextScenes?.filter(scene => scene.episodeId === activeEpisode.id) || [];
      setCurrentScenes(scenesForEpisode);
    } else {
      setCurrentScenes([]); 
    }
  }, [activeProject, activeEpisode, contextScenes]); 

  const handleUploadSuccess = (newlyExtractedScenes) => {
    console.log('Upload successful, received scenes:', newlyExtractedScenes);
    setCurrentScenes(prevScenes => [...prevScenes, ...newlyExtractedScenes]);
  };

  if (!activeProject) {
    return (
      <div className="flex items-center justify-center h-full p-6">
        <div className="text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun projet sélectionné</h3>
          <p className="mt-1 text-sm text-gray-500">
            Veuillez sélectionner un projet existant ou en créer un nouveau.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-6 p-6">
      {/* Colonne de gauche - Informations du projet */}
      <div className="col-span-1">
        <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <h3 className="text-sm font-medium text-gray-700">Informations du projet</h3>
          </div>
          <div className="p-4">
            <h2 className="font-bold text-xl mb-1">{activeProject.name}</h2>
            <p className="text-gray-600 text-sm mb-3">
              Créé le: {activeProject.createdAt ? new Date(activeProject.createdAt).toLocaleDateString() : 'Date inconnue'}
            </p>
            
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{activeProject.episodes?.length || 0}</div>
                <div className="text-xs text-gray-600">Épisodes</div>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{activeProject.totalScenes || 0}</div>
                <div className="text-xs text-gray-600">Scènes</div>
              </div>
            </div>
            
            <div className="flex flex-col space-y-2">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                Nouvel épisode
              </button>
              <button className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center justify-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                </svg>
                Exporter le projet
              </button>
            </div>
          </div>
        </div>
        
        {/* Sélecteur d'épisodes */}
        <EpisodeSelector />
      </div>
      
      {/* Colonne centrale et droite - Upload et Scènes */}
      <div className="col-span-2">
        {/* Passer les props nécessaires à UploadStoryboard */}
        <UploadStoryboard 
          projectId={activeProject?.id} 
          episodeId={activeEpisode?.id} 
          onUploadSuccess={handleUploadSuccess} 
        />
        <div className="mt-6">
          {/* Passer les scènes locales à SceneGrid */}
          <SceneGrid scenes={currentScenes} />
        </div>
      </div>
    </div>
  );
};

export default ProjectView;