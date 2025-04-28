import React, { useContext } from 'react';
import { AppContext } from '../../context/AppContext';

const Header = () => {
  const { activeProject, activeEpisode, addNotification } = useContext(AppContext);

  return (
    <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
      <div>
        {activeProject ? (
          <div>
            <h1 className="text-xl font-semibold text-gray-800">
              {activeProject.name}
              {activeEpisode && (
                <span className="ml-2 text-gray-500">
                  / Épisode {activeEpisode.number}: {activeEpisode.name}
                </span>
              )}
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {activeProject.episodes?.length || 0} épisode(s) · {activeEpisode?.scenes?.length || 0} scène(s)
            </p>
          </div>
        ) : (
          <h1 className="text-xl font-semibold text-gray-800">Dashboard</h1>
        )}
      </div>

      <div className="flex items-center space-x-3">
        {activeProject && (
          <>
            <button 
              className="px-4 py-2 bg-indigo-50 text-indigo-600 rounded-md hover:bg-indigo-100 flex items-center"
              onClick={() => {
                // Ouvrirait la timeline d'autosauvegarde
                addNotification("Affichage des versions d'autosauvegarde", "info");
              }}
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Historique
            </button>

            <button 
              className="px-4 py-2 bg-green-50 text-green-600 rounded-md hover:bg-green-100 flex items-center"
              onClick={() => addNotification("Export lancé", "success")}
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
              </svg>
              Exporter
            </button>
          </>
        )}

        <div className="relative">
          <button className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300">
            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;