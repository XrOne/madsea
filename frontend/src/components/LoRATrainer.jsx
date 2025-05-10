import React, { useState } from 'react';

function LoRATrainer() {
  const [dataset, setDataset] = useState(null);
  const [loraName, setLoraName] = useState('');
  const [epochs, setEpochs] = useState(10);
  const [learningRate, setLearningRate] = useState('1e-4');
  const [progress, setProgress] = useState('');
  const [logs, setLogs] = useState('');
  const [resultPath, setResultPath] = useState('');
  const [isTraining, setIsTraining] = useState(false);

  const handleFileChange = (e) => {
    setDataset(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!dataset) {
      setProgress('Veuillez sélectionner un zip d’images.');
      return;
    }
    setIsTraining(true);
    setProgress('Entraînement en cours...');
    setLogs('');
    setResultPath('');
    const formData = new FormData();
    formData.append('dataset', dataset);
    formData.append('lora_name', loraName);
    formData.append('epochs', epochs);
    formData.append('learning_rate', learningRate);
    try {
      const response = await fetch('http://localhost:5000/api/lora/train', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setProgress('Entraînement terminé !');
        setLogs(data.logs);
        setResultPath(data.lora_path);
      } else {
        setProgress('Erreur pendant l’entraînement.');
        setLogs(data.error);
      }
    } catch (err) {
      setProgress('Erreur réseau.');
      setLogs(err.message);
    }
    setIsTraining(false);
  };

  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow-md mb-4">
      <h3 className="text-lg font-semibold mb-2">Créer un LoRA personnalisé</h3>
      <form onSubmit={handleSubmit} className="flex flex-col gap-2">
        <label className="font-medium">Archive ZIP d’images d’entraînement :</label>
        <input type="file" accept=".zip" onChange={handleFileChange} />
        <label className="font-medium">Nom du LoRA :</label>
        <input type="text" value={loraName} onChange={e => setLoraName(e.target.value)} placeholder="Nom du modèle" />
        <label className="font-medium">Epochs :</label>
        <input type="number" value={epochs} min={1} max={100} onChange={e => setEpochs(e.target.value)} />
        <label className="font-medium">Learning Rate :</label>
        <input type="text" value={learningRate} onChange={e => setLearningRate(e.target.value)} />
        <button type="submit" disabled={isTraining} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-2">
          {isTraining ? 'Entraînement...' : 'Lancer l’entraînement'}
        </button>
      </form>
      {progress && <p className="mt-2 font-medium">{progress}</p>}
      {logs && <pre className="bg-gray-200 p-2 rounded mt-2 text-xs overflow-x-auto max-h-40">{logs}</pre>}
      {resultPath && (
        <div className="mt-2">
          <p className="text-green-600 font-medium">Modèle généré :</p>
          <a href={`file:///${resultPath}`} target="_blank" rel="noopener noreferrer" className="text-blue-700 underline">{resultPath}</a>
        </div>
      )}
    </div>
  );
}

export default LoRATrainer;
