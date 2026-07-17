/* Return form — image preview + order→product cascade (single-product, Sprint K1).
   Form submit là multipart standard, không cần JS intercept. */
(function () {
    "use strict";
    document.addEventListener("DOMContentLoaded", function () {
        // Image preview
        const fileInput = document.querySelector('input[name="images"]');
        const grid = document.getElementById("image-preview-grid");
        if (fileInput && grid) {
            fileInput.addEventListener("change", function () {
                grid.innerHTML = "";
                Array.from(fileInput.files).slice(0, 12).forEach(function (file) {
                    if (!file.type.startsWith("image/")) return;
                    const url = URL.createObjectURL(file);
                    const col = document.createElement("div");
                    col.className = "col-3 col-md-2";
                    col.innerHTML = `<img src="${url}" class="img-fluid rounded"/>`;
                    grid.appendChild(col);
                });
            });
        }

        // Cascade: đơn hàng gốc → sản phẩm (dòng đơn). data-lines = JSON {orderId: [{id,label}]}.
        document.querySelectorAll("select.wj-return-order").forEach(function (orderSel) {
            let lineMap = {};
            try {
                lineMap = JSON.parse(orderSel.dataset.lines || "{}");
            } catch (e) {
                lineMap = {};
            }
            const form = orderSel.closest("form");
            const lineSel = form && form.querySelector("select.wj-return-line");
            if (!lineSel) return;

            function refill() {
                const lines = lineMap[orderSel.value] || [];
                lineSel.innerHTML = "";
                const ph = document.createElement("option");
                ph.value = "";
                ph.textContent = lines.length ? "— Chọn sản phẩm —" : "— Đơn không có sản phẩm —";
                lineSel.appendChild(ph);
                lines.forEach(function (l) {
                    const opt = document.createElement("option");
                    opt.value = l.id;
                    opt.textContent = l.label;
                    lineSel.appendChild(opt);
                });
            }
            orderSel.addEventListener("change", refill);
            if (orderSel.value) refill();
        });
    });
})();
