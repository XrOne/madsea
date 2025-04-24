import React from 'react';

export default function SceneCard({ scene }) {
  if (!scene) return null;
  return (
    <div style={{ border: '1px solid #ccc', borderRadius: 8, margin: 10, padding: 16, maxWidth: 400 }}>
      {scene.image_url && (
        <img src={scene.image_url} alt={scene.title} style={{ width: '100%', maxHeight: 220, objectFit: 'contain', borderRadius: 6 }} />
      )}
      <h3>{scene.title}</h3>
      <div><b>VOIX OFF</b><br/>{scene.voix_off || <em>(aucune)</em>}</div>
      <div style={{ margin: '8px 0', color: '#c96', fontWeight: 'bold' }}>{scene.indication_plan}</div>
      <div><b>Description</b><br/>{scene.description || <em>(aucune)</em>}</div>
      <div><b>Type de plan</b>: {scene.type_plan || <em>(non précisé)</em>}</div>
      <div><b>Notes</b>: <i>{scene.notes || ''}</i></div>
    </div>
  );
}
