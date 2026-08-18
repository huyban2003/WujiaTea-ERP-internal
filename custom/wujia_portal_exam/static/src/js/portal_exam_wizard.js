/* ============================================================================
   Mobile "Đăng ký thi" wizard (Figma #4755:2, s1→s5) — WIRED (Sprint 45).
   4 step panels [data-exam-step] + bottom-sheet khung giờ. Calendar & khung giờ
   nạp thật qua JSON (/portal/exam/calendar, /portal/exam/slots); submit POST
   /portal/exam/register (server-resolve franchise/member/requester, backend tự
   capacity-lock). Lỗi validate/hết chỗ hiện inline thay vì toast giả.
   ========================================================================== */
(function (window, document) {
    'use strict';

    var MAX_PHOTO_BYTES = 5 * 1024 * 1024;
    /* Giống hệt PHONE_RE của model — client chặn trước, server vẫn kiểm lại. */
    var PHONE_RE = /^(0|\+84)[0-9]{8,10}$/;

    function jsonRpc(url, params) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                jsonrpc: '2.0', method: 'call', params: params || {},
            }),
        }).then(function (r) { return r.json(); })
          .then(function (j) { return j.result || {}; });
    }

    function init() {
        var wizard = document.querySelector('.wujia-mexam-wizard');
        if (!wizard) { return; }

        var panels = wizard.querySelectorAll('[data-exam-step]');
        var sheet = wizard.querySelector('.wujia-mexam-sheet');
        var backdrop = wizard.querySelector('.wujia-mexam-sheet-backdrop');
        var confirmSlotBtn = wizard.querySelector('[data-exam-slot-confirm]');
        var grid = wizard.querySelector('[data-exam-cal-grid]');
        var slotList = wizard.querySelector('[data-exam-slotlist]');
        var personList = wizard.querySelector('[data-exam-personlist]');
        var personTpl = personList
            ? personList.querySelector('[data-exam-person]').cloneNode(true) : null;

        var courseId = 0;
        var courseName = '';
        var calYear = grid ? parseInt(grid.getAttribute('data-exam-year'), 10) : 0;
        var calMonth = grid ? parseInt(grid.getAttribute('data-exam-month'), 10) : 0;

        var pendingIso = '';          // ISO ngày đang bấm
        var pendingDateLabel = '';    // "Thứ 5, 02/07/2026"
        var pendingSessionId = 0;
        var pendingTime = '';
        var pendingLoc = '';
        var pendingMax = 0;

        var chosen = { sessionId: 0, dateLabel: '', time: '', loc: '', max: 0 };

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

        /* ---------- Bottom-sheet ---------- */
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

        /* ---------- Calendar render ---------- */
        function renderCalendar(cal) {
            if (!grid || !cal) { return; }
            grid.querySelectorAll('.wujia-mexam-cal-day').forEach(function (d) {
                d.remove();
            });
            (cal.weeks || []).forEach(function (week) {
                week.forEach(function (d) {
                    var node;
                    if (!d.in_month) {
                        node = document.createElement('span');
                        node.className = 'wujia-mexam-cal-day is-out';
                        node.textContent = d.day;
                    } else if (d.state === 'available') {
                        node = document.createElement('button');
                        node.type = 'button';
                        node.className = 'wujia-mexam-cal-day is-available';
                        node.setAttribute('data-exam-date', d.date_label);
                        node.setAttribute('data-exam-iso', d.date);
                        node.setAttribute('data-exam-open-slots', '1');
                        node.innerHTML =
                            '<span class="wujia-mexam-cal-daynum">' + d.day + '</span>' +
                            '<span class="wujia-mexam-cal-daydot"></span>';
                    } else {
                        node = document.createElement('span');
                        node.className = 'wujia-mexam-cal-day is-none';
                        node.textContent = d.day;
                    }
                    grid.appendChild(node);
                });
            });
            var label = wizard.querySelector('[data-exam-cal-label]');
            if (label) { label.textContent = cal.label || ''; }
            calYear = cal.year; calMonth = cal.month;
            grid.setAttribute('data-exam-year', cal.year);
            grid.setAttribute('data-exam-month', cal.month);
        }

        function loadCalendar(year, month) {
            if (!courseId) { return; }
            jsonRpc('/portal/exam/calendar', {
                course_id: courseId, year: year, month: month,
            }).then(function (res) {
                if (res && res.calendar) { renderCalendar(res.calendar); }
            });
        }

        /* ---------- Slots render ---------- */
        function renderSlots(slots) {
            if (!slotList) { return; }
            slotList.innerHTML = '';
            if (!slots || !slots.length) {
                slotList.innerHTML =
                    '<p class="wujia-mexam-slot-empty">Ngày này chưa có khung giờ mở.</p>';
                return;
            }
            slots.forEach(function (s) {
                var btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'wujia-mexam-slot' + (s.available ? '' : ' is-disabled');
                if (!s.available) { btn.setAttribute('disabled', 'disabled'); }
                else {
                    btn.setAttribute('data-exam-session-id', s.session_id);
                    btn.setAttribute('data-exam-time', s.time);
                    btn.setAttribute('data-exam-loc', s.location || '');
                    btn.setAttribute('data-exam-max', s.max_per_reg);
                }
                btn.innerHTML =
                    '<i class="feather icon-clock wujia-mexam-slot-ico"></i>' +
                    '<span class="wujia-mexam-slot-time">' + s.time + '</span>' +
                    '<span class="wujia-mexam-slot-status">' + s.status + '</span>' +
                    '<span class="wujia-mexam-slot-radio"><i class="feather icon-check"></i></span>';
                slotList.appendChild(btn);
            });
        }

        function loadSlots(iso) {
            if (!slotList) { return; }
            slotList.innerHTML =
                '<p class="wujia-mexam-slot-empty">Đang tải khung giờ…</p>';
            jsonRpc('/portal/exam/slots', {
                course_id: courseId, exam_date: iso,
            }).then(function (res) {
                renderSlots(res && res.slots);
            });
        }

        function selectSlot(btn) {
            wizard.querySelectorAll('.wujia-mexam-slot').forEach(function (s) {
                s.classList.remove('is-selected');
            });
            btn.classList.add('is-selected');
            pendingSessionId = parseInt(btn.getAttribute('data-exam-session-id'), 10) || 0;
            pendingTime = btn.getAttribute('data-exam-time') || '';
            pendingLoc = btn.getAttribute('data-exam-loc') || '';
            pendingMax = parseInt(btn.getAttribute('data-exam-max'), 10) || 0;
            if (confirmSlotBtn) { confirmSlotBtn.disabled = false; }
        }

        /* ---------- People ---------- */
        function personRows() {
            return wizard.querySelectorAll('[data-exam-personlist] [data-exam-person]');
        }
        function renumberPeople() {
            var rows = personRows();
            rows.forEach(function (p, i) {
                var nameEl = p.querySelector('.wujia-mexam-person-name');
                if (nameEl) { nameEl.textContent = 'Nhân sự ' + (i + 1); }
                var del = p.querySelector('[data-exam-person-del]');
                var req = p.querySelector('[data-exam-person-req]');
                // Người 1 bắt buộc, không xóa; còn lại xóa được.
                if (i === 0) {
                    if (del) { del.setAttribute('hidden', 'hidden'); }
                    if (req) { req.removeAttribute('hidden'); }
                } else {
                    if (del) { del.removeAttribute('hidden'); }
                    if (req) { req.setAttribute('hidden', 'hidden'); }
                }
            });
        }
        function addPerson() {
            if (!personList || !personTpl) { return; }
            if (chosen.max && personRows().length >= chosen.max) {
                flashPersonLimit();
                return;
            }
            var node = personTpl.cloneNode(true);
            node.classList.add('is-open');
            node.querySelectorAll('input').forEach(function (inp) {
                if (inp.type === 'file') { inp._photoData = ''; }
                else { inp.value = ''; }
            });
            var pt = node.querySelector('.wujia-mexam-photo-text');
            if (pt) { pt.textContent = 'Thêm ảnh (tùy chọn)'; }
            clearPersonErr(node);
            personList.appendChild(node);
            renumberPeople();
        }
        function flashPersonLimit() {
            var last = personRows()[personRows().length - 1];
            if (last) { showPersonErr(last, 'Tối đa ' + chosen.max + ' người mỗi phiếu.'); }
        }
        function showPersonErr(person, msg) {
            var err = person.querySelector('[data-exam-person-err]');
            if (err) { err.textContent = msg; err.removeAttribute('hidden'); }
        }
        function clearPersonErr(person) {
            var err = person.querySelector('[data-exam-person-err]');
            if (err) { err.textContent = ''; err.setAttribute('hidden', 'hidden'); }
        }
        function readField(person, name) {
            var el = person.querySelector('[name="' + name + '"]');
            return el ? el.value.trim() : '';
        }

        /* Trả về danh sách participant hợp lệ, hoặc null nếu có lỗi (đã hiện). */
        function collectParticipants() {
            var out = [];
            var ok = true;
            personRows().forEach(function (person) {
                clearPersonErr(person);
                var name = readField(person, 'employee_name');
                var phone = readField(person, 'phone');
                if (!name || !phone) {
                    showPersonErr(person, 'Cần họ tên và số điện thoại.');
                    ok = false;
                    return;
                }
                if (!PHONE_RE.test(phone)) {
                    showPersonErr(person,
                        'Số điện thoại không hợp lệ (vd 0901234567).');
                    ok = false;
                    return;
                }
                var p = {
                    employee_name: name,
                    phone: phone,
                    birth_year: readField(person, 'birth_year'),
                    job_position: readField(person, 'job_position'),
                };
                var file = person.querySelector('[data-exam-photo]');
                if (file && file._photoData) { p.photo = file._photoData; }
                out.push(p);
            });
            return ok ? out : null;
        }

        /* ---------- Confirm summary ---------- */
        function buildConfirm(participants) {
            var box = wizard.querySelector('[data-exam-cf-people]');
            if (!box) { return; }
            box.innerHTML = '';
            /* WJ-EXAM-003 — đủ 4 nhãn để người đăng ký đối chiếu trước khi gửi. */
            participants.forEach(function (p) {
                var row = document.createElement('div');
                row.className = 'wujia-mexam-cfperson';
                row.innerHTML =
                    '<span class="wujia-mexam-cfperson-name"></span>' +
                    '<span class="wujia-mexam-cfperson-kv"></span>' +
                    '<span class="wujia-mexam-cfperson-kv"></span>' +
                    '<span class="wujia-mexam-cfperson-kv"></span>';
                var kv = row.querySelectorAll('.wujia-mexam-cfperson-kv');
                row.querySelector('.wujia-mexam-cfperson-name').textContent = p.employee_name;
                kv[0].textContent = 'Số điện thoại: ' + p.phone;
                kv[1].textContent = 'Năm sinh: ' + (p.birth_year || '—');
                kv[2].textContent = 'Chức vụ: ' + (p.job_position || '—');
                box.appendChild(row);
            });
        }

        /* ---------- Submit error ---------- */
        function showSubmitErr(msg) {
            var box = wizard.querySelector('[data-exam-submit-err]');
            var txt = wizard.querySelector('[data-exam-submit-err-text]');
            if (txt) { txt.textContent = msg; }
            if (box) { box.removeAttribute('hidden'); }
        }
        function hideSubmitErr() {
            var box = wizard.querySelector('[data-exam-submit-err]');
            if (box) { box.setAttribute('hidden', 'hidden'); }
        }

        /* ---------- Photo pick ---------- */
        function onPhotoPick(input) {
            var file = input.files && input.files[0];
            var person = input.closest('[data-exam-person]');
            var textEl = input.parentNode.querySelector('.wujia-mexam-photo-text');
            if (!file) { input._photoData = ''; return; }
            if (file.size > MAX_PHOTO_BYTES) {
                input.value = ''; input._photoData = '';
                if (person) { showPersonErr(person, 'Ảnh vượt 5 MB.'); }
                return;
            }
            var reader = new FileReader();
            reader.onload = function () {
                input._photoData = reader.result || '';
                if (textEl) { textEl.textContent = file.name; }
                if (person) { clearPersonErr(person); }
            };
            reader.readAsDataURL(file);
        }

        /* ---------- Course filter chips ---------- */
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

        function chooseCourse(card) {
            courseId = parseInt(card.getAttribute('data-exam-course-id'), 10) || 0;
            var titleEl = card.querySelector('.wujia-mexam-course-title');
            var metaEl = card.querySelector('.wujia-mexam-course-meta');
            courseName = titleEl ? titleEl.textContent.trim() : '';
            wizard.querySelectorAll('.wujia-mexam-selcard-title').forEach(function (el) {
                el.textContent = courseName;
            });
            if (metaEl) {
                wizard.querySelectorAll('.wujia-mexam-selcard-meta').forEach(function (el) {
                    if (!el.hasAttribute('data-exam-sched-line')) {
                        el.textContent = metaEl.textContent;
                    }
                });
            }
            loadCalendar(calYear, calMonth);
            showStep(2);
        }

        /* ---------- Delegated click ---------- */
        wizard.addEventListener('click', function (ev) {
            var t = ev.target;

            var courseChoose = t.closest('.wujia-mexam-course-choose');
            if (courseChoose) {
                ev.preventDefault();
                var card = courseChoose.closest('.wujia-mexam-course');
                if (card) { chooseCourse(card); }
                return;
            }

            var monthBtn = t.closest('[data-exam-cal-month]');
            if (monthBtn) {
                ev.preventDefault();
                var dir = monthBtn.getAttribute('data-exam-cal-month') === 'prev' ? -1 : 1;
                var m = calMonth + dir, y = calYear;
                if (m < 1) { m = 12; y -= 1; }
                else if (m > 12) { m = 1; y += 1; }
                loadCalendar(y, m);
                return;
            }

            var day = t.closest('[data-exam-open-slots]');
            if (day) {
                ev.preventDefault();
                grid.querySelectorAll('.wujia-mexam-cal-day.is-available').forEach(function (d) {
                    d.classList.remove('is-selected');
                });
                day.classList.add('is-selected');
                pendingIso = day.getAttribute('data-exam-iso') || '';
                pendingDateLabel = day.getAttribute('data-exam-date') || '';
                pendingSessionId = 0; pendingTime = '';
                if (confirmSlotBtn) { confirmSlotBtn.disabled = true; }
                var sub = wizard.querySelector('[data-exam-slot-sub]');
                if (sub) {
                    sub.textContent = pendingDateLabel + (courseName ? ' • ' + courseName : '');
                }
                loadSlots(pendingIso);
                openSheet();
                return;
            }

            var slot = t.closest('[data-exam-session-id]');
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
                if (!pendingSessionId) { return; }
                chosen.sessionId = pendingSessionId;
                chosen.dateLabel = pendingDateLabel;
                chosen.time = pendingTime;
                chosen.loc = pendingLoc;
                chosen.max = pendingMax;
                var line = wizard.querySelector('[data-exam-sched-line]');
                if (line) { line.textContent = chosen.dateLabel + ' • ' + chosen.time; }
                var cfDate = wizard.querySelector('[data-exam-cf-date]');
                if (cfDate) { cfDate.textContent = chosen.dateLabel; }
                var cfSlot = wizard.querySelector('[data-exam-cf-slot]');
                if (cfSlot) { cfSlot.textContent = chosen.time; }
                var cfLoc = wizard.querySelector('[data-exam-cf-loc]');
                if (cfLoc && chosen.loc) { cfLoc.textContent = chosen.loc; }
                closeSheet();
                showStep(3);
                return;
            }

            var del = t.closest('[data-exam-person-del]');
            if (del) {
                ev.preventDefault();
                var person = del.closest('[data-exam-person]');
                if (person && personRows().length > 1) {
                    person.remove(); renumberPeople();
                }
                return;
            }
            if (t.closest('[data-exam-add-person]')) {
                ev.preventDefault();
                addPerson();
                return;
            }

            var chip = t.closest('[data-exam-cfilter]');
            if (chip) {
                ev.preventDefault();
                filterCourses(chip.getAttribute('data-exam-cfilter'), chip);
                return;
            }

            // "Tiếp tục" bước 3→4: validate + dựng tóm tắt trước khi chuyển.
            var goto4 = t.closest('[data-exam-goto]');
            if (goto4 && goto4.getAttribute('data-exam-goto') === '4' &&
                !goto4.hasAttribute('data-exam-submit')) {
                ev.preventDefault();
                var parts = collectParticipants();
                if (!parts) { return; }
                buildConfirm(parts);
                showStep(4);
                return;
            }
            var goto = t.closest('[data-exam-goto]');
            if (goto) {
                ev.preventDefault();
                showStep(goto.getAttribute('data-exam-goto'));
                return;
            }

            var submit = t.closest('[data-exam-submit]');
            if (submit) {
                ev.preventDefault();
                hideSubmitErr();
                if (!chosen.sessionId) {
                    showSubmitErr('Vui lòng chọn khung giờ thi.');
                    return;
                }
                var participants = collectParticipants();
                if (!participants) {
                    showSubmitErr('Kiểm tra lại thông tin nhân sự.');
                    showStep(3);
                    return;
                }
                submit.disabled = true;
                submit.textContent = 'Đang gửi…';
                jsonRpc('/portal/exam/register', {
                    session_id: chosen.sessionId,
                    participants: participants,
                }).then(function (res) {
                    if (res && res.success && res.redirect) {
                        window.location = res.redirect;
                        return;
                    }
                    submit.disabled = false;
                    submit.textContent = 'Xác nhận đăng ký';
                    showSubmitErr((res && res.message) ||
                        'Không gửi được yêu cầu. Vui lòng thử lại.');
                }).catch(function () {
                    submit.disabled = false;
                    submit.textContent = 'Xác nhận đăng ký';
                    showSubmitErr('Có lỗi kết nối. Vui lòng thử lại.');
                });
                return;
            }
        });

        wizard.addEventListener('change', function (ev) {
            var photo = ev.target.closest('[data-exam-photo]');
            if (photo) { onPhotoPick(photo); }
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
