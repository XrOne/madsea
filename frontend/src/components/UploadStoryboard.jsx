import React, { useRef, useState } from 'react';

// Ce composant reproduit le formulaire d'upload de l'ancien index.html
export default function StoryboardUploader({ onUploadSuccess, onError }) {
  const fileInput = useRef();
  const [loading, setLoading] = useState(false);
  const [error, setErrorState] = useState(null);
  const [fileName, setFileName] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFileName(file ? file.name : '');
    setErrorState(null); // Reset error on new file selection
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setErrorState(null);
    const file = fileInput.current.files[0];

    if (!file) {
      const msg = 'Veuillez sélectionner un fichier (PDF, ZIP, images).';
      setErrorState(msg);
      if (onError) onError(msg);
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('storyboard_file', file);

    // Reproduit l'appel fetch de 003-prototype-ui-projects.js
    try {
      const res = await fetch('/api/upload_storyboard', {
        method: 'POST',
        body: formData,
      });

      const responseText = await res.text(); // Lire comme texte d'abord pour debug
      let data;
      try {
        data = JSON.parse(responseText); // Essayer de parser en JSON
      } catch (jsonError) {
        console.error("Réponse non-JSON reçue:", responseText);
        throw new Error(`Le serveur a retourné une réponse invalide (${res.status}).`);
      }

      if (!res.ok) {
        throw new Error(data.error || `Erreur serveur (${res.status})`);
      }

      setLoading(false);
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }

    } catch (err) {
      console.error("Erreur fetch:", err);
      setLoading(false);
      const errorMsg = err.message || 'Une erreur inconnue est survenue lors de l\'upload.';
      setErrorState(errorMsg);
      if (onError) onError(errorMsg);
    }
  };

  // Utilisation des classes Tailwind vues dans l'ancien index.html
  return (
    <form onSubmit={handleUpload} className="mb-8 p-6 bg-white rounded-lg shadow-md">
      <label htmlFor="storyboard-upload" className="block text-sm font-medium text-gray-700 mb-2">
        Uploader un Storyboard (PDF, ZIP, Images)
      </label>
      <div className="flex items-center space-x-4">
        <label className="cursor-pointer bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-md transition duration-150 ease-in-out">
          <span>Choisir un fichier</span>
          <input 
            id="storyboard-upload"
            type="file" 
            accept=".pdf,.zip,.jpg,.jpeg,.png" 
            ref={fileInput}
            onChange={handleFileChange}
            className="sr-only" // Cache l'input natif
          />
        </label>
        <span className="text-gray-500 text-sm truncate max-w-xs" title={fileName}>{fileName || 'Aucun fichier choisi'}</span>
        <button 
          type="submit" 
          disabled={loading}
          className={`py-2 px-6 rounded-md font-semibold text-white transition duration-150 ease-in-out ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}`}
        >
          {loading ? (
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : 'Uploader'}
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </form>
  );
}
