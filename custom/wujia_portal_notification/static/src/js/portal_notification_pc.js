/* WujiaTea PC notification list — bulk "Đánh dấu đã đọc" (Sprint PC-3).
   Runs only on the list page (presence of #wj-noti-bulk-read).
   Collects current page's unread row IDs → POST /portal/notification/mark-read → reload. */
(function () {
    "use strict";
    document.addEventListener("DOMContentLoaded", function () {
        var btn = document.getElementById("wj-noti-bulk-read");
        if (!btn) return;
        btn.addEventListener("click", function () {
            var ids = Array.prototype.slice
                .call(document.querySelectorAll("#wj-noti-table tr.wj-pc-noti-row--unread[data-noti-id]"))
                .map(function (tr) { return parseInt(tr.getAttribute("data-noti-id"), 10); })
                .filter(function (x) { return !isNaN(x); });
            if (!ids.length) { window.location.reload(); return; }
            btn.disabled = true;
            fetch("/portal/notification/mark-read", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    jsonrpc: "2.0", method: "call",
                    params: { notification_ids: ids },
                }),
            })
                .then(function (r) { return r.json(); })
                .then(function () { window.location.reload(); })
                .catch(function () { btn.disabled = false; });
        });
    });
})();
