# F0 — Mốc đo trước chuẩn hoá (17/09/2026, Mac, HEAD `355cae0`)

Mốc để F1–F5 chứng minh "trước = sau" bằng máy. File số liệu: `docs/f0-baseline/`. Ảnh (205 ô, 35 MB,
gitignored): `scratchpad/f0-before/shots/{anh,em}/` trên máy Mac.

## 1. DB copy giống UAT — `wujia_f0`, port 8099

| Hạng mục | UAT (đọc XML-RPC chỉ-đọc 17/09) | `wujia_f0` |
|---|---|---|
| 25 module `wujia_*` | installed, `portal_layout 19.0.51.0.0`… | **khớp 25/25 phiên bản** |
| Khảo sát (`wujia_franchise_inspection` + `wujia_portal_inspection`) | installed | installed (luật E #1) |
| `wujia_mobile_core` + 7 `muk_web_*` | installed | installed |
| Ngôn ngữ | en_US · th_TH · vi_VN, user portal `vi_VN` | như UAT |

Dựng lại (máy Mac, python env `/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python` = `$PY`):

```
createdb -h 127.0.0.1 -U odoo19 wujia_f0
pg_dump -h 127.0.0.1 -U odoo19 -Fc wujia_tea_19 -f x.dump && pg_restore -h 127.0.0.1 -U odoo19 -d wujia_f0 --no-owner x.dump
cp -R data/filestore/wujia_tea_19 data/filestore/wujia_f0
cd odoo19 && $PY odoo-bin -c ../config/odoo.conf -d wujia_f0 --db-filter='^wujia_f0$' --http-port=8299 \
  -u <21 module wujia_* đang cài> \
  -i wujia_franchise_contract,wujia_franchise_inspection,wujia_franchise_operations,wujia_mobile_core,muk_web_theme,muk_web_appsbar,muk_web_chatter,muk_web_colors,muk_web_dialog,muk_web_group,muk_web_refresh \
  --load-language=vi_VN,th_TH --stop-after-init
# 14 seed idempotent, thứ tự reseed_full.sh + d5/d6/e3/e3c:
for s in seed_admin_franchise seed_fleet_demo seed_products_demo seed_portal_demo seed_knowledge_demo seed_support_demo \
  seed_exam_demo seed_notification_demo seed_debt_demo seed_ui12_demo seed_d5_datalist_demo seed_d6_return_demo \
  seed_e3_pager_demo seed_e3c_pager_demo; do $PY odoo19/odoo-bin shell -c config/odoo.conf -d wujia_f0 --no-http < scripts/$s.py; done
# chỉ trên DB copy: user demo anh.owner/em.hcm/cuong.staff đặt lại mật khẩu wujia@test123
$PY odoo-bin -c ../config/odoo.conf -d wujia_f0 --db-filter='^wujia_f0$' --http-port=8099 --gevent-port=8199
```

Bẫy gặp khi dựng:
- `createdb -T wujia_tea_19` bị chặn khi server 8019 đang mở kết nối ⇒ dùng `pg_dump | pg_restore`, không tắt server của chủ dự án.
- `wujia_franchise_inspection` import `jwt` ⇒ env Mac thiếu `PyJWT` (đã `pip install PyJWT`), `-i` chết ở bước load registry.
- DB `wujia_tea_19` local **cũ** (`portal_layout 19.0.35`) và mật khẩu seed `wujia@test123` không còn đúng ⇒ `wj_measure` báo "ĐĂNG NHẬP HỎNG".
- DB thiếu `vi_VN`/`th_TH` ⇒ user `vi_VN` rơi về tiếng Anh (bề rộng chữ khác UAT) + `test_c10_lang` đỏ. Nạp ngôn ngữ xong: 520/520.
- DB local chỉ có 10 phiếu bù hàng, 0 chuyến giao, 0 ticket/phiếu thi/yêu cầu cho `anh.owner` ⇒ route chi tiết của B4 (`/delivery/3`, `/support/40`…) redirect ⇒ Pass rỗng. Seed xong mới có mẫu.
- zsh không tách biến chứa danh sách route (`--routes $L` thành 1 URL) ⇒ viết route trực tiếp.

## 2. Số đo

| Phép đo | Lệnh | Kết quả |
|---|---|---|
| Test 10 module portal có `tests/` | `-u <10 module> --test-enable --test-tags /wujia_portal_base,…,/wujia_portal_sale` | **520/520**, 0 failed, 0 error |
| B4 | `scripts/ba_spec/b4_regression.py --base http://127.0.0.1:8099` | **286/286** |
| `wj_measure` anh.owner | 26 route (13 danh sách + 13 chi tiết/form) × 5 khổ, `--screenshots` | 130 ô · 0 tràn ngang · 0 lỗi JS · HIERARCHY 3 · redirect 10 |
| `wj_measure` em.hcm | 15 route (danh sách + 4 chi tiết HCM, có phiếu `compensation`) × 5 khổ | 75 ô · 0 tràn · 0 lỗi JS · HIERARCHY 0 · redirect 0 |
| `css_owner.py --layout-domain` | | 380 nhóm · **193 của 1 màn** · 88 component · 84 khung · 15 orphan |
| `css_owner.py --overrides` | | 81 rule chạm component/khung · **41 đổi dáng** · 40 chỉ bố cục |
| `check_layers.py` | | 25 module · **4 vi phạm** (bảng §3) |

Mọi route có ít nhất một khổ với `card > 0` ở cả hai tài khoản (không route nào "mẫu rỗng").

Cờ có sẵn, không phải hồi quy — F1–F5 so theo diff, không so theo 0:
- **10 redirect** = `/portal/inspection` và `/portal/inspection/detail/1` tự thêm tiền tố `/vi/` (module Khảo sát của anh Thái); trang có nội dung thật (`card` 1–9).
- **3 HIERARCHY** = `/portal/notification/1` ở 1440/1024/992.

Histogram cỡ tiêu đề card (anh.owner): `14.7×10 · 16×52 · 18×108 · 20×3 · 22×6 · 24×13 · 32×2`;
nhịp header→body: `0×21 · 8×30 · 12×60`.

So sánh ở phiên sau:
```
$PY scripts/qa/wj_measure.py --base http://127.0.0.1:8099 --portal-login anh.owner --out after.json --routes <như measure_anh.txt>
$PY scripts/qa/wj_measure.py --diff docs/f0-baseline/measure_anh.json after.json
```

## 3. Vi phạm tầng ADR-027 hiện có (`check_layers.py`, report-only)

| Module | Depend | Luật | Chủ | Ghi chú |
|---|---|---|---|---|
| `wujia_franchise` | `wujia_mobile_core` | R1 nghiệp vụ không depend khung | Thái | mục D |
| `wujia_franchise_inspection` | `wujia_mobile_core` | R1 | Thái | mục D |
| `wujia_sale` | `wujia_mobile_core` | R1 | Thái (commit 17/09) | mục D |
| `wujia_portal_order_window` | thiếu `wujia_portal_base` | R4 | Dev portal | là module nghiệp vụ đội lốt portal, xử lý khi tách F7 |

Phép phá (trong bộ nhớ, không sửa manifest): thêm depend nghiệp vụ→layout, layout→nghiệp vụ,
portal_base→portal_x, mobile_x→portal_x, bỏ depend portal_base ⇒ mỗi phép +1 vi phạm (5/5).

## 4. Lệch Phụ lục A/B (heuristic 17/09) — chủ dự án chốt dùng số mới

- **A: 176 → 193** (tổng 380 khớp). Heuristic gán theo tên, script gán theo nơi dùng thật (view lxml + JS + controller).
  Phân bổ đổi: Đặt hàng 55→78, Home 56→49, Lịch sử 0→19, Hỗ trợ 0→7, Công nợ 17→3 (họ `msheet-item` là component
  dùng ở debt + Khảo sát), Đổi trả 11→3 (họ `mticket-*` thật ra của Hỗ trợ), Khảo sát 4 (Thái, không dời).
- **B: 30 → 41.** +14 rule đè lên tên con BEM heuristic bỏ sót (`wj-empty-state-title`, `wj-pc-td--muted`,
  `wj-pc-metric-card__value`, `wujia-badge`…); −3 rule chỉ đổi bố cục (`portal_debt.css:227,296`, `portal_support.css:2`).
- Hai bẫy khi dựng script: đếm class lẻ thay vì nhóm BEM (253), và tính component nằm ở tổ tiên selector
  (`.wujia-mpage .wujia-mexam-title` ⇒ 46). Phép phá: thêm tạm class `wujia-mknow-row` vào module thứ 2 ⇒ nhóm đổi sang `component`.

Phụ lục A/B trong `docs/next-session-clusters-F.md` đã thay bằng output script.
