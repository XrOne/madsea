import React, { useContext, useEffect } from 'react';
import { AppContext } from '../context/AppContext';
import UploadStoryboard from '../components/project/UploadStoryboard';
import SceneGrid from '../components/scene/SceneGrid';
import EpisodeSelector from '../components/project/EpisodeSelector';

const Home = () => {
  const { fetchProjects, activeProject, activeEpisode } = useContext(AppContext);

  // Charger les projets au chargement du composant
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Colonne de gauche - Sélection d'épisode */}
        <div className="lg:col-span-1">
          <EpisodeSelector />
        </div>
        
        {/* Colonnes de droite - Upload et visualisation */}
        <div className="lg:col-span-3">
          {activeProject && activeEpisode ? (
            <>
              <div className="mb-6">
                <UploadStoryboard />
              </div>
              <div>
                <SceneGrid />
              </div>
            </>
          ) : (
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-blue-700">
                    Veuillez sélectionner un projet et un épisode dans le menu latéral pour commencer. Si vous n'avez pas encore de projet, vous pouvez en créer un nouveau.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;