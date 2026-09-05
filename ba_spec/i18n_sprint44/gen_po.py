#!/usr/bin/env python3
"""B4 — sinh custom/<module>/i18n/vi_VN.po. Chạy qua: odoo-bin shell < gen_po.py

Export .po thật từ Odoo (đúng tập msgid + reference), rồi điền msgstr từ vi_en_map.json
tra ngược en->vi. Module đã có vi_VN.po -> MERGE: giữ msgstr cũ, chỉ điền chỗ trống.
"""
import io
import json
import re
from pathlib import Path

from odoo.tools.translate import trans_export

# `odoo-bin shell < gen_po.py` exec từ stdin nên không có __file__ -> pin đường dẫn.
SCRATCH = Path("/home/huyban/odoo-dev/WujiaTea/scripts/ba_spec/i18n_sprint44")
CUSTOM = Path("/home/huyban/odoo-dev/WujiaTea/custom")

MODULES = [
    "wujia_core", "wujia_delivery", "wujia_fleet", "wujia_franchise", "wujia_sale",
    "wujia_portal_exam", "wujia_portal_notification", "wujia_portal_return",
    "wujia_portal_info_request", "wujia_portal_knowledge", "wujia_portal_support",
    "wujia_portal_order_window", "wujia_portal_debt", "wujia_portal_purchase_history",
]

vi_en = json.loads((SCRATCH / "vi_en_map.json").read_text(encoding="utf-8"))
EN_VI = {}
for vi, en in vi_en.items():
    EN_VI.setdefault(en, vi)
# Chuỗi Việt cũ phục vụ 2 ngữ cảnh (nút "Hủy chuyến" vs trạng thái) -> tách nhãn EN riêng,
# nên phải khai lại bản dịch ngược cho nhãn mới.
EN_VI["Trip cancelled"] = "Hủy chuyến"
EN_VI["Vehicle"] = "Xe"
EN_VI["Delivery vehicle"] = "Xe giao"
EN_VI["Time slot"] = "Ca thi"
# Sprint 44 / W1 — tách "động từ (nút)" vs "tính từ (state/filter)".
# 2 msgid khác nhau trả cùng 1 msgstr là hợp lệ trong .po; kết quả là người xem vi_VN
# thấy y hệt chữ trước sprint (Reject/Rejected -> "Từ chối", Archive/Archived -> "Lưu trữ").
EN_VI["Rejected"] = "Từ chối"
EN_VI["Archived"] = "Lưu trữ"
EN_VI["Lock portal"] = "Khóa portal"
# Nút cũ ghi "Đã gán xe" (thể bị động) — nay là động từ cho khớp nguyên tắc nút = hành động.
EN_VI["Assign vehicle"] = "Gán xe"

# Sprint 44 / W5d — 3 nhãn lọt lưới vì i18n_tool lọc theo DẤU tiếng Việt, mà các chuỗi này
# là ASCII thuần ("Ca thi", "SL giao", "Xe") nên extract trả 0 dù vẫn là tiếng Việt.
# "Time slot" đã có sẵn map bên dưới. 2 nhãn còn lại thêm ở đây.
EN_VI["Delivery qty"] = "SL giao"
EN_VI["Wujia Fleet Vehicle"] = "Wujia Fleet Vehicle — Xe"
EN_VI.update({
    "Franchise store receiving the goods. Copied from the SO on confirm; can be set manually for internal pickings.": "Cửa hàng nhượng quyền nhận hàng. Tự copy từ SO khi confirm; có thể set thủ công cho picking nội bộ.",
    "Shipping cost allocated in proportion to the picking planned_weight within the total planned_weight of the batch.": "Chi phí vận chuyển phân bổ theo tỉ lệ planned_weight của picking trong tổng planned_weight của batch.",
    "Shipping pricelist. Auto-suggested from vehicle type + carrier + date; can be overridden manually.": "Bảng giá vận chuyển. Auto-suggest theo loại xe + đội xe + ngày; có thể override thủ công.",
    'Display name, e.g. "51C-12345 — 3.5T payload".': 'Tên hiển thị, ví dụ "51C-12345 — Tải 3.5T".',
    "A price line can cover several areas — it matches when the area of the picking is in this list.": "Một dòng giá có thể áp dụng cho nhiều khu vực — match khi area của picking nằm trong danh sách này.",
    'Carrier name, e.g. "Nguyen Dung Transport Co., Ltd".': 'Tên đội xe / nhà xe, ví dụ "CTY TNHH Vận Tải Nguyễn Dũng".',
    "Link to the Odoo contact / vendor when the carrier is a supplier and a PO has to be issued.": "Link tới contact / vendor của Odoo nếu đội xe là nhà cung cấp và cần xuất PO.",
    'e.g. "1.9T truck", "17T refrigerated truck".': 'Ví dụ "Xe tải 1.9T", "Xe đông lạnh 17T".',
    "= payload_capacity_ton × 1000. Used to compare against planned_weight for the batch overload warning.": "= payload_capacity_ton × 1000. Dùng để compare với planned_weight cho cảnh báo vượt tải batch.",
    'Display name, e.g. "[H010] 219 Vinh Vien store".': 'Tên hiển thị, ví dụ "[H010] Cửa hàng 219 Vĩnh Viễn".',
    "Turn on to publish the product on the ordering portal (/portal/order). A published product must have a minimum quantity > 0.": "Bật để public sản phẩm lên portal đặt hàng (/portal/order). Sản phẩm public bắt buộc có số lượng tối thiểu > 0.",
    "Total planned weight of the SO = sum(line.planned_weight). Early reference only, not the authoritative source for vehicle planning.": "Tổng khối lượng dự kiến của SO = sum(line.planned_weight). Tham khảo sớm, không phải nguồn chính sắp xe.",
    "Snapshot of the weight of one product unit taken when the product is selected. Not user-editable; stored so historical data stays unchanged even if product.weight changes.": "Snapshot khối lượng 1 đơn vị product tại lúc chọn sản phẩm. Không cho user nhập tay; lưu để dữ liệu cũ giữ nguyên kể cả khi product.weight đổi.",
    "Snapshot of weight_per_unit from sale.order.line when the move comes from an SO; falls back to product_id.weight for moves without an SO line.": "Snapshot weight_per_unit từ sale.order.line nếu move sinh từ SO; fallback product_id.weight cho move không gắn SO line.",
    "Total planned weight of the delivery order = sum(move_ids.planned_weight). This is the authoritative source for planning batches/trips.": "Tổng khối lượng dự kiến của phiếu xuất = sum(move_ids.planned_weight). Đây là nguồn chính để sắp batch/chuyến xe.",
    "Total planned weight of the batch = sum(picking_ids.planned_weight). Used to pick a suitable vehicle.": "Tổng khối lượng dự kiến của batch = sum(picking_ids.planned_weight). Dùng để chọn xe phù hợp.",
    'Leave empty to broadcast to every store. The "By criteria" mode fills this field in when sending.': 'Để trống = broadcast cho mọi cửa hàng. Chế độ "Theo tiêu chí" tự điền field này khi gửi.',
    "All = every store, nothing to select. By criteria = filter by area/province/status. Manual selection = tick each store yourself.": "Tất cả = mọi cửa hàng, không cần chọn gì. Theo tiêu chí = lọc theo khu vực/tỉnh thành/trạng thái. Chọn tay = tự tick từng cửa hàng.",
    "active + state = Sent + shown on portal. It does NOT exclude expired notifications, because the portal history must stay accessible.": "active + state = Đã gửi + hiện trên portal. KHÔNG loại thông báo hết hiệu lực vì lịch sử portal vẫn phải mở được.",
    "exact: compensate exactly the missing quantity; accumulate: build up until a full delivery unit is reached (the remainder carries over to the next period).": "exact: bù đúng số lượng còn thiếu; accumulate: cộng dồn đủ một đơn vị giao mới bù (phần lẻ chuyển kỳ sau).",
    "Entitlement quantity for one compensation delivery unit (e.g. 1 bag = 10 kg). Used as the default suggestion when HQ approves a request.": "SL quyền lợi tương ứng một đơn vị giao bù (vd 1 bịch = 10 kg). Gợi ý mặc định khi HQ duyệt yêu cầu.",
    "Enable/disable the portal ordering time window. When off, ordering is allowed at any time regardless of `wujia.order.window`.": "Bật/tắt giới hạn khung giờ đặt hàng cho portal. Nếu tắt thì cho phép đặt mọi lúc, bất kể `wujia.order.window`.",
    'e.g. "Morning window HN" — shown in the portal UI when reporting that ordering is outside the window.': 'Vd "Khung sáng HN" — hiển thị trong UI portal khi báo ngoài khung giờ.',
    "The window applies only to franchises located in this area. An area can have several windows (e.g. morning + evening) — the controller checks them all and allows ordering while at least one is open.": "Khung giờ chỉ áp cho franchise thuộc khu vực này. Một khu vực có thể có nhiều khung giờ (vd sáng + tối) — controller check tất cả, miễn 1 khung đang mở là cho phép.",
})
# .po dùng ký tự thật, không dùng XML entity.
EN_VI = {k.replace("&amp;", "&"): v.replace("&amp;", "&") for k, v in EN_VI.items()}

MSGID = re.compile(r'^msgid ((?:"[^\n]*"\n(?!msgstr))*"[^\n]*")\nmsgstr ((?:"[^\n]*"\n?)+)',
                   re.M)


def unquote(block):
    return "".join(
        re.sub(r'\\(.)', lambda m: {'n': '\n', 't': '\t'}.get(m.group(1), m.group(1)), s)
        for s in re.findall(r'"((?:[^"\\]|\\.)*)"', block)
    )


def quote(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


report = []
pot_done = []
for mod in MODULES:
    # BẪY: PoFileReader tự merge <mod>/i18n/<mod>.pot vào .po khi nạp (tools/translate.py).
    # .pot cũ còn msgid tiếng Việt -> mọi msgid tiếng Anh mới bị polib đánh dấu obsolete
    # và bị bỏ qua => .po nạp vào DB nhưng không có tác dụng. Phải sinh lại .pot cùng lúc.
    pot = CUSTOM / mod / "i18n" / f"{mod}.pot"
    if pot.exists():
        pbuf = io.BytesIO()
        trans_export(None, [mod], pbuf, "po", env)        # noqa: F821
        pot.write_text(pbuf.getvalue().decode("utf-8"), encoding="utf-8")
        pot_done.append(mod)

    buf = io.BytesIO()
    trans_export("vi_VN", [mod], buf, "po", env)          # noqa: F821 (env do odoo shell cấp)
    po = buf.getvalue().decode("utf-8")

    old = {}
    dest = CUSTOM / mod / "i18n" / "vi_VN.po"
    if dest.exists():
        for m in MSGID.finditer(dest.read_text(encoding="utf-8")):
            k, v = unquote(m.group(1)), unquote(m.group(2))
            if k and v:
                old[k] = v

    stat = {"filled": 0, "kept": 0, "blank": 0}
    misses = []

    def fill(m):
        msgid, cur = unquote(m.group(1)), unquote(m.group(2))
        if not msgid:
            return m.group(0)
        new = old.get(msgid) or EN_VI.get(msgid)
        if not new:
            if not cur:
                stat["blank"] += 1
                misses.append(msgid)
            return m.group(0)
        if msgid in old and old[msgid] == new:
            stat["kept"] += 1
        else:
            stat["filled"] += 1
        return f'msgid {m.group(1)}\nmsgstr {quote(new)}\n'

    po = MSGID.sub(fill, po)
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(po, encoding="utf-8")
    report.append((mod, stat["filled"], stat["kept"], stat["blank"], misses))

print("\n=== vi_VN.po ===")
tot_blank = 0
for mod, filled, kept, blank, misses in report:
    tot_blank += blank
    print(f"{mod:34s} filled={filled:4d} kept={kept:4d} CHƯA DỊCH={blank:4d}")
    for s in misses[:8]:
        print(f"      ? {s[:100]!r}")
print(f"TỔNG chưa dịch = {tot_blank}")
print(f".pot sinh lại: {pot_done or '(không có module nào có .pot)'}")

# --- W1 assert: 5 nhãn tách mới phải có msgstr đúng trong .po đã ghi ---
W1_EXPECT = {
    "Rejected": "Từ chối",
    "Archived": "Lưu trữ",
    "Rejection reason": "Lý do từ chối",
    "Lock portal": "Khóa portal",
    "Assign vehicle": "Gán xe",
}
print("\n=== W1 assert (msgid tách mới) ===")
bad = 0
for mod in MODULES:
    dest = CUSTOM / mod / "i18n" / "vi_VN.po"
    if not dest.exists():
        continue
    got = {unquote(m.group(1)): unquote(m.group(2))
           for m in MSGID.finditer(dest.read_text(encoding="utf-8"))}
    for k, want in W1_EXPECT.items():
        if k in got:
            ok = got[k] == want
            bad += 0 if ok else 1
            print(f"{'OK ' if ok else 'FAIL'} {mod:32s} {k!r} -> {got[k]!r}")
print(f"W1 assert FAIL = {bad}")
