/* WujiaTea Portal Exam — desktop "Đăng ký thi" (Figma WJ_Exam_PC v1.2).
   UI-only: không gọi backend. Chỉ điều khiển các state của frame 07_UIStates
   (loading lịch / tháng rỗng / ngày rỗng / validation / đang gửi / xung đột /
   thành công) và 2 modal 03 + 04.

   >>> PC submit deferred — Sprint 45 wire MOBILE-first (list/chi tiết/kết quả PC
   đã đọc dữ liệu thật do server render, không cần JS). Sprint sau: thay 3 hàm
   mock cuối file (renderMonth / bindSlots / send handler) bằng lời gọi JSON-RPC
   /portal/exam/calendar, /portal/exam/slots, /portal/exam/register (đã tồn tại). */
(function () {
    "use strict";

    const MONTHS_WITH_SCHEDULE = 0;   // offset 0 = tháng demo duy nhất có lịch

    function qs(root, sel) { return root.querySelector(sel); }
    function qsa(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }
    function show(el) { if (el) { el.hidden = false; } }
    function hide(el) { if (el) { el.hidden = true; } }
    function pad2(n) { return (n < 10 ? "0" : "") + n; }

    function init(root) {
        const cal        = qs(root, "[data-wj-exam-cal]");
        const calBody    = qs(root, "[data-wj-exam-cal-body]");
        const calSkel    = qs(root, "[data-wj-exam-cal-skel]");
        const calEmpty   = qs(root, "[data-wj-exam-cal-empty]");
        const calLabel   = cal ? qs(cal, ".wj-exam-pc-cal__label") : null;
        const slotList   = qs(root, "[data-wj-exam-slot-list]");
        const slotEmpty  = qs(root, "[data-wj-exam-slot-empty]");
        const slotTitle  = qs(root, ".wj-exam-pc-slots__title");
        const partBody   = qs(root, "[data-wj-exam-part-body]");
        const sendHint   = qs(root, "[data-wj-exam-send-hint]");
        const conflict   = qs(root, "[data-wj-exam-conflict]");
        const success    = qs(root, "[data-wj-exam-success]");
        const phoneErr   = qs(root, "[data-wj-exam-phone-err]");
        const fieldHelp  = qs(root, "[data-wj-exam-field-help]");
        const sumValues  = qsa(root, ".wj-exam-pc-sumkv__value");

        /* Tháng gốc do server render — dùng lại khi người dùng quay về. */
        const baseLabel = calLabel ? calLabel.textContent.trim() : "";
        const baseGrid  = calBody ? calBody.innerHTML : "";
        const baseMonth = parseLabel(baseLabel);
        let monthOffset = 0;
        let skelTimer = null;

        function parseLabel(text) {
            const m = /Tháng\s+(\d+)\s+(\d{4})/.exec(text || "");
            return m ? { month: parseInt(m[1], 10), year: parseInt(m[2], 10) }
                     : { month: 1, year: 2026 };
        }

        function labelFor(offset) {
            const idx = (baseMonth.month - 1) + offset;
            const year = baseMonth.year + Math.floor(idx / 12);
            const month = ((idx % 12) + 12) % 12 + 1;
            return "Tháng " + month + " " + year;
        }

        /* ---------- 1. Đang tải lịch → 2. Tháng chưa có lịch ---------- */
        function renderMonth(offset) {
            monthOffset = offset;
            if (calLabel) { calLabel.textContent = labelFor(offset); }
            hide(calBody);
            hide(calEmpty);
            show(calSkel);
            window.clearTimeout(skelTimer);
            skelTimer = window.setTimeout(function () {
                hide(calSkel);
                if (offset === MONTHS_WITH_SCHEDULE) {
                    if (calBody) { calBody.innerHTML = baseGrid; }
                    show(calBody);
                    bindDays();
                    hide(slotEmpty);
                    if (slotList) { slotList.hidden = false; }
                } else {
                    show(calEmpty);
                    /* 3. ngày không còn khung giờ khả dụng */
                    if (slotList) { slotList.hidden = true; }
                    show(slotEmpty);
                }
            }, 550);
        }

        qsa(root, "[data-wj-exam-month]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                renderMonth(monthOffset + (btn.dataset.wjExamMonth === "prev" ? -1 : 1));
            });
        });

        /* ---------- Chọn ngày ---------- */
        function selectedDayText() {
            const day = qs(root, ".wj-exam-pc-day.is-selected");
            if (!day) { return ""; }
            const m = parseLabel(calLabel ? calLabel.textContent : baseLabel);
            return pad2(parseInt(day.dataset.wjExamDay, 10)) + "/" + pad2(m.month) + "/" + m.year;
        }

        function bindDays() {
            qsa(root, ".wj-exam-pc-day--available").forEach(function (day) {
                day.addEventListener("click", function () {
                    qsa(root, ".wj-exam-pc-day").forEach(function (d) {
                        d.classList.remove("is-selected");
                        const dot = qs(d, ".wj-exam-pc-day__dot");
                        if (d.classList.contains("wj-exam-pc-day--available") && !dot) {
                            const i = document.createElement("i");
                            i.className = "wj-exam-pc-day__dot";
                            d.appendChild(i);
                        }
                    });
                    day.classList.add("is-selected");
                    const dot = qs(day, ".wj-exam-pc-day__dot");
                    if (dot) { dot.remove(); }
                    if (slotTitle) { slotTitle.textContent = "Khung giờ ngày " + selectedDayText(); }
                    hide(conflict);
                    syncSummary();
                });
            });
        }
        bindDays();

        /* ---------- Chọn khung giờ ---------- */
        function bindSlots() {
            qsa(root, ".wj-exam-pc-slot--open").forEach(function (slot) {
                slot.addEventListener("click", function () {
                    qsa(root, ".wj-exam-pc-slot").forEach(function (s) { s.classList.remove("is-selected"); });
                    slot.classList.add("is-selected");
                    hide(conflict);
                    syncSummary();
                });
            });
        }
        bindSlots();

        /* Cột phải: ô thứ 2 là "Ngày & giờ thi". */
        function syncSummary() {
            const slot = qs(root, ".wj-exam-pc-slot.is-selected");
            const date = selectedDayText();
            if (sumValues.length > 1 && date && slot) {
                const time = qs(slot, ".wj-exam-pc-slot__time");
                sumValues[1].textContent = date + " · " + (time ? time.textContent.trim() : "");
            }
        }

        /* "Chọn ngày khác" / "Chọn khung giờ khác" — đưa người dùng về lịch. */
        qsa(root, "[data-wj-exam-pick-other-day], [data-wj-exam-pick-other-slot]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                hide(conflict);
                if (cal) { cal.scrollIntoView({ behavior: "smooth", block: "center" }); }
            });
        });

        /* ---------- Modal 03 + 04 ---------- */
        function openModal(name) {
            const modal = qs(root, '[data-wj-exam-modal="' + name + '"]');
            if (!modal) { return; }
            show(modal);
            document.body.style.overflow = "hidden";
            const first = qs(modal, "input, select, textarea");
            if (first) { first.focus(); }
        }

        function closeModals() {
            qsa(root, "[data-wj-exam-modal]").forEach(hide);
            document.body.style.overflow = "";
        }

        qsa(root, "[data-wj-exam-open]").forEach(function (btn) {
            btn.addEventListener("click", function () { openModal(btn.dataset.wjExamOpen); });
        });
        qsa(root, "[data-wj-exam-close]").forEach(function (btn) {
            btn.addEventListener("click", function () { closeModals(); });
        });
        qsa(root, "[data-wj-exam-modal]").forEach(function (modal) {
            modal.addEventListener("click", function (ev) {
                if (ev.target === modal) { closeModals(); }
            });
        });
        document.addEventListener("keydown", function (ev) {
            if (ev.key === "Escape") { closeModals(); }
        });

        /* ---------- 5. Validation người tham gia ---------- */
        const addBtn = qs(root, ".wj-exam-pc-mbtn--add");
        const nameInput = qs(root, "#wj_exam_p_name");
        const phoneInput = qs(root, "#wj_exam_p_phone");
        if (addBtn) {
            addBtn.addEventListener("click", function (ev) {
                const name = nameInput ? nameInput.value.trim() : "";
                const phone = phoneInput ? phoneInput.value.trim() : "";
                const phoneOk = /^[0-9 .+-]{9,15}$/.test(phone);
                if (!name || !phoneOk) {
                    ev.stopImmediatePropagation();
                    ev.preventDefault();
                    if (phoneInput) {
                        phoneInput.closest(".wj-pc-field").classList.toggle("is-invalid", !phoneOk);
                    }
                    if (nameInput) {
                        nameInput.closest(".wj-pc-field").classList.toggle("is-invalid", !name);
                    }
                    if (!phoneOk) { show(phoneErr); } else { hide(phoneErr); }
                    show(fieldHelp);
                    return;
                }
                hide(phoneErr);
                hide(fieldHelp);
                qsa(root, ".wj-exam-pc-formgrid .wj-pc-field").forEach(function (f) {
                    f.classList.remove("is-invalid");
                });
            }, true);
        }

        /* ---------- Xóa dòng người tham gia (client-side) ---------- */
        if (partBody) {
            partBody.addEventListener("click", function (ev) {
                const btn = ev.target.closest("[data-wj-exam-line-remove]");
                if (!btn) { return; }
                const row = btn.closest("tr");
                if (row) { row.remove(); }
            });
        }

        /* ---------- Xem trước ảnh nhân viên (FileReader, không upload) ---------- */
        const thumb = qs(root, ".wj-exam-pc-thumb");
        const fileName = qs(root, ".wj-exam-pc-photobox__file");
        const changeBtn = qs(root, ".wj-exam-pc-photobtn");
        const delBtn = qs(root, ".wj-exam-pc-photobtn--del");
        if (changeBtn && thumb) {
            const picker = document.createElement("input");
            picker.type = "file";
            picker.accept = "image/png,image/jpeg";
            picker.hidden = true;
            root.appendChild(picker);
            changeBtn.addEventListener("click", function () { picker.click(); });
            picker.addEventListener("change", function () {
                const file = picker.files && picker.files[0];
                if (!file) { return; }
                const reader = new FileReader();
                reader.onload = function () {
                    thumb.innerHTML = "";
                    const img = document.createElement("img");
                    img.src = reader.result;
                    img.alt = file.name;
                    img.style.cssText = "width:100%;height:100%;object-fit:cover;border-radius:inherit;";
                    thumb.appendChild(img);
                };
                reader.readAsDataURL(file);
                if (fileName) {
                    fileName.textContent = file.name + " · " + (file.type.split("/")[1] || "").toUpperCase();
                }
            });
        }
        if (delBtn && thumb) {
            delBtn.addEventListener("click", function () {
                thumb.innerHTML = '<i class="feather icon-user"></i>';
                if (fileName) { fileName.textContent = "Chưa chọn ảnh"; }
            });
        }

        /* ---------- 6. Đang gửi → 8. Thành công ---------- */
        const sendBtn = qs(root, "[data-wj-exam-send]");
        if (sendBtn) {
            sendBtn.addEventListener("click", function (ev) {
                ev.stopImmediatePropagation();
                const label = sendBtn.textContent;
                sendBtn.disabled = true;
                sendBtn.textContent = sendBtn.dataset.wjExamBusyLabel || "Đang gửi yêu cầu...";
                show(sendHint);
                window.setTimeout(function () {
                    sendBtn.disabled = false;
                    sendBtn.textContent = label;
                    hide(sendHint);
                    closeModals();
                    hide(conflict);
                    show(success);
                    if (success) { success.scrollIntoView({ behavior: "smooth", block: "center" }); }
                }, 900);
            }, true);
        }

        /* ---------- Đổi khóa thi → tải lại lịch ---------- */
        const course = qs(root, "[data-wj-exam-course]");
        if (course) {
            course.addEventListener("change", function () { renderMonth(monthOffset); });
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        qsa(document, '[data-wj-exam-pc="register"]').forEach(init);
    });
})();
