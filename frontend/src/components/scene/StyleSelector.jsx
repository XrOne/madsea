import React, { useState, useContext, useEffect } from 'react';
import { AppContext } from '../../context/AppContext';

const StyleSelector = ({ sceneId, currentStyle, onStyleChange }) => {
  const { addNotification } = useContext(AppContext);
  const [styles, setStyles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [customizing, setCustomizing] = useState(false);
  const [newStyleName, setNewStyleName] = useState('');
  const [referenceImages, setReferenceImages] = useState([]);

  // Charger les styles disponibles
  useEffect(() => {
    const fetchStyles = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/styles');
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des styles');
        }
        const data = await response.json();
        setStyles(data.styles);
      } catch (error) {
        addNotification('Erreur: ' + error.message, 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchStyles();
  }, [addNotification]);

  const handleStyleSelect = (styleId) => {
    onStyleChange(styleId);
    addNotification(`Style "${styles.find(s => s.id === styleId)?.name}" sélectionné`, 'info');
  };

  const handleFileSelect = (e) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      if (filesArray.length > 10) {
        addNotification('Vous ne pouvez pas sélectionner plus de 10 images de référence', 'warning');
        return;
      }
      
      // Vérifier que tous les fichiers sont des images
      const invalidFiles = filesArray.filter(file => !file.type.startsWith('image/'));
      if (invalidFiles.length > 0) {
        addNotification('Certains fichiers ne sont pas des images', 'error');
        return;
      }
      
      setReferenceImages(filesArray);
    }
  };

  const handleCreateStyle = async (e) => {
    e.preventDefault();
    
    if (!newStyleName.trim()) {
      addNotification('Veuillez entrer un nom pour le style', 'warning');
      return;
    }
    
    if (referenceImages.length === 0) {
      addNotification('Veuillez sélectionner au moins une image de référence', 'warning');
      return;
    }
    
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('name', newStyleName);
      referenceImages.forEach((image, index) => {
        formData.append(`reference_image_${index}`, image);
      });
      
      const response = await fetch('/api/styles/create', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Erreur lors de la création du style');
      }
      
      const data = await response.json();
      setStyles(prevStyles => [...prevStyles, data.style]);
      addNotification(`Style "${data.style.name}" créé avec succès`, 'success');
      
      // Réinitialiser le formulaire
      setNewStyleName('');
      setReferenceImages([]);
      setCustomizing(false);
      
      // Sélectionner automatiquement le nouveau style
      onStyleChange(data.style.id);
      
    } catch (error) {
      addNotification('Erreur: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="text-sm font-medium text-gray-700">Styles visuels</h3>
        <button
          className="text-sm text-blue-600 hover:text-blue-800"
          onClick={() => setCustomizing(!customizing)}
        >
          {customizing ? 'Annuler' : '+ Créer un style'}
        </button>
      </div>
      
      {customizing ? (
        <div className="p-4">
          <form onSubmit={handleCreateStyle}>
            <div className="mb-4">
              <label htmlFor="style-name" className="block text-xs font-medium text-gray-700 mb-1">
                Nom du style
              </label>
              <input
                type="text"
                id="style-name"
                value={newStyleName}
                onChange={(e) => setNewStyleName(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                placeholder="ex: Aquarelle, Noir & Blanc, etc."
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="reference-images" className="block text-xs font-medium text-gray-700 mb-1">
                Images de référence (max. 10)
              </label>
              <input
                type="file"
                id="reference-images"
                multiple
                accept="image/*"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <p className="mt-1 text-xs text-gray-500">
                Ces images serviront de référence pour l'entraînement du style.
              </p>
              
              {referenceImages.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {referenceImages.map((image, index) => (
                    <div key={index} className="relative w-16 h-16 bg-gray-100 rounded overflow-hidden">
                      <img
                        src={URL.createObjectURL(image)}
                        alt={`Référence ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                      <button
                        type="button"
                        className="absolute top-0 right-0 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center"
                        onClick={() => setReferenceImages(prev => prev.filter((_, i) => i !== index))}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                disabled={loading}
              >
                {loading ? 'Création...' : 'Créer le style'}
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="p-2 max-h-60 overflow-y-auto">
          {loading ? (
            <div className="flex justify-center items-center py-4">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Chargement des styles...</span>
            </div>
          ) : styles.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <p>Aucun style disponible</p>
              <button
                className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                onClick={() => setCustomizing(true)}
              >
                Créer votre premier style
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {styles.map((style) => (
                <button
                  key={style.id}
                  onClick={() => handleStyleSelect(style.id)}
                  className={`relative text-left p-2 rounded-md transition ${
                    currentStyle === style.id
                      ? 'bg-blue-100 border border-blue-300'
                      : 'hover:bg-gray-100 border border-transparent'
                  }`}
                >
                  {style.thumbnailUrl ? (
                    <div className="w-full h-24 rounded overflow-hidden mb-1">
                      <img
                        src={style.thumbnailUrl}
                        alt={style.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ) : (
                    <div className="w-full h-24 bg-gray-200 rounded flex items-center justify-center mb-1">
                      <span className="text-gray-400">{style.name}</span>
                    </div>
                  )}
                  <div className="font-medium text-sm">{style.name}</div>
                  <div className="text-xs text-gray-500">
                    {style.isCustom ? 'Personnalisé' : 'Intégré'}
                  </div>
                  
                  {currentStyle === style.id && (
                    <div className="absolute top-1 right-1 bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StyleSelector;