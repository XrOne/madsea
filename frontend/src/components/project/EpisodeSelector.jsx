import React, { useState, useContext } from 'react';
import { AppContext } from '../../context/AppContext';

const EpisodeSelector = () => {
  const { activeProject, activeEpisode, selectEpisode, addEpisode, addNotification } = useContext(AppContext);
  const [showAddForm, setShowAddForm] = useState(false);
  const [episodeNumber, setEpisodeNumber] = useState('');
  const [episodeName, setEpisodeName] = useState('');

  // Si aucun projet actif, ne rien afficher
  if (!activeProject) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!episodeNumber || !episodeName) {
      addNotification("Veuillez remplir tous les champs", "error");
      return;
    }
    
    try {
      await addEpisode(activeProject.id, {
        number: episodeNumber,
        name: episodeName
      });
      
      // Réinitialiser le formulaire
      setEpisodeNumber('');
      setEpisodeName('');
      setShowAddForm(false);
    } catch (error) {
      console.error("Erreur lors de l'ajout de l'épisode:", error);
    }
  };

  return (
    <div className="mt-4 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="text-sm font-medium text-gray-700">Épisodes</h3>
        <button
          className="text-sm text-blue-600 hover:text-blue-800"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Annuler' : '+ Ajouter un épisode'}
        </button>
      </div>

      {showAddForm && (
        <div className="p-4 bg-blue-50 border-b border-blue-100">
          <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="episode-number" className="block text-xs font-medium text-gray-700 mb-1">
                  Numéro
                </label>
                <input
                  type="text"
                  id="episode-number"
                  value={episodeNumber}
                  onChange={(e) => setEpisodeNumber(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  placeholder="ex: 101"
                />
              </div>
              <div>
                <label htmlFor="episode-name" className="block text-xs font-medium text-gray-700 mb-1">
                  Titre
                </label>
                <input
                  type="text"
                  id="episode-name"
                  value={episodeName}
                  onChange={(e) => setEpisodeName(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  placeholder="Titre de l'épisode"
                />
              </div>
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                Ajouter
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="p-2 max-h-64 overflow-y-auto">
        {activeProject.episodes?.length === 0 ? (
          <div className="text-center py-6 text-gray-500 text-sm">
            <p>Aucun épisode dans ce projet</p>
            <button
              className="mt-2 text-blue-600 hover:text-blue-800"
              onClick={() => setShowAddForm(true)}
            >
              Ajouter le premier épisode
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-2">
            {activeProject.episodes?.map((episode) => (
              <button
                key={episode.id}
                onClick={() => selectEpisode(episode.id)}
                className={`text-left px-4 py-3 rounded-md transition ${
                  activeEpisode?.id === episode.id
                    ? 'bg-blue-100 text-blue-800'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <span className="font-medium">Épisode {episode.number}</span>
                    <p className="text-sm text-gray-600">{episode.name}</p>
                  </div>
                  <div className="text-xs text-gray-500">
                    {episode.scenes?.length || 0} scène(s)
                  </div>
                </div>
                {activeEpisode?.id === episode.id && (
                  <div className="mt-2 pt-2 border-t border-blue-200 text-xs text-blue-600 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Épisode actif
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default EpisodeSelector;