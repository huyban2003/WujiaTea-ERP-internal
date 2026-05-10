/* WujiaTea Portal — store picker
   Hỗ trợ cả Bootstrap 4 (jQuery $.fn.modal) và Bootstrap 5 (window.bootstrap.Modal).
   Vuexy theme dùng BS4. Fallback manual class manipulation nếu cả hai không có. */
(function () {
    "use strict";

    function showModalNow() {
        const modal = document.getElementById("wujiaStorePickerModal");
        if (!modal) return;

        // 1. Bootstrap 5 (window.bootstrap)
        if (window.bootstrap && window.bootstrap.Modal) {
            const m = window.bootstrap.Modal.getOrCreateInstance(modal, {
                backdrop: "static", keyboard: false,
            });
            m.show();
            return;
        }

        // 2. Bootstrap 4 (jQuery $.fn.modal — Vuexy theme dùng cái này)
        if (window.jQuery && window.jQuery.fn && window.jQuery.fn.modal) {
            window.jQuery(modal).modal({ backdrop: "static", keyboard: false });
            return;
        }

        // 3. Fallback manual — class + inline style + backdrop div
        modal.classList.add("show", "d-block");
        modal.setAttribute("aria-hidden", "false");
        modal.setAttribute("role", "dialog");
        modal.style.cssText = "display: block !important; padding-right: 17px;";
        document.body.classList.add("modal-open");
        if (!document.querySelector(".wujia-store-picker-backdrop")) {
            const bd = document.createElement("div");
            bd.className = "modal-backdrop fade show wujia-store-picker-backdrop";
            bd.style.cssText = "z-index: 1040;";
            document.body.appendChild(bd);
        }
        modal.style.zIndex = "1050";
    }

    function highlightSelectedRadio(modal) {
        modal.querySelectorAll(".store-picker-item").forEach(function (item) {
            item.addEventListener("click", function () {
                modal.querySelectorAll(".store-picker-item").forEach(function (it) {
                    it.classList.remove("active");
                });
                item.classList.add("active");
                const radio = item.querySelector(".store-picker-radio");
                if (radio) radio.checked = true;
            });
        });
    }

    function init() {
        const modal = document.getElementById("wujiaStorePickerModal");
        if (!modal) return;

        const mustPick = document.body.dataset.mustPickFranchise === "1";
        if (mustPick) {
            showModalNow();
        }

        // Trigger button "Đổi cửa hàng" trên top navbar
        document.querySelectorAll('[data-action="open-store-picker"]').forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                showModalNow();
            });
        });

        highlightSelectedRadio(modal);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        // DOM đã sẵn — chạy ngay (trường hợp script load defer SAU DOMContentLoaded)
        init();
    }
})();
