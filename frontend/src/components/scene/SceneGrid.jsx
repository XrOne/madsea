import React, { useContext } from 'react';
import { AppContext } from '../../context/AppContext';
import SceneDisplay from './SceneDisplay';

const SceneGrid = ({ scenes }) => {
  const { activeProject, activeEpisode, addNotification } = useContext(AppContext);
  
  // Si aucun projet ou épisode sélectionné, afficher un message
  if (!activeProject || !activeEpisode) {
    return (
      <div className="text-center py-10">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path>
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun contenu à afficher</h3>
        <p className="mt-1 text-sm text-gray-500">
          Sélectionnez un projet et un épisode pour voir les scènes.
        </p>
      </div>
    );
  }
  
  // Si l'épisode n'a pas de scènes ou si le tableau de scènes est vide
  if (!activeEpisode.scenes || activeEpisode.scenes.length === 0) {
    return (
      <div className="text-center py-10 bg-gray-50 rounded-lg border border-dashed border-gray-300">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune scène</h3>
        <p className="mt-1 text-sm text-gray-500">
          Cet épisode ne contient pas encore de scènes.
        </p>
        <div className="mt-6">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            onClick={() => {
              // Rediriger vers la section de téléchargement de storyboard
              addNotification("Veuillez télécharger un storyboard pour ajouter des scènes", "info");
            }}
          >
            <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            Télécharger un storyboard
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-medium text-gray-900">Scènes ({activeEpisode.scenes.length})</h2>
        <div className="flex space-x-2">
          <button
            className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded border border-blue-200 hover:bg-blue-100"
            onClick={() => {
              // Logique pour générer toutes les scènes
              addNotification("Génération de toutes les scènes - Fonctionnalité à venir", "info");
            }}
          >
            Générer toutes
          </button>
          <button
            className="px-3 py-1 text-sm bg-gray-50 text-gray-700 rounded border border-gray-200 hover:bg-gray-100"
            onClick={() => {
              // Logique pour exporter les scènes
              addNotification("Export des scènes - Fonctionnalité à venir", "info");
            }}
          >
            Exporter
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {scenes.map((scene) => (
          <SceneDisplay key={scene.id} scene={scene} />
        ))}
      </div>
    </div>
  );
};

export default SceneGrid;