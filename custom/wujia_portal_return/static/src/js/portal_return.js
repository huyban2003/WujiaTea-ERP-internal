/* Return form — image preview + add/remove dynamic lines.
   Skeleton: form submit chưa có handler thật, chỉ alert placeholder. */
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

        // Add line
        const btnAdd = document.getElementById("btn-add-line");
        const tbody = document.querySelector("#return-line-table tbody");
        if (btnAdd && tbody) {
            btnAdd.addEventListener("click", function () {
                const tpl = tbody.querySelector(".return-line-row");
                if (!tpl) return;
                const clone = tpl.cloneNode(true);
                clone.querySelectorAll("input").forEach(function (i) { i.value = ""; });
                clone.querySelector('input[name="line_qty[]"]').value = 1;
                tbody.appendChild(clone);
            });
        }

        // Remove line (delegated)
        if (tbody) {
            tbody.addEventListener("click", function (ev) {
                const btn = ev.target.closest(".btn-remove-line");
                if (!btn) return;
                const rows = tbody.querySelectorAll(".return-line-row");
                if (rows.length > 1) {
                    btn.closest(".return-line-row").remove();
                } else {
                    btn.closest(".return-line-row").querySelectorAll("input").forEach(function (i) { i.value = ""; });
                }
            });
        }

        // Submit placeholder
        document.querySelectorAll('form[action="/portal/return/new"]').forEach(function (form) {
            form.addEventListener("submit", function (ev) {
                ev.preventDefault();
                alert("Tính năng gửi yêu cầu đổi trả sẽ được kích hoạt ở sprint BE workflow tiếp theo.");
            });
        });
    });
})();
