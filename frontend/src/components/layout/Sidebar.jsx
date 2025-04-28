import React, { useContext } from 'react';
import { AppContext } from '../../context/AppContext';

const Sidebar = () => {
  const { projects, activeProject, selectProject } = useContext(AppContext);

  return (
    <div className="fixed left-0 top-0 w-64 h-full bg-gray-900 text-white p-4 overflow-y-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-1">Madsea</h1>
        <p className="text-sm text-gray-400">Storyboard to Visual Sequences</p>
      </div>

      <nav className="mb-6">
        <ul className="space-y-2">
          <li>
            <a href="#" className="flex items-center p-2 rounded hover:bg-gray-700 transition">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
              </svg>
              Dashboard
            </a>
          </li>
          <li>
            <a href="#" className="flex items-center p-2 rounded hover:bg-gray-700 transition">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              Nouveau projet
            </a>
          </li>
          <li>
            <a href="#" className="flex items-center p-2 rounded hover:bg-gray-700 transition">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              Génération IA
            </a>
          </li>
          <li>
            <a href="#" className="flex items-center p-2 rounded hover:bg-gray-700 transition">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              Paramètres
            </a>
          </li>
        </ul>
      </nav>

      <div className="mb-4">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Projets récents</h2>
        <ul className="space-y-1">
          {projects.map(project => (
            <li key={project.id}>
              <button
                onClick={() => selectProject(project.id)}
                className={`w-full text-left px-3 py-2 rounded text-sm transition hover:bg-gray-700 ${
                  activeProject && activeProject.id === project.id ? 'bg-blue-600 hover:bg-blue-700' : ''
                }`}
              >
                {project.name}
                {project.episodes && project.episodes.length > 0 && (
                  <span className="ml-2 text-xs text-gray-400">
                    ({project.episodes.length} épisode{project.episodes.length > 1 ? 's' : ''})
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-auto pt-4 border-t border-gray-700">
        <a href="#" className="flex items-center p-2 rounded hover:bg-gray-700 transition text-sm">
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Aide
        </a>
        <div className="flex items-center p-2 text-sm text-gray-400">
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"></path>
          </svg>
          v1.0.0
        </div>
      </div>
    </div>
  );
};

export default Sidebar;