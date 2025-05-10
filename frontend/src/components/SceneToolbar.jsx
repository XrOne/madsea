import React, { useState } from 'react';
import ConfigUploader from './ConfigUploader';
import ImageTester from './ImageTester';

function SceneToolbar() {
  const [isAutoMode, setIsAutoMode] = useState(false);

  const handleToggleAutoMode = () => {
    setIsAutoMode(!isAutoMode);
    // TODO: Intégrer la logique pour basculer entre les endpoints manuels et automatiques
    alert(`Mode ${!isAutoMode ? 'Automatique' : 'Manuel'} activé`);
  };

  return (
    <div className="bg-gray-200 p-4 flex flex-col lg:flex-row justify-between items-center shadow-md">
      <h2 className="text-xl font-bold text-gray-800 mb-2 lg:mb-0">Barre d'outils de scène</h2>
      <div className="flex flex-col lg:flex-row gap-4 items-center">
        <div className="flex items-center">
          <label htmlFor="autoModeToggle" className="mr-2 text-gray-700 font-medium">
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
