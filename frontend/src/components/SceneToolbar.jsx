import React, { useState, useContext } from 'react';
import ConfigUploader from './ConfigUploader';
import ImageTester from './ImageTester';
import { AppContext } from '../context/AppContext';

function SceneToolbar() {
  const [isAutoMode, setIsAutoMode] = useState(false);
  const { addNotification } = useContext(AppContext);

  const handleToggleAutoMode = () => {
    const newMode = !isAutoMode;
    setIsAutoMode(newMode);
    
    // Configuration des endpoints pour les deux modes
    const endpoint = newMode 
      ? 'http://localhost:5000/api/puppeteer/process' // Endpoint automatique (MCP Puppeteer)
      : 'http://localhost:5000/api/comfyui/process_plans'; // Endpoint manuel
    
    // Mettre à jour la configuration globale ou le contexte
    localStorage.setItem('madsea_generation_mode', newMode ? 'auto' : 'manual');
    localStorage.setItem('madsea_generation_endpoint', endpoint);
    
    // Notification à l'utilisateur
    addNotification(`Mode ${newMode ? 'Automatique' : 'Manuel'} activé`, 'info');
  };

  return (
    <div className="bg-gray-200 p-4 flex flex-col lg:flex-row justify-between items-center shadow-md">
      <h2 className="text-xl font-bold text-gray-800 mb-2 lg:mb-0">Barre d'outils de scène</h2>
      <div className="flex flex-col lg:flex-row gap-4 items-center">
        <div className="flex items-center">
          <label htmlFor="autoModeToggle" className="mr-2 text-gray-700 font-medium" title="Mode auto génère toutes les scènes en un clic avec MCP Puppeteer">
            Mode Automatique
          </label>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              id="autoModeToggle"
              checked={isAutoMode}
              onChange={handleToggleAutoMode}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-300 rounded-full peer peer-checked:bg-blue-500 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
          </label>
        </div>
        <div className="w-full lg:w-auto">
          <ConfigUploader />
        </div>
        <div className="w-full lg:w-auto">
          <ImageTester />
        </div>
      </div>
    </div>
  );
}

export default SceneToolbar;
