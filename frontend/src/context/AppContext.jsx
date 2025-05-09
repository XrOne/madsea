import React, { createContext, useState, useEffect } from 'react';

// Création du contexte
export const AppContext = createContext();

// Provider du contexte qui enveloppe l'application
export const AppContextProvider = ({ children }) => {
  // État global de l'application
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [activeEpisode, setActiveEpisode] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [selectedScenes, setSelectedScenes] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState({
    upload: false,
    generate: false,
    export: false
  });

  // Récupérer les projets au chargement de l'application
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch('/api/projects');
        if (response.ok) {
          const data = await response.json();
          setProjects(data.projects || []);
        }
      } catch (error) {
        console.error('Erreur lors du chargement des projets:', error);
        addNotification('Impossible de charger les projets', 'error');
      }
    };

    fetchProjects();
  }, []);

  // Sélectionner un projet
  const selectProject = (projectId) => {
    const project = projects.find(p => p.id === projectId);
    setActiveProject(project || null);
    setActiveEpisode(null);
    
    // Si le projet a des épisodes, charger les scènes du premier épisode
    if (project && project.episodes && project.episodes.length > 0) {
      selectEpisode(project.episodes[0].id);
    } else {
      setScenes([]);
    }
  };

  // Sélectionner un épisode
  const selectEpisode = (episodeId) => {
    if (!activeProject) return;
    
    const episode = activeProject.episodes.find(e => e.id === episodeId);
    setActiveEpisode(episode || null);
    
    // Charger les scènes de cet épisode
    if (episode) {
      setScenes(episode.scenes || []);
    } else {
      setScenes([]);
    }
  };

  // Créer un nouveau projet
  const createProject = async (projectData) => {
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(projectData)
      });
      
      if (response.ok) {
        const newProject = await response.json();
        setProjects([...projects, newProject]);
        addNotification(`Projet "${newProject.name}" créé avec succès`, 'success');
        return newProject;
      } else {
        throw new Error('Erreur serveur');
      }
    } catch (error) {
      console.error('Erreur lors de la création du projet:', error);
      addNotification('Impossible de créer le projet', 'error');
      return null;
    }
  };

  // Ajouter un épisode
  const addEpisode = async (projectId, episodeData) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/episodes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(episodeData)
      });
      
      if (response.ok) {
        const newEpisode = await response.json();
        const updatedProjects = projects.map(p => {
          if (p.id === projectId) {
            return {
              ...p,
              episodes: [...p.episodes, newEpisode]
            };
          }
          return p;
        });
        
        setProjects(updatedProjects);
        
        // Mettre à jour le projet actif si c'est celui-ci
        if (activeProject && activeProject.id === projectId) {
          setActiveProject({
            ...activeProject,
            episodes: [...activeProject.episodes, newEpisode]
          });
        }
        
        addNotification(`Épisode "${newEpisode.name}" ajouté avec succès`, 'success');
        return newEpisode;
      } else {
        throw new Error('Erreur serveur');
      }
    } catch (error) {
      console.error('Erreur lors de l\'ajout de l\'épisode:', error);
      addNotification('Impossible d\'ajouter l\'épisode', 'error');
      return null;
    }
  };

  // Upload d'un storyboard
  const uploadStoryboard = async (file) => {
    setIsLoading({ ...isLoading, upload: true });
    
    try {
      const formData = new FormData();
      formData.append('storyboard_file', file);
      
      const response = await fetch('/api/upload_storyboard', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        setScenes(data.scenes || []);
        
        // Si nous avons un épisode actif, mettre à jour ses scènes
        if (activeEpisode && activeProject) {
          // Mettre à jour l'épisode actif
          const updatedEpisode = { ...activeEpisode, scenes: data.scenes || [] };
          
          // Mettre à jour le projet actif
          const updatedProject = {
            ...activeProject,
            episodes: activeProject.episodes.map(ep => 
              ep.id === updatedEpisode.id ? updatedEpisode : ep
            )
          };
          
          setActiveEpisode(updatedEpisode);
          setActiveProject(updatedProject);
          
          // Mettre à jour la liste de tous les projets
          setProjects(projects.map(p => 
            p.id === updatedProject.id ? updatedProject : p
          ));
        }
        
        addNotification('Storyboard extrait avec succès', 'success');
        setIsLoading({ ...isLoading, upload: false });
        return data;
      } else {
        throw new Error('Erreur serveur');
      }
    } catch (error) {
      console.error('Erreur lors de l\'upload du storyboard:', error);
      addNotification('Échec de l\'extraction du storyboard', 'error');
      setIsLoading({ ...isLoading, upload: false });
      return null;
    }
  };

  // Sélectionner plusieurs scènes
  const selectScenes = (sceneIds) => {
    setSelectedScenes(sceneIds);
  };

  // Basculer la sélection d'une scène
  const toggleSceneSelection = (sceneId) => {
    setSelectedScenes(prev => 
      prev.includes(sceneId) 
        ? prev.filter(id => id !== sceneId) 
        : [...prev, sceneId]
    );
  };

  // Mettre à jour une scène
  const updateScene = (sceneId, sceneData) => {
    const updatedScenes = scenes.map(scene => 
      scene.id === sceneId ? { ...scene, ...sceneData } : scene
    );
    
    setScenes(updatedScenes);
    
    // Si nous avons un épisode actif, mettre à jour ses scènes
    if (activeEpisode && activeProject) {
      // Mettre à jour l'épisode actif
      const updatedEpisode = { 
        ...activeEpisode, 
        scenes: activeEpisode.scenes.map(scene => 
          scene.id === sceneId ? { ...scene, ...sceneData } : scene
        ) 
      };
      
      // Mettre à jour le projet actif
      const updatedProject = {
        ...activeProject,
        episodes: activeProject.episodes.map(ep => 
          ep.id === updatedEpisode.id ? updatedEpisode : ep
        )
      };
      
      setActiveEpisode(updatedEpisode);
      setActiveProject(updatedProject);
      
      // Mettre à jour la liste de tous les projets
      setProjects(projects.map(p => 
        p.id === updatedProject.id ? updatedProject : p
      ));
    }
    
    addNotification('Scène mise à jour', 'success');
  };

  // Ajouter une notification
  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [
      ...prev, 
      { id, message, type, timestamp: new Date() }
    ]);
    
    // Supprimer automatiquement la notification après 5 secondes
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  // Valeur du contexte
  const contextValue = {
    // État
    projects,
    activeProject,
    activeEpisode,
    scenes,
    selectedScenes,
    notifications,
    isLoading,
    
    // Actions
    selectProject,
    selectEpisode,
    createProject,
    addEpisode,
    uploadStoryboard,
    selectScenes,
    toggleSceneSelection,
    updateScene,
    addNotification
  };

  // Fournir le contexte à l'application
  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};