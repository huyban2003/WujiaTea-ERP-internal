/* WujiaTea Portal Order — client-side stub.
   Skeleton: nút "Add to cart" / "Submit" chưa gọi BE thật, chỉ alert placeholder.
   Khi sprint BE workflow xong (Phase 1.0 BE), sẽ thay bằng rpc.call. */
(function () {
    "use strict";
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".btn-add-cart").forEach(function (btn) {
            btn.addEventListener("click", function (ev) {
                ev.preventDefault();
                const card = btn.closest(".product-card");
                const qtyInput = card ? card.querySelector(".product-qty-input") : null;
                const productId = btn.dataset.productId;
                const qty = qtyInput ? qtyInput.value : 1;
                console.info("[portal_order] add-cart placeholder:", { productId, qty });
                btn.classList.add("btn-success");
                btn.classList.remove("btn-primary");
                setTimeout(function () {
                    btn.classList.remove("btn-success");
                    btn.classList.add("btn-primary");
                }, 800);
            });
        });
        const submitBtn = document.querySelector(".btn-submit-order");
        if (submitBtn) {
            submitBtn.addEventListener("click", function (ev) {
                ev.preventDefault();
                console.info("[portal_order] submit-order placeholder");
                alert("Tính năng đặt hàng sẽ được kích hoạt ở sprint BE workflow tiếp theo.");
            });
        }
    });
})();
