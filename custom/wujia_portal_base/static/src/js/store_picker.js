/* WujiaTea Portal — store picker
   Mở modal chặn khi must_pick_franchise=True (multi-franchise + chưa chọn).
   Vanilla JS, không phụ thuộc Bootstrap JS API (dùng class fallback nếu chưa có). */
(function () {
    "use strict";
    document.addEventListener("DOMContentLoaded", function () {
        const modal = document.getElementById("wujiaStorePickerModal");
        if (!modal) return;

        const mustPick = document.body.dataset.mustPickFranchise === "1";
        const useBootstrap = window.bootstrap && window.bootstrap.Modal;

        function showModal() {
            if (useBootstrap) {
                const m = window.bootstrap.Modal.getOrCreateInstance(modal, {
                    backdrop: "static",
                    keyboard: false,
                });
                m.show();
            } else {
                // Fallback nếu Bootstrap JS chưa load — show via class manipulation
                modal.classList.add("show", "d-block");
                modal.style.display = "block";
                document.body.classList.add("modal-open");
                if (!document.querySelector(".modal-backdrop")) {
                    const bd = document.createElement("div");
                    bd.className = "modal-backdrop fade show";
                    document.body.appendChild(bd);
                }
            }
        }

        if (mustPick) {
            showModal();
        }

        // Trigger button "Đổi cửa hàng" trên top navbar
        document.querySelectorAll('[data-action="open-store-picker"]').forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                showModal();
            });
        });

        // UX: highlight radio item khi chọn
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
    });
})();
