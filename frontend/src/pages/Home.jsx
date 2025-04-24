import React, { useState } from 'react';
import UploadStoryboard from '../components/UploadStoryboard';
import SceneCard from '../components/SceneCard';

export default function Home() {
  const [scenes, setScenes] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [message, setMessage] = useState('');

  const handleUploadSuccess = (data) => {
    setSessionId(data.session_id || null);
    if (data.images && Array.isArray(data.images)) {
      setScenes(data.images.map((img, idx) => ({ image_url: img, title: `Plan ${idx + 1}` })));
      setMessage(data.message || 'Storyboard uploadé avec succès.');
    } else if (data.scenes) {
      setScenes(data.scenes);
      setMessage('Storyboard extrait avec succès.');
    } else {
      setMessage('Aucune scène trouvée.');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h1>Madsea - Extraction Storyboard</h1>
      <UploadStoryboard onUploadSuccess={handleUploadSuccess} />
      {message && <div style={{ margin: '10px 0', color: '#2a8' }}>{message}</div>}
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        {scenes.map((scene, idx) => (
          <SceneCard key={idx} scene={scene} />
        ))}
      </div>
    </div>
  );
}
