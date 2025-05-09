import React from 'react';

const PromptStructure = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-6 text-center text-gray-800">Structure des prompts pour la génération d'images</h2>
      
      <div className="space-y-8">
        <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
          <h3 className="font-bold text-blue-700 mb-2">Prompt complet</h3>
          <div className="bg-white p-3 rounded shadow-sm text-sm font-mono">
            <span className="text-purple-600">{"{"}</span>
            <span className="text-green-600">description du lieu</span>
            <span className="text-purple-600">{"}"}</span> + 
            <span className="text-purple-600">{"{"}</span>
            <span className="text-blue-600">indications visuelles</span>
            <span className="text-purple-600">{"}"}</span> + 
            <span className="text-purple-600">{"{"}</span>
            <span className="text-red-600">style visuel</span>
            <span className="text-purple-600">{"}"}</span> + 
            <span className="text-purple-600">{"{"}</span>
            <span className="text-orange-600">qualificateurs techniques</span>
            <span className="text-purple-600">{"}"}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-green-200 rounded-lg p-4 bg-green-50">
            <h3 className="font-bold text-green-700 mb-2">Description du lieu</h3>
            <p className="text-sm text-gray-700 mb-3">Extrait du texte de la scène (location)</p>
            <div className="bg-white p-2 rounded shadow-sm text-sm">
              <ul className="space-y-1">
                <li><span className="font-mono">INT. Laboratoire - Nuit</span> → <span className="font-mono text-green-600">Intérieur d'un laboratoire scientifique de nuit</span></li>
                <li><span className="font-mono">EXT. Base lunaire</span> → <span className="font-mono text-green-600">Extérieur d'une base lunaire, surface lunaire grise</span></li>
              </ul>
            </div>
          </div>
          
          <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
            <h3 className="font-bold text-blue-700 mb-2">Indications visuelles</h3>
            <p className="text-sm text-gray-700 mb-3">Éléments importants mentionnés dans l'indication</p>
            <div className="bg-white p-2 rounded shadow-sm text-sm">
              <ul className="space-y-1">
                <li><span className="font-mono">Pierre regarde le ciel étoilé</span> → <span className="font-mono text-blue-600">personnage regardant vers le haut, ciel étoilé visible</span></li>
                <li><span className="font-mono">Vue par-dessus l'épaule</span> → <span className="font-mono text-blue-600">vue en plongée, cadrage par-dessus l'épaule</span></li>
              </ul>
            </div>
          </div>
          
          <div className="border border-red-200 rounded-lg p-4 bg-red-50">
            <h3 className="font-bold text-red-700 mb-2">Style visuel</h3>
            <p className="text-sm text-gray-700 mb-3">Dépend du style sélectionné</p>
            <div className="bg-white p-2 rounded shadow-sm text-sm">
              <ul className="space-y-1">
                <li><span className="font-bold">Ombre chinoise:</span> <span className="font-mono text-red-600">silhouette en contre-jour, contraste élevé, style théâtre d'ombres, noir sur fond coloré</span></li>
                <li><span className="font-bold">Laboratoire:</span> <span className="font-mono text-red-600">rendu photoréaliste, éclairage néon doux, ambiance scientifique</span></li>
                <li><span className="font-bold">Expressionniste:</span> <span className="font-mono text-red-600">contrastes intenses, angles dramatiques, ombres prononcées</span></li>
              </ul>
            </div>
          </div>
          
          <div className="border border-orange-200 rounded-lg p-4 bg-orange-50">
            <h3 className="font-bold text-orange-700 mb-2">Qualificateurs techniques</h3>
            <p className="text-sm text-gray-700 mb-3">Standards de qualité et directives techniques</p>
            <div className="bg-white p-2 rounded shadow-sm text-sm">
              <ul className="space-y-1">
                <li><span className="font-mono text-orange-600">éclairage cinématographique, rendu professionnel, haute qualité</span></li>
                <li><span className="font-mono text-orange-600">rim light, global illumination, ombres portées douces</span></li>
                <li><span className="font-mono text-orange-600">bokeh cinématographique, profondeur de champ réduite</span></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h3 className="font-bold text-gray-700 mb-2">Exemples complets</h3>
          <div className="space-y-3">
            <div className="bg-white p-3 rounded shadow-sm text-sm">
              <h4 className="font-semibold mb-1 text-gray-800">Style Ombre Chinoise:</h4>
              <p className="font-mono text-xs break-words">Intérieur d'un laboratoire scientifique de nuit, personnage debout près d'une machine, silhouette en contre-jour, contraste élevé, style théâtre d'ombres, noir sur fond bleu, minimaliste, éclairage dramatique, qualité cinématographique, rendu épuré</p>
            </div>
            
            <div className="bg-white p-3 rounded shadow-sm text-sm">
              <h4 className="font-semibold mb-1 text-gray-800">Style Laboratoire:</h4>
              <p className="font-mono text-xs break-words">Intérieur d'un laboratoire scientifique de nuit, personnage debout près d'une machine d'analyse, écrans lumineux, rendu photoréaliste, éclairage néon doux, ambiance scientifique, détails techniques, reflets sur les surfaces métalliques, rim light, global illumination, haute qualité, style cinéma</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptStructure;
