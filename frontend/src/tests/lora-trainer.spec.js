// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('LoRA Trainer Component Tests', () => {
  test('should render LoRA trainer form correctly', async ({ page }) => {
    // Naviguer vers la page contenant le LoRA Trainer
    await page.goto('http://localhost:3000/scene-generation');
    
    // Vérifier que le composant est visible
    const trainerTitle = await page.locator('text=Créer un LoRA personnalisé');
    await expect(trainerTitle).toBeVisible();
    
    // Vérifier les éléments du formulaire
    await expect(page.locator('text=Archive ZIP d\'images d\'entraînement')).toBeVisible();
    await expect(page.locator('text=Nom du LoRA')).toBeVisible();
    await expect(page.locator('text=Epochs')).toBeVisible();
    await expect(page.locator('text=Learning Rate')).toBeVisible();
    await expect(page.locator('button:has-text("Lancer l\'entraînement")')).toBeVisible();
  });
  
  test('should show validation error when submitting without file', async ({ page }) => {
    await page.goto('http://localhost:3000/scene-generation');
    
    // Cliquer sur le bouton sans sélectionner de fichier
    await page.locator('button:has-text("Lancer l\'entraînement")').click();
    
    // Vérifier le message d'erreur
    await expect(page.locator('text=Veuillez sélectionner un zip d\'images')).toBeVisible();
  });
  
  // Ce test nécessiterait des mocks pour être exécuté correctement
  test.skip('should show progress when submitting valid data', async ({ page }) => {
    await page.goto('http://localhost:3000/scene-generation');
    
    // TODO: Simuler le téléchargement d'un fichier ZIP
    // await page.setInputFiles('input[type="file"]', 'path/to/test/file.zip');
    
    // Remplir le formulaire
    await page.fill('input[placeholder="Nom du modèle"]', 'test-lora');
    await page.fill('input[type="number"]', '5'); // Epochs
    
    // Soumettre le formulaire
    await page.locator('button:has-text("Lancer l\'entraînement")').click();
    
    // Vérifier l'état de progression
    await expect(page.locator('text=Entraînement en cours...')).toBeVisible();
  });
});