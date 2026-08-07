/** @odoo-module **/

(function () {
    function initDetailScripts() {
        // 1. Click scroll to section from Grid 2x2
        var summaryCards = document.querySelectorAll('.summary-2x2-card');
        summaryCards.forEach(function (card) {
            card.addEventListener('click', function (e) {
                var targetId = card.getAttribute('href');
                if (targetId && targetId.startsWith('#')) {
                    var targetElem = document.getElementById(targetId.substring(1));
                    if (targetElem) {
                        e.preventDefault();
                        targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            });
        });

        // 2. Close button for bottom fixed action bar
        var closeBtn = document.getElementById('close_bottom_bar_btn');
        if (closeBtn) {
            closeBtn.onclick = function (e) {
                if (e) e.preventDefault();
                var bar = document.getElementById('bottom_remediation_bar');
                if (!bar) {
                    bar = document.getElementById('fixed_bottom_bar');
                }
                if (bar) {
                    bar.style.display = 'none';
                    bar.classList.add('d-none');
                }
            };
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDetailScripts);
    } else {
        initDetailScripts();
    }
})();
