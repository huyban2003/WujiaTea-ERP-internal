/* ==========================================================================
   Wujia Franchise - Supervision Inspection Report Scripts
   ========================================================================== */

(function () {
    'use strict';

    function getFormattedPdfName() {
        const storeEl = document.querySelector('.store-name-sub');
        const dateEl = document.querySelector('.report-date-text strong');
        let storeName = "";
        if (storeEl) {
            storeName = storeEl.innerText.replace(/\(.*?\)/g, '').trim();
        }
        let dateStr = "";
        if (dateEl) {
            dateStr = dateEl.innerText.trim().replace(/\//g, '-');
        }
        if (storeName && dateStr) {
            return `Báo cáo Khảo sát Giám sát [${storeName}] [${dateStr}]`;
        }
        return document.title || "Báo cáo Khảo sát Giám sát";
    }

    function applyDynamicTitle() {
        const formattedTitle = getFormattedPdfName();
        document.title = formattedTitle;
        try {
            if (window.parent && window.parent.document) {
                window.parent.document.title = formattedTitle;
            }
            if (window.top && window.top.document) {
                window.top.document.title = formattedTitle;
            }
        } catch (e) {}
    }

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
        applyDynamicTitle();

        window.addEventListener('beforeprint', function () {
            maskUrl();
            applyDynamicTitle();
        });

        const btnPrint = document.getElementById('btnPrintReport');
        if (btnPrint) {
            btnPrint.addEventListener('click', function () {
                maskUrl();
                applyDynamicTitle();
                window.print();
            });
        }
    });
})();
