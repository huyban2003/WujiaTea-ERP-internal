# Tồn đọng toàn dự án WujiaTea — gom 05/10/2026

Một chỗ duy nhất liệt kê mọi việc còn treo, chia lô làm dần. Mỗi phiên: làm lô đầu bảng "Thứ tự làm", xong thì gạch ở đây +
ghi `f-progress.md`. Nguồn gom: compact summary §5, `f-progress.md` (mục Nợ), chapter 74/77/78, `next-session-clusters-{H,J}.md`.

## 1. Thứ tự làm (chủ dự án chốt 04–05/10)

| # | Lô | Nội dung | Số phiên | Plan |
|---|---|---|---|---|
| 1 | **Phần V — Việt hoá source** | 2 659 chuỗi VN viết cứng → tiếng Anh + `.po` (~~V0~~ ✅ 05/10 → **V1** … V8 → ★VR) | 9 còn lại | `next-session-clusters-J.md` §6 |
| 2 | J-T4 | Tool dịch: nhập/xuất CSV kiểu Thái + zip `.po/.pot` | 1 | `next-session-clusters-J.md` §5 |
| 2b | J-T5 | Tool dịch: dịch tự động DeepL — chọn ngôn ngữ → dịch hàng loạt → rà → Áp dụng | 1 | `next-session-clusters-J.md` §6b |
| 3 | J-O0…O4 + ★JR | Portal Vận hành nhượng quyền (O0 đối chiếu + câu hỏi BA → O1 luật → O2 → O3+O4 → review) — **tạm gác, chủ dự án hỏi BA trước (05/10)**; chưa có trả lời thì nhảy sang lô 4 | 5 | `next-session-clusters-J.md` §5 |
| 4 | Issue List — cụm I | I1 #155 → I2 #62 → I3 #154 → I4a/b #152 → I5 #153 → ★IR | 6 | `next-session-clusters-H.md` §3 |
| 5 | Issue List — 10 issue mới | STT 156, 157, 159, 160, 162–167 — **chưa phân cụm** (164, 167 dính ngôn ngữ ⇒ xem gộp vào Phần V) | ? | phân cụm ở đầu lô |
| 6 | Cụm H | Chuẩn hoá component lượt 2 (H0–H10 + ★HR-1/2) | 12 | `next-session-clusters-H.md` |

Issue List vẫn là task thường trực: đầu mỗi phiên chạy `issue_queue.py --dev`; issue **Retest Failed** / Severity High mới thì báo
chủ dự án trước khi làm lô kế.

## 2. Chờ lệnh chủ dự án (làm được ngay khi có lệnh)

- [x] ~~Commit J-T1+T2~~ — `ba08698e`, đã push 05/10.
- [ ] **Commit J-V0** (`wujia_i18n` 19.0.1.1.0 + `wujia_portal_layout` 19.0.60.1.0 + 2 script mới + docs/i18n-pairs + baseline).
- [ ] **Deploy UAT J-V0**: gộp vào lệnh `-i wujia_i18n` (tự bật zh_CN) (`wujia_portal_layout` đã có trong lệnh `-u` J-B2 ⇒ không thêm lệnh).
- [ ] **Deploy UAT J-B2**: `-u wujia_core,wujia_portal_layout,wujia_portal_base,wujia_portal_debt,wujia_portal_sale,wujia_portal_exam,`
      `wujia_portal_return,wujia_portal_support,wujia_portal_delivery,wujia_portal_notification,wujia_portal_purchase_history,wujia_return`.
- [ ] **Deploy UAT J-T1+T2**: `-i wujia_i18n` → app "Bản dịch" → Quét chuỗi.
- [ ] **Top bar PC 992 (`bea5fa8`)**: đã push `origin/main`; **chưa xác nhận đã deploy UAT** ⇒ deploy `-u wujia_portal_layout,wujia_portal_base`
      + đo chỉ-đọc 992/993/1000/1199 với `em.hcm`.

## 3. Chờ BA / chủ dự án trả lời

| Chủ đề | Câu hỏi | Chặn lô |
|---|---|---|
| ~~Phần V~~ | ✅ chốt 05/10 (§6 plan J): JS qua `data-wj-msg-*` · mặc định vi_VN · bật hết vi/en/th/zh · EN không cần BA duyệt, ZH/TH DeepL — **gửi BA 1 danh sách câu cần sửa ở ★VR** | — |
| Vận hành | Chấm công/nghỉ phép có trong portal? · duyệt ca (cửa hàng/HQ) · Staff xem gì · gắn nhân viên ↔ tài khoản portal · spec Model Field mục G lệch backend · Figma | J-O0 |
| Dịch tự động | Tài khoản DeepL (Free/Pro) + API key · đồng ý gửi chuỗi giao diện ra DeepL · ai rà từng ngôn ngữ | J-T5 |
| ADR-027 | 7 câu hỏi BA (chapter 74 §Câu hỏi) | áp `auto_install` |
| Chuẩn component | 19 câu "CẦN BA CHỐT" (`ba-component-spec-proposal.xlsx`) + gửi 2 PDF chuẩn component | cụm H |
| Issue #146 (G4) | Routing `/` — BA đã xoá dòng khỏi sheet, chờ BA mở lại | — |
| UAT dữ liệu | Bảng giá UAT đang USD — đổi VNĐ? · cột R sheet 6 dòng | — |
| BA retest | 11 ID Ready for Retest từ cụm G (theo dõi qua `issue_queue`) | — |

## 4. Nợ kỹ thuật (xếp vào phiên gần nhất cùng module)

- [ ] Áp `auto_install: True` cho module ghép thuần (`portal_report`, `portal_purchase_history`, `portal_delivery`, 3 mobile Thái) — 1 phiên, sau 7 câu ADR-027.
- [ ] Nợ chapter 77: ghi trực tiếp ở `portal_sale` (chuyển về L2) · `_sql_constraints` cũ → `models.Constraint` · tài liệu bàn giao Thái.
- [ ] 2 error fixture có sẵn trong suite `wujia_sale`.
- [ ] `lang.js` code chết (template đầu tư) vẫn nạp ở `wujia_portal_layout/views/assets.xml:119` ⇒ xoá ở J-V1.
- [ ] `@route(type='json')` deprecated (Odoo 19 ⇒ `jsonrpc`) ở 5 controller portal (exam, info_request, knowledge, notification, sale) + `wj_ks_dashboard_ninja` — gộp vào phiên V cùng module (`wujia_franchise_inspection` là của Thái).
- [ ] `check_layers.py`: 3 module chưa phân tầng (`wujia_audit`, `wujia_fields_value`, `wujia_metabase_connector`) · R7 ×2 trong `wujia_franchise` (Thái).
- [ ] Tool dịch: vi_VN báo "chưa dịch" với câu gốc đã là tiếng Việt (tự hết sau Phần V) · chuỗi code chỉ áp sau xuất `.po` + restart (J-T4).
- [ ] Token `--wujia-kpi-separator-*` còn trong layout · FYI BA về màu thanh tiến độ/pill vai trò (từ G3a).
- [ ] Safe area chưa đo iPhone thật · nhánh Đặt hàng không có danh mục chưa đo trình duyệt.

**Code của Thái — chỉ báo, không sửa:** 284 chuỗi VN viết cứng (lọc `owner=Thái` trong `vn-hardcode-inventory.csv`) · chart Khảo sát
`#28A9DF` chưa theo màu brand (`wujia_portal_inspection`) · `.po` của `wujia_franchise_inspection` lỗi "unknown occurrence:
web_survey_ui" · `msgid ""` rỗng ở `wujia_franchise_inspection.py:1725` · test `wujia_franchise` import file đã xoá (vì vậy không
`-u wujia_core --test-enable` trên DB đủ module).

## 5. Dọn máy local (không ảnh hưởng UAT)

- [ ] Khôi phục filestore local (`scripts/dev/filestore_pack.py` máy còn filestore → `filestore_restore.py` trên Mac).
- [ ] Xoá DB nháp: `wujia_b1`, `wujia_b1t`, `wujia_b2`, `wujia_b2h`, `wujia_b2t`, `wujia_b2u`, `wujia_t1`, `wujia_t1t` + các DB đo cũ
      (`wujia_e4*`, `wujia_f*`, `wujia_fra3_*`, `wujia_g*`, `wujia_rhythm_*`) + filestore tương ứng + worktree `scratchpad/b2/head`.
- [ ] Dừng các server Odoo cũ còn giữ slot Postgres (g1, g3s, g5s:8055, e4b1, b2…).
