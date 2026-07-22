/* WujiaTea Portal — Cart sync (Sprint 31).

   Giỏ chung theo store. Module gom tương tác giỏ (stepper/xoá/ghi chú) qua EVENT
   DELEGATION trên document + reconcile CÙNG-TAB không reload: mỗi mutation → fetch lại
   partial giỏ (server-render `/portal/order/cart/fragment`, 1 nguồn QWeb) → swap DOM +
   cập nhật badge/floatbar/header. Số liệu qty/giá lấy TỪ server (pricelist có bậc).

   CROSS-SESSION realtime (subscribe bus `wujia_cart_changed`) TẠM TẮT — xem block
   comment `willStart` dưới (gây banner "page out of date" khi WebSocket chưa sẵn). */
import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

function formatVnd(n) {
    return String(Math.round(n || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function debounce(fn, wait) {
    let t;
    return function (...args) {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), wait);
    };
}

export class WujiaCartSync extends Interaction {
    static selector = "#wj-cart-sync";

    setup() {
        this.franchiseId = parseInt(this.el.dataset.franchiseId, 10) || null;
        this._refreshing = false;
        this._queued = false;
        this._chain = Promise.resolve();
        this.saveNote = debounce((val) => rpc("/portal/order/cart/note", { note: val }), 600);
        // Catalog add-to-cart (portal_order.js) gọi refresh() sau khi thêm.
        window.WujiaCartSync = this;
        document.addEventListener("click", this.onClick.bind(this));
        document.addEventListener("input", this.onInput.bind(this));
        // WJ-ORD-003: quay lại bằng back/forward (BFCache) → trang khôi phục từ
        // cache có thể hiển thị giỏ cũ → fetch lại state từ server để đồng bộ.
        this._onPageShow = (ev) => { if (ev.persisted) { this.refresh(); } };
        window.addEventListener("pageshow", this._onPageShow);
    }

    // ------------------------------------------------------------------
    // Cross-session realtime (bus.bus) TẠM TẮT — subscribe bus khởi động
    // WebSocket worker; khi hạ tầng WebSocket chưa sẵn (Werkzeug dev / proxy
    // prod chưa route /websocket) worker báo "outdated" → Odoo hiện banner
    // "The page is out of date". Server vẫn publish `wujia_cart_changed` (S30)
    // → bật lại chỉ cần bỏ comment block dưới khi WebSocket đã chạy chắc chắn.
    // Phần cùng-tab (thêm/sửa/xoá giỏ không reload) KHÔNG cần bus, vẫn chạy.
    // ------------------------------------------------------------------
    // async willStart() {
    //     if (!this.franchiseId) { return; }
    //     const bus = this.services.bus_service;
    //     bus.addChannel(`wujia.franchise_${this.franchiseId}`);
    //     bus.subscribe("wujia_cart_changed", this.onCartChanged.bind(this));
    // }
    // onCartChanged(payload) {
    //     if (!payload || payload.franchise_id !== this.franchiseId) { return; }
    //     this.refresh();
    // }

    // -------- tương tác giỏ (delegation) --------
    onClick(ev) {
        const step = ev.target.closest(".wj-pc-cart-step, .wujia-mcart-step");
        if (step) {
            ev.preventDefault();
            this.handleStep(step);
            return;
        }
        const del = ev.target.closest(".wj-pc-cart-del, .wujia-mcart-del");
        if (del) {
            ev.preventDefault();
            this.handleRemove(del);
        }
    }

    onInput(ev) {
        const ta = ev.target.closest(".wj-pc-cart-note");
        if (ta) {
            this.saveNote(ta.value || "");
        }
    }

    handleStep(btn) {
        const row = btn.closest(".wj-pc-cart-row, .wujia-mcart-row");
        if (!row) {
            return;
        }
        const lineId = parseInt(row.dataset.lineId, 10);
        const isInc = btn.dataset.action === "inc" || btn.classList.contains("wujia-mcart-step-plus");
        // WJ-ORD-002: gửi HƯỚNG, server cộng delta = ±min_qty NGUYÊN TỬ (không
        // set qty tuyệt đối) → 2 lần giảm gần đồng thời áp tuần tự, không lost
        // update. Bound min/max do server enforce (dưới min → xoá dòng, chạm
        // max → cap + cảnh báo). Giảm ở min = xoá dòng (đồng nhất hành vi cũ).
        this.mutate("/portal/order/cart/step", { line_id: lineId, direction: isInc ? "inc" : "dec" });
    }

    handleRemove(btn) {
        const row = btn.closest(".wj-pc-cart-row, .wujia-mcart-row");
        if (!row) {
            return;
        }
        const lineId = parseInt(row.dataset.lineId, 10);
        if (!window.confirm("Xoá sản phẩm này khỏi giỏ?")) {
            return;
        }
        this.mutate("/portal/order/cart/remove", { line_id: lineId });
    }

    mutate(url, params) {
        // WJ-ORD-002: KHÔNG drop khi đang chạy — NỐI ĐUÔI (queue) để mỗi lần
        // bấm là 1 delta được áp tuần tự (server cộng nguyên tử). _doMutate tự
        // nuốt lỗi nên chain không bao giờ reject/đứt.
        this._chain = this._chain.then(() => this._doMutate(url, params));
        return this._chain;
    }

    async _doMutate(url, params) {
        try {
            const res = await rpc(url, params);
            if (!res || res.error) {
                this.toast((res && res.message) || "Có lỗi xảy ra, vui lòng thử lại", false);
                return;
            }
            if (res.warning && res.message) {
                this.toast(res.message, false);
            }
            await this.refresh();
        } catch (e) {
            this.toast("Lỗi kết nối", false);
        }
    }

    // -------- fetch state + swap partial (coalesce overlapping) --------
    async refresh() {
        if (this._refreshing) {
            this._queued = true;
            return;
        }
        this._refreshing = true;
        try {
            const res = await rpc("/portal/order/cart/fragment", {});
            if (res && !res.error) {
                this.apply(res);
            }
        } catch (e) {
            // im lặng — lần refresh sau (hoặc reload) sẽ đồng bộ lại
        } finally {
            this._refreshing = false;
            if (this._queued) {
                this._queued = false;
                this.refresh();
            }
        }
    }

    apply(res) {
        const noteFocused = this.isNoteFocused();
        // Swap panel giỏ (giữ nguyên khi user đang gõ ghi chú → không mất focus/nội dung)
        const pc = document.querySelector(".wj-pc-cart");
        if (pc && res.pc_html && !noteFocused) {
            pc.outerHTML = res.pc_html;
        }
        const mc = document.querySelector(".wujia-mcart");
        if (mc && res.mobile_html) {
            mc.innerHTML = res.mobile_html;
        }
        this.applyState(res);
    }

    applyState(res) {
        const count = res.line_count || 0;
        // Header cart badge (mọi trang portal có header)
        document.querySelectorAll(".wujia-header-cart-count").forEach((b) => {
            b.textContent = count;
            b.classList.toggle("is-active", count > 0);
        });
        // Badge nút thêm trên catalog (PC + mobile) + highlight dòng in-cart
        const qmap = res.qty_map || {};
        document.querySelectorAll(".btn-add-cart[data-product-id]").forEach((btn) => {
            const pid = parseInt(btn.dataset.productId, 10);
            const qty = qmap[pid] || 0;
            const badge = btn.querySelector(".wj-pc-order-add-badge, .wujia-morder-row-qty");
            if (badge) {
                badge.textContent = qty;
                badge.classList.toggle("d-none", qty <= 0);
            }
            const pcRow = btn.closest(".wj-pc-order-row");
            if (pcRow) {
                pcRow.classList.toggle("wj-pc-order-row--incart", qty > 0);
            }
        });
        // Floating cart bar mobile
        const fb = document.querySelector(".wujia-morder-floatbar");
        if (fb) {
            fb.classList.toggle("d-none", count <= 0);
            fb.dataset.cartTotal = Math.round(res.total_amount || 0);
            const c = fb.querySelector(".wujia-morder-floatbar-count");
            if (c) {
                c.textContent = count;
            }
            const t = fb.querySelector(".wujia-morder-floatbar-total");
            if (t) {
                t.textContent = formatVnd(res.total_amount);
            }
        }
    }

    isNoteFocused() {
        const a = document.activeElement;
        return !!(a && a.classList && a.classList.contains("wj-pc-cart-note"));
    }

    toast(msg, ok) {
        const el = document.createElement("div");
        el.className = "alert alert-" + (ok ? "success" : "danger");
        el.style.cssText = "position:fixed;top:20px;right:20px;z-index:9999;min-width:240px;";
        el.textContent = msg;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 2500);
    }
}

registry
    .category("public.interactions")
    .add("wujia_portal_sale.cart_sync", WujiaCartSync);
