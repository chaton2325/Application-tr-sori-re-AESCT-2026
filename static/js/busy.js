/*
 * Indicateurs d'activité globaux.
 * Ajoute un spinner sur chaque bouton (ou lien-bouton) cliqué :
 *  - soumission de formulaire -> spinner sur le bouton submit
 *  - clic sur un lien .btn ou .nav-link -> spinner pendant la navigation
 * Les boutons sont réactivés automatiquement (retour arrière, téléchargement PDF/Excel...).
 */
(function () {
    'use strict';

    var RESET_DELAY = 10000; // filet de sécurité (téléchargements, etc.)

    function setBusy(el) {
        if (!el || el.classList.contains('is-busy')) return;
        el.classList.add('is-busy');
        el.setAttribute('aria-busy', 'true');

        if (el.tagName === 'INPUT') {
            // <input type="submit"> ne peut pas contenir de HTML
            el.dataset.busyValue = el.value;
            el.value = 'Veuillez patienter…';
            el.disabled = true;
        } else {
            var spinner = document.createElement('span');
            spinner.className = 'spinner-border spinner-border-sm busy-spinner me-2';
            spinner.setAttribute('role', 'status');
            spinner.setAttribute('aria-hidden', 'true');
            el.insertBefore(spinner, el.firstChild);
            if (el.tagName === 'BUTTON') {
                el.disabled = true;
            }
        }

        el.dataset.busyTimer = String(setTimeout(function () {
            clearBusy(el);
        }, RESET_DELAY));
    }

    function clearBusy(el) {
        if (!el.classList.contains('is-busy')) return;
        el.classList.remove('is-busy');
        el.removeAttribute('aria-busy');
        el.disabled = false;

        if (el.dataset.busyTimer) {
            clearTimeout(Number(el.dataset.busyTimer));
            delete el.dataset.busyTimer;
        }
        if (el.tagName === 'INPUT' && el.dataset.busyValue) {
            el.value = el.dataset.busyValue;
            delete el.dataset.busyValue;
        }
        var spinner = el.querySelector('.busy-spinner');
        if (spinner) spinner.remove();
    }

    function clearAll() {
        document.querySelectorAll('.is-busy').forEach(clearBusy);
    }

    // 1) Soumission de formulaires (login, enregistrements, exports PDF...)
    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (e.defaultPrevented || !form.checkValidity || !form.checkValidity()) return;

        var btn = e.submitter || form.querySelector('[type="submit"]');
        if (!btn) return;

        // Désactiver après l'envoi pour que la valeur du bouton soit bien transmise
        setTimeout(function () { setBusy(btn); }, 0);
    });

    // 2) Liens boutons et liens de navigation
    document.addEventListener('click', function (e) {
        var link = e.target.closest('a.btn, a.nav-link');
        if (!link || e.defaultPrevented) return;

        var href = link.getAttribute('href') || '';
        if (!href || href.charAt(0) === '#' || href.indexOf('javascript:') === 0) return;
        if (link.target === '_blank' || link.hasAttribute('download')) return;
        if (link.hasAttribute('data-bs-toggle') || link.classList.contains('is-busy')) return;
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;

        setBusy(link);
    });

    // Réinitialisation au retour sur la page (bouton retour / bfcache)
    window.addEventListener('pageshow', clearAll);
})();
