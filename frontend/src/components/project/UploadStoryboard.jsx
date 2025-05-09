import React, { useState, useContext, useRef } from 'react';
import { AppContext } from '../../context/AppContext';

const UploadStoryboard = () => {
  const { activeProject, activeEpisode, addNotification, updateProjectLastModified } = useContext(AppContext);
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  // Options pour l'extraction
  const [options, setOptions] = useState({
    detectPanels: true,
    extractText: true,
    enhanceQuality: false,
    extractCaptions: true
  });

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      // Vérifier le type de fichier
      if (selectedFile.type === 'application/pdf' || selectedFile.type.startsWith('image/')) {
        setFile(selectedFile);
      } else {
        addNotification('Format de fichier non supporté. Veuillez utiliser un PDF ou une image.', 'error');
        fileInputRef.current.value = '';
      }
    }
  };

  const handleOptionChange = (e) => {
    const { name, checked } = e.target;
    setOptions(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      addNotification('Veuillez sélectionner un fichier à télécharger', 'warning');
      return;
    }
    
    if (!activeProject || !activeEpisode) {
      addNotification('Veuillez sélectionner un projet et un épisode', 'error');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', activeProject.id);
    formData.append('episode_id', activeEpisode.id);
    formData.append('options', JSON.stringify(options));
    
    try {
      setIsUploading(true);
      setProgress(0);
      
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentage = Math.round((event.loaded * 100) / event.total);
          setProgress(percentage);
        }
      });
      
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          setIsUploading(false);
          
          if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            addNotification('Storyboard téléchargé avec succès', 'success');
            // Met à jour le timestamp de dernière modification du projet
            updateProjectLastModified(activeProject.id);
            // Réinitialiser le formulaire
            setFile(null);
            fileInputRef.current.value = '';
            
            // Si la réponse contient des scènes, vous pourriez vouloir les traiter ici
            console.log('Scènes extraites:', response.scenes);
          } else {
            addNotification('Erreur lors du téléchargement: ' + (xhr.responseText || 'Erreur réseau'), 'error');
          }
        }
      };
      
      xhr.open('POST', '/api/upload_storyboard', true);
      xhr.send(formData);
      
    } catch (error) {
      setIsUploading(false);
      addNotification('Erreur lors du téléchargement: ' + error.message, 'error');
    }
  };

  if (!activeProject || !activeEpisode) {
    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              Veuillez sélectionner un projet et un épisode avant de télécharger un storyboard.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="text-sm font-medium text-gray-700">Ajouter un storyboard</h3>
      </div>
      
      <div className="p-4">
        <form onSubmit={handleUpload}>
          <div className="mb-4">
            <div className="flex items-center justify-center w-full">
              <label
                htmlFor="dropzone-file"
                className={`flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer 
                ${file ? 'border-green-300 bg-green-50' : 'border-gray-300 bg-gray-50'} hover:bg-gray-100`}
              >
                {!file ? (
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                    <p className="mb-2 text-sm text-gray-500">
                      <span className="font-semibold">Cliquez pour uploader</span> ou glissez-déposez
                    </p>
                    <p className="text-xs text-gray-500">PDF ou images (PNG, JPG)</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center">
                    <svg className="w-10 h-10 mb-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <button 
                      type="button"
                      className="mt-3 text-xs text-red-600 hover:text-red-800"
                      onClick={() => {
                        setFile(null);
                        fileInputRef.current.value = '';
                      }}
                    >
                      Retirer le fichier
                    </button>
                  </div>
                )}
                <input
                  id="dropzone-file"
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".pdf,image/*"
                  onChange={handleFileChange}
                  disabled={isUploading}
                />
              </label>
            </div>
          </div>
          
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Options d'extraction</h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center">
                <input
                  id="detect-panels"
                  name="detectPanels"
                  type="checkbox"
                  checked={options.detectPanels}
                  onChange={handleOptionChange}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  disabled={isUploading}
                />
                <label htmlFor="detect-panels" className="ml-2 block text-sm text-gray-700">
                  Détecter les panneaux
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="extract-text"
                  name="extractText"
                  type="checkbox"
                  checked={options.extractText}
                  onChange={handleOptionChange}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  disabled={isUploading}
                />
                <label htmlFor="extract-text" className="ml-2 block text-sm text-gray-700">
                  Extraire le texte (OCR)
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="enhance-quality"
                  name="enhanceQuality"
                  type="checkbox"
                  checked={options.enhanceQuality}
                  onChange={handleOptionChange}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  disabled={isUploading}
                />
                <label htmlFor="enhance-quality" className="ml-2 block text-sm text-gray-700">
                  Améliorer la qualité
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="extract-captions"
                  name="extractCaptions"
                  type="checkbox"
                  checked={options.extractCaptions}
                  onChange={handleOptionChange}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  disabled={isUploading}
                />
                <label htmlFor="extract-captions" className="ml-2 block text-sm text-gray-700">
                  Extraire les légendes
                </label>
              </div>
            </div>
          </div>
          
          {isUploading && (
            <div className="mb-4">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-medium text-blue-700">Téléchargement</span>
                <span className="text-xs text-blue-700">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">Le téléchargement peut prendre un moment selon la taille du fichier. Ne fermez pas cette fenêtre.</p>
            </div>
          )}
          
          <div className="flex justify-end">
            <button
              type="submit"
              className={`px-4 py-2 rounded text-sm font-medium ${
                isUploading 
                  ? 'bg-gray-300 text-gray-700 cursor-not-allowed' 
                  : file 
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
              disabled={isUploading || !file}
            >
              {isUploading ? 'Téléchargement...' : 'Télécharger et extraire'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadStoryboard;