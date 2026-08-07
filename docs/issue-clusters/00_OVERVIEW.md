# Issue List — phân cụm & chỉ điểm root cause

**Ngày review:** 2026-08-02 · **Nguồn:** tab `5. Issue List` (gid `335593633`), 63 dòng
**Phạm vi:** 37 issue Dev đang giữ việc = 24 `Ready for Dev` + 13 `Retest Failed`
(25 `Done` + 1 `New` không xét)

**Cách review:** đọc CSV công khai → đối chiếu source `custom/` → **đo trực tiếp UAT**
(`http://113.161.187.126:8019`, headless Chromium, 1920×1080 + 391×844, login admin):
bounding-box, computed-style, duyệt `document.styleSheets` tìm rule thắng cascade, submit form thật.

> ⚠️ Nhiều issue `Retest Failed` được BA đo ngày **23–25/07** trên build `cd1025d`/`bd55ef9`,
> trong khi UAT đã deploy tới hết **Sprint 47 (02/08)**. Đã đo lại — 3 issue **không còn tái hiện**.
> Bài học §12: "đa số Retest Failed thực ra đã đúng trên server, BA test build cũ trước deploy".

---

## Bảng tổng — 37 issue → 9 cụm

| Cụm | Issue | Sev | Trạng thái sheet | Root cause | Tin cậy |
|---|---|---|---|---|---|
| **A** Shell PC | UI-PC-SHELL-001 | Low | Retest Failed | `style.css` (0,3,0)`!important` thắng `_wujia_theme.css` (0,1,0) → sidebar kẹt 260px | ✅ 95% |
| **A** | UI-PC-BASE-010 | High | Ready for Dev | *(cùng gốc trên)* + grid logo/menu chưa theo source | ✅ 95% |
| **A** | UI-01 | High | Retest Failed | `html body .content{margin-left:300px}` dính cả `div.navbar-container.content` | ✅ 95% |
| **A** | UI-PC-BASE-001 | Low | Ready for Dev | Vuexy `.content-wrapper{padding 2.2rem; margin-top 6rem}` chưa override | ✅ 95% |
| **B** Header PC phải | UI-03 | High | Retest Failed | thiếu glass pill + avatar đặt sai bên; wrapper 226×62.3 sát mép 1920 | ✅ 90% |
| **B** | UI-PC-BASE-011 | Low | Ready for Dev | cart/notification là `nav-link` cao 62.3px, chưa phải circle 40×40 | ✅ 90% |
| **B** | UI-02 *(hình học)* | Low | Retest Failed | pill @1491.7/4.9 h62.3 — thiếu padding phải 20px, chưa ép 40px | ✅ 90% |
| **C** Mobile shell | UI-04 | Low | Retest Failed | cụm action lệch y −6px, `margin-right:7px` thừa trên glyph avatar | ✅ 95% |
| **C** | RESP-MOB-SHELL-003 | Low | Ready for Dev | `_wujia_theme.css:396-402` set `padding-top` riêng từng trang bằng `:has()` | ✅ 95% |
| **D** Giá & tiền | WJ-ORD-024 | High | Ready for Dev | `_cart_state()` tính `unit × qty`, không qua tax engine | ✅ 95% |
| **D** | WJ-ORD-025 | Medium | Ready for Dev | hardcode `' đ'` + fallback symbol `'đ'` | ✅ 95% |
| **D** | WJ-PH-005 | Medium | Ready for Dev | `unit_price = price_total/qty` là xấp xỉ, BA yêu cầu `compute_all` | ✅ 90% |
| **E** Lịch sử | WJ-PH-002 | Medium | Ready for Dev | trả `create_date` naive UTC, không `context_timestamp` | ✅ 95% |
| **E** | WJ-PH-007 | Medium | Ready for Dev | không validate `date_from <= date_to` | ✅ 100% |
| **E** | WJ-PH-004 | Low | Ready for Dev | template PC còn cột "Thao tác" thừa | ✅ 100% |
| **E** | WJ-PH-006 | Medium | Ready for Dev | **đã đúng** ở `_requester_display()` → chỉ verify | ✅ 95% |
| **F** Đồng bộ giỏ | WJ-ORD-003 | High | Retest Failed | `pageshow` chỉ refresh khi `ev.persisted` | ✅ 95% |
| **F** | WJ-ORD-002 | High | Retest Failed | subscribe `bus.bus` đang bị comment | ✅ 90% |
| **F** | WJ-ORD-020 | Low | Retest Failed | badge chờ JS bật `.is-active` → FOUC 1/5 lần | ⚠️ 70% |
| **G** A11y lẻ | WJ-ORD-012 | Medium | Retest Failed | 1 chỗ duy nhất dùng `.btn-primary` (2.68:1) | ✅ 95% |
| **G** | WJ-ORD-011 | Medium | Retest Failed | vùng chạm < 44×44 mobile | ⚠️ 80% (cần giỏ có hàng) |
| **G** | WJ-ORD-019 *(còn lại)* | Medium | Retest Failed | ô search **mobile** `outline-style:none` | ✅ 90% |
| **H1** ✅ Component PC | UI-PC-BASE-002 | Low | Ready for Dev | title 24/28/30 lẫn lộn, source 30/800 | ✅ 90% |
| **H1** ✅ | UI-PC-BASE-003 | Low | Ready for Dev | FilterBar cao 80–113.6px, source 88px | ✅ 90% |
| **H1** ✅ | UI-PC-BASE-004 | Low | Ready for Dev | badge radius 999px, thiếu min-width 84 | ✅ 90% |
| **H1** ✅ | UI-PC-BASE-008 | Low | Ready for Dev | form còn control Bootstrap 33/38.1px | ✅ 90% |
| **H1** ✅ | UI-PC-BASE-009 | Low | Ready for Dev | thiếu FormActionBar + separator | ✅ 90% |
| **H2** | UI-PC-BASE-005 | Low | Ready for Dev | thiếu page-size selector (exam đã có, copy sang) | ✅ 90% |
| **H2** | UI-PC-BASE-006 | Low | Ready for Dev | BackButton icon-only 44×44, source 122×40 có chữ | ✅ 95% |
| **H2** | UI-PC-BASE-007 | Low | Ready for Dev | màn create/detail không có breadcrumb | ✅ 95% |
| **H2** | WJ-ORD-023 | Low | Ready for Dev | filter Đặt hàng PC xếp dọc 3 hàng | ✅ 95% |
| **H2** | WJ-PH-004 | — | *(cũng ở cụm E)* | bỏ cột Thao tác — làm cùng E cho gọn | — |
| **I** Không code | UI-MOB-SHELL-001 | Low | Ready for Dev | **BLOCKED** — cần BA cấp logo mobile 100×34 | ✅ 95% |
| **I** | WJ-PH-003 | Medium | Ready for Dev | **FORK** — Odoo 19 không có state Đang giao/Hoàn tất | ✅ 90% |
| **I** | UI-PC-BASE-012 | Low | Ready for Dev | href placeholder → sửa được phần "sáng đôi"; link → hỏi BA | ✅ 95% |
| **I** | UI-02 *(cờ/nhãn)* | — | Retest Failed | **KHÔNG tái hiện** — 6/6 route ra cờ VN; nghi `lang` của user test | ✅ 90% |
| **I** | FUNC-MOB-ORDER-006 | High | Retest Failed | **KHÔNG tái hiện** — Enter mobile submit đúng | ✅ 95% |
| **I** | RESP-MOB-ORDER-003 | Low | Retest Failed | **đã fix** (`left/right:16px`), Owner = BA/Tester | ✅ 95% |
| **I** | RESP-MOB-ORDER-001 | Low | Ready for Dev | Owner = BA/Tester, ghi chú cũ mâu thuẫn cột N | ⚠️ cần 1 câu hỏi |

---

## Thứ tự chạy đề xuất

1. **I** — hỏi BA (gộp 5 câu 1 lần) + đẩy 2 issue đã đúng sang Ready for Retest. *Rẻ nhất, gỡ blocker sớm nhất.*
2. **A** — shell PC. Chặn 4 issue, và mọi phép đo PC sau này đều lệch nếu chưa fix.
3. **E** — lịch sử đặt hàng. Rủi ro thấp, 4 issue.
4. **G** — a11y lẻ. Rẻ.
5. **B** — header PC phải.
6. **D** — giá & tiền tệ. Cần test kỹ nhất.
7. **C** — mobile shell.
8. **F** — đồng bộ giỏ (bật `bus.bus`).
9. ~~**H1**~~ (xong 04/08, commit `c25a06b`) → **H2** — rollout component PC.

## Ràng buộc chung cho mọi cụm

- Đọc source trước khi sửa; `grep -rn` blast radius trước khi đụng CSS/token dùng chung.
- CSS portal nạp bằng `<link>` tay có `?v=` → **sửa CSS là phải bump `?v=`** trong `views/assets.xml`.
- Verify trên **DB copy cô lập** (port ≠ 8019), không đụng `wujia_tea_19`.
- Dev **không** tự đóng `Done` — tối đa `Ready for Retest`, kèm cột P/K/R đúng mẫu QA Standard.
