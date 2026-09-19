# E6a — Ma trận nghiệm thu · nền Button `CMP-BTN-001` + 3 route mẫu

Lượt đầu của cụm **E6** (`UI-BUTTON-001`, STT 132, dòng tuyệt đối **125**). E6a dựng **atom**
(`wj-btn` / `wj-iconbtn`), dựng **thước đo** `scripts/qa/wj_button.py`, migrate **3 route mẫu phủ đủ
3 họ class cũ** để E6b/E6c chỉ còn nhân bản. **Issue chưa đóng** — đóng ở E6c.

- Spec nguồn: tab `UI Component` gid `488333015` **dòng 40**, `BA Confirmed` **26/08/2026** (bản
  chụp đầy đủ: `scratchpad/e6a/ba-spec-btn.txt`).
- Đo: DB local `wujia_e4b1`, server **8090/8091** (`--dev=assets`), test **8098/8099**, login `em.hcm`.
- Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (code anh Thái).
- Không đổi quyền / controller / dữ liệu / workflow — chỉ class + CSS + 1 file JS trạng thái loading.

## Phạm vi đã làm

| Module | File | Call site |
|---|---|---|
| `wujia_portal_support` | `views/portal_support.xml` | 7 `wj-btn` + 1 `wj-iconbtn` (×20 hàng) |
| `wujia_portal_return` | `views/portal_return_list.xml` | 2 + 1 (×20 hàng) |
| `wujia_portal_return` | `views/portal_return_form.xml` | 5 |
| `wujia_portal_notification` | `views/portal_notification.xml` | 4 |
| `wujia_portal_notification` | `views/header_bell_inherit.xml` | 1 |
| **Tổng** | 5 file / 3 module | **21 call site** |

Kiểm kê toàn portal (lxml, bỏ `backend_*`/`pc_preview`/module Khảo sát): **133 action / 28 file** —
E6a phủ 21, còn lại chia cho E6b (10 route + màn auth) và E6c (màn Thi + nút dựng bằng JS).

## Bảng nghiệm thu — theo 12 gạch `Kết quả mong muốn` của BA

| # | Gạch của BA | Phép đo | Kết quả |
|---|---|---|---|
| 1 | Mọi action dùng atom chung, hết Bootstrap/class riêng theo route | `test_khong_con_ho_class_cu` (view + CSS) · guard mã `HỌ CŨ` | ✅ 21/21 call site · 5 file sạch 15 họ cũ · guard 0 `HỌ CŨ` |
| 2 | Variant đúng nghĩa · **≤1 Primary mỗi action area** | `test_moi_atom_mang_dung_mot_variant` · guard mã `PRIMARY` | ✅ 0 vi phạm; mũi M7 dựng 2 Primary thì guard đỏ đúng |
| 3 | PC 32/40/46 · mobile 36/44/48 · chạm ≥44 | guard đo `getComputedStyle` + hộp chạm kể cả pseudo | ✅ **144 atom**: icon sm **32**, btn md **40** (PC); btn md **44**, lg **48** (mobile); hộp chạm nhỏ nhất **72×48** |
| 4 | Radius / typo / padding / gap / màu theo token | `test_radius_sm_8_md_lg_12`, `test_typo_ba_bac`, `test_sau_con_so_size_theo_ba` · guard `RADIUS`/`TYPO` | ✅ 8 (sm) / 12 (md-lg); 13/18/600 · 14/20/700 · 15/22/700; số khai bằng token, không px cứng |
| 5 | Đủ default/hover/focus-visible/pressed/disabled/loading; loading giữ width | `test_loading_giu_nguyen_be_rong`, `test_disabled_khong_bam_duoc` · guard `LOADING` | ✅ **24 nút** đo loading, bề rộng trước = sau từng nút (vd `336→336`, `62.03→62.03`) |
| 6 | Semantic đúng · IconButton có tên đọc được · Tab/Enter/Space · focus nhìn rõ | guard tab-walk thật + `test_icon_only_co_ten_doc_duoc` | ✅ **144 nút** đi qua tab-walk, **0** nút thiếu focus ring, **0** nút `disabled` còn nhận focus; 40 link icon-only nay có `aria-label` + `title` tiếng Việt |
| 7 | Điều hướng = link, tại chỗ = button, disabled không click/focus | `test_dieu_huong_la_link_hanh_dong_la_button` · guard `SEMANTIC` | ✅ 0 `<a>` thiếu `href`; template tự chọn nhánh theo `btn_href` |
| 8 | FormActionBar: Primary ngoài cùng phải | soi cấu trúc 4 vùng hành động có ≥2 nút | ✅ 3 vùng có Primary thì Primary **đứng cuối** (`secondary → primary`; form Bù hàng `secondary → outline → primary`); vùng thứ 4 (EmptyState Thông báo) hai nhánh `t-if`/`t-else` nên lúc chạy chỉ 1 nút |
| 9 | Không đổi quyền/dữ liệu/controller/workflow | `git status` phiên: **0 file `.py`** ngoài 4 `__manifest__.py` | ✅ |
| 10 | Không scroll ngang / layout shift / bị BottomNav che | `wj_measure` 13 route × 5 khổ | ✅ **0 tràn ngang · 0 lỗi JS · 0 redirect ngầm · 0 HIERARCHY** |
| 11 | Regression 1440/1024/992/390/360 + **zoom 200%** | guard 9 route × 5 khổ; zoom 200% = khổ CSS **720** và **512** | ✅ **45 ô, 0 vi phạm**; zoom: 5 route × 2 khổ, **0 vi phạm** |
| 12 | Retest 13 route đại diện, nhãn dài, submit lặp, bàn phím | E6a mới phủ 5 route; submit lặp chặn bằng `wujia_button_loading.js`; bàn phím đã đo | ◻ **để E6b/E6c** — ghi rõ ở phần Nợ |

Ngoài bảng BA: `wj_listcard` **0 vi phạm** · `wj_nesting` **0** · `wj_datalist` gap 8 đúng chuẩn ·
`b4_regression` **286/286** · `check_layers` **3 vi phạm R1–R5 + 2 R7 có sẵn**, không thêm.

## Test và mutation

- Suite: **708 tests, 0 failed, 0 error** (mốc E5c **687** ⇒ **+21 test mới**: 15 hợp đồng khung
  `wujia_portal_layout/tests/test_e6_button.py`, 6 quét call site
  `wujia_portal_base/tests/test_scan_e6_button.py`).
- Mutation **7/7 mũi đỏ đúng guard của nó** (`scratchpad/e6a/mutations.py`):

| Mũi | Phá | Phải đỏ ở |
|---|---|---|
| M1 | bậc md 40 → 42 (số cũ của `wj-pc-btn`) | `test_sau_con_so_size_theo_ba` |
| M2 | call site rớt variant | `test_moi_atom_mang_dung_mot_variant` |
| M3 | icon button mất `aria-label` | `test_icon_only_co_ten_doc_duoc` |
| M4 | gỡ vùng chạm 44 của bậc `sm` mobile | `test_vung_cham_44_bang_pseudo_khong_phinh_visual` |
| M5 | module khai lại dáng qua selector có `.wj-btn` | `test_module_khong_khai_lai_dang_cua_atom` |
| M6 | module ép dáng bằng **class riêng** trên cùng phần tử | thước đo `wj_button.py` mã `SIZE` (bản đồ tĩnh không thể thấy) |
| M7 | dựng 2 Primary trong một vùng hành động | thước đo mã `PRIMARY` |

M6/M7 là lý do thước đo phải tồn tại song song với test tĩnh: hai lỗi đó **không** hiện ra trên cây mã.

## Ảnh trước/sau (`scratchpad/e6a/before|after`, 5 màn × 2 khổ)

| Màn | @1440 | @390 |
|---|---|---|
| `/portal/support` | khác — 20 nút xem đổi dáng | **giống hệt** |
| `/portal/return` | khác — 20 nút xem đổi dáng | **giống hệt** |
| `/portal/notification` | khác — nút *Đánh dấu đã đọc* 42→40 | **giống hệt** |
| `/portal/support/new` · `/portal/return/new` | khác — cặp nút form | khác nhẹ — `Hủy` hẹp lại theo padding bậc `lg` |

3/10 ảnh **giống hệt từng byte** đúng ở chỗ phải giống (màn danh sách mobile vốn **0 nút hành động**);
7 ảnh còn lại khác đúng chỗ đã sửa.

## Ba quyết định (tự quyết, đã báo trước trong plan)

1. **Không xoá khối `.wj-pc-btn`** — `wujia_portal_inspection` (anh Thái) còn dùng ở 3 template + 1 JS.
   Luật cụm E #3: thu hẹp, không xoá ⇒ **LIMIT**. `test_ho_cu_cua_khao_sat_khong_bi_dung` canh chiều
   ngược lại: ngày nào Khảo sát hết dùng thì test đỏ để nhắc gỡ.
2. **PC 42 → 40px là đổi dáng có chủ đích** (BA Medium = 40). Token `--wujia-btn-height: 42px` giữ
   nguyên cho Khảo sát; atom dùng token riêng `--wj-btn-*`.
3. **Nút trong EmptyState migrate visual sang atom**, `wj-empty-state-btn` chỉ còn là hook bố cục.

## Phát hiện trong phiên (chưa có trong plan)

- **FilterBar là boundary, không phải họ cũ.** Nút *Tìm kiếm*/*Xóa lọc* mang `wj-pc-btn` nhưng
  **FB-08 cho Filter giữ 42/38/32 và nói rõ ưu tiên hơn size mặc định của CMP-BTN-001** ⇒ thước đo
  loại cả tiền tố `wj-filter*`/`wj-pc-filterbar*`, không phải chỉ nút kính lúp. (Trước khi sửa, đây
  là 18 báo nhầm.)
- **Hover viền theo WJ-PORTAL-UI-001, không theo BTN.** BA ghi hover border `#BFE8F7`, nhưng C6 đã
  chốt *"interaction state dùng chung tiếp tục theo WJ-PORTAL-UI-001"* (`#28A9DF`) ⇒ giữ C6, variant
  nền trung tính đi theo danh sách bề mặt của `_interaction.css`; `--ghost` cố ý **không** nằm trong
  danh sách đó để tránh khai hai nơi (cùng độ đặc hiệu, file sau đè file trước).
- **Màn danh sách mobile có 0 nút hành động** — BA đếm "mobile 40 action" chủ yếu là boundary
  (BottomNav, stepper, pager) + màn form. Ảnh hưởng cách đọc số của E6b/E6c.
- **Nút icon của header** (`wujia-header-icon-btn`, giỏ hàng + chuông, 40×40) là của khung shell,
  xuất hiện trên mọi route ⇒ để **E6b** làm một lần cho cả portal.
- **Hai màn danh sách trước đây dùng hai variant khác nhau cho cùng một vai trò** (`--outline` bên
  Bù hàng, `--secondary` bên Hỗ trợ) — đã thống nhất về `--secondary`.
- **Lỗi a11y thật được vá luôn**: 40 link icon-only ở PC (support + return) trước đây **không có tên
  đọc được nào** (`title` đặt trên thẻ `<i>`), nay có `aria-label` + `title` tiếng Việt.
- **16 ô `b4_regression` đỏ là id cố định đã cũ**, không phải hồi quy: `/portal/delivery/3`,
  `/portal/notification/41`, `/portal/support/40`, `/portal/return/12` đều **redirect về danh sách**
  vì tài khoản `anh.owner` trên DB này không còn/không thấy bản ghi đó (kể cả route của module E6a
  **không** đụng tới). Đo lại bằng bản ghi có thật (`em.hcm`, id 162/11/36/123) ⇒ **286/286**.

## Bump

| Module | Version |
|---|---|
| `wujia_portal_layout` | `19.0.55.1.0` → **`19.0.56.0.0`** |
| `wujia_portal_support` | **`19.0.3.24.0`** |
| `wujia_portal_return` | **`19.0.3.7.0`** |
| `wujia_portal_notification` | **`19.0.2.19.0`** |

`?v=` trong `views/assets.xml`: `_variables.css` 1295→**1296** · `_components.css` 1314→**1315** ·
`_interaction.css` 1293→**1294**; thêm `wujia_button_loading.js?v=1315`.

## Nợ để lại

- Gạch **12** của BA (retest 13 route, nhãn dài VI/EN/ZH, submit lặp trên máy chủ) — E6c.
- 112 call site còn lại: **E6b** 10 route portal + **màn auth** (login 9 · đổi mật khẩu 9 · quên mật
  khẩu 2 — chủ dự án chốt migrate luôn, lệch scope BA vốn chỉ liệt 13 route portal ⇒ ghi IMPACT);
  **E6c** màn Thi (30 nút XML + nút dựng bằng JS) rồi đóng issue.
- Cân nhắc ở E6b: đưa chính nút của FilterBar về atom kèm một lớp phủ 42px riêng cho Filter.
- `.wj-pc-btn` chỉ còn người dùng là nhóm Khảo sát (LIMIT #1).

## Lệnh đã chạy

```bash
PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python

$PY scripts/qa/wj_button.py --base http://127.0.0.1:8090 --json scratchpad/e6a/button-after.json
$PY scripts/qa/wj_button.py --base http://127.0.0.1:8090 --breakpoints 720 512 \
    --routes /portal/support /portal/support/new /portal/return /portal/return/new /portal/notification
$PY scripts/qa/wj_measure.py  --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_listcard.py --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_nesting.py  --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_datalist.py --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scratchpad/e6a/b4_emhcm.py --base http://127.0.0.1:8090     # b4 với id có thật
$PY scripts/qa/check_layers.py
$PY scratchpad/e6a/mutations.py
$PY scratchpad/e6a/shots.py scratchpad/e6a/after

$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8098 --gevent-port=8099 \
  -u wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_return,wujia_portal_notification \
  --test-enable --log-handler "odoo.tests.result:INFO" --stop-after-init
```

**Lệnh deploy khi tới lượt (E6c gộp):**
`-u wujia_portal_layout,wujia_portal_support,wujia_portal_return,wujia_portal_notification`
