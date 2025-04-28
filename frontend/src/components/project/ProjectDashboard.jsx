import React, { useState, useContext } from 'react';
import { AppContext } from '../../context/AppContext';
import NewProjectModal from '../ui/NewProjectModal';

const ProjectDashboard = () => {
  const { projects, selectProject, addNotification } = useContext(AppContext);
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);
  const [showArchived, setShowArchived] = useState(false);

  // Filtrer les projets actifs/archivés
  const filteredProjects = projects.filter(project => project.archived === showArchived);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Projets</h1>
          <p className="text-gray-500">Gérez vos storyboards et générations</p>
        </div>
        <div className="flex space-x-3">
          <button
            className={`px-4 py-2 rounded border ${
              !showArchived ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-300 text-gray-700'
            }`}
            onClick={() => setShowArchived(false)}
          >
            Actifs
          </button>
          <button
            className={`px-4 py-2 rounded border ${
              showArchived ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-300 text-gray-700'
            }`}
            onClick={() => setShowArchived(true)}
          >
            Archivés
          </button>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            onClick={() => setShowNewProjectModal(true)}
          >
            Nouveau projet
          </button>
        </div>
      </div>

      {filteredProjects.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun projet {showArchived ? 'archivé' : ''}</h3>
          <p className="mt-1 text-sm text-gray-500">
            {showArchived 
              ? 'Vous n\'avez pas encore archivé de projets.' 
              : 'Commencez par créer un nouveau projet.'}
          </p>
          {!showArchived && (
            <div className="mt-6">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                onClick={() => setShowNewProjectModal(true)}
              >
                <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                Créer un projet
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map(project => (
            <div 
              key={project.id}
              className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden hover:shadow-md transition"
            >
              <div 
                className="h-32 bg-gradient-to-r from-blue-500 to-indigo-600 relative"
                onClick={() => selectProject(project.id)}
              >
                {project.thumbnail && (
                  <img
                    src={project.thumbnail}
                    alt={project.name}
                    className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-50"
                  />
                )}
                <div className="absolute inset-0 flex items-center justify-center">
                  <h3 className="text-2xl font-bold text-white">{project.name}</h3>
                </div>
              </div>
              <div className="p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm text-gray-500">
                      {project.episodes?.length || 0} épisode(s) · {project.totalScenes || 0} scène(s)
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Dernière modification: {project.lastModified ? new Date(project.lastModified).toLocaleDateString() : 'Jamais'}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      className="p-2 text-gray-400 hover:text-gray-600"
                      onClick={() => {
                        // Toggler l'archivage
                        const newStatus = !project.archived;
                        // Ici, on ferait un appel API pour mettre à jour le statut
                        addNotification(`Projet ${newStatus ? 'archivé' : 'désarchivé'}`, 'success');
                      }}
                      title={showArchived ? 'Désarchiver' : 'Archiver'}
                    >
                      {showArchived ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path>
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path>
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
                <div className="mt-4 flex justify-between">
                  <button
                    className="px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => {
                      // Afficher l'historique des autosauvegardes
                      addNotification("Affichage de l'historique des versions", "info");
                    }}
                  >
                    Versions
                  </button>
                  <button
                    className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                    onClick={() => selectProject(project.id)}
                  >
                    Ouvrir
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal pour la création de nouveau projet */}
      {showNewProjectModal && (
        <NewProjectModal onClose={() => setShowNewProjectModal(false)} />
      )}
    </div>
  );
};

export default ProjectDashboard;