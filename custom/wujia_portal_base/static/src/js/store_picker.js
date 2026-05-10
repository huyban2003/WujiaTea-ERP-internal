/* WujiaTea Portal — store picker overlay toggle.
   - Modal đã render SSR trong DOM (luôn có nếu user multi-franchise).
   - Khi must_pick=True: server đã thêm class wujia-store-overlay--show.
   - Click button "Đổi cửa hàng" trên top navbar → toggle class.
   - Click nút × hoặc Hủy → ẩn (chỉ khi user đã pick — lúc must_pick thì
     không có button đóng → không thoát được).
   - Click nền (overlay) ngoài card cũng ẩn (chỉ khi đã pick). */
(function () {
    "use strict";

    function init() {
        const overlay = document.getElementById("wujiaStoreOverlay");
        if (!overlay) return;

        function show() {
            overlay.classList.add("wujia-store-overlay--show");
        }
        function hide() {
            overlay.classList.remove("wujia-store-overlay--show");
        }

        // Trigger từ badge top navbar / button "Đổi cửa hàng"
        document.querySelectorAll('[data-action="open-store-picker"]').forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                show();
            });
        });

        // Nút × và Hủy đóng modal (chỉ tồn tại khi must_pick=False)
        overlay.querySelectorAll('[data-action="close-store-picker"]').forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                hide();
            });
        });

        // Click nền (overlay) đóng nếu cho phép — phát hiện qua data-action close
        // sự tồn tại của nút Hủy trong card thì cho phép đóng nền.
        const allowDismissOnBackdrop = overlay.querySelector('[data-action="close-store-picker"]') !== null;
        if (allowDismissOnBackdrop) {
            overlay.addEventListener("click", function (ev) {
                if (ev.target === overlay) hide();
            });
        }

        // UX: highlight item khi click, sync radio
        overlay.querySelectorAll(".wujia-store-item").forEach(function (item) {
            item.addEventListener("click", function () {
                overlay.querySelectorAll(".wujia-store-item").forEach(function (it) {
                    it.classList.remove("wujia-store-item--active");
                });
                item.classList.add("wujia-store-item--active");
                const radio = item.querySelector(".wujia-store-radio");
                if (radio) radio.checked = true;
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
