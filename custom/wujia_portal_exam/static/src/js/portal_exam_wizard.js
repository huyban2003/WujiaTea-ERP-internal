/* ============================================================================
   Sprint 26 — Mobile "Đăng ký thi" wizard (Figma #4755:2, s1→s5). UI-only.
   Single-page: 4 step panels [data-exam-step] toggled client-side + bottom-sheet
   "Chọn khung giờ". No backend persistence — submit = toast + redirect.
   ========================================================================== */
(function (window, document) {
    'use strict';

    function init() {
        var wizard = document.querySelector('.wujia-mexam-wizard');
        if (!wizard) {
            return;
        }

        var panels = wizard.querySelectorAll('[data-exam-step]');
        var sheet = wizard.querySelector('.wujia-mexam-sheet');
        var backdrop = wizard.querySelector('.wujia-mexam-sheet-backdrop');
        var confirmSlotBtn = wizard.querySelector('[data-exam-slot-confirm]');
        var courseName = (wizard.querySelector('.wujia-mexam-selcard-title') || {}).textContent || '';
        courseName = courseName.trim();

        var pendingDate = '';   // "Thứ 5, 02/07/2026" (day đang bấm)
        var pendingSlot = '';   // "08:20"
        var chosenDate = '';    // đã xác nhận khung giờ
        var chosenSlot = '';

        /* ---------- Step navigation ---------- */
        function showStep(n) {
            panels.forEach(function (p) {
                if (p.getAttribute('data-exam-step') === String(n)) {
                    p.removeAttribute('hidden');
                } else {
                    p.setAttribute('hidden', 'hidden');
                }
            });
            window.scrollTo(0, 0);
        }

        /* ---------- Bottom-sheet khung giờ ---------- */
        function openSheet() {
            sheet.classList.add('is-open');
            backdrop.classList.add('is-open');
            document.body.classList.add('wujia-msheet-open');
        }
        function closeSheet() {
            sheet.classList.remove('is-open');
            backdrop.classList.remove('is-open');
            document.body.classList.remove('wujia-msheet-open');
        }
        function selectSlot(btn) {
            wizard.querySelectorAll('.wujia-mexam-slot').forEach(function (s) {
                s.classList.remove('is-selected');
            });
            btn.classList.add('is-selected');
            pendingSlot = btn.getAttribute('data-exam-slot') || '';
            if (confirmSlotBtn) {
                confirmSlotBtn.disabled = false;
            }
        }

        /* ---------- People ---------- */
        function renumberPeople() {
            wizard.querySelectorAll('.wujia-mexam-person').forEach(function (p, i) {
                var nameEl = p.querySelector('.wujia-mexam-person-name');
                if (nameEl) {
                    nameEl.textContent = 'Nhân sự ' + (i + 1);
                }
            });
        }
        function personMarkup() {
            return '' +
                '<div class="wujia-mexam-person-head">' +
                '  <span class="wujia-mexam-person-name">Nhân sự</span>' +
                '  <span class="wujia-mexam-person-tools">' +
                '    <a href="#" class="wujia-mexam-person-toggle" data-exam-person-toggle="1">Nhập thông tin</a>' +
                '    <button type="button" class="wujia-mexam-person-del" data-exam-person-del="1"><i class="feather icon-trash-2"></i></button>' +
                '  </span>' +
                '</div>' +
                '<div class="wujia-mexam-person-body" hidden="hidden">' +
                '  <input class="wujia-mexam-field" placeholder="Họ và tên"/>' +
                '  <input class="wujia-mexam-field" placeholder="Số điện thoại"/>' +
                '  <div class="wujia-mexam-field-row">' +
                '    <input class="wujia-mexam-field" placeholder="Năm sinh"/>' +
                '    <input class="wujia-mexam-field" placeholder="Chức vụ"/>' +
                '  </div>' +
                '  <p class="wujia-mexam-person-hint">Thông tin dùng để ghi nhận kết quả thi.</p>' +
                '</div>';
        }
        function togglePerson(link) {
            var person = link.closest('.wujia-mexam-person');
            var body = person.querySelector('.wujia-mexam-person-body');
            var open = person.classList.toggle('is-open');
            if (open) {
                body.removeAttribute('hidden');
                link.textContent = 'Thu gọn';
            } else {
                body.setAttribute('hidden', 'hidden');
                link.textContent = 'Nhập thông tin';
            }
        }

        /* ---------- Toast (giống portal_exam.js) ---------- */
        function toast(msg) {
            var el = document.createElement('div');
            el.className = 'alert alert-success';
            el.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);z-index:9999;min-width:240px;text-align:center;';
            el.textContent = msg;
            document.body.appendChild(el);
            setTimeout(function () { el.remove(); }, 2400);
        }

        /* ---------- Course filter chips (s1) ---------- */
        function filterCourses(mode, chip) {
            wizard.querySelectorAll('[data-exam-cfilter]').forEach(function (c) {
                c.classList.remove('is-active');
            });
            chip.classList.add('is-active');
            wizard.querySelectorAll('.wujia-mexam-course').forEach(function (course) {
                var closed = course.getAttribute('data-exam-closed') === '1';
                var show = mode === 'all' ||
                    (mode === 'open' && !closed) ||
                    (mode === 'closed' && closed);
                course.style.display = show ? '' : 'none';
            });
        }

        /* ---------- Delegated click ---------- */
        wizard.addEventListener('click', function (ev) {
            var t = ev.target;

            var goto = t.closest('[data-exam-goto]');
            if (goto) {
                ev.preventDefault();
                showStep(goto.getAttribute('data-exam-goto'));
                return;
            }
            var day = t.closest('[data-exam-open-slots]');
            if (day) {
                ev.preventDefault();
                wizard.querySelectorAll('.wujia-mexam-cal-day.is-available').forEach(function (d) {
                    d.classList.remove('is-selected');
                });
                day.classList.add('is-selected');
                pendingDate = day.getAttribute('data-exam-date') || '';
                var sub = wizard.querySelector('[data-exam-slot-sub]');
                if (sub) {
                    sub.textContent = pendingDate + (courseName ? ' • ' + courseName : '');
                }
                openSheet();
                return;
            }
            var slot = t.closest('[data-exam-slot]');
            if (slot && !slot.classList.contains('is-disabled')) {
                ev.preventDefault();
                selectSlot(slot);
                return;
            }
            if (t.closest('[data-exam-slot-close]')) {
                ev.preventDefault();
                closeSheet();
                return;
            }
            if (t.closest('[data-exam-slot-confirm]')) {
                ev.preventDefault();
                if (!pendingSlot) { return; }
                chosenDate = pendingDate;
                chosenSlot = pendingSlot;
                var line = wizard.querySelector('[data-exam-sched-line]');
                if (line) { line.textContent = chosenDate + ' • ' + chosenSlot; }
                var cfDate = wizard.querySelector('[data-exam-cf-date]');
                if (cfDate) { cfDate.textContent = chosenDate; }
                var cfSlot = wizard.querySelector('[data-exam-cf-slot]');
                if (cfSlot) { cfSlot.textContent = chosenSlot; }
                closeSheet();
                showStep(3);
                return;
            }
            var toggle = t.closest('[data-exam-person-toggle]');
            if (toggle) {
                ev.preventDefault();
                togglePerson(toggle);
                return;
            }
            var del = t.closest('[data-exam-person-del]');
            if (del) {
                ev.preventDefault();
                var person = del.closest('.wujia-mexam-person');
                if (person) { person.remove(); renumberPeople(); }
                return;
            }
            if (t.closest('[data-exam-add-person]')) {
                ev.preventDefault();
                var list = wizard.querySelector('[data-exam-personlist]');
                if (list) {
                    var node = document.createElement('div');
                    node.className = 'wujia-mexam-person';
                    node.innerHTML = personMarkup();
                    list.appendChild(node);
                    renumberPeople();
                }
                return;
            }
            var chip = t.closest('[data-exam-cfilter]');
            if (chip) {
                ev.preventDefault();
                filterCourses(chip.getAttribute('data-exam-cfilter'), chip);
                return;
            }
            if (t.closest('[data-exam-submit]')) {
                ev.preventDefault();
                toast('Đã gửi yêu cầu đăng ký!');
                setTimeout(function () { window.location = '/portal/exam'; }, 1200);
                return;
            }
        });

        document.addEventListener('keydown', function (ev) {
            if (ev.key === 'Escape' && sheet && sheet.classList.contains('is-open')) {
                closeSheet();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(window, document);
