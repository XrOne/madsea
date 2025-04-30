import React from 'react';

const MadseaWorkflow = () => {
  const ArrowRight = () => (
    <div className="flex items-center justify-center">
      <svg width="30" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </div>
  );

  const workflowSteps = [
    {
      title: "Import",
      icon: "📥",
      description: "Téléchargement et extraction de storyboard",
      subSteps: [
        "Upload PDF/Images",
        "Découpage auto des cases",
        "Extraction texte (OCR)",
        "Indexation des plans"
      ]
    },
    {
      title: "Sélection",
      icon: "✏️",
      description: "Organisation des plans et métadonnées",
      subSteps: [
        "Filtrage par séquence",
        "Sélection par lots",
        "Édition des métadonnées",
        "Configuration batch"
      ]
    },
    {
      title: "Style",
      icon: "🎨",
      description: "Choix des paramètres visuels",
      subSteps: [
        "Style Ombres chinoises",
        "Style Laboratoire",
        "Style Expressionniste",
        "LoRA personnalisé"
      ]
    },
    {
      title: "Génération",
      icon: "⚙️",
      description: "Traitement via ComfyUI",
      subSteps: [
        "Application ControlNet",
        "Prompting automatique",
        "Inférence image",
        "Rendu par lot"
      ]
    },
    {
      title: "Validation",
      icon: "✅",
      description: "Vérification et itérations",
      subSteps: [
        "Revue des résultats",
        "Sélection des meilleures versions",
        "Ajustements si nécessaire",
        "Re-génération ciblée"
      ]
    },
    {
      title: "Export",
      icon: "📤",
      description: "Finalisation et livraison",
      subSteps: [
        "Format 16/9",
        "PNG haute qualité",
        "Métadonnées et nomenclature",
        "Transfert post-production"
      ]
    }
  ];

  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-6 text-center text-gray-800">Workflow Madsea</h2>
      
      <div className="flex flex-col space-y-6">
        <div className="flex flex-wrap justify-center items-start gap-2">
          {workflowSteps.map((step, index) => (
            <React.Fragment key={index}>
              <div className="bg-white rounded-lg shadow-md p-4 w-56">
                <div className="flex items-center mb-2">
                  <span className="text-2xl mr-2">{step.icon}</span>
                  <h3 className="font-bold text-lg">{step.title}</h3>
                </div>
                <p className="text-sm text-gray-600 mb-3">{step.description}</p>
                <ul className="text-xs space-y-1">
                  {step.subSteps.map((subStep, subIndex) => (
                    <li key={subIndex} className="flex items-center">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 flex-shrink-0"></span>
                      {subStep}
                    </li>
                  ))}
                </ul>
              </div>
              
              {index < workflowSteps.length - 1 && (
                <div className="flex items-center text-gray-400 self-center">
                  <ArrowRight />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
        
        <div className="mt-8 bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="font-semibold mb-2 text-center">Intégration ComfyUI</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-3 rounded shadow-sm">
              <h4 className="font-medium text-sm text-center mb-2">ENTRÉES</h4>
              <ul className="text-xs space-y-1">
                <li>• Images source</li>
                <li>• Guide ControlNet</li>
                <li>• Choix de style</li>
                <li>• Prompts texte</li>
              </ul>
            </div>
            <div className="bg-white p-3 rounded shadow-sm">
              <h4 className="font-medium text-sm text-center mb-2">TRAITEMENT</h4>
              <ul className="text-xs space-y-1">
                <li>• Workflows personnalisés</li>
                <li>• Modèles SD (RealVisXL, etc.)</li>
                <li>• LoRA style + Adapters</li>
                <li>• ControlNets multiples</li>
              </ul>
            </div>
            <div className="bg-white p-3 rounded shadow-sm">
              <h4 className="font-medium text-sm text-center mb-2">SORTIES</h4>
              <ul className="text-xs space-y-1">
                <li>• Images stylisées</li>
                <li>• Format 16/9</li>
                <li>• Nomenclature standard</li>
                <li>• Métadonnées intégrées</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MadseaWorkflow;
