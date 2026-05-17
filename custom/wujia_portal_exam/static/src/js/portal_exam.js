/* WujiaTea Portal Exam — register / cancel AJAX.
   JSON-RPC style giống portal_order.js — Odoo type=json built-in. */
(function () {
    "use strict";

    function jsonRpc(url, params) {
        return fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                jsonrpc: "2.0", method: "call",
                params: params || {},
            }),
        }).then(function (r) { return r.json(); })
          .then(function (j) { return j.result || {}; });
    }

    function toast(msg, ok) {
        const el = document.createElement("div");
        el.className = "alert alert-" + (ok ? "success" : "danger");
        el.style.cssText = "position:fixed;top:20px;right:20px;z-index:9999;min-width:240px;";
        el.textContent = msg;
        document.body.appendChild(el);
        setTimeout(function () { el.remove(); }, 2800);
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".btn-register-exam, .btn-exam-register").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const scheduleId = parseInt(btn.dataset.scheduleId, 10);
                btn.disabled = true;
                jsonRpc("/portal/exam/register", { schedule_id: scheduleId })
                    .then(function (res) {
                        if (res.success) {
                            btn.textContent = "Đã đăng ký";
                            btn.classList.remove("btn-primary");
                            btn.classList.add("btn-success");
                            toast("Đăng ký thành công!", true);
                        } else {
                            btn.disabled = false;
                            const labels = {
                                schedule_closed: "Lịch thi đã đóng",
                                full: "Lịch thi đã đầy",
                                duplicate: "Bạn đã đăng ký lịch này",
                                no_active_franchise: "Chưa chọn cửa hàng",
                            };
                            toast(labels[res.error] || res.error || "Lỗi", false);
                        }
                    })
                    .catch(function () {
                        btn.disabled = false;
                        toast("Lỗi kết nối", false);
                    });
            });
        });

        document.querySelectorAll(".btn-exam-cancel").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                if (!confirm("Huỷ đăng ký lịch thi này?")) return;
                const regId = parseInt(btn.dataset.regId, 10);
                btn.disabled = true;
                jsonRpc("/portal/exam/cancel/" + regId, {})
                    .then(function (res) {
                        if (res.success) {
                            toast("Đã huỷ đăng ký", true);
                            setTimeout(function () { location.reload(); }, 700);
                        } else {
                            btn.disabled = false;
                            toast(res.error || "Lỗi", false);
                        }
                    });
            });
        });
    });
})();
