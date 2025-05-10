import React, { useState } from 'react';

function ConfigUploader() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.json')) {
      setFile(selectedFile);
      setUploadStatus('');
    } else {
      setFile(null);
      setUploadStatus('Erreur : Veuillez sélectionner un fichier JSON.');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Erreur : Aucun fichier sélectionné.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/workflow/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus(`Succès : ${result.message}`);
      } else {
        const error = await response.json();
        setUploadStatus(`Erreur : ${error.error}`);
      }
    } catch (error) {
      setUploadStatus(`Erreur réseau : ${error.message}`);
    }
  };

  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow-md mb-4">
      <h3 className="text-lg font-semibold mb-2">Uploader un Workflow JSON</h3>
      <input
        type="file"
        accept=".json"
        onChange={handleFileChange}
        className="mb-2"
      />
      <button
        onClick={handleUpload}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Uploader
      </button>
      {uploadStatus && (
        <p className={`mt-2 ${uploadStatus.includes('Erreur') ? 'text-red-500' : 'text-green-500'}`}>
          {uploadStatus}
        </p>
      )}
    </div>
  );
}

export default ConfigUploader;
