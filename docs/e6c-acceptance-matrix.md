# E6c — Ma trận nghiệm thu · Button `CMP-BTN-001` cho màn Thi + gạch 12 + khép `UI-BUTTON-001`

Lượt cuối của cụm **E6** (`UI-BUTTON-001`, STT 132, dòng sheet 125). E6a dựng atom + thước đo + 21 call site;
E6b1 32 call site + luật ranh giới thanh lọc; E6b2 19 call site (giỏ + auth). **E6c** phủ màn **Thi**
(nút XML + nút dựng bằng JS), làm **gạch 12** của BA, vá **tràn ngang màn đăng nhập**, rồi gộp một lần
deploy UAT cho cả cụm.

- Spec nguồn: tab `UI Component` gid `488333015` dòng 40, `BA Confirmed` 26/08/2026.
- Đo: DB local `wujia_e4b1`, server **8090/8091**, test **8098/8099**, login `em.hcm` (45 đăng ký thi)
  + `anh.owner` (0 đăng ký — trạng thái rỗng) + context **chưa đăng nhập** cho màn auth.
- Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (mã anh Thái).
- Không đổi quyền / controller / dữ liệu / workflow — chỉ class + CSS + JS giao diện + sổ test + thước đo.

Chốt đầu phiên của chủ dự án (23/09):
1. Ô chọn ngày, ô khung giờ, FAB, nút lùi wizard = **boundary nhưng đọc token `--wj-btn-*`** — đổi token nút
   một chỗ là các ô này đi theo, không phải sửa riêng.
2. `/portal/login@390` tràn 74px ⇒ **vá** (IMPACT, báo BA).
3. Cuối phiên **commit + push `main`**; chủ dự án tự deploy UAT.

## Phạm vi đã làm — 30 call site / 3 file / 1 module (+ vá màn đăng nhập)

| Nơi | Về atom | Chi tiết |
|---|---|---|
| `views/portal_exam.xml` | **21 `.wj-btn`** | CTA trạng thái rỗng · 2 nút *Quay lại* PC · panel rỗng · 2 nút trong cảnh báo · thêm người · kiểm tra thông tin · 2 nút ảnh · 4 nút modal · 6 nút wizard mobile · *Đăng ký thi mới* (kết quả) |
| `views/portal_exam.xml` | **7 `.wj-iconbtn`** + `aria-label` | 2 nút đổi tháng PC · 2 nút đổi tháng mobile · 2 nút đóng modal · xóa nhân sự (mobile) |
| `static/src/js/portal_exam_pc.js` | **2 `.wj-iconbtn`** dựng bằng JS | *Sửa người tham gia* · *Xóa người tham gia* (dòng bảng PC) |
| `portal_exam_pc.js` · `portal_exam_wizard.js` | loading của atom | gửi đăng ký dùng `setBusy()` = `.is-loading` + `disabled` + `aria-busy`, thay kiểu đổi chữ *Đang gửi…* |
| `wujia_portal_layout/.../_auth.css` | — | vá tràn ngang màn đăng nhập (xem IMPACT 1) |

Họ class bị xoá khỏi màn Thi: `wujia-mexam-btn*` (cả khối CSS), `wj-exam-pc-navbtn`, `wj-exam-pc-iconbtn`,
`wujia-mexam-cal-navbtn`, `wujia-mexam-person-del`, `wj-empty-state-btn`, `wj-pc-btn--primary/--secondary`.

## Bảng nghiệm thu — theo 12 gạch `Kết quả mong muốn` của BA

| # | Gạch của BA | Phép đo | Kết quả |
|---|---|---|---|
| 1 | Mọi action dùng atom chung, hết Bootstrap/class riêng theo route | `test_khong_con_ho_class_cu` (sổ 22 dòng) · thước đo mã `HỌ CŨ` | ✅ 30/30 call site màn Thi · 0 họ cũ ở view, JS lẫn CSS |
| 2 | Variant đúng nghĩa · **≤1 Primary mỗi action area** | mã `PRIMARY` + đo riêng từng trạng thái màn Thi | ✅ 0 vi phạm. Modal gắn `data-wj-action-area="modal"` để primary của modal không bị đếm chung với primary của trang |
| 3 | PC 32/40/46 · mobile 36/44/48 · chạm ≥44 | thước đo `getComputedStyle` + hộp chạm, **32 route × 5 khổ** | ✅ **358 ô atom** toàn portal: PC **32**×225, **40**×69, **46**×12; mobile **36**×8, **44**×30, **48**×14 |
| 4 | Radius / typo / padding / gap / màu theo token | mã `RADIUS`/`TYPO` + `test_boundary_doc_token_nut` | ✅ 0 vi phạm · 5 khối boundary **đọc `--wj-btn-*`**, không còn số cứng |
| 5 | Đủ default/hover/focus-visible/pressed/disabled/loading | hợp đồng khung E6a + `test_gui_dang_ky_dung_loading_cua_atom` | ✅ gửi đăng ký (PC + mobile) dùng `.is-loading` của atom |
| 6 | Semantic đúng · IconButton có tên · Tab/Enter/Space · focus rõ | tab-walk thật + `test_icon_only_co_ten_doc_duoc` + `test_nut_dung_bang_js_la_atom_co_ten` | ✅ 9 nút icon có `aria-label` tiếng Việt (7 XML + 2 JS) · 4 nút lùi wizard (boundary) cũng có tên |
| 7 | Điều hướng = link, tại chỗ = button, disabled không click/focus | mã `SEMANTIC` | ✅ 0 vi phạm |
| 8 | FormActionBar: Primary ngoài cùng phải | soi 4 modal/footer | ✅ modal *Thêm người* `Hủy ← Thêm người`, modal gửi `Quay lại chỉnh sửa ← Gửi yêu cầu`, footer wizard `Quay lại ← Tiếp tục` / `Quay lại ← Xác nhận đăng ký` |
| 9 | Không đổi quyền/dữ liệu/controller/workflow | `git status`: 0 file `.py` ngoài 2 `__manifest__.py` + sổ test | ✅ |
| 10 | Không scroll ngang / layout shift / bị BottomNav che | `wj_measure` trước/sau (stash) + đo `scrollWidth` | ✅ `wj_measure` **0 dòng khác** giữa trước và sau · **login hết tràn** 464 → 390 |
| 11 | Regression 1440/1024/992/390/360 + **zoom 200%** | 32 route × 5 khổ; zoom 200% = khổ **720**/**512** | ✅ **0 vi phạm** · **0 lỗi JS** |
| 12 | Retest 13 route đại diện, nhãn dài VI/EN/ZH, submit lặp, bàn phím | `scratchpad/e6c/bullet12.py` | ✅ có 2 LIMIT — xem mục *Gạch 12* |

Ngoài bảng BA: `wj_filterbar` **ĐẠT** · `wj_listcard` **0** · `wj_nesting` **0** · `b4_regression`
**286/286** · `check_layers` chỉ còn 2 R7 có sẵn (mã anh Thái), không thêm.

## Gạch 12 — chi tiết

**13 route đại diện** (đúng danh sách ưu tiên của BA): `/portal` · `/portal/order` · `/portal/order/cart` ·
`/portal/purchase-history` · `/portal/delivery` · `/portal/debt` · `/portal/notification` ·
`/portal/knowledge` · `/portal/support` · `/portal/support/new` · `/portal/exam` · `/portal/exam/register` ·
`/portal/change-password`.

| Phép đo | Cách đo | Kết quả |
|---|---|---|
| **Nhãn dài VI/EN/ZH** | Thay nhãn **mọi** nút atom đang hiện bằng chuỗi dài (VI 35 ký tự, EN 44 ký tự, ZH 13 chữ Hán), 13 route × 1440/390/360 = **126 lượt nút** | Mọi nút **giữ một dòng, giữ cỡ chữ** (đúng "không tự giảm font" của BA), trang **không cuộn ngang** ở lượt nào. 50 ghi nhận, gom thành 2 LIMIT dưới đây |
| **Submit lặp — form thường** | `/portal/support/new`: bấm đúp + Enter; đếm submit không bị chặn (không gửi thật) | ✅ **1 lần gửi**, rộng **136,6 → 136,6px**, nút mang `.is-loading` |
| **Submit lặp — gửi đăng ký thi (fetch)** | lịch/khung giờ giả + giữ request rồi trả lỗi giả — **không tạo đăng ký** | ✅ **1 request**, rộng **174 → 174px**, `.is-loading` + `disabled`; nhận lỗi thì nút **mở lại** |
| **Bàn phím** | Enter và Space trên từng `<button>` atom, đếm số lần kích hoạt — 5 màn | ✅ **28/28** đúng một lần (Thi 8/8 · Công nợ 8/8 · Hỗ trợ mới 2/2 · Giỏ 8/8 · Đổi MK 2/2) |

**LIMIT 1 — nút hành động trong dòng bảng PC** (49/50 ghi nhận): nút *Xem* ở Giao hàng và Công nợ nằm trong
bảng dữ liệu. Nhãn 35–44 ký tự làm cột rộng ra, bảng **cuộn ngang bên trong khung bảng** (`wj-data-viewport`)
đúng như thiết kế DataTable, **trang không cuộn**. Đây là hành vi của bảng (CMP DataTable), không phải lỗi
Button; quy ước: nhãn nút trong dòng bảng giữ ngắn (≤ 12 ký tự, như *Xem*, *Chi tiết*, *查看*).

**LIMIT 2 — nhãn rất dài trong nút full-width ở khổ 360** (1/50): `/portal/change-password@360`, nhãn EN
44 ký tự rộng hơn nút **6px** (314 > 308). BA chốt "nhãn một dòng, không tự giảm font" nên atom **không**
tự xuống dòng hay thu chữ. Quy ước cho người dịch: nhãn nút ≤ **40 ký tự Latin** (≈ 20 chữ Hán).

## Boundary đọc token — chốt của chủ dự án

| Class | Trước (số cứng) | Sau (token) | Số đo sau |
|---|---|---|---|
| `.wj-exam-pc-day` (ô ngày PC) | cao 32 · radius **6** | `--wj-btn-h-sm` · `--wj-btn-radius-sm` | 32 · r**8** |
| `.wj-exam-pc-slot` (ô khung giờ PC) | cao 58 · radius component | `calc(--wj-btn-h-lg + 12px)` · `--wj-btn-radius` | 58 · r12 |
| `.wujia-mexam-cal-day` (ô ngày mobile) | **38×38** | `--wj-btn-icon-sm` | **36×36** |
| `.wujia-mexam-slot` (ô khung giờ mobile) | padding 13px (cao ~51) | `min-height: --wj-btn-h-lg` · `--wj-btn-radius` | **48** |
| `.wujia-mexam-fab` (nút nổi Đăng ký) | padding 12/20 · nền `#28A9DF` | `--wj-btn-h-md` · `--wj-btn-pad-lg` · nền `--wujia-cta` | 44 · nền `#0F7CA8` |
| `.wujia-mexam-back` (nút lùi wizard) | — | giữ dáng BackPageHeader, thêm `aria-label` | — |
| Trạng thái **đang chọn** (ngày/khung giờ PC + mobile) | nền `--wujia-primary` | nền `--wujia-cta` = màu primary của atom | — |

`test_boundary_doc_token_nut` đỏ nếu bất kỳ khối nào quay về số px cứng; `test_boundary_khong_mang_atom`
đỏ nếu ai kéo các ô này về `.wj-btn` (JS đổi class của chúng theo trạng thái lịch).

## IMPACT (cần BA nhìn ảnh)

| IMPACT | Trước | Sau | Vì sao |
|---|---|---|---|
| **1. Màn đăng nhập điện thoại** — tràn ngang + cụm ngôn ngữ | trang cuộn ngang **74px** (`scrollWidth` 464 ở 390); cờ bị bóp còn **3px** (thành một chấm); tên ngôn ngữ tràn ra ngoài viên thuốc 72px; **hai mũi tên** | **hết tràn** ở 360/390/991 (đo cả khi tắt lưới an toàn); cờ đủ **20px**; tên ngôn ngữ ẩn mắt ở điện thoại (trình đọc màn hình vẫn đọc); **một mũi tên** | Nguyên nhân thật không phải khối trang trí mà là **tên ngôn ngữ** (thêm ở `WJ-LANG-001` 18/08) nhét vào viên thuốc 72px của Figma vốn chỉ đủ cờ + mũi tên. `overflow-x` trên `.wj-auth` giữ lại làm **lưới an toàn**. UAT hiện đang lỗi y hệt (đã đo chỉ-đọc: `scrollWidth` 464) |
| 2. Mũi tên trùng ở cụm ngôn ngữ PC | caret Bootstrap + chevron Figma | chỉ chevron Figma | caret Bootstrap của `.dropdown-toggle` chưa từng được tắt |
| 3. FAB *Đăng ký thi* (mobile) | nền `#28A9DF` | nền `#0F7CA8` | cùng màu primary của atom — `#28A9DF` + chữ trắng chỉ 2,68:1, trượt WCAG AA (chốt 20/09) |
| 4. Ô ngày lịch mobile | 38×38 | **36×36** | đọc token `--wj-btn-icon-sm` |
| 5. Ô ngày lịch PC | bo 6px | bo **8px** | đọc token `--wj-btn-radius-sm` |
| 6. Ô khung giờ mobile | cao ~51 | **48** | đọc token `--wj-btn-h-lg` |
| 7. Nút gửi đăng ký khi đang gửi | chữ đổi thành *Đang gửi…* (nút co giãn) | giữ nguyên chữ + bề rộng, spinner đè lên | BA: "loading giữ nguyên chiều rộng, có spinner" |
| 8. Nút đóng modal (PC) | dấu × xám 24px | nút icon ghost 32px, × màu primary | đồng bộ với nút đóng modal Công nợ + chọn cửa hàng (E6b1/E6b2) |
| 9. Đổi tháng lịch | PC 32×28 · mobile 30×30 | PC **32×32** · mobile **36×36** (chạm ≥44) | về `wj-iconbtn--sm` |

LIMIT: 4 nút lùi wizard mobile (`wujia-mexam-back`) có vùng chạm 28×30, dưới mức 44 của BA — thuộc
**BackPageHeader** (CMP-BPH-001, phiếu `UI-BACKPAGEHEADER-001`), không phải Button nên E6 không đổi dáng;
chỉ thêm `aria-label`. Xin BA cho biết mở phiếu riêng hay gộp vào lượt BackPageHeader kế tiếp.

## Ảnh trước/sau (`scratchpad/e6c/before|after`)

| Màn | @1440 | @390 | Đọc số |
|---|---|---|---|
| `/portal/exam` | 0,00% | 1,84% | chỉ FAB đổi màu |
| `/portal/exam/register` | 4,03% | 0,00% (bước 1) | nút đổi tháng về atom, *Quay lại* về atom; ô lịch đổi bo 6→8 |
| wizard bước 2/3/4 + bottom-sheet (390) | — | 2,8–3,8% | nút chân trang về atom (secondary trắng / primary `#0F7CA8`) |
| modal *Thêm người* / *Gửi* (1440) | 4,45% / 4,77% | — | nút modal + nút đóng về atom |
| kết quả đăng ký #49/#52 | 4,87% / 3,60% | 5,23% | CTA *Đăng ký thi mới* về atom `lg block` |
| `/portal/login` | 0,00% | **khác kích thước 464 → 390** | hết tràn ngang |

`wj_measure` trước/sau đo **cùng DB, cùng dữ liệu** bằng `git stash`: **0 dòng khác**, 0 ô mất record.

## Test và mutation

- Suite: **729 tests, 0 failed, 0 error** (mốc E6b2 **722** ⇒ **+7 test**: 6 ở
  `wujia_portal_exam/tests/test_button_e6c.py` + 1 guard chung mới).
- Mutation **10/10 mũi đỏ đúng guard** (`scratchpad/e6c/mutations.py`):

| Mũi | Phá | Phải đỏ ở |
|---|---|---|
| M1 | FAB bị kéo về atom | `test_boundary_khong_mang_atom` |
| M2 | ô ngày PC khai cứng `height: 32px` | `test_boundary_doc_token_nut` |
| M3 | ô ngày đang chọn quay về màu primary cũ | `test_trang_thai_chon_dung_mau_primary_cua_atom` |
| M4 | nút xóa dòng dựng bằng JS mất `aria-label` | `test_nut_dung_bang_js_la_atom_co_ten` |
| M5 | wizard quay về đổi chữ *Đang gửi…* | `test_gui_dang_ky_dung_loading_cua_atom` |
| M6 | nút lùi bước 2 mất tên | `test_nut_lui_wizard_co_ten_doc_duoc` |
| M7 | họ `wj-exam-pc-navbtn` sống lại | `test_khong_con_ho_class_cu` |
| M8 | class đi kèm atom (`.wj-exam-pc-back`) khai lại `height` | `test_class_di_kem_atom_khong_gianh_dang` (**guard mới**) |
| M9 | rớt call site: nút đóng modal về nút trơn | `test_du_so_call_site` |
| M10 | CSS module ép *Quay lại* cao 36 | thước đo mã `SIZE` (36 ≠ 40) |

**M8 lần đầu SAI** — không test nào đỏ. Guard cũ `test_module_khong_khai_lai_dang_cua_atom` chỉ bắt
selector có chữ `.wj-btn`; một class **đứng cùng phần tử** với atom (`.wj-exam-pc-back`) khai `height` là
thắng atom mà không ai biết (thước đo trình duyệt bắt được — M10 — nhưng test tĩnh thì không). Đã thêm
guard chung `test_class_di_kem_atom_khong_gianh_dang`: gom mọi class đi kèm atom ở view + JS của toàn bộ
`wujia_portal*`, cấm CSS module khai dáng cho chúng (trừ trạng thái `.is-*`). Quét toàn portal: **0 vi phạm**
(hai chỗ `.is-copied` của Công nợ là phản hồi trạng thái, được miễn).

## Thước đo — sửa trong phiên

1. `wj_button.py`: `/portal/exam/register` + màn kết quả dò động `@exam_detail` vào `MIGRATED`; `/portal/exam`
   vào `WATCH`; 6 class boundary + 5 họ cũ của màn Thi vào danh sách.
2. `keyboard_probe` bỏ qua phần tử `visibility: hidden` (nút trong bottom-sheet đang đóng từng bị đếm là
   "không nhận focus").
3. `scratchpad/e6c/exam_states.py` mở từng trạng thái màn Thi (wizard bước 2–4, bottom-sheet, 2 modal, cảnh
   báo, dòng người thi dựng bằng JS, trạng thái rỗng, màn kết quả) rồi mới đo — **0 vi phạm** ở 5 khổ. Nhấn
   Shift trước khi đo: click chuột làm Chrome tắt `:focus-visible` cho focus bằng mã.

## Bài học — môi trường đo

`wj_filterbar` báo **CHƯA ĐẠT** (5 màn "còn `page=`", 3 màn "ngày không lọc thật") và **chạy lại trên code
HEAD không có E6c cũng y hệt** ⇒ không do E6c. Truy tới cùng: thanh lọc được `wj_ajax_list.js` (có từ 07/08)
chặn submit rồi tải danh sách bằng `fetch` + `pushState`; server đo đang chạy `--dev=xml` (đọc lại QWeb từ
đĩa mỗi request) nên một lượt lọc mất **3,1 giây**, quá thời gian chờ của thước đo. Chạy lại server
**không** `--dev=xml`: **ĐẠT**. ⇒ Đo giao diện luôn dùng server không `--dev=xml`; cần nạp lại view thì
`-u` module rồi khởi động lại.

## Bump

| Module | Version |
|---|---|
| `wujia_portal_layout` | `19.0.56.3.0` |
| `wujia_portal_exam` | `19.0.5.19.0` |

`?v=` trong `views/assets.xml`: `_auth.css` 1171 → **1172**. CSS/JS màn Thi nạp qua asset bundle (hash tự đổi).

## Deploy UAT — một lần cho cả cụm E6

Chưa lượt nào của E6 lên UAT, nên lệnh `-u` gộp đủ module của E6a + E6b1 + E6b2 + E6c:

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_return,wujia_portal_notification,wujia_portal_delivery,wujia_portal_knowledge,wujia_portal_info_request,wujia_portal_purchase_history,wujia_portal_debt,wujia_portal_sale,wujia_portal_exam
```

Sau deploy: đo lại chỉ-đọc trên UAT (`latest_version` qua XML-RPC + `wj_button` + `scrollWidth` màn đăng
nhập), rồi `qa_sync.py` đưa `UI-BUTTON-001` sang **Ready for Retest**. Nhớ `/portal/forgot-pass` có
`rate_limit` 10 lần/giờ theo IP.

## Lệnh đã chạy

```bash
PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python

$PY scripts/qa/wj_button.py    --base http://127.0.0.1:8090 --portal-login em.hcm --json scratchpad/e6c/button-final.json
$PY scripts/qa/wj_button.py    --base http://127.0.0.1:8090 --portal-login em.hcm --breakpoints 720 512
(cd scratchpad/e6c && $PY exam_states.py)                 # từng trạng thái màn Thi
(cd scratchpad/e6c && $PY bullet12.py)                    # gạch 12: nhãn dài + submit lặp + bàn phím
$PY scratchpad/e6c/login_overflow.py                      # scrollWidth màn auth
$PY scripts/qa/wj_measure.py   --portal-login em.hcm --out scratchpad/e6c/measure-after.json   # + before qua git stash
$PY scripts/qa/wj_filterbar.py --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_listcard.py  --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_nesting.py   --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scratchpad/e6a/b4_emhcm.py
$PY scripts/qa/check_layers.py
$PY scratchpad/e6c/mutations.py
```
