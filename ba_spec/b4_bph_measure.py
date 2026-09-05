#!/usr/bin/env python3
"""B4 — đo CMP-BPH-001 (BackPageHeader) trên 7 route form/detail × 2 breakpoint.

Chân lý = spec BA tab `UI Component` dòng CMP-BPH-001 (BA Confirmed 07/08/2026).
Harness sai thì sửa harness (L7/L9).

    python3 b4_bph_measure.py [--base http://127.0.0.1:8055]
"""
import argparse
import json
import re
import sys

from playwright.sync_api import sync_playwright

USER, PWD = "anh.owner", "wujia@test123"

# route → (đường dẫn, list cha kỳ vọng)
ROUTES = [
    ("purchase-history/{id}", "/portal/purchase-history/28", "/portal/purchase-history"),
    ("delivery/{id}",         "/portal/delivery/3",          "/portal/delivery"),
    ("notification/{id}",     "/portal/notification/41",     "/portal/notification"),
    ("support/{id}",          "/portal/support/40",          "/portal/support"),
    ("support/new",           "/portal/support/new",         "/portal/support"),
    ("return/{id}",           "/portal/return/12",           "/portal/return"),
    ("return/new",            "/portal/return/new",          "/portal/return"),
]

VIEWPORTS = [("mobile", 391, 844), ("pc", 1920, 1080)]

ARROW_LEFT = ""
CHEVRON_LEFT = ""

MEASURE_JS = """
() => {
  const vis = el => {
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && el.offsetParent !== null;
  };
  const backs = [...document.querySelectorAll('.wj-page-header__back')];
  const shown = backs.filter(vis);
  const out = {n_back_dom: backs.length, n_back_visible: shown.length,
               overflow_x: document.documentElement.scrollWidth - document.documentElement.clientWidth};
  if (!shown.length) return out;
  const a = shown[0];
  const r = a.getBoundingClientRect(), s = getComputedStyle(a);
  const i = a.querySelector('i'), si = getComputedStyle(i), sib = getComputedStyle(i, '::before');
  const label = a.querySelector('.wj-page-header__back-label');
  const sl = label ? getComputedStyle(label) : null;
  const after = getComputedStyle(a, '::after');
  const hdr = a.closest('.wj-page-header'), rh = hdr.getBoundingClientRect();
  const title = hdr.querySelector('.wj-page-header__title');
  const st = getComputedStyle(title), rt = title.getBoundingClientRect();
  Object.assign(out, {
    w: +r.width.toFixed(1), h: +r.height.toFixed(1),
    radius: s.borderRadius, bg: s.backgroundColor, border: s.borderColor,
    border_w: s.borderTopWidth, color: s.color,
    icon_content: sib.content, icon_color: si.color,
    label_visible: label ? getComputedStyle(label).display !== 'none' : false,
    label_size: sl ? sl.fontSize : null, label_weight: sl ? sl.fontWeight : null,
    label_color: sl ? sl.color : null,
    hit_w: after.width, hit_h: after.height,
    header_h: +rh.height.toFixed(1),
    title_size: st.fontSize, title_lh: st.lineHeight, title_weight: st.fontWeight,
    title_text: title.textContent.trim(),
    overlap: rt.left < r.right - 0.5,
    href: a.getAttribute('href'),
  });
  return out;
}
"""

STATE_JS = """
() => {
  const a = [...document.querySelectorAll('.wj-page-header__back')]
    .find(el => getComputedStyle(el).display !== 'none' && el.offsetParent !== null);
  if (!a) return null;
  const s = getComputedStyle(a), si = getComputedStyle(a.querySelector('i'));
  return {bg: s.backgroundColor, border: s.borderColor, color: s.color,
          icon_color: si.color, outline: s.outlineWidth + ' ' + s.outlineStyle + ' ' + s.outlineColor,
          focused: document.activeElement === a};
}
"""


def login(ctx, base):
    p = ctx.new_page()
    # Portal có trang đăng nhập riêng /portal/login (form Wujia); /web/login trả form core ẩn.
    p.goto(f"{base}/portal/login", wait_until="domcontentloaded")
    p.fill("#wj-auth-login", USER)
    p.fill("#wj-auth-password", PWD)
    p.press("#wj-auth-password", "Enter")
    p.wait_for_url(lambda u: "/portal/login" not in u, timeout=20000)
    p.close()


def norm_rgb(v):
    m = re.findall(r"\d+", v or "")
    return tuple(int(x) for x in m[:3]) if len(m) >= 3 else None


HEX = {"#FFFFFF": (255, 255, 255), "#E5E7EB": (229, 231, 235), "#374151": (55, 65, 81),
       "#28A9DF": (40, 169, 223), "#EAF7FD": (234, 247, 253), "#BFE8F7": (191, 232, 247)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8055")
    a = ap.parse_args()

    rows, errors = [], []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context()
        login(ctx, a.base)
        for vname, w, h in VIEWPORTS:
            ctx2 = br.new_context(viewport={"width": w, "height": h},
                                  storage_state=ctx.storage_state())
            for label, path, parent in ROUTES:
                p = ctx2.new_page()
                errs = []
                p.on("pageerror", lambda e: errs.append(str(e)))
                resp = p.goto(a.base + path, wait_until="load")
                m = p.evaluate(MEASURE_JS)
                m.update(route=label, viewport=vname, status=resp.status,
                         js_errors=errs, parent=parent)
                # a11y: đếm link tên "Quay lại" trong accessibility tree
                m["a11y_back"] = p.get_by_role("link", name="Quay lại").count()
                if m.get("n_back_visible"):
                    # hover
                    p.hover(".wj-page-header__back:visible")
                    m["hover"] = p.evaluate(STATE_JS)
                    p.mouse.move(0, 0)
                    # focus bằng bàn phím (để :focus-visible ăn)
                    p.evaluate("() => document.body.focus()")
                    for _ in range(60):
                        p.keyboard.press("Tab")
                        st = p.evaluate(STATE_JS)
                        if st and st["focused"]:
                            m["focus"] = st
                            break
                rows.append(m)
                p.close()
            ctx2.close()
        br.close()

    print(json.dumps(rows, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
