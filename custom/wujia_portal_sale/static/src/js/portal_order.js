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
        document.querySelectorAll(".btn-add-cart").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
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
        });

        // Product detail: Add-to-cart (có ô nhập số lượng).
        document.querySelectorAll(".btn-add-cart-detail").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const productId = parseInt(btn.dataset.productId, 10);
                const qtyEl = document.getElementById("product-detail-qty");
                const qty = qtyEl ? parseInt(qtyEl.value, 10) || 0 : 0;
                const msgEl = document.getElementById("product-detail-msg");
                btn.disabled = true;
                jsonRpc("/portal/order/cart/add", qty ? { product_id: productId, qty: qty } : { product_id: productId })
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
    });
})();
