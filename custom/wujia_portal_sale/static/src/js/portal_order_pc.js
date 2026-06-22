/* WujiaTea Portal Order — PC cart panel client (Sprint PC-1).
   Drives the shared wj-pc-cart panel (combined /portal/order right column +
   standalone /portal/order/cart). Reuses the same JSON endpoints as desktop/mobile:
     - stepper − / +  → /portal/order/cart/update
     - remove (trash) → /portal/order/cart/remove
   Live-updates qty, line subtotal, count + grand total without reload.
   Self-contained (own helpers) so it doesn't depend on portal_order.js internals. */
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

    /* VND format: dot thousands separator (1352000 → "1.352.000"). */
    function formatVnd(n) {
        return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    function refreshHeaderBadge(count) {
        document.querySelectorAll(".wujia-header-cart-count").forEach(function (b) {
            b.textContent = count;
            b.classList.toggle("is-active", count > 0);
        });
    }

    function updateLineSubtotal(row) {
        const unit = parseInt(row.dataset.unitPrice || "0", 10);
        const qtyEl = row.querySelector(".wj-pc-cart-qty");
        const qty = qtyEl ? (parseInt(qtyEl.textContent, 10) || 0) : 0;
        const subEl = row.querySelector(".wj-pc-cart-subtotal");
        if (subEl) subEl.textContent = formatVnd(unit * qty) + " đ";
    }

    /* Sync the catalog-side add button badge + row highlight when the cart changes
       (combined page only; no-op on the standalone cart page). */
    function syncCatalogBadge(tmplId, qty) {
        if (!tmplId) return;
        const addBtn = document.querySelector('.wj-pc-order-add[data-product-id="' + tmplId + '"]');
        if (!addBtn) return;
        const badge = addBtn.querySelector(".wj-pc-order-add-badge");
        if (badge) {
            badge.textContent = qty;
            badge.classList.toggle("d-none", qty <= 0);
        }
        const row = addBtn.closest(".wj-pc-order-row");
        if (row) row.classList.toggle("wj-pc-order-row--incart", qty > 0);
    }

    function recomputeTotals() {
        const rows = document.querySelectorAll(".wj-pc-cart-row");
        let grand = 0, count = 0;
        rows.forEach(function (r) {
            const unit = parseInt(r.dataset.unitPrice || "0", 10);
            const qEl = r.querySelector(".wj-pc-cart-qty");
            const q = qEl ? (parseInt(qEl.textContent, 10) || 0) : 0;
            grand += unit * q;
            count += 1;
        });
        const g = document.querySelector(".wj-pc-cart-grand");
        if (g) g.textContent = formatVnd(grand) + " đ";
        const txt = count + " sản phẩm";
        const c = document.querySelector(".wj-pc-cart-count");
        if (c) c.textContent = txt;
        const tq = document.querySelector(".wj-pc-cart-total-qty");
        if (tq) tq.textContent = txt;
    }

    document.addEventListener("DOMContentLoaded", function () {
        // Stepper − / +
        document.querySelectorAll(".wj-pc-cart-step").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const row = btn.closest(".wj-pc-cart-row");
                if (!row) return;
                const qtyEl = row.querySelector(".wj-pc-cart-qty");
                const lineId = parseInt(row.dataset.lineId, 10);
                const tmplId = row.dataset.productTmplId;
                const cur = qtyEl ? (parseInt(qtyEl.textContent, 10) || 0) : 0;
                const next = Math.max(0, cur + (btn.dataset.action === "inc" ? 1 : -1));
                if (next === cur) return;
                btn.disabled = true;
                jsonRpc("/portal/order/cart/update", { line_id: lineId, qty: next })
                    .then(function (res) {
                        btn.disabled = false;
                        if (res.error) return;
                        if (res.removed) {
                            row.remove();
                        } else {
                            if (qtyEl) qtyEl.textContent = next;
                            updateLineSubtotal(row);
                        }
                        syncCatalogBadge(tmplId, res.removed ? 0 : next);
                        recomputeTotals();
                        refreshHeaderBadge(res.cart_count);
                        if (res.cart_count === 0) location.reload();
                    })
                    .catch(function () { btn.disabled = false; });
            });
        });

        // Remove line (trash)
        document.querySelectorAll(".wj-pc-cart-del").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const row = btn.closest(".wj-pc-cart-row");
                if (!row) return;
                const lineId = parseInt(row.dataset.lineId, 10);
                const tmplId = row.dataset.productTmplId;
                if (!confirm("Xoá sản phẩm này khỏi giỏ?")) return;
                jsonRpc("/portal/order/cart/remove", { line_id: lineId })
                    .then(function (res) {
                        if (res.error) return;
                        row.remove();
                        syncCatalogBadge(tmplId, 0);
                        recomputeTotals();
                        refreshHeaderBadge(res.cart_count);
                        if (res.cart_count === 0) location.reload();
                    });
            });
        });
    });
})();
