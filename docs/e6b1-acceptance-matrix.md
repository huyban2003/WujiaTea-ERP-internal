# E6b1 — Ma trận nghiệm thu · Button `CMP-BTN-001` cho nghiệp vụ còn lại + Công nợ

Lượt thứ hai của cụm **E6** (`UI-BUTTON-001`, STT 132). E6a đã dựng atom + thước đo + 21 call site
mẫu. E6b1 migrate **32 call site / 7 module** còn lại của nhóm nghiệp vụ, và dựng **luật ranh giới
đọc được bằng máy** giữa nút của thanh lọc (E4, FB-08) và nút hành động (E6, CMP-BTN-001).
**Issue vẫn mở** — đóng ở E6c. **Chưa deploy UAT** (E6c gộp một lần).

- Spec nguồn: tab `UI Component` gid `488333015` dòng 40, `BA Confirmed` 26/08/2026
  (bản chụp: `scratchpad/e6a/ba-spec-btn.txt`).
- Đo: DB local `wujia_e4b1`, server **8090/8091** (`--dev=assets`), test **8098/8099**, login `em.hcm`
  (+ `dung.multi` cho store picker vì cần tài khoản nhiều cửa hàng).
- Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (mã anh Thái).
- Không đổi quyền / controller / dữ liệu / workflow — chỉ class + CSS + sổ test + thước đo.

## Phạm vi đã làm

| Module | File | Call site về atom |
|---|---|---|
| `wujia_portal_delivery` | `views/portal_delivery.xml` | 6 |
| `wujia_portal_knowledge` | `views/portal_knowledge.xml` | 3 |
| `wujia_portal_info_request` | `portal_info_request_form.xml` 3 · `_list.xml` 1 · `_detail.xml` 1 | 5 |
| `wujia_portal_purchase_history` | `views/portal_history.xml` | 2 |
| `wujia_portal_base` | `store_picker_modal.xml` 3 · `portal_franchises_in_layout.xml` 1 · `portal_franchise_profile.xml` 1 | 5 |
| `wujia_portal_debt` | `views/portal_debt.xml` | 10 |
| `wujia_portal_sale` · `wujia_portal_notification` | `header_cart_inherit.xml` · `header_bell_inherit.xml` | 0 — **boundary**, chỉ vá a11y |
| **Tổng** | 11 file / 7 module | **32 call site** |

Lệch plan: plan ghi 34 (gồm 2 nút icon navbar) và "Công nợ 11/13". Thực tế **navbar là boundary**
(LIMIT #1 bên dưới) và Công nợ là **10 migrate / 3 nút lọc giữ nguyên** ⇒ **32**.

## Bảng nghiệm thu — theo 12 gạch `Kết quả mong muốn` của BA

| # | Gạch của BA | Phép đo | Kết quả |
|---|---|---|---|
| 1 | Mọi action dùng atom chung, hết Bootstrap/class riêng theo route | `test_khong_con_ho_class_cu` (12 dòng sổ) · thước đo mã `HỌ CŨ` | ✅ 32/32 call site · sạch `btn-primary/secondary/outline-primary/outline-danger/btn-sm`, `wj-pc-dlv-btn-xem`, `wj-debt-pc-pdf` · 0 `HỌ CŨ` |
| 2 | Variant đúng nghĩa · **≤1 Primary mỗi action area** | `test_moi_atom_mang_dung_mot_variant` · thước đo mã `PRIMARY` | ✅ 0 vi phạm; mũi **M7** dựng 2 Primary ở form Yêu cầu ⇒ thước đo đỏ đúng |
| 3 | PC 32/40/46 · mobile 36/44/48 · chạm ≥44 | thước đo `getComputedStyle` + hộp chạm (kể cả pseudo), 18 route × 5 khổ | ✅ **278 ô atom**: PC **32**×201, **40**×45; mobile **36**×8, **44**×20, **48**×4; hộp chạm mobile nhỏ nhất **44** |
| 4 | Radius / typo / padding / gap / màu theo token | `test_radius_sm_8_md_lg_12`, `test_typo_ba_bac` · thước đo `RADIUS`/`TYPO` | ✅ radius **8**×209 (sm) / **12**×69 (md-lg); typo 3 bậc đúng; 3 số của thanh lọc nay cũng là token |
| 5 | Đủ default/hover/focus-visible/pressed/disabled/loading | hợp đồng khung E6a chạy lại + thước đo `LOADING` | ✅ 0 vi phạm, không màn nào khai lại dáng |
| 6 | Semantic đúng · IconButton có tên đọc được · Tab/Enter/Space · focus nhìn rõ | tab-walk thật + `test_icon_only_co_ten_doc_duoc` | ✅ 0 nút thiếu focus ring · 0 nút `disabled` còn focus; **8 nút icon mới có `aria-label`**: 4 sao chép công nợ, 1 xem yêu cầu, 2 đóng modal, 1 xem chi tiết |
| 7 | Điều hướng = link, tại chỗ = button, disabled không click/focus | `test_dieu_huong_la_link_hanh_dong_la_button` · mã `SEMANTIC` | ✅ 0 vi phạm |
| 8 | FormActionBar: Primary ngoài cùng phải | soi 3 vùng hành động có ≥2 nút | ✅ Yêu cầu cập nhật: `Hủy(secondary) → Lưu nháp(outline) → Gửi(primary)`; store picker: `Hủy → Đổi cửa hàng`; modal công nợ: 1 nút |
| 9 | Không đổi quyền/dữ liệu/controller/workflow | `git status`: **0 file `.py`** ngoài 9 `__manifest__.py` + sổ test | ✅ |
| 10 | Không scroll ngang / layout shift / bị BottomNav che | `wj_measure` 13 route × 5 khổ | ✅ **0 tràn ngang · 0 lỗi JS · 0 redirect ngầm · 0 HIERARCHY** |
| 11 | Regression 1440/1024/992/390/360 + **zoom 200%** | thước đo 18 route × 5 khổ; zoom 200% = khổ **720**/**512** | ✅ **90 ô, 0 vi phạm**; zoom 18 route × 2 khổ **0 vi phạm** |
| 12 | Retest 13 route đại diện, nhãn dài, submit lặp, bàn phím | E6b1 phủ 18 route + 2 lớp phủ | ◻ **để E6c** (nhãn dài VI/EN/ZH + submit lặp trên máy chủ) |

Ngoài bảng BA: `wj_filterbar` **ĐẠT, 0 lệch so với mốc E4** · `wj_listcard` **0** · `wj_nesting` **0** ·
`wj_datalist` đúng chuẩn · `b4_regression` **286/286** · `check_layers` **3 R1–R5 + 2 R7 có sẵn**, không thêm.

## Luật ranh giới thanh lọc — trả lời câu "làm sao đồng bộ"

Trong **cùng một file** `portal_debt.xml`, **cùng một tên class** `wj-pc-btn--primary` vừa là nút
*Tìm kiếm* của thanh lọc (**phải giữ 42** theo FB-08, E4 đã ký duyệt) vừa là nút *Thanh toán số còn
lại* (**phải về 40** theo CMP-BTN-001). Tên class không phân biệt được hai vai trò ⇒ đồng bộ bằng
**ngữ cảnh**, ở bốn tầng, không đổi một pixel nào:

1. **Token hoá** 42/38/32 trong `_variables.css` (`--wj-filter-btn-h-pc|-m|-sm`); `portal_debt.css`,
   `portal_order.css`, `_components.css` đọc token thay vì số cứng.
2. **CSS khai theo ngữ cảnh**, không theo họ class: `.wj-pc-filterbar__actions .wj-pc-btn`,
   `.wj-debt-pc-filter .wj-pc-btn` — vì `.wj-pc-btn` còn phục vụ màn Khảo sát.
3. **Thước đo nhận diện theo tổ tiên DOM**: phần tử nằm trong `<form>`/khối có token `filter`/`search`
   là boundary lọc, không áp luật size của E6 (trước đây dò bằng danh sách tiền tố ⇒ mù).
4. **Test bắt chéo hai chiều** (`TestRanhGioiThanhLoc`): (A) không nút nào trong 3 form lọc được mang
   `.wj-btn`/`.wj-iconbtn`; (B) từng khối CSS của 3 nút lọc tự dựng phải đọc token, **không** còn
   `height|width: <số>px`.

## Test và mutation

- Suite: **714 tests, 0 failed, 0 error** (mốc E6a **708** ⇒ **+6 test mới**).
- Mutation **8/8 mũi đỏ đúng guard của nó** (`scratchpad/e6b1/mutations.py`):

| Mũi | Phá | Phải đỏ ở |
|---|---|---|
| M1 | nút lọc PC Công nợ giành số riêng 40px | `test_nut_thanh_loc_doc_token_dung_chung` |
| M2 | `.wj-btn` mọc trong form lọc Công nợ | `test_nut_thanh_loc_khong_bi_keo_ve_atom` |
| M3 | nút sao chép rớt `aria-label` | `test_icon_only_co_ten_doc_duoc` |
| M4 | module giành lại `height` cho atom | `test_module_khong_khai_lai_dang_cua_atom` |
| M5 | atom quay lại màn dựng bằng khung Odoo gốc | `test_man_khung_goc_khong_dung_atom` |
| M6 | nút chuông navbar bị kéo về atom | `test_nut_navbar_khong_mang_atom` |
| M7 | 2 Primary trong một vùng hành động | thước đo mã `PRIMARY` |
| M8 | sổ `MIGRATED` ghi route không dựng nổi nút nào | thước đo `KHÔNG CÓ NÚT HÀNH ĐỘNG NÀO` |

M1 làm lộ một test yếu: bản đầu chỉ tìm chuỗi `--wj-filter-btn-h-` trong **cả file** nên đổi riêng
một khối vẫn lọt ⇒ đã siết thành kiểm **từng khối** rồi mới tính mũi này là đỏ đúng.

## Bẫy "Pass rỗng" — phần sửa lớn nhất của phiên

Lần đo đầu ra **0 vi phạm** nhưng **6/9 route trong sổ đo ra 0 atom / 0 action**: bảng xanh vì
*không có gì được dựng*. Truy ra bốn nguyên nhân, sửa từng cái:

| Route trong sổ | Sự thật | Sửa |
|---|---|---|
| `/portal/franchise-information` | render template khác, không có call site nào | thay bằng `/portal/franchises` + `/portal/franchises/3/profile` |
| `/portal`, `/portal/knowledge`, `/portal/purchase-history` | nút chỉ dựng ở **khối rỗng** (lọc không khớp) | thêm biến thể `?q=`/`?keyword=` không khớp; route trần chuyển sang `WATCH` |
| `/portal/info-request` | bảng `wujia.info.update.request` **0 bản ghi** | gieo 1 bản ghi local (`INF-000016`, chủ sở hữu `em.hcm` để nút *Hủy yêu cầu* mới dựng) |
| `/portal/debt/payment-history` | màn này **không có nút hành động nào** | chuyển sang `WATCH`, thêm `/portal/debt/pay` (3 atom) vào sổ |

Đồng thời siết chính thước đo:

- Route trong sổ mà **không dựng nổi nút nào ở bất kỳ khổ nào** ⇒ **vi phạm** (trước đây chỉ bắt khi
  *có* nút mà *không* có atom — đúng kẽ hở đã để 6 route lọt). Chỉ kết luận khi lượt đo có khổ ≥992,
  vì màn danh sách vốn 0 nút ở khổ hẹp.
- So route bằng **chuỗi đầy đủ** (trước đây cắt ở `?` nên biến thể lọc không được tính là đã migrate).
- So URL sau khi **giải mã %** (slug tiếng Việt bị báo nhầm là chuyển hướng).
- **Màn chi tiết dò lúc chạy** (`resolve_dynamic`) từ trang danh sách thay vì ghi cứng slug/id —
  slug ghi cứng đầu tiên trỏ đúng vào một bài **đã lưu trữ** nên route chuyển hướng lặng lẽ.
- **`scratchpad/e6b1/overlay_probe.py`** — 5 call site nằm trong lớp phủ (store picker 3, modal thanh
  toán 2) không route nào đo được vì mặc định ẩn. Probe mở lớp phủ rồi chạy đúng PROBE/check của
  thước đo: **0 vi phạm**, đủ cả hai trạng thái của store picker (bắt buộc chọn / đổi cửa hàng).

## Quyết định trong phiên

1. **LIMIT — nút icon navbar (chuông + giỏ) là boundary, không về atom.** Plan định migrate; đo ra
   96 vi phạm: `_pc_account.css` @≥1200 cố ý cho hai nút này **40×40 bo 20 nền kính** ở độ đặc hiệu
   (0,5,2) để thắng padding `.nav-link` của Vuexy. Kéo về atom thì hoặc mất dáng navbar, hoặc phải
   khai đè cao/bo/nền — tức module giành dáng của atom. Cùng loại với BottomNavigation mà BA đã liệt
   là boundary ⇒ giữ nguyên, ghim bằng `TestNutNavbarLaBoundary`. **Vẫn vá a11y**: hai nút nay có
   `aria-label` + `title` tiếng Việt ("Giỏ hàng", "Thông báo").
2. **LIMIT — `/my/franchises` dùng khung `portal.portal_layout` của Odoo.** Đã migrate rồi phải trả
   lại: CSS design system nạp bằng `<link>` trong vỏ Wujia, khung gốc không có nên atom ra **nút
   trần** (thước đo bắt: bo 0, chữ 14/400, không focus ring). Bản Vuexy của cùng danh sách là
   `/portal/franchises` — nút ở đó là atom, đo sạch. Ghim hai chiều bằng `TestKhungPortalGocLaBoundary`.
3. **IMPACT — nền Primary của atom đổi `#28A9DF` → `#0F7CA8`** (chủ dự án chốt 20/09). Màu BA ghi cho
   Button trượt WCAG AA (2.68 với chữ trắng); `#0F7CA8` đạt 4.7 và đã là CTA portal từ Sprint 38 theo
   đúng một issue a11y của chính BA. Sửa tại **một** chỗ trong `_components.css` thay vì đẻ ngoại lệ
   từng màn. **Ảnh hưởng ngược 21 call site của E6a** ⇒ đã chụp lại 3 màn E6a để đối chiếu.
4. **`btn-outline-danger` (Hủy yêu cầu) → `wj-btn--danger` đặc.** BA không liệt bậc outline-danger;
   hành động phá huỷ có xác nhận đi nút đặc cho rõ.
5. **`.wj-debt-filter__go` nay khai chiều cao tường minh** (trước dựa vào dáng mặc định) — nút này chỉ
   hiện trong `<noscript>`, giữ đúng 38 của FB-08.

## Ảnh trước/sau (`scratchpad/e6b1/before|after`, 9 màn × 2 khổ + 3 màn mới chỉ có bản sau)

| Màn | @1440 | @390 | Đọc số |
|---|---|---|---|
| `/portal/debt` | **4.76%** khác | 0.15% khác | CTA đổi màu + PDF/sao chép về atom |
| `/portal/info-request` | 3.39% | 4.08% | **dữ liệu**: gieo 1 bản ghi nên danh sách hết rỗng |
| `/portal/info-request/new` | 0.82% | cao +2px | 3 nút form về bậc chuẩn |
| `/portal/delivery` | cao **−40px** | giống hệt | 20 hàng × nút *Xem* 34→32 |
| `/portal/knowledge`, `/portal` | 0.10% · 0.12% | giống hệt | **dữ liệu**: probe làm tăng `view_count` |
| `/portal/purchase-history`, `/portal/debt/payment-history`, `/portal/franchise-information` | giống hệt | giống hệt | đúng — không đụng gì ở đó |

Chụp lại 3 màn E6a sau khi đổi màu Primary (`scratchpad/e6b1/e6a-recheck` ↔ `scratchpad/e6a/after`):
chỉ màn **có nút Primary** đổi (`/portal/notification` 0.43%, `/portal/*/new` 0.39–2.44%); hai màn
danh sách `/portal/support`, `/portal/return` **giống hệt từng byte** ở cả hai khổ — đúng như mong đợi.

## Bump

| Module | Version |
|---|---|
| `wujia_portal_layout` | `19.0.56.1.0` |
| `wujia_portal_base` | `19.0.7.20.0` |
| `wujia_portal_debt` | `19.0.4.10.0` |
| `wujia_portal_delivery` | `19.0.3.18.0` |
| `wujia_portal_knowledge` | `19.0.3.17.0` |
| `wujia_portal_info_request` | `19.0.1.12.0` |
| `wujia_portal_purchase_history` | `19.0.3.16.0` |
| `wujia_portal_sale` | `19.0.4.20.0` |
| `wujia_portal_notification` | `19.0.2.20.0` |

`?v=` trong `views/assets.xml`: `_variables.css` 1296→**1297** · `_components.css` 1315→**1316**.

## Nợ để lại

- **E6b2**: màn Đặt hàng/giỏ (25 action đo được ở `/portal/order`) + màn auth (submit **50 → 46**
  theo bậc Large của BA, mobile giữ 48 — ghi IMPACT + ảnh trước/sau).
- **E6c**: màn Thi (30 nút XML + nút dựng bằng JS), gạch **12** của BA, **một lần deploy UAT**, rồi đóng issue.
- Sổ `MIGRATED` của thước đo có 2 route phụ thuộc dữ liệu mẫu (`/portal/franchises/3/profile`,
  biến thể `?q=` không khớp) — màn chi tiết đã dò động, hai cái này vẫn ghi cứng.
- `.wj-pc-btn` còn 3 người dùng ở Công nợ (nút lọc, boundary) + nhóm Khảo sát (LIMIT #1 của E6a).

## Lệnh đã chạy

```bash
PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python

$PY scripts/qa/wj_button.py    --base http://127.0.0.1:8090 --portal-login em.hcm --json scratchpad/e6b1/button-after.json
$PY scripts/qa/wj_button.py    --base http://127.0.0.1:8090 --portal-login em.hcm --breakpoints 720 512
$PY scratchpad/e6b1/overlay_probe.py                       # store picker + modal công nợ
$PY scripts/qa/wj_filterbar.py --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_measure.py   --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_listcard.py  --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_datalist.py  --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_nesting.py   --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/check_layers.py
$PY scratchpad/e6a/b4_emhcm.py --base http://127.0.0.1:8090
$PY scratchpad/e6b1/mutations.py
$PY scratchpad/e6b1/shots.py   scratchpad/e6b1/after
$PY scratchpad/e6a/shots.py    scratchpad/e6b1/e6a-recheck
$PY scratchpad/e6b1/diff_shots.py scratchpad/e6b1/before scratchpad/e6b1/after

$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8098 --gevent-port=8099 \
  -u wujia_portal_layout,wujia_portal_base,wujia_portal_delivery,wujia_portal_knowledge,\
wujia_portal_info_request,wujia_portal_purchase_history,wujia_portal_debt,wujia_portal_sale,wujia_portal_notification \
  --test-enable --log-handler "odoo.tests.result:INFO" --stop-after-init
```

**Lệnh deploy khi tới lượt (E6c gộp):**
`-u wujia_portal_layout,wujia_portal_base,wujia_portal_delivery,wujia_portal_knowledge,wujia_portal_info_request,wujia_portal_purchase_history,wujia_portal_debt,wujia_portal_sale,wujia_portal_notification`
