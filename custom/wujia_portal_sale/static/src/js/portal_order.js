/* WujiaTea Portal Order — cart AJAX client.
   Endpoints type=json (Odoo style): {jsonrpc:"2.0", method:"call", params:{...}}.
   Reuses session cookie → CSRF không cần (Odoo built-in cho type=json).
*/
(function () {
    "use strict";

    function jsonRpc(url, params) {
        return fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
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
        setTimeout(function () { el.remove(); }, 2500);
    }

    function debounce(fn, wait) {
        let t;
        return function () {
            const args = arguments, ctx = this;
            clearTimeout(t);
            t = setTimeout(function () { fn.apply(ctx, args); }, wait);
        };
    }

    function refreshCartBadge(count) {
        document.querySelectorAll(".cart-badge, .badge.bg-primary").forEach(function (b) {
            if (b.dataset.cartBadge !== undefined || b.classList.contains("cart-badge")) {
                b.textContent = count;
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        // ============ Catalog page: Add-to-cart buttons ============
        document.querySelectorAll(".btn-add-cart").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const card = btn.closest(".product-card");
                const qtyInput = card ? card.querySelector(".product-qty-input") : null;
                const productId = parseInt(btn.dataset.productId, 10);
                const qty = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
                btn.disabled = true;
                jsonRpc("/portal/order/cart/add", { product_id: productId, qty: qty })
                    .then(function (res) {
                        btn.disabled = false;
                        if (res.error) {
                            toast("Lỗi: " + res.error, false);
                            return;
                        }
                        toast("Đã thêm vào giỏ (" + res.qty + ")", true);
                        refreshCartBadge(res.cart_count);
                    })
                    .catch(function () {
                        btn.disabled = false;
                        toast("Lỗi kết nối", false);
                    });
            });
        });

        // ============ Product detail page: Add-to-cart ============
        document.querySelectorAll(".btn-add-cart-detail").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const productId = parseInt(btn.dataset.productId, 10);
                const qtyEl = document.getElementById("product-detail-qty");
                const qty = qtyEl ? parseInt(qtyEl.value, 10) || 1 : 1;
                const msgEl = document.getElementById("product-detail-msg");
                btn.disabled = true;
                jsonRpc("/portal/order/cart/add", { product_id: productId, qty: qty })
                    .then(function (res) {
                        btn.disabled = false;
                        if (res.error) {
                            if (msgEl) msgEl.innerHTML = '<div class="alert alert-danger">' + res.error + "</div>";
                            return;
                        }
                        if (msgEl) msgEl.innerHTML = '<div class="alert alert-success">Đã thêm ' + res.qty + ' vào giỏ. <a href="/portal/order/cart">Xem giỏ →</a></div>';
                        refreshCartBadge(res.cart_count);
                    })
                    .catch(function () {
                        btn.disabled = false;
                        if (msgEl) msgEl.innerHTML = '<div class="alert alert-danger">Lỗi kết nối</div>';
                    });
            });
        });

        // ============ Cart page: qty change (debounced 500ms) ============
        document.querySelectorAll(".cart-qty-input").forEach(function (input) {
            const handler = debounce(function () {
                const lineId = parseInt(input.dataset.lineId, 10);
                const qty = Math.max(0, parseInt(input.value, 10) || 0);
                jsonRpc("/portal/order/cart/update", { line_id: lineId, qty: qty })
                    .then(function (res) {
                        if (res.error) {
                            toast("Lỗi: " + res.error, false);
                            return;
                        }
                        if (res.removed) {
                            const row = document.querySelector('tr[data-line-id="' + lineId + '"]');
                            if (row) row.remove();
                        }
                        refreshCartBadge(res.cart_count);
                        toast("Đã cập nhật", true);
                    });
            }, 500);
            input.addEventListener("change", handler);
        });

        // ============ Cart page: remove line ============
        document.querySelectorAll(".btn-cart-remove").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const lineId = parseInt(btn.dataset.lineId, 10);
                if (!confirm("Xoá dòng này khỏi giỏ?")) return;
                jsonRpc("/portal/order/cart/remove", { line_id: lineId })
                    .then(function (res) {
                        if (res.error) {
                            toast("Lỗi: " + res.error, false);
                            return;
                        }
                        const row = document.querySelector('tr[data-line-id="' + lineId + '"]');
                        if (row) row.remove();
                        refreshCartBadge(res.cart_count);
                        if (res.cart_count === 0) location.reload();
                    });
            });
        });
    });
})();
