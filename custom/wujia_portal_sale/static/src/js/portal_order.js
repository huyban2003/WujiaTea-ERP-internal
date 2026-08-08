/* WujiaTea Portal Order — Add-to-cart (catalog + product detail).

   Thêm vào giỏ → server tăng theo bước min_qty (BA row 6) → reconcile realtime qua
   WujiaCartSync (badge/floatbar/panel, không reload). Tương tác TRONG giỏ (stepper/
   xoá/ghi chú) + đồng bộ cross-session nằm ở portal_cart_sync.js. */
(function () {
    "use strict";

    function jsonRpc(url, params) {
        return fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: params || {} }),
        }).then(function (r) { return r.json(); })
          .then(function (j) { return j.result || {}; });
    }

    function toast(msg, ok) {
        const el = document.createElement("div");
        el.className = "alert alert-" + (ok ? "success" : "danger");
        el.style.cssText = "position:fixed;top:20px;right:20px;z-index:9999;min-width:240px;";
        el.textContent = msg;
        document.body.appendChild(el);
        setTimeout(function () { el.remove(); }, 2500);
    }

    function errText(res) {
        return res.message || ("Lỗi: " + res.error);
    }

    /* Reconcile giỏ (badge/floatbar/panel) qua module realtime — không reload. */
    function syncCart() {
        if (window.WujiaCartSync) {
            window.WujiaCartSync.refresh();
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        // Catalog: Add-to-cart (desktop + mobile) — server tự tăng theo bước min_qty.
        // Delegation: nút nằm trong vùng swap của wj_ajax_list (lọc/phân trang thay DOM),
        // bind trực tiếp sẽ mất listener sau lần lọc đầu.
        document.addEventListener("click", function (ev) {
            const btn = ev.target.closest ? ev.target.closest(".btn-add-cart") : null;
            if (!btn || btn.disabled) return;
            ev.preventDefault();
            const productId = parseInt(btn.dataset.productId, 10);
            btn.disabled = true;
            jsonRpc("/portal/order/cart/add", { product_id: productId })
                .then(function (res) {
                    btn.disabled = false;
                    if (res.error) {
                        toast(errText(res), false);
                        return;
                    }
                    if (res.warning) toast(res.message, false);
                    else toast("Đã thêm vào giỏ (" + res.qty + ")", true);
                    syncCart();
                })
                .catch(function () {
                    btn.disabled = false;
                    toast("Lỗi kết nối", false);
                });
        });

        // Product detail: Add-to-cart (có ô nhập số lượng).
        document.querySelectorAll(".btn-add-cart-detail").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const productId = parseInt(btn.dataset.productId, 10);
                const step = parseInt(btn.dataset.minQty, 10) || 1;
                const max = parseInt(btn.dataset.maxQty, 10) || 0; // 0 = không giới hạn
                const qtyEl = document.getElementById("product-detail-qty");
                const msgEl = document.getElementById("product-detail-msg");
                const raw = qtyEl ? String(qtyEl.value).trim() : "";
                const qty = Number(raw);
                // WJ-ORD-001: validate ngay tại client — KHÔNG gửi request khi
                // quantity invalid; lỗi tiếng Việt cạnh input.
                let err = null;
                if (raw === "" || !Number.isFinite(qty)) {
                    err = "Vui lòng nhập số lượng hợp lệ.";
                } else if (!Number.isInteger(qty)) {
                    err = "Số lượng phải là số nguyên.";
                } else if (qty < step) {
                    err = "Số lượng tối thiểu là " + step + ".";
                } else if (qty % step !== 0) {
                    err = "Số lượng phải tăng theo bước " + step + ".";
                } else if (max && qty > max) {
                    err = "Số lượng tối đa là " + max + ".";
                }
                if (err) {
                    if (msgEl) msgEl.innerHTML = '<div class="alert alert-danger">' + err + "</div>";
                    if (qtyEl) { qtyEl.classList.add("is-invalid"); qtyEl.focus(); }
                    return;
                }
                if (qtyEl) qtyEl.classList.remove("is-invalid");
                btn.disabled = true;
                jsonRpc("/portal/order/cart/add", { product_id: productId, qty: qty })
                    .then(function (res) {
                        btn.disabled = false;
                        if (res.error) {
                            if (msgEl) msgEl.innerHTML = '<div class="alert alert-danger">' + errText(res) + "</div>";
                            return;
                        }
                        if (msgEl) msgEl.innerHTML = '<div class="alert alert-success">Số lượng trong giỏ: ' + res.qty + '. <a href="/portal/order/cart">Xem giỏ →</a></div>';
                        syncCart();
                    })
                    .catch(function () {
                        btn.disabled = false;
                        if (msgEl) msgEl.innerHTML = '<div class="alert alert-danger">Lỗi kết nối</div>';
                    });
            });
        });

        /* Figma 4963:2 màn 02 — overlay "Đang tạo đơn" + chống bấm 2 lần.
           Lớp UI thuần: chặn thật nằm ở server (khoá giỏ FOR UPDATE NOWAIT →
           CART_IS_PROCESSING; lần 2 sau khi giỏ đã clear → CART_EMPTY).
           Delegation trên document vì panel giỏ bị cart-sync swap innerHTML. */
        const overlay = document.getElementById("wj-order-submitting");

        function setOverlay(show) {
            if (!overlay) return;
            overlay.classList.toggle("wujia-msubmit--show", show);
            overlay.setAttribute("aria-hidden", show ? "false" : "true");
        }

        function mobileSubmitForm(target) {
            const form = target && target.closest ? target.closest("form[action='/portal/order/submit']") : null;
            // Chỉ luồng mobile (hidden flow=m) — form PC dùng chung route, không đụng.
            return form && form.querySelector("input[name='flow'][value='m']") ? form : null;
        }

        document.addEventListener("submit", function (ev) {
            const form = mobileSubmitForm(ev.target);
            if (!form) return;
            if (form.dataset.wjSubmitting === "1") {
                ev.preventDefault();
                return;
            }
            form.dataset.wjSubmitting = "1";
            // Nút submit không có attribute name → disable không làm mất payload;
            // portal_note vẫn gửi vì nằm cùng form (FUNC-MOB-ORDER-005).
            const btn = form.querySelector(".wujia-mcart-submit");
            if (btn) btn.disabled = true;
            setOverlay(true);
        });

        // WJ-ORD-003: back/forward khôi phục trang từ BFCache → overlay/nút bị
        // đóng băng ở trạng thái "đang gửi". Reset lại để giỏ dùng được ngay.
        window.addEventListener("pageshow", function (ev) {
            if (!ev.persisted) return;
            setOverlay(false);
            document.querySelectorAll("form[action='/portal/order/submit']").forEach(function (f) {
                if (f.dataset.wjSubmitting !== "1") return;
                delete f.dataset.wjSubmitting;
                // Chỉ mở lại nút mà CHÍNH ta đã khoá — nút bị server disable vì
                // ngoài khung giờ (WJ-ORD-006) phải giữ nguyên trạng thái khoá.
                const b = f.querySelector(".wujia-mcart-submit");
                if (b) b.disabled = false;
            });
        });
    });
})();
