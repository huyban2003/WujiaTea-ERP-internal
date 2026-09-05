#!/usr/bin/env python3
"""W5b — đổi ngôn ngữ admin 2 chiều rồi so nhãn header trên CÙNG 1 bản ghi.

Bug W1 phải chứng minh đã hết: script dịch hàng loạt ép "Từ chối"/"Lưu trữ" (phục vụ cả
NÚT lẫn TRẠNG THÁI) thành một từ tiếng Anh duy nhất, nên header hiện 2 chữ y hệt cạnh nhau.
Sau W1: nút = động từ (Reject/Archive), state = tính từ (Rejected/Archived).

Kỳ vọng:
  en_US : nút và state là 2 TOKEN KHÁC nhau.
  vi_VN : cả hai đều ra "Từ chối" / "Lưu trữ" — y hệt trước sprint 44 (2 msgid -> 1 msgstr
          là hợp lệ trong .po).

So khớp theo TOKEN chính xác (tách header theo dòng), không dùng `in` — vì "Reject" là
substring của "Rejected" nên phép `in` luôn pass rỗng.

Chạy: python3 toggle_lang_check.py     (server phải đang chạy ở 8019)
Script TRẢ admin về vi_VN khi kết thúc; W5e mới là bước đổi hẳn sang en_US.
"""
import sys
import xmlrpc.client

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8019"
DB, USER, PWD = "wujia_tea_19", "admin", "admin"

# res_id chọn theo STATE, không chọn bừa:
#  - return.request có statusbar_visible="submitted,...,done" (bỏ rejected) và nút Reject
#    ẩn khi state == rejected => KHÔNG bản ghi nào thấy được cả hai. Phải soi 2 bản ghi.
#  - notification / fleet.pricelist thì nút Archive và state Archived hiện cùng lúc —
#    đây đúng là chỗ trước W1 hiện 2 chữ trùng nhau.
CASES = [
    ("Phiếu đổi trả — đã từ chối (state)", "wujia.return.request", 14,
     {"has_en": ["Rejected"], "no_en": ["Reject"], "has_vi": ["Từ chối"]}),
    ("Phiếu đổi trả — đã gửi (nút)", "wujia.return.request", 12,
     {"has_en": ["Reject"], "no_en": ["Rejected"], "has_vi": ["Từ chối"]}),
    ("Thông báo — nút + state cùng lúc", "wujia.notification", 41,
     {"has_en": ["Archive", "Archived"], "no_en": [], "has_vi": ["Lưu trữ"]}),
    ("Bảng giá xe — nút + state cùng lúc", "wujia.fleet.pricelist", 1,
     {"has_en": ["Archive", "Archived"], "no_en": [], "has_vi": ["Lưu trữ"]}),
]

common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")


def rpc(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PWD, model, method, list(args), kw)


def resolve_action(model):
    ids = rpc("ir.actions.act_window", "search",
              [("res_model", "=", model)], limit=1)
    return ids[0] if ids else None


def header_tokens(page):
    """Danh sách nhãn trong header form (nút hành động + bậc statusbar)."""
    el = page.query_selector(".o_form_statusbar")
    txt = el.inner_text() if el else ""
    return [t.strip() for t in txt.split("\n") if t.strip()]


def run(pw, lang, actions):
    rpc("res.users", "write", [uid], {"lang": lang})
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1600, "height": 1000})
    p = ctx.new_page()
    p.goto(f"{BASE}/web/login", wait_until="domcontentloaded")
    p.fill("input[name=login]", USER)
    p.fill("input[name=password]", PWD)
    p.press("input[name=password]", "Enter")
    try:
        p.wait_for_url(lambda u: "/web/login" not in u, timeout=25000)
    except Exception:
        pass
    p.wait_for_timeout(1500)

    out = {}
    for label, model, res_id, _exp in CASES:
        p.goto(f"{BASE}/odoo/action-{actions[model]}/{res_id}", wait_until="load")
        p.wait_for_timeout(2500)
        out[(model, res_id)] = header_tokens(p)
        p.screenshot(path=f"/tmp/w5b_{lang}_{model.replace('.', '_')}_{res_id}.png")
    br.close()
    return out


actions = {m: resolve_action(m) for _l, m, _i, _e in CASES}
missing_act = [m for m, a in actions.items() if not a]
if missing_act:
    sys.exit(f"Không tìm thấy act_window cho: {missing_act}")

with sync_playwright() as pw:
    en = run(pw, "en_US", actions)
    vi = run(pw, "vi_VN", actions)

bad = 0
for label, model, res_id, exp in CASES:
    key = (model, res_id)
    te, tv = en[key], vi[key]
    print(f"\n### {label}  (id={res_id})")
    print(f"    en_US: {te}")
    print(f"    vi_VN: {tv}")
    checks = [
        ("en có", [w for w in exp["has_en"] if w not in te]),
        ("en KHÔNG có", [w for w in exp["no_en"] if w in te]),
        ("vi có", [w for w in exp["has_vi"] if w not in tv]),
    ]
    for what, miss in checks:
        bad += len(miss)
        print(f"    [{'OK  ' if not miss else 'FAIL'}] {what}: "
              f"{'đúng' if not miss else miss}")

rpc("res.users", "write", [uid], {"lang": "vi_VN"})
print(f"\nFAIL = {bad}   (admin đã trả về vi_VN)")
sys.exit(1 if bad else 0)
