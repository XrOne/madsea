import React from 'react';

// Ce composant reproduit l'affichage d'une scène tel que généré par l'ancien script
export default function SceneDisplay({ scene, index }) {
  if (!scene) return null;

  // Classes Tailwind migrées de l'ancien index.html et de la structure générée par JS
  const cardClasses = "scene-card bg-white rounded-lg shadow-lg overflow-hidden m-4 w-full md:w-1/3 lg:w-1/4 flex flex-col";
  const imgClasses = "w-full h-48 object-contain bg-gray-100"; // Ajusté pour 'object-contain'
  const contentClasses = "p-4 flex flex-col flex-grow";
  const titleClasses = "text-lg font-semibold text-gray-800 mb-2 truncate";
  const textClasses = "text-sm text-gray-600 mb-1";
  const strongClasses = "font-medium text-gray-700";

  // Utilisation des mêmes clés que dans le JSON retourné par le backend et utilisé par l'ancien JS
  const title = scene.title || `Plan ${index + 1}`;

  return (
    <div className={cardClasses}>
      {scene.image_url ? (
        <img 
          src={scene.image_url} 
          alt={title} 
          className={imgClasses}
          onError={(e) => { e.target.style.display = 'none'; /* Cache l'image si erreur */ }}
        />
      ) : (
        <div className={`${imgClasses} flex items-center justify-center text-gray-400`}>Image non disponible</div>
      )}
      <div className={contentClasses}>
        <h3 className={titleClasses} title={title}>{title}</h3>
        {/* Reproduction exacte des champs et labels de l'ancien front */}
        <p className={textClasses}>
          <strong className={strongClasses}>Voix Off:</strong> {scene.voix_off || <em>(aucune)</em>}
        </p>
        <p className={textClasses}>
          <strong className={strongClasses}>Indication Plan:</strong> {scene.indication_plan || <em>(aucune)</em>}
        </p>
        <p className={textClasses}>
          <strong className={strongClasses}>Description:</strong> {scene.description || <em>(aucune)</em>}
        </p>
        <p className={textClasses}>
          <strong className={strongClasses}>Type de plan:</strong> {scene.type_plan || <em>(non précisé)</em>}
        </p>
        <p className={`${textClasses} mt-auto pt-2 border-t border-gray-200`}> {/* Notes en bas */} 
          <strong className={strongClasses}>Notes:</strong> <i>{scene.notes || ''}</i>
        </p>
      </div>
    </div>
  );
}
