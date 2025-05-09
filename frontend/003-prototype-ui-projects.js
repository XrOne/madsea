// 003-prototype-ui-projects.js
// Prototype UI Projects Madsea — création/sélection projet/épisode (inline, simple, évolutif)

// Stockage temporaire en localStorage (remplaçable par API backend)
const PROJECTS_KEY = 'madsea_projects';

function getProjects() {
    return JSON.parse(localStorage.getItem(PROJECTS_KEY) || '{"projects":[]}');
}

function saveProjects(data) {
    localStorage.setItem(PROJECTS_KEY, JSON.stringify(data));
}

function renderProjectsUI() {
    const container = document.getElementById('projects-container');
    if (!container) return;
    const data = getProjects();
    container.innerHTML = `
        <h2 class="text-xl font-bold mb-2">Projects</h2>
        <button id="add-project-btn" class="bg-blue-500 text-white px-3 py-1 rounded mb-2">New Project</button>
        <ul>
            ${data.projects.map((proj, i) => `
                <li class="mb-2">
                    <span class="font-semibold">${proj.name}</span>
                    <button class="ml-2 text-xs text-green-600" onclick="selectProject('${proj.id}')">Select</button>
                    <ul class="ml-4">
                        ${proj.episodes.map(ep => `
                            <li>
                                Ep. ${ep.number} — ${ep.name}
                                <button class="ml-2 text-xs text-blue-600" onclick="selectEpisode('${proj.id}','${ep.id}')">Select</button>
                            </li>`).join('')}
                    </ul>
                    <button class="ml-2 text-xs text-gray-500" onclick="addEpisode('${proj.id}')">+ Episode</button>
                </li>
            `).join('')}
        </ul>
        <div id="project-form" class="mt-4"></div>
        <div id="episode-form" class="mt-4"></div>
    `;
    document.getElementById('add-project-btn').onclick = showProjectForm;
}

function showProjectForm() {
    const form = document.getElementById('project-form');
    form.innerHTML = `
        <input id="project-name" placeholder="Project name" class="border px-2 py-1 mr-2" />
        <button onclick="createProject()" class="bg-green-600 text-white px-2 py-1 rounded">Create</button>
    `;
}

function createProject() {
    const name = document.getElementById('project-name').value.trim();
    if (!name) return;
    const data = getProjects();
    const newProj = {
        id: 'proj_' + Date.now(),
        name,
        episodes: []
    };
    data.projects.push(newProj);
    saveProjects(data);
    renderProjectsUI();
}

function addEpisode(projId) {
    const form = document.getElementById('episode-form');
    form.innerHTML = `
        <input id="ep-number" placeholder="Episode number" class="border px-2 py-1 mr-2" />
        <input id="ep-name" placeholder="Episode name" class="border px-2 py-1 mr-2" />
        <button onclick="createEpisode('${projId}')" class="bg-green-600 text-white px-2 py-1 rounded">Add Episode</button>
    `;
}

function createEpisode(projId) {
    const number = document.getElementById('ep-number').value.trim();
    const name = document.getElementById('ep-name').value.trim();
    if (!number || !name) return;
    const data = getProjects();
    const proj = data.projects.find(p => p.id === projId);
    if (!proj) return;
    proj.episodes.push({
        id: 'ep_' + Date.now(),
        number,
        name,
        scenes: []
    });
    saveProjects(data);
    renderProjectsUI();
}

function selectProject(projId) {
    localStorage.setItem('madsea_active_project', projId);
    alert('Project selected!');
}

function selectEpisode(projId, epId) {
    localStorage.setItem('madsea_active_project', projId);
    localStorage.setItem('madsea_active_episode', epId);
    alert('Episode selected!');
}

// Pour intégration dans index.html :
// <div id="projects-container"></div>
// <script src="003-prototype-ui-projects.js"></script>
// <script>renderProjectsUI();</script>
