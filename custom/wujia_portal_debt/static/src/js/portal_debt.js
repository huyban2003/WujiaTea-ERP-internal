/* Wujia Portal — Công nợ & thanh toán.
 *
 * Hành vi (Figma không có tương tác nào khác):
 *   1. Bộ lọc tuần/kỳ: <select> phủ kín card → đổi là submit luôn, khỏi nút "Xem".
 *   2. Nút copy số tài khoản / nội dung chuyển khoản (màn 07 + modal PC).
 *   3. PC (STT10): mở/đóng modal QR "Thanh toán số còn lại" (open-pay / close-pay /
 *      click backdrop / phím Esc). Nút "PDF" và "Tải mã QR" là <button type="button">
 *      không handler ⇒ no-op MVP (chưa có endpoint/file — đúng ghi chú BA).
 *
 * Vanilla + delegation trên document: trang render server-side, không có OWL
 * component nào ở đây, và cùng pattern với các script portal khác của Wujia.
 */
(function () {
    'use strict';

    document.addEventListener('change', function (ev) {
        var select = ev.target.closest ? ev.target.closest('[data-wj-debt="filter"]') : null;
        if (!select) {
            return;
        }
        var form = select.form;
        if (!form) {
            return;
        }
        // requestSubmit (KHÔNG phải submit): submit() bỏ qua listener 'submit' nên
        // wj_ajax_list.js không bắt được, đổi kỳ lại reload cả trang như cũ.
        if (form.requestSubmit) {
            form.requestSubmit();
        } else {
            form.submit();
        }
    });

    /* ---- Modal QR (PC): mở/đóng thuần bằng thuộc tính [hidden] ---- */
    function payModal() {
        return document.querySelector('[data-wj-debt-modal="pay"]');
    }
    function openModal() {
        var modal = payModal();
        if (modal) {
            modal.removeAttribute('hidden');
        }
    }
    function closeModal() {
        var modal = payModal();
        if (modal) {
            modal.setAttribute('hidden', 'hidden');
        }
    }

    document.addEventListener('click', function (ev) {
        if (!ev.target.closest) {
            return;
        }

        if (ev.target.closest('[data-wj-debt="open-pay"]')) {
            ev.preventDefault();
            openModal();
            return;
        }
        // Nút X / "Đóng", hoặc click ra nền tối (chính backdrop, không phải panel con).
        if (ev.target.closest('[data-wj-debt="close-pay"]') ||
            ev.target.matches('[data-wj-debt-modal="pay"]')) {
            ev.preventDefault();
            closeModal();
            return;
        }

        var btn = ev.target.closest('[data-wj-debt="copy"]');
        if (!btn) {
            return;
        }
        ev.preventDefault();
        var value = btn.getAttribute('data-wj-debt-value') || '';
        copyText(value).then(function (ok) {
            if (!ok) {
                return;
            }
            btn.classList.add('is-copied');
            window.setTimeout(function () {
                btn.classList.remove('is-copied');
            }, 1500);
        });
    });

    document.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape') {
            var modal = payModal();
            if (modal && !modal.hasAttribute('hidden')) {
                closeModal();
            }
        }
    });

    /* navigator.clipboard chỉ có trên secure context; UAT hiện chạy http →
       fallback execCommand để nút vẫn dùng được. */
    function copyText(value) {
        if (!value) {
            return Promise.resolve(false);
        }
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(value).then(function () {
                return true;
            }).catch(function () {
                return legacyCopy(value);
            });
        }
        return Promise.resolve(legacyCopy(value));
    }

    function legacyCopy(value) {
        var ta = document.createElement('textarea');
        ta.value = value;
        ta.setAttribute('readonly', 'readonly');
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        var ok = false;
        try {
            ok = document.execCommand('copy');
        } catch (err) {
            ok = false;
        }
        document.body.removeChild(ta);
        return ok;
    }
})();
