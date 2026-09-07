# Prompt phiên sau — D4g: soi UAT cho D4f + khép cụm SurfaceCard

> Dán nguyên file này sau khi chạy `/wujia-start`.

Làm **lượt D4g** của cụm SurfaceCard, issue `UI-SURFACECARD-001` (STT 127 · `CMP-SC-001` ·
tab `UI Component` gid 488333015 · đang `Ready for Dev`).

Phiên này có **hai phần tách bạch, làm đúng thứ tự**:
**Phần 1 — soi UAT cho D4f đã đẩy lên** (bắt buộc, chặn mọi thứ phía sau).
**Phần 2 — khép nốt cụm** rồi mới bàn tới `Ready for Retest`.

---

## Bối cảnh

D4f (commit `a3d4614`, nhánh `dev/2026-09-05-d4c`) đã gỡ hẳn Bootstrap `.card` khỏi Portal:
31 call site, 89 thẻ `.card` hiện → **0**, `wujia_portal_layout` `19.0.38.0.0`, assets `?v=1220`.
Số đo đầy đủ ở **`docs/d4f-acceptance-matrix.md`** — **đọc trước khi làm gì**, đặc biệt §12 LIMIT.
Bài học kỹ thuật ở `docs/next-session-clusters-D.md` mục **"Bài học D4f"** (11 mục).
Tiến độ cụm: **144/384 ≈ 37%**.

---

## PHẦN 1 — Soi UAT (chặn, không làm xong thì đừng sang phần 2)

### 1.1 Vì sao đây là rủi ro CAO NHẤT của cả cụm

D4f không dời dáng giữa các lớp của Wujia như 5 lượt trước. Nó **dựa vào việc `.card` biến mất
khỏi DOM** để thoát khỏi tranh chấp với bundle `web.assets_frontend` của Odoo. Mà **UAT có
`website` + `website_sale` nên bundle frontend KHÁC hẳn local** — chuyện này đã lật ngược kết quả
ở C6 và D2. Local xanh **không** kết luận được gì cho UAT.

### 1.2 Thứ tự bắt buộc — đo được là phải deploy TRƯỚC

Không đo UAT được khi UAT chưa có code. Nên:

1. Kiểm tra UAT đã mang commit `a3d4614` chưa. Cách rẻ nhất: mở
   `http://113.161.187.126:8019/` (login `admin/Wujia@2026`), xem asset URL trong HTML nguồn có
   `_components.css?v=1220` không, và `ir_module_module.latest_version` của `wujia_portal_layout`
   có phải `19.0.38.0.0` không.
2. **Chưa có** ⇒ **DỪNG, báo chủ dự án deploy** (`git pull` + `-u` 7 module:
   `wujia_portal_layout,wujia_portal_base,wujia_portal_return,wujia_portal_sale,
   wujia_portal_support,wujia_portal_knowledge,wujia_portal_info_request`). Đừng tự deploy.
3. **Đã có** ⇒ chạy tiếp 1.3.

### 1.3 Đo UAT — CHỈ ĐỌC, theo giới hạn QA §10

🔴 **Không tạo đơn / hoá đơn / email thật. Không `-u`. Không sửa dữ liệu.** Chỉ GET + đọc DOM.

Harness dùng lại: `scratchpad/d4f_measure.py`, `d4f_shot.py`, `d3_review.py` — trỏ `BASE` sang
`http://113.161.187.126:8019`. Ba con số phải trả lời:

| Câu hỏi | Ngưỡng đạt |
|---|---|
| Còn thẻ `.card` nào hiện trên UAT không? | **0** — nếu >0 thì bundle UAT render khác local, phải truy ngay |
| Viền/bo góc/bóng của `.wj-surface-card` trên UAT | viền `#EEF2F5` PC / `#E5E7EB` mobile · radius 16/14 · **shadow none** |
| `website`/`website_sale` có chèn rule nào đè `.wj-surface-card` không? | dùng bộ truy chủ CSSOM `scratchpad/d4f_who75.py` — **0 rule ngoài `_components.css`** |

Ít nhất 3 route × 3 khổ (1440/390/360): một màn có `__head`+`__foot` (`/portal/support/<id>`),
một màn `--flush` bảng tràn mép (`/portal/return`), một màn lưới thẻ (`/portal/franchises/<id>/profile`).
⚠️ Route/dữ liệu trên UAT khác local — **tra id thật trước**, đừng chép id 2/40 của bản copy.

**Ra kết quả:**
- **Khớp local** ⇒ ghi vào `docs/d4f-acceptance-matrix.md` mục mới "§13 Soi UAT", gỡ LIMIT 7,
  rồi chạy `scripts/ba_spec/qa_deploy_mark.py`.
- **Lệch** ⇒ **đây là phát hiện chính của phiên**. Ghi lại chuỗi rule khớp theo thứ tự nạp, xác
  định rule nào của `website` đang đè, rồi hỏi chủ dự án trước khi sửa. Không tự vá.

---

## PHẦN 2 — Khép nốt cụm D4

### 2.1 🔴 Đính chính số liệu TRƯỚC khi lập kế hoạch

Kiểm kê `docs/d4-surfacecard-inventory.md` ghi phần còn lại là **"`wj-auth-card` (15) + nhóm
Khảo sát (17)"**. **Con số 15 SAI** — đó là đếm chuỗi con. Đếm theo **token lớp** (`class=` tách
`.split()`) ra:

| Token | Số lượng | Là gì |
|---|---:|---|
| `wj-auth-card` | **4** | **shell thật** — `login_page.xml:12 · 73 · 115 · 158` |
| `wj-auth-card--forgot` | 3 | modifier |
| `wj-auth-card__title` | 4 | **nội dung**, không phải khung |
| `wj-auth-card__sub` | 4 | **nội dung**, không phải khung |

Đây đúng cái bẫy đã thổi kiểm kê `.card` từ 44 lên 75 (bài học D4f #2). **Đếm lại nhóm Khảo sát
bằng cùng phương pháp trước khi ước lượng khối lượng.**

### 2.2 Hai họ còn lại — và cả hai đều VƯỚNG, phải hỏi trước

**(a) `wj-auth-card` — 4 shell, `_auth.css:189` + `:465` (trong `@media`)**

Khai `padding, border-radius, background, box-shadow`. Về kỹ thuật là migrate được ngay.
**Nhưng cụm auth thuộc THIẾT KẾ ĐÃ NGHIỆM THU S39.** Luật §7 của inventory: chỗ chỏi issue đã
nghiệm thu thì **ghi LIMIT, KHÔNG tự đè**.
⚠️ Lưu ý: `wj-auth-card` có **shadow**, mà SurfaceCard **cấm shadow** theo BA — nên migrate là
**đổi dáng thấy được** ở 4 màn đăng nhập thật (khác hẳn 3 call site auth của D4f, vốn là template
chết, render 0 thẻ).
→ **Hỏi chủ dự án**: migrate và chấp nhận mất shadow ở 4 màn auth, hay giữ nguyên + ghi LIMIT?

**(b) Nhóm Khảo sát — module `wujia_portal_inspection` đang `uninstalled`**

7 họ có khai dáng khung, tất cả ở `portal_inspection.css`:

| Lớp | Khai |
|---|---|
| `.detail-card-box` | background, border-radius, border, **box-shadow** |
| `.summary-2x2-card` (+ `.severe-card`) | border-radius, border, background, padding |
| `.wj-success-card` | background, border-radius, padding, **box-shadow** |
| `.wj-warning-card` | background, border-radius, padding, **box-shadow** |
| `.wj-dist-card` | background, border, border-radius |
| `.inspection-card-item` | border-radius, border, background |
| `.form-card-box` (4 call site) | — không khai dáng, kiểm tra lại xem có phải chỉ là lớp bố cục |

Ba chuyện chặn: module **chưa cài** nên không đo được lúc chạy · BA ghi nhóm này *provisional* ·
và chính nó là nguồn của **2 test đỏ có sẵn** + **1 cờ RULE 1** (404 tràn ngang 11px @360).
→ **Hỏi chủ dự án**: cài `wujia_portal_inspection` lên DB đo để migrate cho trọn cụm, hay hoãn
sang khi BA chốt spec (và cụm D4 đóng ở mức 144 + 4 auth)?

### 2.3 Nếu được chốt làm — theo đúng khuôn D4f

Luật chung #1–#9 ở `docs/next-session-clusters-D.md` **cộng thêm** bài học D4f:
- Lớp của **framework** thì bỏ; lớp riêng của **module** thì giữ.
- Đếm bằng **token**, cả trong kiểm kê lẫn trong regex của guard.
- Guard dùng `_rules_anywhere()` chứ đừng `_rule()` (chỉ trả rule đầu tiên).
- Guard phải **đếm**, đừng dùng `in` (view nhiều thẻ sẽ xanh oan).
- Vòng đột biến phải tự phát hiện **"0 test đã chạy"**, nếu không `-u` abort = xanh giả.
- `overflow: hidden` là tài sản riêng, gỡ thì phải trả bằng radius trên chính phần tử con.
- Utility `p-2`/`py-2` ở call site là nhịp cố ý — giữ.

Đo phải có đủ: bảng trước–sau 5 khổ (1440/1024/992/390/360) kèm `pageH` **và số record trong
viewport** (BA #11) · nhịp header→body **tuyệt đối** (mốc `0×2 · 12×50`, không được vỡ) ·
RULE 1+2 (`d3_review.py --portal-login anh.owner` — **bắt buộc** cờ này, mặc định rơi về `admin`
là Pass rỗng; mốc 5 cờ) · ảnh trước–sau + diff pixel · quét đặc hiệu CSS toàn `custom/**/*.css`
(**loại tên con BEM**) · đột biến 100% đỏ đúng chỗ + run đối chứng xanh
(mốc: **74 test, 2 lỗi đỏ có sẵn**).

### 2.4 Điều kiện để bàn tới `Ready for Retest`

Chỉ khi **cả ba** đạt: Phần 1 UAT khớp · 2 họ ở 2.2 đã có chủ (migrate xong **hoặc** có LIMIT
được chủ dự án chốt) · `Kết quả mong muốn` của issue đạt **≥90%**.
**Dev KHÔNG tự đóng `Done`** (QA Operating Standard §2). `qa_sync.py` chạy dry-run trước;
`--apply` chỉ khi chủ dự án chốt.
⚠️ `scripts/ba_spec` là **symlink** ⇒ `qa_sync.py` tự tính ledger thành
`/home/huyban/docs/qa-issue-ledger.yaml` và chết `FileNotFoundError`. Nạp module rồi ép
`m.LEDGER` trỏ đúng repo, **đừng sửa file toolchain**.
⚠️ Khối tiến độ D4 trong ledger là **comment YAML** cố ý, nên `qa_sync` báo "không có trong
ledger" — **đúng như thiết kế**, không phải lỗi.

---

## Ngoài phạm vi — thấy cũng để yên

12 call site module bên thứ ba (`wj_ks_dashboard_ninja` ×10, `wj_ks_dn_advance` ×1, `mcp_server`
×1) · `/my/franchises/<id>` chạy bundle `portal.portal_layout` của Odoo, không nạp CSS Wujia
(guard đã ghim thành ngoại lệ 1 phần tử) · 26 lượt bề mặt trắng mobile (20 → `CMP-ES-001`,
4 → `UI-DATALIST-001`, 2 chưa có chủ) · CardHeader = cụm **D3** · bug tz `Asia/Saigon` = **R3**
· 2 ô nhịp `0px` ở `/portal/notification/41` = **R2** · hội tụ token `--wujia-border` ↔
`--wujia-morder-border` (**phải hỏi trước**).

## Quy tắc phiên

- Portal đo bằng **`anh.owner` / `wujia@test123`** — quá 5 lần sai dính *Too many login failures*.
- Cổng: `8070`/`8071` cụm R · `8072` server đo · `8019` **UAT** — đừng đụng. `8075` vừa trả lại.
- Log của server đo đặt tên theo **giờ UTC**, không phải giờ máy — đọc nhầm file là **xanh giả**.
- Đừng `pkill -f "odoo.<x>.conf"` (tự giết phiên); lấy PID bằng `ps aux | grep "[o]doo…"`.
- `scratchpad/` và `scripts/ba_spec/` là **dev-only, gitignored, KHÔNG commit**.
  `.gitignore` không khớp symlink nên `scripts/ba_spec` vẫn hiện `??` — **đừng `git add -A`**.
- Hạn chế comment trong code.
- Hết cụm D4 thì chạy `/wujia-end-sprint`.
