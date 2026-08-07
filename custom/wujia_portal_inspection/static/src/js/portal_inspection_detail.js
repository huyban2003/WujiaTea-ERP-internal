/** @odoo-module **/

document.addEventListener('DOMContentLoaded', function () {
    // 1. Click scroll to section from Grid 2x2
    const summaryCards = document.querySelectorAll('.summary-2x2-card[data-target-sec]');
    summaryCards.forEach(function (card) {
        card.addEventListener('click', function (e) {
            const targetId = card.getAttribute('data-target-sec');
            if (targetId) {
                const targetElem = document.getElementById(targetId);
                if (targetElem) {
                    targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    // 2. Close button for bottom fixed action bar
    const closeBtn = document.getElementById('close_bottom_bar_btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const bar = document.getElementById('fixed_bottom_bar');
            if (bar) {
                bar.classList.add('d-none-bar');
            }
        });
    }
});
