import React, { useRef, useState } from 'react';

export default function UploadStoryboard({ onUploadSuccess }) {
  const fileInput = useRef();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    setError(null);
    const file = fileInput.current.files[0];
    if (!file) {
      setError('Veuillez sélectionner un fichier PDF ou ZIP.');
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('storyboard_file', file);
    try {
      const res = await fetch('/api/upload_storyboard', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Erreur lors de l\'upload');
      const data = await res.json();
      setLoading(false);
      if (onUploadSuccess) onUploadSuccess(data);
    } catch (err) {
      setLoading(false);
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleUpload} style={{ marginBottom: 20 }}>
      <input type="file" accept=".pdf,.zip,.jpg,.jpeg,.png" ref={fileInput} />
      <button type="submit" disabled={loading}>Uploader</button>
      {loading && <span>Envoi en cours...</span>}
      {error && <span style={{ color: 'red' }}>{error}</span>}
    </form>
  );
}
