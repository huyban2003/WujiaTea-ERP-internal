/* Wujia Portal — Giao hàng: lọc/phân trang không reload cả trang.
 *
 * Chip trạng thái và pager vốn là <a href> thường → mỗi lần bấm là điều hướng
 * thật, server dựng lại nguyên shell portal (navbar, sidebar, chuông) dù chỉ có
 * danh sách đổi. Ở đây bắt click, gọi /portal/delivery/results (chỉ trả 3 khối
 * kết quả) rồi thay tại chỗ + pushState để URL vẫn share/F5/back được.
 *
 * Không có JS (hoặc fetch lỗi) → rơi về điều hướng thường, hành vi y như cũ.
 */
(function () {
    "use strict";

    var LIST_PATH = "/portal/delivery";
    var FRAGMENT_PATH = "/portal/delivery/results";
    // Khối swap: id trong fragment === id trong trang.
    var SLOTS = ["wj-dlv-pc-card", "wj-dlv-mchips", "wj-dlv-mbody"];

    var pending = null;

    function isListUrl(url) {
        return url.pathname === LIST_PATH;
    }

    function setBusy(busy) {
        SLOTS.forEach(function (id) {
            var el = document.getElementById(id);
            if (el) {
                el.setAttribute("aria-busy", busy ? "true" : "false");
                el.classList.toggle("wj-dlv-busy", busy);
            }
        });
    }

    /* Form lọc nằm NGOÀI vùng swap → đồng bộ tay để lần submit sau không mang
       trạng thái cũ (hidden bs mobile + select bs desktop). */
    function syncFilterControls(params) {
        var bs = params.get("bs") || "";
        var hidden = document.getElementById("wj-dlv-bs");
        if (hidden) {
            hidden.value = bs;
        }
        document.querySelectorAll('.wj-pc-filterbar select[name="bs"]').forEach(function (sel) {
            sel.value = bs;
        });
    }

    function swap(html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var swapped = 0;
        SLOTS.forEach(function (id) {
            var target = document.getElementById(id);
            var fresh = doc.getElementById(id);
            if (target && fresh) {
                target.replaceWith(fresh);
                swapped += 1;
            }
        });
        return swapped > 0;
    }

    function load(url, push) {
        if (pending) {
            pending.abort();
        }
        var controller = new AbortController();
        pending = controller;
        setBusy(true);

        var fragmentUrl = new URL(FRAGMENT_PATH, window.location.origin);
        fragmentUrl.search = url.search;

        fetch(fragmentUrl.toString(), {
            credentials: "same-origin",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            signal: controller.signal,
        })
            .then(function (res) {
                if (!res.ok) {
                    throw new Error("HTTP " + res.status);
                }
                return res.text();
            })
            .then(function (html) {
                if (!swap(html)) {
                    throw new Error("no slot");
                }
                pending = null;
                setBusy(false);
                syncFilterControls(url.searchParams);
                if (push) {
                    window.history.pushState({ wjDlv: true }, "", url.pathname + url.search);
                }
                window.scrollTo({ top: 0, behavior: "smooth" });
            })
            .catch(function (err) {
                if (err && err.name === "AbortError") {
                    return;
                }
                pending = null;
                setBusy(false);
                window.location.assign(url.toString()); // fallback: điều hướng như cũ
            });
    }

    function onClick(ev) {
        var link = ev.target.closest("a[data-wj-dlv-nav]");
        if (!link || ev.defaultPrevented || ev.button !== 0 ||
            ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) {
            return;
        }
        var url = new URL(link.getAttribute("href"), window.location.origin);
        if (!isListUrl(url)) {
            return;
        }
        ev.preventDefault();
        load(url, true);
    }

    function onSubmit(ev) {
        var form = ev.target.closest("form");
        if (!form || ev.defaultPrevented) {
            return;
        }
        var action = new URL(form.getAttribute("action") || window.location.pathname,
                             window.location.origin);
        if (!isListUrl(action) || form.method.toLowerCase() !== "get") {
            return;
        }
        var url = new URL(LIST_PATH, window.location.origin);
        new FormData(form).forEach(function (value, key) {
            if (value !== "") {
                url.searchParams.set(key, value); // bỏ tham số rỗng cho URL gọn
            }
        });
        ev.preventDefault();
        load(url, true);
    }

    function onPopState() {
        var url = new URL(window.location.href);
        if (isListUrl(url)) {
            load(url, false);
        }
    }

    function init() {
        if (!document.getElementById("wj-dlv-mbody") &&
            !document.getElementById("wj-dlv-pc-card")) {
            return; // không phải trang danh sách giao hàng
        }
        document.addEventListener("click", onClick);
        document.addEventListener("submit", onSubmit);
        window.addEventListener("popstate", onPopState);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
