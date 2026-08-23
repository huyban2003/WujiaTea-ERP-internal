# Refactor plan — cụm R1–R5 (khảo sát 2026-08-23)

**Nguồn:** phiên review code 23/08/2026 theo yêu cầu chủ dự án — lo ngại code chấp vá sau
~10 sprint fix-theo-issue, không chắc đạt rule perf 1500 user. Review **4 chiều**
(perf / clean-dead code / security sudo-IDOR / spec-drift vs Google Sheet) trên toàn bộ
custom **TRỪ phần anh Thái** (`wujia_portal_inspection`, models
inspection/attendance/document + survey controllers + CSV-runtime i18n trong
`wujia_franchise`, toolchain dịch) và trừ dashboard `wj_ks_*` (workstream riêng).

**Cách dùng:** `/wujia-start` → nói "làm cụm R<n>" → đọc khối tương ứng dưới đây.

---

## KẾT LUẬN TỔNG (đọc trước khi hoảng)

**Code KHÔNG mục nát.** Khác với lo ngại, phần nền giữ kỷ luật tốt qua các sprint fix:

- **Perf 1500-user đạt ở các đường nóng**: badge chuông = 2 câu đếm cho mọi trang
  (`wujia_portal_notification/controllers/portal.py:125`, có chú thích 1500-user);
  Home `_dashboard_values` = 1 query batched/metric, không ORM trong template loop;
  helper `portal_money`/`paginate`/`group_counts` (1 `_read_group` thay N `search_count`)
  tập trung ở `wujia_portal_base/controllers/utils.py`; ormcache đúng chỗ
  (`_get_accessible_franchise_ids`, `_wj_portal_langs`, `wujia.return.issue.type`);
  133 field `index=True`.
- **Security: mẫu guard fail-closed nhất quán** ở các chỗ đã soi (sale `_get_store_line`
  verify ownership trước khi dùng; return verify `line.order_id.franchise_id` +
  attachment whitelist theo record; info_request check accessible trước sudo browse;
  exam dùng `.exists()` + domain published). **0 `csrf=False`**, `auth='public'` chỉ ở
  auth/redirect/set-lang (hợp lệ).
- Nợ thật sự nằm ở **dọn dẹp** (comment sử ký, hex cứng, CSS chết) và **vài điểm lệch
  spec cần BA phân loại** — chia cụm dưới đây.

**Quick-win đã làm ngay 23/08** (commit `2d323fe`): xoá **42 rule / 190 declaration CSS
chết** khỏi `_components.css` (họ back-row/title cũ bị `wj_page_header` S33 thay, 3 class
listhead C8 đã xoá ở template nhưng CSS còn sót, utility chưa từng dùng). Diff ngữ nghĩa
0 thay đổi ngoài xoá; acceptance + B4 286/286 + 24 test xanh sau xoá.

---

## Bảng cụm

| Cụm | Việc | Module đụng | Rủi ro | Ưu tiên |
|---|---|---|---|---|
| R1 | Dọn comment sử ký + hex→var | ~15 module (top: portal_home.xml 9, portal_support.xml 8, layouts/assets/knowledge 6) | Thấp (0 hành vi) | Trung |
| R2 | Chuẩn hoá datetime/date format còn sót | portal_base (6 chỗ), rà thêm | Thấp | Thấp |
| R3 | Perf backend nhỏ + bug tz báo cáo | wujia_delivery, wujia_portal_report | Thấp | Trung (có 1 bug thật) |
| R4 | Spec-drift: báo BA phân loại phase | 0 code — chỉ sheet/ghi chú | 0 | Cao (rẻ, tránh hiểu nhầm) |
| R5 | Utility class layer: giữ hay bỏ | wujia_portal_layout | Thấp | Thấp |

Không cụm nào chặn nhau — làm rời từng session, mỗi cụm 1 lần `-u` module tương ứng.

---

## R1 — Dọn comment sử ký + hex cứng → token (1 session)

**Hiện trạng:** 168 chỗ comment kể lịch sử sprint kiểu "Sprint 12 (2026-06-07): …" trong
py/xml/js (đếm theo file → `scratchpad` scan 23/08, top: `portal_home.xml` 9,
`portal_support.xml` 8, `layouts.xml` 6, `assets.xml` 6, `portal_knowledge.xml` 6,
`utils.py` 5). 63 hex cứng trong 4 file CSS layer mình
(`_components/_pc_components/_interaction/_wujia_theme`).

**Luật làm (chốt theo rule 15/08 "comment ít thôi"):**
- Comment giải thích **tại sao** (gotcha, blast radius, quyết định BA) → **GIỮ**, chỉ cắt
  tiền tố "Sprint N (ngày):" nếu phần còn lại vẫn đủ nghĩa.
- Comment kể **cái gì đã đổi so với sprint trước** (code tự nói) → xoá.
- Hex → `var(--wujia-*)` CHỈ khi token cùng giá trị đã tồn tại trong `_variables.css`
  (ca 1-1). Hex không có token tương ứng → **để nguyên + liệt kê ra file cho BA/chủ dự án
  chốt thêm token**, KHÔNG tự đẻ token mới (đúng rule Ask-don't-assume).
- `rgba(...)` shadow/overlay đặc thù từng component → để nguyên.

**Nghiệm thu:** build `-u` RC=0; diff CSS qua semantic-parser (mẫu script phiên 23/08 —
parse rule set cũ/mới, declarations mất = đúng danh sách chủ đích, THÊM = 0); smoke 5 trang
× 2 viewport; grep đếm lại "Sprint [0-9]" giảm về ~0 ở file đã xử.

---

## R2 — Date format còn sót (nửa session, ghép được với R1)

**Hiện trạng:** 6 chỗ `t-out="....strftime('%d/%m/%Y') or '—'"` ở
`portal_franchise_profile.xml:48,98,100` + `portal_franchise_information.xml:194,218,223`.
Đây là field **Date** (không phải Datetime) nên **KHÔNG có bug lệch giờ** — chỉ là biểu
thức lặp 6 lần và lệch convention (mọi chỗ khác đi qua `wj_dt`/`fmt_local_dt`).

**Việc:** thêm nhánh format date thuần vào helper sẵn có (hoặc helper `wj_d` cạnh `wj_dt`
trong cùng file `utils.py` — KHÔNG file mới), thay 6 chỗ. Rà thêm toàn portal xem còn
`strftime` nào trên **Datetime** không qua helper (scan 23/08 không thấy, double-check khi
làm).

**Nghiệm thu:** 2 trang franchise profile/information trước–sau byte-identical phần render
(cùng data), build RC=0.

---

## R3 — Perf backend nhỏ + 1 bug thật (1 session)

1. **Bug thật (làm trước):** `/portal/reports/orders` **500** khi user có
   `tz='Asia/Saigon'` (pytz không nhận) — pre-existing, đã ghi §5 compact summary từ lâu.
   Fix ở `portal_tz()` (`wujia_portal_base/controllers/utils.py:38`): map alias
   `Asia/Saigon`→`Asia/Ho_Chi_Minh` (hoặc try/except UnknownTimeZoneError → fallback),
   sửa MỘT chỗ helper là mọi trang hưởng. Kèm test user tz rác.
2. `wujia_delivery/models/wujia_fleet_management.py:20` `_compute_current_batch`:
   1 `Batch.search`/vehicle (N+1). Backend fleet ít record nên không cháy, nhưng sửa rẻ:
   1 search gộp `('vehicle_id','in',self.ids)` order sẵn rồi map lấy bản ghi đầu mỗi xe.
3. `wujia_portal_notification/models/wujia_notification.py:222`
   `_compute_target_preview_count`: mode `filter` đếm 1 query/record — **hợp lệ**
   (mỗi record một domain riêng, backend form ít record; broadcast đã memo). **Không sửa**,
   ghi lại để khỏi soi lại lần nữa.

**Nghiệm thu:** đặt tz `Asia/Saigon` cho user test → `/portal/reports/orders` 200; đếm
query `_compute_current_batch` với 5 xe = 1 câu; hồi quy delivery + report 2 viewport.

---

## R4 — Spec-drift: cần BA phân loại, KHÔNG code (nửa session, chủ yếu viết note gửi BA)

Đối chiếu tab `1. Model Field` (293 field nhận diện được) với source: **50 field sheet có
mà code không có**. Soi từng nhóm thì KHÔNG phải thiếu sót code:

- **~40 field họ Employee/Attendance/Shift/Leave/Expense** (`check_in`, `shift_id`,
  `work_date`, `planned_hours`, `store_employee_*`…) = tính năng **Phase 2 Employee Mgmt**
  (đúng danh sách Phase 2 ở compact summary §5) — chưa build, sheet không đánh dấu phase.
- **4 field `ticket_max_file_*` / `ticket_allowed_file_types`**: BA spec giới hạn file
  ticket **cấu hình được**, code đang hardcode default 5MB/10 file ở helper
  `attach_files_to_record` (`utils.py:165`). Nếu BA thật sự cần chỉnh runtime → mở issue
  riêng (thêm `ir.config_parameter`, vẫn 1 chỗ ở helper); nếu không → BA sửa sheet.
- **`author_name`/`author_role`/`has_hq_reply`/`is_internal`**: spec message ticket kiểu
  bảng riêng, code đã đi `mail.message` qua `message_post()` theo **ADR-016** — drift có
  chủ đích, đề nghị BA chú thích ADR vào sheet.
- **`order_from`/`order_to`**: code là `order_time_from/order_time_to`
  (`wujia_order_window.py:25`) — BA đặt tên lý tưởng hoá, chức năng đủ.

**Việc:** viết 1 note ngắn (theo bài học 07-31 "ghi sheet thì ghi ít") gửi BA đề nghị:
(a) đánh dấu cột Phase cho nhóm Employee/Attendance; (b) chốt ticket limits config hay
default; (c) chú thích ADR-016 + tên field thật. **Không tự sửa sheet nội dung spec.**

---

## R5 — Utility class layer: quyết định giữ hay bỏ (nửa session, cần chủ dự án)

`_components.css` đầu file còn **lớp utility Sprint 8**: `.wujia-btn/-primary/-secondary`
(alias cạnh `.btn` Bootstrap), `.wujia-h1/h2` (alias cạnh `h1/h2`). Các selector này đi
KÈM selector sống (`.btn`, `h1`) trong cùng rule nên phiên 23/08 **không xoá** (xoá là đổi
styling thẻ thật). Alias riêng phần `.wujia-*` hiện **0 chỗ dùng** trong xml/js.

**Câu hỏi cho chủ dự án:** coi đây là API utility cho code sau (giữ, ghi vào
`wujia-design-system.md`) hay legacy (tách alias khỏi rule chung rồi xoá)? Làm theo đáp án,
30 phút.

---

## Những thứ đã soi và CHỐT KHÔNG LÀM (để session sau khỏi soi lại)

- `sudo()` 191 chỗ trong controllers: đã spot-audit các module nóng nhất (sale 24, base 23,
  notification 15, return 12, exam 11, info_request 8) — đều có guard
  accessible/franchise/ownership **trước** sudo, mẫu fail-closed. Không mở cụm audit riêng;
  duy trì bằng luật "sudo mới phải kèm guard" khi review từng PR.
- `search_count` 66 chỗ: phân bố constraint/count hợp lệ, các chỗ nóng đã batch
  (`group_counts`). Không gộp thêm.
- Duplicate helper: KHÔNG thấy copy-paste helper giữa module — các module đều import từ
  `wujia_portal_base.controllers.utils` (mẫu tốt, giữ).
- `wujia_franchise/models/wujia_supervision_schedule.py:147` `search_count([]) + 1` làm
  sequence (race): **code anh Thái** — ngoài scope theo quyết định chủ dự án 23/08.

## Tiến độ cụm

R1 ⬜ · R2 ⬜ · R3 ⬜ · R4 ⬜ · R5 ⬜ — quick-win dead CSS ✅ 23/08/2026 `2d323fe`.
