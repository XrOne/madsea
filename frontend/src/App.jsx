import React from 'react';
import { AppContextProvider } from './context/AppContext';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import NotificationCenter from './components/layout/NotificationCenter';
import ProjectDashboard from './components/project/ProjectDashboard';
import ProjectView from './pages/ProjectView';
import SceneGenerationView from './pages/SceneGenerationView';

function App() {
  // État simple pour gérer les vues de l'application
  // Dans une application plus complexe, nous utiliserions un routeur comme react-router
  const [view, setView] = React.useState('dashboard'); // 'dashboard', 'project', 'generation'
  const [viewHistory, setViewHistory] = React.useState([]);

  // Fonction pour changer de vue avec historique de navigation
  const switchView = (newView) => {
    setViewHistory(prev => [...prev, view]);
    setView(newView);
  };

  // Fonction pour revenir à la vue précédente
  const goBack = () => {
    if (viewHistory.length > 0) {
      const previousView = viewHistory[viewHistory.length - 1];
      setViewHistory(prev => prev.slice(0, -1));
      setView(previousView);
    } else {
      // Pas d'historique, retourner au dashboard par défaut
      setView('dashboard');
    }
  };

  // Déterminer le titre de la page en fonction de la vue
  let pageTitle = "Madsea";
  switch (view) {
    case 'dashboard':
      pageTitle = "Projets";
      break;
    case 'project':
      pageTitle = "Détails du projet";
      break;
    case 'generation':
      pageTitle = "Génération de séquence";
      break;
    default:
      pageTitle = "Madsea";
  }

  // Définir la classe CSS pour l'animation de transition
  const getTransitionClass = () => {
    return "animate-fadeIn";
  };

  return (
    <AppContextProvider>
      <div className="flex h-screen bg-gray-100">
        {/* Sidebar */}
        <Sidebar onNavigate={switchView} currentView={view} />
        
        {/* Contenu principal */}
        <div className="flex-1 flex flex-col ml-64">
          {/* Header */}
          <Header title={pageTitle} onBack={goBack} showBackButton={viewHistory.length > 0} />
          
          {/* Contenu de la page */}
          <main className="flex-1 overflow-y-auto pb-10">
            <div className={getTransitionClass()}>
              {view === 'dashboard' && (
                <ProjectDashboard onProjectSelect={() => switchView('project')} />
              )}
              
              {view === 'project' && (
                <ProjectView 
                  onBack={goBack} 
                  onGenerateView={() => switchView('generation')} 
                />
              )}
              
              {view === 'generation' && (
                <SceneGenerationView onBack={goBack} />
              )}
            </div>
          </main>
        </div>
        
        {/* Centre de notifications */}
        <NotificationCenter />
      </div>
    </AppContextProvider>
  );
}

export default App;
