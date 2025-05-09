import React, { useState, useContext } from 'react';
import { AppContext } from '../../context/AppContext';

const NewProjectModal = ({ onClose }) => {
  const { createProject, addNotification } = useContext(AppContext);
  const [projectName, setProjectName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!projectName.trim()) {
      addNotification('Veuillez entrer un nom de projet', 'warning');
      return;
    }
    
    try {
      setIsCreating(true);
      await createProject({ name: projectName });
      addNotification('Projet créé avec succès', 'success');
      onClose();
    } catch (error) {
      addNotification('Erreur lors de la création du projet: ' + error.message, 'error');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md overflow-hidden">
        <div className="px-6 py-4 bg-blue-600 text-white flex justify-between items-center">
          <h3 className="text-lg font-medium">Nouveau projet</h3>
          <button 
            onClick={onClose}
            className="text-white hover:text-blue-100"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-4">
            <label htmlFor="project-name" className="block text-sm font-medium text-gray-700 mb-1">
              Nom du projet
            </label>
            <input
              type="text"
              id="project-name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Ex: Mon super storyboard"
              autoFocus
            />
          </div>

          <p className="text-sm text-gray-500 mb-4">
            Vous pourrez ajouter des épisodes et télécharger des storyboards après la création du projet.
          </p>
          
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              disabled={isCreating}
            >
              {isCreating ? 'Création...' : 'Créer le projet'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewProjectModal;