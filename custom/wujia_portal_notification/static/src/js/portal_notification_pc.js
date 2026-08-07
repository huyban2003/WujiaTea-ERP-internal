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
    // Delegation: nút nằm trong vùng swap của wj_ajax_list — bind trực tiếp sẽ mất
    // listener sau lần lọc đầu tiên (node cũ đã bị thay).
    document.addEventListener("click", function (ev) {
        var btn = ev.target.closest ? ev.target.closest("#wj-noti-bulk-read") : null;
        if (!btn || btn.disabled) return;
        btn.disabled = true;
        fetch("/portal/notification/mark-all-read", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: {} }),
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                var out = (res && res.result) || {};
                if (out.error) {
                    // Ví dụ chưa chọn cửa hàng — hiện message nghiệp vụ, không reload.
                    toast(out.message || "Chưa thể đánh dấu đã đọc. Vui lòng thử lại.");
                    btn.disabled = false;
                    return;
                }
                toast("Đã đánh dấu " + (out.updated_count || 0) + " thông báo là đã đọc.");
                setTimeout(function () { window.location.reload(); }, 600);
            })
            .catch(function () { btn.disabled = false; });
    });
})();
