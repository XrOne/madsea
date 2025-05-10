import React, { useState } from 'react';

function ImageTester() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [resultImage, setResultImage] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && (selectedFile.name.endsWith('.png') || selectedFile.name.endsWith('.jpg') || selectedFile.name.endsWith('.jpeg'))) {
      setFile(selectedFile);
      setUploadStatus('');
    } else {
      setFile(null);
      setUploadStatus('Erreur : Veuillez sélectionner un fichier PNG ou JPG.');
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
      const response = await fetch('http://localhost:5000/api/puppeteer/process-image', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus(`Succès : ${result.message}`);
        if (result.result && result.result.output_path) {
          setResultImage(result.result.output_path);
        }
      } else {
        const error = await response.json();
        setUploadStatus(`Erreur : ${error.message}`);
      }
    } catch (error) {
      setUploadStatus(`Erreur réseau : ${error.message}`);
    }
  };

  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow-md mb-4">
      <h3 className="text-lg font-semibold mb-2">Uploader une Image de Test</h3>
      <input
        type="file"
        accept=".png,.jpg,.jpeg"
        onChange={handleFileChange}
        className="mb-2"
      />
      <button
        onClick={handleUpload}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Tester
      </button>
      {uploadStatus && (
        <p className={`mt-2 ${uploadStatus.includes('Erreur') ? 'text-red-500' : 'text-green-500'}`}>
          {uploadStatus}
        </p>
      )}
      {resultImage && (
        <div className="mt-4">
          <h4 className="text-md font-medium">Résultat :</h4>
          <img src={`file:///${resultImage}`} alt="Image générée" className="max-w-xs mt-2 border rounded" />
          <p className="text-sm text-gray-600">Chemin : {resultImage}</p>
        </div>
      )}
    </div>
  );
}

export default ImageTester;
