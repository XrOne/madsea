// 003-prototype-puppeteer-comfyui.js
// Prototype d'automatisation ComfyUI via Puppeteer pour Madsea

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Configurable
const COMFYUI_URL = 'http://localhost:8188'; // Adapter pour RunPod/cloud si besoin
const WORKFLOW_JSON = 'OmbresChinoises.json';
const INPUT_IMAGES_DIR = 'i:/Madsea/outputs/nomenclature_test/E202/extracted-raw';
const OUTPUT_DIR = 'i:/Madsea/outputs/puppeteer_results';
const NOMENCLATURE = (episode, sequence, plan, tache, version, ext) => `E${episode}_${sequence}-${plan}_${tache}_v${version}.${ext}`;

async function automateComfyUI({episode, sequence, plans, workflowJson, params, style}) {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.goto(COMFYUI_URL);

    // Charger le workflow JSON
    // (Supposons un bouton d'import ou drag&drop)
    // TODO: Automatiser l'import du workflowJson si nécessaire

    for (let plan of plans) {
        // 1. Upload de l'image source
        const imagePath = path.join(INPUT_IMAGES_DIR, plan.input_image);
        const uploadInput = await page.$('input[type=file]');
        await uploadInput.uploadFile(imagePath);

        // 2. Configurer les paramètres IA (sliders, prompts, etc.)
        // TODO: Adapter les sélecteurs selon le workflow ComfyUI utilisé
        // Exemple : await page.type('#prompt', plan.prompt);
        // await page.evaluate((steps) => { document.querySelector('#steps').value = steps; }, params.steps);

        // 3. Lancer la génération
        await page.click('#generate-btn'); // Adapter le sélecteur

        // 4. Attendre la génération et télécharger le résultat
        await page.waitForSelector('.result-image');
        const outputImage = await page.$('.result-image');
        const buffer = await outputImage.screenshot();
        const outputName = NOMENCLATURE(episode, sequence, plan.plan_id, 'AI-concept', '0001', 'png');
        fs.writeFileSync(path.join(OUTPUT_DIR, outputName), buffer);

        // 5. Log
        console.log(`Plan ${plan.plan_id} généré et sauvegardé sous ${outputName}`);
    }
    await browser.close();
}

// Exemple d'appel
if (require.main === module) {
    automateComfyUI({
        episode: '202',
        sequence: 'SQ0010',
        plans: [
            { plan_id: '0010', input_image: 'E202_P0001-I0001_extracted-raw_v0001.png', prompt: 'Silhouette dramatique' },
            // ...
        ],
        workflowJson: WORKFLOW_JSON,
        params: { steps: 30, cfg: 7.5, lora_strength: 0.9 },
        style: 'ombres_chinoises'
    });
}

// TODO :
// - Automatiser l'import du workflow JSON
// - Adapter les sélecteurs aux composants réels de ComfyUI
// - Gérer les erreurs et logs détaillés
// - Supporter le batch multi-séquence/plan
