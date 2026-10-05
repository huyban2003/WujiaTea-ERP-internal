/* J-V1 (05/10/2026): đã xoá khối ví/đầu tư/rút tiền của template Vuexy cũ
   (#form_withdraw, #register_investment, payment_confirmation → route /bcore/* không tồn tại,
   không view nào render) — nó là nơi duy nhất gọi _t() của lang.js, file đó cũng đã xoá. */
/* Sprint 4.2: defensive — ensure .show-overlay class is never stuck after
   page load. On the production server, JS init ordering with Odoo's
   web.assets_frontend bundle can leave this class active, which causes
   the content-overlay (rgba(0,0,0,0.5)) to cover the sidebar. */
$(document).ready(function () {
    $('.app-content').removeClass('show-overlay');
});
$(window).on('load', function () {
    $('.app-content').removeClass('show-overlay');
});

/* Sprint 4.2+: force body.menu-expanded on desktop so Vuexy's menu-modern
   CSS shows the sidebar even when app-menu.js init() bails out without
   adding the class. E8b: chỉ ≥1200 (sidebar cố định); 992–1199 là drawer
   đóng mặc định do wujia_sidebar.js điều khiển. */
function _wujiaForceMenuExpanded() {
    if (window.matchMedia('(min-width: 1200px)').matches) {
        $('body').removeClass('menu-hide menu-collapsed').addClass('menu-expanded menu-open');
    }
}
$(document).ready(_wujiaForceMenuExpanded);
$(window).on('load', _wujiaForceMenuExpanded);
$(window).on('resize', _wujiaForceMenuExpanded);

/* Sprint 4.2+: neutralize Vuexy app-menu.js so it doesn't run hide/expand/
   PerfectScrollbar animations at window.load that cause a visible flicker
   ("load twice"). The sidebar has only one static item — we don't need
   accordion, scrollbar, or breakpoint-aware hide. Override before Vuexy's
   $(window).on('load') handler in app.js fires (handlers run in registration
   order, my_js.js is loaded after app-menu.js and app.js so by the time
   app.js's load handler runs, $.app.menu.init is our no-op). */
if (typeof $ !== 'undefined' && $.app && $.app.menu) {
    $.app.menu.init = function () {};
    $.app.menu.change = function () {};
    if ($.app.menu.manualScroller) {
        $.app.menu.manualScroller.init = function () {};
        $.app.menu.manualScroller.update = function () {};
        $.app.menu.manualScroller.updateHeight = function () {};
    }
}

/* Sprint 4.2+: app.js line 492 calls i18next.use(XHRBackend).init({...})
   with loadPath '../../../app-assets/data/locales/{{lng}}.json' which
   returns 404 — that path isn't served anywhere in this repo. Portal strings
   are translated server-side (QWeb + data-wj-msg-*, see wj_msg.js), so i18next is unused.
   No-op the chain to silence the console 404. */
if (typeof i18next !== 'undefined') {
    i18next.use = function () { return i18next; };
    i18next.init = function (opts, cb) {
        if (typeof cb === 'function') { cb(null, function (k) { return k; }); }
        return i18next;
    };
}
