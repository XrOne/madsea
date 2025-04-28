import React, { useState, useEffect, useContext } from 'react';
import { AppContext } from '../../context/AppContext';

const AutosaveTimeline = ({ projectId, onRestore, onClose }) => {
  const { addNotification } = useContext(AppContext);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [comparing, setComparing] = useState(false);
  const [restoring, setRestoring] = useState(false);

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/project/${projectId}/autosaves`);
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des versions');
        }
        const data = await response.json();
        setVersions(data.versions);
        
        // Sélectionner la version la plus récente par défaut
        if (data.versions.length > 0) {
          setSelectedVersion(data.versions[0].id);
        }
      } catch (error) {
        addNotification('Erreur: ' + error.message, 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchVersions();
  }, [projectId, addNotification]);

  const handleCompareVersion = () => {
    if (!selectedVersion) return;
    
    setComparing(true);
    // Logique pour afficher une comparaison
    addNotification('Comparaison en cours...', 'info');
    
    // Simulation - remplacer par l'API réelle
    setTimeout(() => {
      setComparing(false);
      addNotification('Comparaison terminée', 'success');
    }, 1500);
  };

  const handleRestoreVersion = async () => {
    if (!selectedVersion) return;
    
    if (window.confirm('Êtes-vous sûr de vouloir restaurer cette version ? Les modifications non sauvegardées seront perdues.')) {
      try {
        setRestoring(true);
        const response = await fetch(`/api/project/${projectId}/restore/${selectedVersion}`, {
          method: 'POST',
        });
        
        if (!response.ok) {
          throw new Error('Erreur lors de la restauration');
        }
        
        addNotification('Version restaurée avec succès', 'success');
        onRestore(); // Callback pour informer le parent de la restauration
      } catch (error) {
        addNotification('Erreur: ' + error.message, 'error');
      } finally {
        setRestoring(false);
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] flex flex-col">
        <div className="px-6 py-4 bg-blue-600 text-white flex justify-between items-center">
          <h3 className="text-lg font-medium">Historique des versions</h3>
          <button 
            onClick={onClose}
            className="text-white hover:text-blue-100"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div className="p-6 flex-grow overflow-y-auto">
          {loading ? (
            <div className="flex justify-center items-center h-40">
              <svg className="animate-spin -ml-1 mr-3 h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-lg">Chargement des versions...</span>
            </div>
          ) : versions.length === 0 ? (
            <div className="text-center py-10">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune version disponible</h3>
              <p className="mt-1 text-sm text-gray-500">
                Les versions sont créées automatiquement à chaque modification importante.
              </p>
            </div>
          ) : (
            <>
              <p className="mb-4 text-sm text-gray-600">
                Les 10 dernières versions sont conservées automatiquement. Vous pouvez comparer et restaurer n'importe quelle version à tout moment.
              </p>
              
              <div className="relative mb-8 mt-8">
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1 bg-gray-200"></div>
                <div className="relative flex justify-between">
                  {versions.map((version, index) => (
                    <button
                      key={version.id}
                      className={`relative z-10 flex flex-col items-center group focus:outline-none ${
                        selectedVersion === version.id ? '' : 'opacity-70 hover:opacity-100'
                      }`}
                      onClick={() => setSelectedVersion(version.id)}
                    >
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        selectedVersion === version.id
                          ? 'bg-blue-600 border-2 border-blue-600'
                          : 'bg-white border-2 border-gray-400'
                      }`}>
                        <div className={`w-2 h-2 rounded-full ${
                          selectedVersion === version.id ? 'bg-white' : 'bg-gray-400'
                        }`}></div>
                      </div>
                      <div className="mt-2 text-xs font-medium">
                        {new Date(version.timestamp).toLocaleTimeString()}
                      </div>
                      <div className="text-xs">
                        {new Date(version.timestamp).toLocaleDateString()}
                      </div>
                      <div className={`p-2 rounded absolute top-8 left-1/2 transform -translate-x-1/2 bg-blue-100 text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity mt-2 ${
                        index === 0 ? 'left-0 translate-x-0' : 
                        index === versions.length - 1 ? 'left-auto right-0 translate-x-0' : ''
                      }`}>
                        {version.description || `Autosauve #${version.id}`}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
              
              {selectedVersion && (
                <div className="mt-6 bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h4 className="font-medium mb-2">Détails de la version</h4>
                  {versions.find(v => v.id === selectedVersion) && (
                    <>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <p className="text-sm text-gray-600">Date</p>
                          <p className="font-medium">
                            {new Date(versions.find(v => v.id === selectedVersion).timestamp).toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Déclencheur</p>
                          <p className="font-medium">
                            {versions.find(v => v.id === selectedVersion).trigger || 'Automatique'}
                          </p>
                        </div>
                      </div>
                      
                      <div className="mb-4">
                        <p className="text-sm text-gray-600">Modifications</p>
                        <ul className="list-disc list-inside text-sm ml-2">
                          {(versions.find(v => v.id === selectedVersion).changes || []).map((change, index) => (
                            <li key={index}>{change}</li>
                          ))}
                          {(!versions.find(v => v.id === selectedVersion).changes || versions.find(v => v.id === selectedVersion).changes.length === 0) && (
                            <li className="text-gray-500">Aucun détail disponible</li>
                          )}
                        </ul>
                      </div>
                      
                      <div className="flex space-x-3">
                        <button
                          onClick={handleCompareVersion}
                          disabled={comparing}
                          className="px-4 py-2 border border-gray-300 rounded text-sm bg-white hover:bg-gray-50 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {comparing ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Comparaison...
                            </>
                          ) : (
                            <>
                              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
                              </svg>
                              Comparer
                            </>
                          )}
                        </button>
                        <button
                          onClick={handleRestoreVersion}
                          disabled={restoring}
                          className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {restoring ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Restauration...
                            </>
                          ) : (
                            <>
                              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                              </svg>
                              Restaurer cette version
                            </>
                          )}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </div>
        
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex justify-end">
            <button 
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutosaveTimeline;