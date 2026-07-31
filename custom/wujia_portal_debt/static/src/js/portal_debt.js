/* Wujia Portal — Công nợ & thanh toán.
 *
 * 2 hành vi duy nhất (Figma không có tương tác nào khác):
 *   1. Bộ lọc tuần/kỳ: <select> phủ kín card → đổi là submit luôn, khỏi nút "Xem".
 *   2. Nút copy số tài khoản / nội dung chuyển khoản (màn 07).
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
        if (form) {
            form.submit();
        }
    });

    document.addEventListener('click', function (ev) {
        var btn = ev.target.closest ? ev.target.closest('[data-wj-debt="copy"]') : null;
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
