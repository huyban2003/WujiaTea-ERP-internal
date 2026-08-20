# Việc tồn — Thông báo nhượng quyền (sau Sprint 41)

**Lập:** 2026-07-31 · **Trạng thái sprint:** S41 đã deploy UAT · **Source: CHƯA sửa gì**

---

## Prompt mở phiên sau — paste thẳng

```
/wujia-start

Làm tiếp phần Thông báo nhượng quyền sau Sprint 41.

Đọc trước, đừng làm gì cả:
1. WujiaTea/docs/next-session-tasks-notification.md — ĐỌC HẾT, đặc biệt §0 (lượt trước
   tôi kết luận sai và đã phải gỡ khỏi sheet BA).
2. custom/wujia_portal_notification/ — models, controllers, security, views.

Ràng buộc lượt này:
- KHÔNG ghi gì lên Google Sheet. Sheet đang đúng, chỉ có phần đổi tên field. Muốn báo BA
  điều gì thì nói với tôi trước.
- Phạm vi tôi chốt là trần, không phải sàn. Thấy thêm gì đáng nói thì báo, đừng tự làm.
- Trước khi nói cái gì "đã làm / đã nghiệm thu / mâu thuẫn" — mở cột trạng thái và cột
  Out-of-scope của đúng task đó trên tab Tasks. Lượt trước sai đúng chỗ này.
- Read-before-write, ask-don't-assume. UAT chỉ đọc.

Việc cần làm, theo thứ tự:
- NOTI-03 (nhãn priority normal → "Thông thường") — làm được ngay, không phụ thuộc BA,
  không cần migration. Bắt đầu từ đây.
- NOTI-02 bước 1 (chặn mark-read khi chưa chọn cửa hàng) — làm được ngay, chưa đụng
  migration, chưa set required.
- NOTI-01 (franchise_ids) — CHỜ BA trả lời câu hỏi §1. Chưa có trả lời thì không đụng.
- NOTI-04 — để sau, gộp vào NOTI-02 bước 2.

Đọc xong thì báo tôi kế hoạch cho NOTI-03 + NOTI-02 (blast radius, file nào đụng, test
nào chạy) rồi chờ tôi duyệt.
```

Nếu BA đã trả lời câu hỏi §1, thêm dòng: *"BA trả lời câu §1 là (a)/(b): …"* và đổi thứ tự
ưu tiên — NOTI-01 lên đầu, dùng prompt riêng ở §2.

---

## 0. Dev đã làm sai gì trong lượt 31/07 — đọc trước khi làm tiếp

Chủ dự án chốt phạm vi là **chỉ đổi tên field trên sheet**. Dev làm quá phạm vi: tự ghi thêm một
cột ghi chú vào phần F của BA, và nội dung ghi chú **sai về bản chất**:

| # | Sai | Sự thật |
|---|---|---|
| 1 | Ghi "❗XUNG ĐỘT — BA sai / nhờ BA sửa" về chuyện gửi theo cửa hàng | **BA nhất quán.** Phần F dòng 742/816/872 nói không target; và Out-of-scope của chính task *"Xây dựng controller Notification MVP cho Portal"* (`Tasks` row 6) cũng ghi *"Không thêm cơ chế target theo cửa hàng, khu vực, role hoặc user"*. Chỗ lệch là **source**: `franchise_ids` thêm từ Sprint 32, **trước** khi có spec F |
| 2 | Trích `FEATURE CHECKLIST!E31` cho POR-024 | POR-024 ở **row 30**; row 31 là POR-025 |
| 3 | Viết POR-024 "đã nghiệm thu theo đúng yêu cầu đó" | Cột `Feature Status` (J) của POR-024 **đang trống** — chưa nghiệm thu |
| 4 | Viết CT-011/CT-041 "đã code xong Sprint 32" như căn cứ | Task controller Notification (`Tasks` row 6, giao 25/07, `Sẵn sàng cho AI = Yes`) có **`Trạng thái (AI)` trống → chưa nhận, chưa làm**. CT-011 thậm chí **không nằm trong phạm vi task đó** (cột E trỏ `A42:H45` = CT-041..044) |

**Đã khắc phục:** xoá sạch 20 ô cột L phần F; `Tasks!Q3` viết lại gọn, có câu thu hồi + xin lỗi BA.
Sheet hiện **chỉ còn phần đổi tên field**, mọi câu nghiệp vụ của BA nguyên văn.

**Bài học phải nhớ:** (a) phạm vi user chốt là trần, không phải sàn — "chỉ đổi field" nghĩa là
**chỉ** đổi field; (b) trước khi kết luận "tài liệu BA mâu thuẫn", phải đọc **cột Out-of-scope của
task tương ứng trên tab `Tasks`**, không chỉ đọc spec F + tab Controller; (c) kiểm tra cột
`Feature Status` / `Trạng thái (AI)` trước khi nói cái gì "đã nghiệm thu / đã làm".

---

## 1. Chờ BA trả lời (đã hỏi ở `Tasks!Q3`)

> Ô `3. Controller!H12` (CT-011) và `!H42` (CT-041) ghi *"đúng đối tượng (nhận)"*. Nên hiểu là
> **(a)** chỉ trả thông báo cho user có membership hợp lệ tại cửa hàng hiện tại, hay **(b)** thật sự
> gửi theo cửa hàng?

Chưa có câu trả lời thì **không đụng `franchise_ids`**. Task controller Notification chưa bắt đầu
nên trả lời sớm sẽ tránh làm lại.

---

## 2. Việc Dev tự sửa — source lệch spec, không phải BA sai

### NOTI-01 · `franchise_ids` nằm ngoài phạm vi MVP

`wujia.notification.franchise_ids` (M2M "Cửa hàng nhận") thêm từ Sprint 32, spec F sau đó chốt MVP
là global. Hiện **đang để trống nên vẫn broadcast** → hành vi thực tế chưa sai, không gấp.

Phụ thuộc: 11 chỗ trong `custom/wujia_portal_notification/controllers/portal.py` ·
`security/wujia_notification_rules.xml` (ir.rule portal lọc bằng field này) · form view backend.

Chờ câu trả lời §1 rồi mới chọn: đóng băng (ẩn khỏi view, luôn để trống) hay gỡ hẳn.

> **Prompt session sau:**
> "Đọc `docs/next-session-tasks-notification.md` §2 NOTI-01. BA đã trả lời câu hỏi ở §1 là <a/b>.
> Đọc source `custom/wujia_portal_notification/` trước, liệt kê đủ chỗ dùng `franchise_ids`
> (controllers, ir.rule, views, tests), rồi đề xuất 1 phương án + blast radius trước khi sửa."

### NOTI-02 · mark-read khi chưa chọn cửa hàng — code sai thật

Spec F dòng 796 ghi `franchise_id` **Required**, dòng 884 đã có sẵn message
*"Vui lòng chọn cửa hàng trước khi thao tác."* Nhưng CT-043/CT-044 vẫn cho thao tác khi
`get_active_franchise_id()` trả `False` → ghi row `franchise_id = NULL`. **UAT: 6/9 row NULL.**

Làm 2 bước: (1) chặn ở controller + trả message dòng 884 — **không cần migration**; (2) xử lý 6 row
cũ (gán hay xoá — hỏi chủ dự án) → `required=True` → gỡ được `_uniq_noti_user_no_store`.

> **Prompt session sau:**
> "Làm NOTI-02 trong `docs/next-session-tasks-notification.md` — bước 1 thôi: chặn mark-read và
> mark-all-read khi chưa chọn cửa hàng, trả đúng message spec F dòng 884. Chưa đụng migration,
> chưa set required. Đọc `wujia_portal_notification/controllers/portal.py` +
> `wujia_portal_base/controllers/portal.py:37-67` trước."

### NOTI-03 · nhãn priority `normal` → "Thông thường"

Spec F dòng 782 ghi "Thông thường", code + portal đang hiện "Lưu ý" (BA FINAL Sprint 32). Chủ dự án
đã chốt **theo BA**, tách task riêng vì S41 cấm đụng UI Portal.

5 chỗ hardcode: `models/wujia_notification.py:11` · `controllers/portal.py:43` ·
`views/portal_notification.xml:11,263` · `static/src/js/header_bell_badge.js:21` (còn key legacy
`low`). Nhớ bump `?v=` + chạy `-u`.

**KHÔNG cần migration** — `normal` là giá trị lưu DB, "Lưu ý" chỉ là nhãn hiển thị.

> **Prompt session sau:**
> "Làm NOTI-03 trong `docs/next-session-tasks-notification.md`: đổi nhãn priority `normal` từ
> 'Lưu ý' sang 'Thông thường' ở đủ 5 chỗ hardcode, bump `?v=`, chạy `-u` cho RC=0. Grep lại
> `'Lưu ý'` trong `custom/` để chắc không sót chỗ nào."

### NOTI-04 · các điểm nhỏ khác (làm khi tiện, hoặc gộp vào NOTI-02)

| | Spec F | Source | Ghi chú |
|---|---|---|---|
| `published_date` | dòng 765: Conditional / Default Empty | `required=True` + `default=now` | đổi sẽ ảnh hưởng `_order`; UAT 15/15 có giá trị |
| `content` | dòng 753 Required=Yes ↔ dòng 819 cho lưu nháp | validate khi publish | **spec tự mâu thuẫn**, đã hỏi BA ở Q3 |
| `type.code` | dòng 788: Required=No | `required=True` + unique | portal trả `type_code` cho FE chọn màu |

---

## 3. Việc BA phải tự làm (đã nhắc ở `Tasks!Q3`, đừng tự sửa hộ)

- `Tasks!J3` (Acceptance) vẫn ghi `wujia.announcement*` → BA cập nhật theo bảng đối chiếu tên.
- Field có trong source nhưng chưa có dòng trong spec F, nếu BA muốn bổ sung:
  `dispatch_number`, `franchise_ids`, `pin_expiry_date`, `priority_label`; trên `type`:
  `bg_color`, `text_color`, `icon`.

---

## 4. Đã làm xong, đừng làm lại

- Đổi tên model/field: `1. Model/ Field` phần F **33 ô** + `3. Controller` **5 ô** (E12, E42–E45).
  Script: `scripts/ba_spec/spec_f_sync.py` (dev-only, gitignored).
- `Tasks` row 3: P3/Q3/R3 viết lại tiếng Việt có dấu. Script: `task_s41_rewrite.py`.
- Xoá 20 ô ghi chú cột L. Script: `spec_f_wipe_notes.py`.
- Backup 3 tab + xlsx toàn sổ trong scratchpad phiên 31/07 — **bridge không có undo**, lần sau backup
  trước khi ghi.

**Bẫy đã trả giá:** tên tab thật là `1. Model/ Field` (có `/`). Đừng lấy tên từ
`export?format=xlsx` — Excel cấm `/` nên bị sanitize thành `1. Model Field`, gửi cho bridge là lỗi.
Cũng đừng dò bằng gviz `sheet=<name>` — sai tên nó **im lặng trả tab đầu tiên**. Cách đúng:
`sheet_io._post({'action':'ping','sheet':'1. Model'})` → bridge trả tên thật.
