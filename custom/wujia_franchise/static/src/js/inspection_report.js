/* ==========================================================================
   Wujia Franchise - Supervision Inspection Report Scripts
   ========================================================================== */

(function () {
    'use strict';

    function maskUrl() {
        try {
            if (window.history && window.history.replaceState) {
                window.history.replaceState({}, '', '/wujiateavn');
            }
        } catch (e) {
            console.error(e);
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        maskUrl();

        const codeEl = document.querySelector('.report-code-badge');
        const storeEl = document.querySelector('.store-name-sub');
        let docTitle = "";
        if (codeEl) {
            docTitle = codeEl.innerText.trim();
            if (storeEl) docTitle += " - " + storeEl.innerText.trim();
        } else {
            docTitle = "wujiateavn";
        }
        document.title = docTitle;

        window.addEventListener('beforeprint', function () {
            maskUrl();
        });

        const btnPrint = document.getElementById('btnPrintReport');
        if (btnPrint) {
            btnPrint.addEventListener('click', function () {
                maskUrl();
                window.print();
            });
        }
    });
})();
