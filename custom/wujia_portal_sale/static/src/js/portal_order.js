/* WujiaTea Portal Order — cart AJAX client.
   Endpoints type=json (Odoo style): {jsonrpc:"2.0", method:"call", params:{...}}.
   Reuses session cookie → CSRF không cần (Odoo built-in cho type=json).

   Sprint 11: thêm wiring cho UI mobile (BA Registry v3):
     - catalog add → cập nhật green qty badge + floating cart bar.
     - cart stepper (− / +) → /portal/order/cart/update + cập nhật Thành tiền / Tạm tính.
     - cart delete (.wujia-mcart-del) → /portal/order/cart/remove.
   Desktop handlers (.cart-qty-input / .btn-cart-remove / tr[data-line-id]) giữ nguyên.
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
        document.querySelectorAll(".cart-badge, .badge.bg-primary, .wujia-header-cart-count").forEach(function (b) {
            if (b.dataset.cartBadge !== undefined || b.classList.contains("cart-badge") || b.classList.contains("wujia-header-cart-count")) {
                b.textContent = count;
                b.classList.toggle("is-active", count > 0);
            }
        });
    }

    /* VND format: dot thousands separator (1352000 → "1.352.000"). */
    function formatVnd(n) {
        return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    /* ---------- Mobile cart (.wujia-mcart) helpers ---------- */
    function mcartUpdateLine(row) {
        const unit = parseInt(row.dataset.unitPrice || "0", 10);
        const qtyEl = row.querySelector(".wujia-mcart-step-qty");
        const qty = qtyEl ? (parseInt(qtyEl.textContent, 10) || 0) : 0;
        const amtEl = row.querySelector(".wujia-mcart-row-amount-value");
        if (amtEl) amtEl.textContent = formatVnd(unit * qty) + " đ";
    }
    function mcartUpdateTotals() {
        const rows = document.querySelectorAll(".wujia-mcart-scroll .wujia-mcart-row");
        let grand = 0, count = 0;
        rows.forEach(function (r) {
            const unit = parseInt(r.dataset.unitPrice || "0", 10);
            const qEl = r.querySelector(".wujia-mcart-step-qty");
            const q = qEl ? (parseInt(qEl.textContent, 10) || 0) : 0;
            grand += unit * q;
            count += 1;
        });
        const g = document.querySelector(".wujia-mcart-grand");
        if (g) g.textContent = formatVnd(grand) + " đ";
        const c = document.querySelector(".wujia-mcart-summary-line.muted span:last-child");
        if (c) c.textContent = count + " sản phẩm";
    }

    document.addEventListener("DOMContentLoaded", function () {
        // ============ Catalog page: Add-to-cart buttons (desktop + mobile) ============
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

                        // Desktop combined page (Sprint PC-1): reload để cart panel phải
                        // + qty badge trên nút phản ánh ngay (server re-render).
                        if (btn.classList.contains("wj-pc-order-add")) {
                            location.reload();
                            return;
                        }

                        // Mobile-only live updates (chỉ khi bấm nút mobile)
                        if (btn.classList.contains("wujia-morder-row-add")) {
                            const mq = btn.querySelector(".wujia-morder-row-qty");
                            if (mq) { mq.textContent = res.qty; mq.classList.remove("d-none"); }
                            const fb = document.querySelector(".wujia-morder-floatbar");
                            if (fb) {
                                const price = parseInt(btn.dataset.price || "0", 10);
                                const total = parseInt(fb.dataset.cartTotal || "0", 10) + price * qty;
                                fb.dataset.cartTotal = total;
                                const tEl = fb.querySelector(".wujia-morder-floatbar-total");
                                if (tEl) tEl.textContent = formatVnd(total);
                                const cEl = fb.querySelector(".wujia-morder-floatbar-count");
                                if (cEl) cEl.textContent = res.cart_count;
                            }
                        }
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

        // ============ Cart page DESKTOP: qty change (debounced 500ms) ============
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

        // ============ Cart page DESKTOP: remove line ============
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

        // ============ Cart page MOBILE: qty stepper (− / +) ============
        document.querySelectorAll(".wujia-mcart-step").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const row = btn.closest(".wujia-mcart-row");
                if (!row) return;
                const qtyEl = row.querySelector(".wujia-mcart-step-qty");
                const lineId = parseInt(row.dataset.lineId, 10);
                const cur = qtyEl ? (parseInt(qtyEl.textContent, 10) || 0) : 0;
                const delta = btn.classList.contains("wujia-mcart-step-plus") ? 1 : -1;
                const next = Math.max(0, cur + delta);
                if (next === cur) return;
                btn.disabled = true;
                jsonRpc("/portal/order/cart/update", { line_id: lineId, qty: next })
                    .then(function (res) {
                        btn.disabled = false;
                        if (res.error) {
                            toast("Lỗi: " + res.error, false);
                            return;
                        }
                        if (res.removed) {
                            row.remove();
                        } else {
                            if (qtyEl) qtyEl.textContent = next;
                            mcartUpdateLine(row);
                        }
                        mcartUpdateTotals();
                        refreshCartBadge(res.cart_count);
                        if (res.cart_count === 0) location.reload();
                    })
                    .catch(function () {
                        btn.disabled = false;
                        toast("Lỗi kết nối", false);
                    });
            });
        });

        // ============ Cart page MOBILE: remove line ============
        document.querySelectorAll(".wujia-mcart-del").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const row = btn.closest(".wujia-mcart-row");
                if (!row) return;
                const lineId = parseInt(row.dataset.lineId, 10);
                if (!confirm("Xoá sản phẩm này khỏi giỏ?")) return;
                jsonRpc("/portal/order/cart/remove", { line_id: lineId })
                    .then(function (res) {
                        if (res.error) {
                            toast("Lỗi: " + res.error, false);
                            return;
                        }
                        row.remove();
                        mcartUpdateTotals();
                        refreshCartBadge(res.cart_count);
                        if (res.cart_count === 0) location.reload();
                    });
            });
        });
    });
})();
