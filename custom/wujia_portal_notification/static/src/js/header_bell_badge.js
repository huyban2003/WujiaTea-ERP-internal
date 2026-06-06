/* WujiaTea Header Notification badge (UI-13, Sprint 9.14, 2026-05-28).
   Fetches unread notification count after DOMContentLoaded and toggles
   .is-active. Endpoint: POST /portal/notification/unread-count
   → {result: {count: N}}. Runs only when .wujia-header-noti-count is
   present (i.e. user is in portal). */
(function () {
    "use strict";
    document.addEventListener("DOMContentLoaded", function () {
        var badge = document.querySelector(".wujia-header-noti-count");
        // Sprint 11: same poll also feeds the portal-wide bottom-nav badge
        // (.wujia-bnav-noti-badge) — no extra query.
        var bnavBadge = document.querySelector(".wujia-bnav-noti-badge");
        if (!badge && !bnavBadge) return;
        fetch("/portal/notification/unread-count", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: {} }),
        })
            .then(function (r) { return r.json(); })
            .then(function (j) {
                var n = (j && j.result && j.result.count) || 0;
                if (badge) {
                    badge.textContent = n;
                    badge.classList.toggle("is-active", n > 0);
                }
                if (bnavBadge) {
                    bnavBadge.textContent = n;
                    bnavBadge.style.display = n > 0 ? "" : "none";
                }
            })
            .catch(function () {});
    });
})();
