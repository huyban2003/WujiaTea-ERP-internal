/* WujiaTea PC notification list — nút "Đánh dấu đã đọc" (BA row 6).
   Server tự đánh dấu TẤT CẢ thông báo còn hiệu lực chưa đọc của user tại cửa hàng hiện tại
   (không gửi ids/filter) → toast "Đã đánh dấu N thông báo là đã đọc" → reload. */
(function () {
    "use strict";
    function toast(msg) {
        var el = document.createElement("div");
        el.className = "wj-noti-toast";
        el.textContent = msg;
        el.style.cssText =
            "position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:2000;" +
            "background:#111827;color:#fff;padding:10px 18px;border-radius:8px;font-size:14px;" +
            "box-shadow:0 6px 20px rgba(0,0,0,.25)";
        document.body.appendChild(el);
        setTimeout(function () { el.remove(); }, 1600);
    }
    document.addEventListener("DOMContentLoaded", function () {
        var btn = document.getElementById("wj-noti-bulk-read");
        if (!btn) return;
        btn.addEventListener("click", function () {
            btn.disabled = true;
            fetch("/portal/notification/mark-all-read", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: {} }),
            })
                .then(function (r) { return r.json(); })
                .then(function (res) {
                    var n = (res && res.result && res.result.updated_count) || 0;
                    toast("Đã đánh dấu " + n + " thông báo là đã đọc.");
                    setTimeout(function () { window.location.reload(); }, 600);
                })
                .catch(function () { btn.disabled = false; });
        });
    });
})();
