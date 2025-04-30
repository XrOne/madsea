import React from 'react';

const MadseaArchitecture = () => {
  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-6 text-center text-gray-800">Architecture Madsea</h2>
      
      <div className="flex flex-col space-y-8">
        {/* User Layer */}
        <div className="bg-blue-100 p-4 rounded-lg border border-blue-200">
          <h3 className="font-semibold mb-2">Interface Utilisateur</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white p-3 rounded shadow-sm">Gestion Projets</div>
            <div className="bg-white p-3 rounded shadow-sm">Import Storyboard</div>
            <div className="bg-white p-3 rounded shadow-sm">Génération Styles</div>
          </div>
        </div>
        
        {/* API Layer */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="border-2 border-gray-400 h-8 border-dashed"></div>
          </div>
          <div className="bg-green-100 p-4 rounded-lg border border-green-200 relative z-10">
            <h3 className="font-semibold mb-2">API Backend</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-white p-2 rounded shadow-sm text-sm">Projets API</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Extraction API</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Génération API</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Export API</div>
            </div>
          </div>
        </div>
        
        {/* Services Layer */}
        <div className="bg-purple-100 p-4 rounded-lg border border-purple-200">
          <h3 className="font-semibold mb-2">Services</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white p-3 rounded shadow-sm">
              <p className="font-medium">Extraction Service</p>
              <p className="text-xs text-gray-500 mt-1">PDF Parser, OCR, Découpage</p>
            </div>
            <div className="bg-white p-3 rounded shadow-sm">
              <p className="font-medium">ComfyUI Service</p>
              <p className="text-xs text-gray-500 mt-1">Workflows, ControlNet, LoRA</p>
            </div>
            <div className="bg-white p-3 rounded shadow-sm">
              <p className="font-medium">Gestion Fichiers</p>
              <p className="text-xs text-gray-500 mt-1">Nomenclature, Versioning</p>
            </div>
          </div>
        </div>
        
        {/* Storage Layer */}
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-yellow-100 p-4 rounded-lg border border-yellow-200">
            <h3 className="font-semibold mb-2">Base de données</h3>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white p-2 rounded shadow-sm text-sm">Projets</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Épisodes</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Scènes</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Générations</div>
            </div>
          </div>
          
          <div className="bg-red-100 p-4 rounded-lg border border-red-200">
            <h3 className="font-semibold mb-2">Stockage Fichiers</h3>
            <div className="grid grid-cols-1 gap-2">
              <div className="bg-white p-2 rounded shadow-sm text-sm">Storyboards sources</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Images extraites</div>
              <div className="bg-white p-2 rounded shadow-sm text-sm">Images générées</div>
            </div>
          </div>
        </div>
        
        {/* External Systems */}
        <div className="bg-gray-200 p-4 rounded-lg border border-gray-300">
          <h3 className="font-semibold mb-2">Systèmes Externes</h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white p-2 rounded shadow-sm text-sm">ComfyUI (local)</div>
            <div className="bg-white p-2 rounded shadow-sm text-sm">API OpenAI</div>
            <div className="bg-white p-2 rounded shadow-sm text-sm">RunwayML</div>
            <div className="bg-white p-2 rounded shadow-sm text-sm">Systèmes de post-prod</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MadseaArchitecture;
