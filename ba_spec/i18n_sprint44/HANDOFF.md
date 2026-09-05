# Sprint 44 — Handoff (2026-07-31)

Hai việc: (1) fix crash kanban Odoo 19, (2) chuẩn hoá nhãn **backend** sang tiếng Anh + sinh `vi_VN.po`.
Kế hoạch gốc đã duyệt: `/home/huyban/.claude/plans/fizzy-strolling-flurry.md`.

---

## ĐÃ XONG (đã build RC=0, chưa commit)

### Task 1 — Crash `Missing 'card' template`
Odoo 19 đổi tên template kanban `kanban-box` → `card`. Sửa 2 chỗ:
- `custom/wujia_portal_support/views/wujia_support_backend_views.xml:188` ← đây là crash khi bấm menu **Hỗ Trợ**
  (action `view_mode=kanban,list,form` nên kanban là view mặc định)
- `custom/wujia_portal_knowledge/views/wujia_knowledge_backend_views.xml:200`

Verify đã chạy: build RC=0; `select id,name from ir_ui_view where arch_db::text like '%kanban-box%'` = 0 dòng;
headless (`check_kanban.py`) render được cả 2 kanban, `owl_errors=0`.

> ⚠️ Reviewer tự động báo 4 "blocker" về `t-name="card"` — **false positive**, đó chính là fix này.

### Task 2 — Chuẩn hoá tiếng Anh
- **636 chuỗi Việt** backend → English, áp lên **81 file** (997 vị trí) XML + Python.
- Vá thêm **24 `help=` Python nối chuỗi nhiều dòng** (extractor chỉ bắt dòng đầu → tail còn tiếng Việt).
- Vá thêm **4 nhãn không dấu** regex bỏ sót: `Xe`→Vehicle, `Xe giao`→Delivery vehicle, `Ca thi`→Time slot.
- Build 14 module: **RC=0, 0 Traceback**.

### Seam portal (bắt buộc, đã làm)
`custom/wujia_portal_purchase_history/controllers/portal.py` — `_batch_status_labels()` trước đây đọc
`stock.picking.batch._fields['delivery_batch_status'].selection`. Nay trả hằng `BATCH_STATUS_LABELS`
(tiếng Việt, pin cứng ngay đầu file) ⇒ portal *Lịch sử đặt hàng* **không đổi một chữ nào**.
Key phải khớp `DELIVERY_BATCH_STATUS` trong `wujia_delivery/models/stock_picking_batch.py`.

### `.po`
14 file `custom/<mod>/i18n/vi_VN.po` sinh từ export thật của Odoo (`trans_export`), merge — **không đè** —
3 file cũ (`wujia_sale`, `wujia_portal_support`, `wujia_portal_knowledge`).
**0 nhãn của sprint bị trống `msgstr`.** Con số "1344 chưa dịch" trong log là msgid QWeb portal (vốn đã
tiếng Việt, để trống là đúng) + field core kế thừa — không phải việc của sprint này.

---

## CÒN LẠI

### 1. Tách 8 va chạm "động từ vs trạng thái" (ưu tiên 1)
Một chuỗi Việt phục vụ 2 ngữ cảnh (nút bấm + nhãn trạng thái) nên bị dịch thành **một** từ. Cần tách:

| File | Chỗ | Sửa thành |
|---|---|---|
| `wujia_portal_return/models/wujia_return_request.py:12` | STATE `('rejected','Reject')` | `'Rejected'` |
| `wujia_portal_return/views/backend_return_request_views.xml:204` | filter `string="Reject"` | `"Rejected"` |
| `wujia_portal_notification/models/wujia_notification.py:21` | state `('archived','Archive')` | `'Archived'` |
| `wujia_portal_notification/views/backend_notification_views.xml:246` | filter `string="Archive"` | `"Archived"` |
| `wujia_portal_info_request/models/wujia_info_update_request.py:27` | STATE `'Reject'` | `'Rejected'` |
| `wujia_portal_info_request/views/info_request_backend.xml:80` | notebook page `string="Reject"` | `"Rejection reason"` |
| `wujia_portal_exam/models/wujia_exam_registration.py:13` | REG_STATE `'Reject'` | `'Rejected'` |
| `wujia_portal_exam/views/backend_exam_registration_views.xml:119` | filter `string="Reject"` | `"Rejected"` |
| `wujia_fleet/models/wujia_fleet_pricelist.py:9` | state `('archived','Archive')` | `'Archived'` |
| `wujia_franchise/views/wujia_franchise_management_views.xml:41` | **nút** `action_lock_portal` `string="Portal locked"` | `"Lock portal"` |
| `wujia_delivery/views/stock_picking_batch_views.xml:10` | **nút** `action_delivery_assign` `string="Vehicle assigned"` | `"Assign vehicle"` |

Nguyên tắc: **nút = động từ** (Reject / Archive / Lock portal / Assign vehicle), **trạng thái/filter = tính từ**
(Rejected / Archived / Portal locked / Vehicle assigned). Giữ nguyên nhãn field boolean `portal_locked`
= "Portal locked" và state `('assigned','Vehicle assigned')`.

Findings đầy đủ (29 mục, gồm cả false positive): `review_findings_raw.txt` cùng thư mục này.

### 2. Sinh lại `.po` sau khi sửa
Thêm cặp EN→VI mới vào `EN_VI.update({...})` trong `gen_po.py`:
`Rejected`→`Từ chối`, `Archived`→`Lưu trữ`, `Rejection reason`→`Lý do từ chối`,
`Lock portal`→`Khóa portal`, `Assign vehicle`→`Gán xe`.
Rồi chạy lại (xem "Cách chạy lại" bên dưới).

### 3. B5 — lang admin
`admin` đang `vi_VN`. Đổi sang `en_US` trên **local** để thấy kết quả chuẩn hoá.
UAT: **hỏi user trước** khi đụng.

### 4. Verify chưa làm
- SQL đối chiếu 2 ngôn ngữ:
  `select field_description->>'en_US', field_description->>'vi_VN' from ir_model_fields where model like 'wujia%'`
  → cột en_US tiếng Anh, vi_VN tiếng Việt, 0 dòng vi_VN rỗng.
- Toggle lang admin en_US ↔ vi_VN, chụp cùng 1 form → nhãn đổi đúng 2 chiều.
- **Smoke portal 391×844 phải Y NGUYÊN tiếng Việt**: `/portal`, `/portal/purchase-history` (soi kỹ nhãn
  trạng thái batch — chỗ seam), `/portal/order`, `/portal/return`, `/portal/notification`, `/portal/debt`.
- Đi hết menu backend Wujia, không menu nào 500/OwlError.
- Build lại có `--test-enable` → 0 failed.

### 5. Chốt sprint
`/wujia-end-sprint`. Trước khi commit: dò tab `5. Issue List` xem BA đã log issue crash kanban chưa —
có thì ghi `docs/qa-issue-ledger.yaml` + `qa_sync.py --apply`, **tối đa `Ready for Retest`**, không tự `Done`.

---

## Cách chạy lại toolchain

Thư mục này (`scripts/ba_spec/i18n_sprint44/`) là **dev-only, đã gitignore, KHÔNG lên server**.

```bash
cd /home/huyban/odoo-dev/WujiaTea/scripts/ba_spec/i18n_sprint44

# 1) Trích chuỗi Việt backend còn sót (đã áp map rồi nên phải ra ~0)
python3 i18n_tool.py extract

# 2) Dựng lại map từ bảng dịch (kiểm 3 điều kiện: không sót / không thừa / EN không trùng)
python3 build_map.py

# 3) Áp map lên source  (dry chạy thử trước)
python3 i18n_tool.py dry && python3 i18n_tool.py apply

# 4) Build
cd /home/huyban/odoo-dev/WujiaTea
./scripts/upgrade.sh wujia_core,wujia_delivery,wujia_fleet,wujia_franchise,wujia_sale,\
wujia_portal_exam,wujia_portal_notification,wujia_portal_return,wujia_portal_info_request,\
wujia_portal_knowledge,wujia_portal_support,wujia_portal_order_window,wujia_portal_debt,\
wujia_portal_purchase_history

# 5) Sinh lại .po
cd odoo19 && /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \
  -c ../config/odoo.conf -d wujia_tea_19 --no-http < ../scripts/ba_spec/i18n_sprint44/gen_po.py

# 6) Verify kanban headless (login admin/admin, port 8019)
python3 ../scripts/ba_spec/i18n_sprint44/check_kanban.py
```

`translations.py` = bảng dịch gốc (khoá đã chuẩn hoá khoảng trắng). `vi_en_map.json` = map sinh ra,
khoá theo chuỗi gốc nguyên văn. Sửa bản dịch thì sửa `translations.py` rồi chạy lại `build_map.py`.

---

## Bẫy đã dính, đừng dính lại

1. **`re.S` trong regex trích chuỗi Python** → `(.*?)` nuốt xuyên dòng, trích ra nguyên khối code.
   Nhãn luôn nằm 1 dòng: dùng `[^'\"\n]*`, không bật `re.S`.
2. **`ast` col_offset tính theo BYTE, không phải ký tự.** Chuỗi tiếng Việt làm lệch offset → cắt hỏng file.
   Phải thao tác trên `src.encode()`.
3. **`pkill -f "odoo-bin -c"` tự giết chính nó** vì pattern nằm trong command line của chính process đó.
   Dùng `pkill -f 'odoo[-]bin'`.
4. **Password admin local là `admin`**, không phải `Wujia@2026` (UAT) hay `wujia_admin` (master DB password).
5. **Port là 8019**, không phải 8069.
6. **English phải injective**: 2 chuỗi Việt khác nhau mà dịch ra cùng 1 English → `.po` chỉ có 1 `msgid`
   → một trong hai nhãn sẽ hiện sai tiếng Việt. `build_map.py` đã có check này.
7. **KHÔNG đụng**: toàn bộ portal QWeb, `data/*.xml`, hằng nhãn trong portal controller
   (`STATE_LABELS`, `PRIORITY_LABELS`, `SALE_STATE_META`), **mọi text `ValidationError`/`UserError`**
   (`wujia_portal_sale/controllers/portal.py:855` so khớp chuỗi `if 'khung giờ' in msg` — đổi là gãy âm thầm),
   comment/docstring tiếng Việt, `tests/`, `wj_ks_dashboard_ninja`, `wj_ks_dn_advance`.
