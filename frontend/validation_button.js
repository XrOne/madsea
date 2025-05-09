// Bouton "Envoyer pour validation [Nom du réalisateur]" pour l'UI Madsea
// Ce script ajoute dynamiquement le bouton et gère l'appel backend

document.addEventListener('DOMContentLoaded', function () {
    // Création du bouton
    const btn = document.createElement('button');
    btn.id = 'validate-director-btn';
    btn.className = 'fixed bottom-8 right-8 px-6 py-3 bg-indigo-700 text-white rounded-full shadow-lg hover:bg-indigo-800 text-lg font-bold z-50';
    btn.innerHTML = '<i class="fa fa-paper-plane mr-2"></i>Envoyer pour validation Réalisateur';

    // Ajout du bouton à la page
    document.body.appendChild(btn);

    // Affichage d'un toast/feedback
    function showToast(msg, success=true) {
        let toast = document.getElementById('madsea-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'madsea-toast';
            toast.className = 'fixed bottom-24 right-8 px-4 py-3 rounded shadow-lg z-50';
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.style.background = success ? '#34d399' : '#f87171';
        toast.style.color = '#fff';
        toast.style.display = 'block';
        setTimeout(() => { toast.style.display = 'none'; }, 4000);
    }

    // Gestion du clic sur le bouton
    btn.addEventListener('click', async function () {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa fa-spinner fa-spin mr-2"></i>Envoi en cours...';
        showToast('Connexion au serveur de validation...', true);
        try {
            // Appel backend (à adapter selon l'endpoint réel)
            const resp = await fetch('/api/export_gazu', { method: 'POST' });
            const data = await resp.json();
            if (data.success) {
                showToast('Export terminé : toutes les images ont été envoyées au réalisateur.', true);
                btn.innerHTML = '<i class="fa fa-check mr-2"></i>Envoyé au réalisateur';
            } else {
                showToast('Erreur lors de l\'export : ' + (data.error || 'inconnue'), false);
                btn.innerHTML = '<i class="fa fa-paper-plane mr-2"></i>Réessayer l\'envoi';
                btn.disabled = false;
            }
        } catch (e) {
            showToast('Erreur réseau ou serveur.', false);
            btn.innerHTML = '<i class="fa fa-paper-plane mr-2"></i>Réessayer l\'envoi';
            btn.disabled = false;
        }
    });
});
