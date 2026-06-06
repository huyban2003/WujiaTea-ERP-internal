# Wujia Portal — Design System (chuẩn giao diện hiện tại)

> **Mục đích.** Tài liệu này là bản **người-đọc** của design system đang chạy trong code,
> để **designer dựng Figma cho khớp** và để BA/dev có 1 nguồn thống nhất khi bàn UI.
>
> **Source of truth thật sự = code**, không phải file này:
> - Tokens (màu/typography/spacing/dimensions): [`_variables.css`](../custom/wujia_portal_layout/static/assets/css/_variables.css)
> - Component classes: [`_components.css`](../custom/wujia_portal_layout/static/assets/css/_components.css)
> - Design rules theo issue: Excel `Wujia_Internal ERP Master Plan.xlsm` → sheet **"5. Issue List"** (UI-01..UI-18)
>
> File này được sinh/cập nhật từ 3 nguồn trên. Khi token đổi trong `_variables.css`,
> cập nhật lại doc này ở cuối mỗi sprint (ritual `/wujia-end-sprint`). **Đừng** sửa giá trị
> ở đây rồi mong code đổi theo — chiều ngược lại.
>
> **Cập nhật:** 2026-06-02 (sinh từ `_variables.css` + `_components.css` + compact-summary; §6
> đối chiếu thẳng **xlsm "5. Issue List" (live)**; §10 = kết nối Figma verified + snapshot).
>
> ℹ️ **Kết nối Figma↔code đã chạy** (xem §10). **BA chưa hoàn thiện Figma** → hiện **theo code**
> (chuẩn) + xlsm spec; **khi BA xong Figma sẽ follow theo Figma của BA**. Doc này phản ánh code hiện tại.
>
> 📄 **BẢN GỬI BA (handoff):** `docs/wujia-figma-brief.tex` → build PDF qua `scripts/build-brief.sh`
> = `docs/wujia-figma-brief.pdf` (10 trang, self-contained, có swatch màu + **Phụ lục A: bảng lệch
> code vs BA spec sheet "2. FE - Portal"**). Đây là file đưa BA để nhờ AI khác dựng Figma. Doc `.md`
> này là bản nội bộ chi tiết hơn; brief PDF là bản trình bày cho BA.
>
> **BA spec token (sheet "2. FE - Portal" R52-143) — giá trị BA đề xuất, để đối chiếu khi reconcile:**
> bg-page `#F6F8FB` · text-primary `#272A30` · text-secondary `#69707A` · border `#E5EAF1` ·
> card-shadow `0 8px 24px rgba(0,0,0,.08)` · table-divider `#E5EAF1` · zebra `#F8FAFC` ·
> input-border `#D9DEE7` · success `#24B269` · warning `#F29A1F` · danger `#EC3845` · info `#22A9DE`.
> Chi tiết drift + khuyến nghị → Phụ lục A của brief PDF.

---

## 1. Cách dùng (cho designer build Figma)

> **Thứ tự ưu tiên nguồn (quan trọng):**
> - **xlsm "5. Issue List" = nguồn chuẩn chính thức** (BA sở hữu, **cập nhật liên tục**).
> - **Code (`_variables.css`) = giá trị đúng hiện tại** — xlsm hay lag nên nhiều chỗ code đã
>   refine sẵn. **Khi xlsm chưa update mà lệch code → theo code.**
> - **Figma = thiết kế BA mình follow, chỉ đọc — KHÔNG sửa.**
>
> ⇒ Doc này §2–§9 phản ánh **code (current)**; §6 + §10 đánh dấu chỗ xlsm/Figma đang lệch
> để BA cập nhật nguồn của họ.

1. Đọc §2–§5 để lấy **palette + typography + spacing + components** chuẩn.
2. Trong Figma: tạo **Color styles / Text styles / Variables** đặt **trùng tên token**
   theo §7 (vd `wujia/primary`, `wujia/text-primary`). Trùng tên = sau này nối MCP/REST
   để sync Figma↔code sẽ khớp 1-1, không phải map tay.
3. Mỗi component (§5) có **anatomy + token áp + class CSS thật** — dựng Figma component
   theo đúng cấu trúc đó (vd KPI card = icon trái → vạch ngăn 1px → content → chevron phải).
4. Design rules theo issue (§6) là **nguyên tắc** BA đã chốt — bám theo, đừng tự đổi.

---

## 2. Color palette

> Tất cả màu đều là CSS variable trong `:root`. Template **không hardcode hex** — luôn
> `var(--wujia-*)`. Hex dưới đây là giá trị hiện tại.

### Brand / primary
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-primary` | `#22A9DE` | Màu thương hiệu chính (cyan) — button primary, icon KPI, link, bullet |
| `--wujia-primary-dark` | `#1598CF` | Hover của primary |
| `--wujia-primary-light` | `#E0F7FF` | Nền nhạt |
| `--wujia-primary-soft` | `#EAF7FD` | Nền active menu (UI-04); nền badge info |
| `--wujia-active-text` | `#24A8E0` | Icon + text menu đang active (UI-04) |

### Surface / layout
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-bg-page` | `#E8ECEF` | Nền trang. **Override BA**: BA spec `#F5F7FA/#F6F8FA`, user chọn `#E8ECEF` (đậm hơn, để card trắng nổi rõ) — 2026-05-25 |
| `--wujia-bg-sidebar` | `#FFFFFF` | Nền sidebar |
| `--wujia-bg-card` | `#FFFFFF` | Nền card |
| `--wujia-border` | `#E5E7EB` | Viền card / divider (UI-11) |
| `--wujia-border-soft` | `#EEF1F5` | Viền nhạt hơn |
| `--wujia-table-header-line` | `#9AA0A6` | Vạch header bảng |

### Text (Tailwind gray scale — BA spec UI-12)
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-text-primary` | `#111827` | Tiêu đề, text đậm (Tailwind gray-900) |
| `--wujia-text-secondary` | `#374151` | Body text (Tailwind gray-700) |
| `--wujia-text-muted` | `#8A9099` | Text mờ, badge muted |
| `--wujia-text-subtitle` | `#6B7280` | Subtitle / mô tả / ngày (UI-09) |

### State / semantic
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-success` | `#24B269` | Text/icon thành công |
| `--wujia-success-bg` | `#E1F8EC` | Nền badge success |
| `--wujia-warning` | `#F29A1F` | Text/icon cảnh báo |
| `--wujia-warning-bg` | `#FFF3E0` | Nền badge warning |
| `--wujia-danger` | `#EC3845` | Text/icon lỗi; **badge đỏ header cart/bell (UI-13)** |
| `--wujia-danger-bg` | `#FFE8EB` | Nền badge danger |
| `--wujia-info` / `--wujia-info-text` | `#1FC160` | Info |
| `--wujia-info-bg` | `#D6F4E0` | Nền info |
| `--wujia-muted-bg` | `#F1F3F6` | Nền badge muted |

> ⚠️ **Cyan primary lệch — cần BA xác nhận (xem §10):** code đang dùng `#22A9DE` (chuẩn hiện tại);
> xlsm (UI-11/UI-12) + Figma ghi `#28A9DF` (dev coi là typo — compact-summary §9 gotcha #6).
> Lệch ~4 ký tự, nhìn gần như nhau. BA chốt 1 giá trị → nếu khác code thì đổi token 1 lần.

---

## 3. Typography

| Thuộc tính | Token | Giá trị |
|---|---|---|
| Font family | `--wujia-font-family` | `'Inter', 'Roboto', Arial, sans-serif` (Inter self-host, không CDN) |
| Body | `--wujia-font-size-body` | `15px` (BA 15–16, low end) |
| H1 | `--wujia-font-size-h1` | `32px` (BA 32–36) — weight 700 |
| H2 | `--wujia-font-size-h2` | `24px` — weight 600 |
| Card title | `--wujia-font-size-card-title` | `20px` (BA 20–22) |
| Page title | `--wujia-page-title-*` | size `24px`, weight `700`, color `#111827` (UI-08) |
| Subtitle | `--wujia-font-size-subtitle` | `14px`, color `#6B7280` (UI-09) |

**Fluid scaling (UI / Sprint 9.6):** `html` font-size tự scale theo viewport nên mọi giá trị
`rem` co giãn theo — template dùng `rem`, không cần media query riêng từng form:

| Breakpoint | `html` font-size |
|---|---|
| < 768px | 14px |
| ≥ 768px | 15px |
| ≥ 992px | 16px |
| ≥ 1200px | 16px |

---

## 4. Spacing & dimensions

| Token | Giá trị | Vai trò |
|---|---|---|
| `--wujia-sidebar-width` | `300px` | Bề rộng sidebar |
| `--wujia-sidebar-logo-h` | `200px` | Chiều cao vùng logo (UI-07) |
| `--wujia-header-height` | `72px` | Chiều cao navbar (Vuexy default) (UI-08) |
| `--wujia-header-padding` | `22px` | Padding header |
| `--wujia-card-radius` | `16px` | Bo góc card (UI-11) |
| `--wujia-card-padding` | `24px` | Padding card |
| `--wujia-card-shadow` | `0 2px 6px rgba(15,23,42,.04)` | Shadow nhẹ |
| `--wujia-section-gap` | `28px` | Khoảng cách giữa các section |
| `--wujia-btn-height` | `42px` | Cao button primary/semantic (BA 40–44) |
| `--wujia-btn-height-secondary` | `38px` | Cao button secondary (BA 36–40) |
| `--wujia-btn-radius` | `8px` | Bo góc button |
| `--wujia-menu-item-height` | `44px` | Cao item sidebar (BA 44–48) |
| `--wujia-menu-icon-size` | `20px` | Icon sidebar (BA 20–22) |
| `--wujia-menu-text-size` | `16px` | Text sidebar |

**Breakpoints chuẩn (Bootstrap-aligned)** — KHÔNG dùng số ad-hoc 550/770/850:

| Token | Giá trị |
|---|---|
| `--wujia-bp-sm` | `576px` |
| `--wujia-bp-md` | `768px` |
| `--wujia-bp-lg` | `992px` |
| `--wujia-bp-xl` | `1200px` |

---

## 5. Components

Mỗi component = **1 class trong `_components.css`** để mọi page tái dùng cùng look. Anatomy +
token + class thực dưới đây. Designer dựng Figma component theo đúng cấu trúc này.

### 5.1 Buttons — `.wujia-btn`, `.wujia-btn-primary`, `.wujia-btn-secondary`
- **Primary** (UI-05): nền `--wujia-primary` cyan, chữ trắng, cao `42px`, radius `8px`, hover → `--wujia-primary-dark`.
- **Secondary**: nền trắng, viền `1px --wujia-border`, chữ `--wujia-text-primary`, cao `38px`. (Gom `.btn-secondary` + `.btn-outline-*` về cùng 1 style để portal nhất quán.)
- Icon trong button: flex-center, `line-height:1`, `gap 6px` (fix lệch baseline Font Awesome).
- Variant: `.btn-sm` cao 32px, `.btn-lg` cao 48px.

### 5.2 Status badge — `.wujia-badge` + `.wujia-badge-{success,warning,danger,info,muted}`
- Pill bo tròn `999px`, padding `4px 10px`, font `12px/600`, nền soft + chữ đậm theo state.
- Legacy `.state-*` (`state-active/draft/locked/expired/closed`) tự upgrade theo cùng look.

### 5.3 KPI card — `.wujia-kpi-card` (+ `-link`, `-icon-*`, `-separator`, `-content`, `-arrow`)
Layout ngang: **icon vuông trái → vạch ngăn dọc 1px → content → chevron phải (optional)**.
- Card: nền trắng, radius `16px`, shadow nhẹ, `min-height 100px` (BA 100–108), padding `16px`, gap `12px`. Hover nhấc `-2px`.
- Icon box: `56×56`, radius `12px`, nền `--wujia-primary`, icon trắng `23px`. Màu icon đổi qua `-icon-{primary,success,warning,danger,info}`.
- Separator: `1px × 48px`, màu `#D1D5DB`.
- Content: `label 14px` (secondary) + `value 28px/700` (primary) + `desc 12px`.
- Chevron: neo mép phải (`margin-left:auto`), `18px`.
- **Mobile < 768px**: icon `52×52`, `min-height 92px`, 1 card/dòng full-width, gap dọc `12px` (UI-15).

### 5.4 Content card — `.wujia-content-card` (+ `-header[-icon,-title,-link]`, `-body`, `-row[-bullet,-content,-date]`, `-empty`)
Card "Xem tất cả" (UI-12) cho home + listing.
- Card: nền trắng, radius `16px`, shadow, padding `22px`.
- Header: **icon tròn cyan 40px** + **title bold 17px** + link **"Xem tất cả" cyan** neo phải.
- Row: grid `auto 1fr auto auto` = bullet cyan `8px` + content + date `#6B7280` + badge; mỗi row có border-bottom (đọc như bảng). Mobile < 576px ẩn cột date.
- `--flush` variant + `.wujia-content-card-table` (negative-margin edge-to-edge) cho trang listing full (order / purchase-history / notification — MẪU 02).

### 5.5 Empty state — `.wujia-empty-state`
Căn giữa, padding `48px 24px`, icon `40px` mờ + text `--wujia-text-secondary`. Dùng khi list rỗng.

### 5.6 Two-pane layout — `.wujia-two-pane`
2 cột (list + detail); < 992px tự stack dọc, mỗi pane full-width.

### 5.7 Responsive utility — `.wujia-container`, `.wujia-grid-responsive`, `.wujia-stack-mobile[.wujia-row-md]`
- Container: `padding-inline clamp(12px,3vw,32px)`, max-width `1400px`.
- Grid: `auto-fit minmax(280px,1fr)`, gap `clamp(12px,2vw,24px)` — thay cho `col-md-X col-lg-Y`.
- Stack: flex column trên mobile, thêm `.wujia-row-md` để chuyển row ở ≥768px.

### 5.8 Navbar pill — Current Store (UI-03)
Pill 2 dòng sát trái navbar cyan: nền frosted trắng `rgba(255,255,255,.18)`, chữ trắng,
label uppercase `11px` mờ, radius `10px`, padding `6px 16px`. Tokens `--wujia-navbar-pill-*`.

### 5.9 Mobile sub-strip — Current Store < 768px (UI-04)
Dải dưới navbar: nền trắng, label cyan uppercase, name đậm, role badge stacked. Tokens `--wujia-mobile-strip-*`.

### 5.10 Header right actions (UI-13) — `.wujia-header-icon-btn` + `.wujia-header-badge`
Bên phải header: **Language + Cart + Bell + Account (name + avatar)**.
- Icon button: `20px`, padding `8px`.
- Badge tròn đỏ (`--wujia-danger #EC3845`) góc trên-phải icon cart/bell, chữ trắng, `18px`,
  hiện qua class `.is-active` (count load AJAX sau page-ready — perf 1500 user).
- ⚠️ Badge bị Vuexy `.badge` chèn → fix scoped `(0,0,5,2)` + `!important` cho bg + color (gotcha §9 #11).

### 5.11 Pagination — `.pagination.wujia-pagination`
Trả về dáng chữ nhật Bootstrap (Vuexy bo tròn 5rem làm vỡ pager), page active nền cyan chữ trắng.

---

## 6. Design rules theo issue (BA "5. Issue List" UI-01..UI-18)

> Bảng dưới đối chiếu **thẳng xlsm "5. Issue List" (live, pull 2026-06-02)** — cột H "Kết quả
> mong muốn" (rút gọn) + cột I "Trạng thái" (BA status). Cột **Impl** = trạng thái code thực tế.
> ⚠️ **Số UI trong xlsm khác compact-summary §9** (BA đã re-number UI-07/UI-08) — bảng này theo **xlsm**.

| ID | Vùng (xlsm) | Kết quả mong muốn — xlsm cột H | BA status | Impl (code) |
|---|---|---|---|---|
| UI-01 | Sidebar | Icon size 20–22, text 16, item height 44–48, gap icon-text 12; active icon+text trắng | Done | ✅ |
| UI-02 | Sidebar | Bỏ block thông tin user | Done | ✅ |
| UI-03 | Header (PC) | Block Current Store: `[H000] Cửa hàng…` + role badge + language + avatar | Done | ✅ |
| UI-04 | Header (mobile) | Như UI-03 cho mobile (code: sub-strip dưới navbar) | Done | ✅ |
| UI-05 | Button | Primary nền xanh/chữ trắng h40–44; Secondary nền trắng/viền xám h36–40; cùng loại giống nhau mọi page | Done | ✅ (h42/h38) |
| UI-06 | Card/nền | Background chung `#F5F7FA`/`#F6F8FA`, card trắng `#FFFFFF` | Done | ⚠️ nền `#E8ECEF` (user override đậm hơn) |
| UI-07 | Top Header/Top Bar | Giảm height còn ~64–72px, căn giữa item theo chiều dọc | Done | ✅ (72px) |
| UI-08 | Page Title | Màu `#111827` (hoặc `#0F172A`), size ~24px, weight 700 | Done | ✅ |
| UI-09 | Page Subtitle | `#6B7280`, 14–15px, weight 400 (hoặc block dạng notification) | Done | ✅ (#6B7280, 14px) |
| UI-10 | Font | Đồng nhất 1 font mọi trang | Done | ✅ (Inter) |
| UI-11 | KPI/Summary card | Card trắng radius 16, shadow nhẹ, height ~100, padding 20–24; icon box vuông radius 16 **72×72** nền **#28A9DF** icon trắng; line dọc 1px `#D1D5DB` cao ~64 | Done | ⚠️ icon **56×56** (giảm theo UI-14), radius 12, sep h48; nền icon `#22A9DE` |
| UI-12 | Content Card | Card trắng radius 16, shadow, padding 20–24; header icon tròn **#28A9DF** + title đậm + "Xem tất cả" **#28A9DF** phải; row bullet **#28A9DF** + nội dung + thời gian + badge; type title `#111827`, body `#374151`, date `#6B7280` | Done | ⚠️ icon/link/bullet `#22A9DE` |
| UI-13 | Header Right Actions | Icon Language + cart + notification + account (user name + avatar) | Done | ✅ (badge đỏ #EC3845) |
| UI-14 | KPI Card Height | Tăng vùng content, giảm icon box, chuẩn hóa height **100–108px** | **New** | ✅ code (gap 12, min-h 100, icon 56, chevron neo phải) |
| UI-15 | KPI Card Mobile | 1 card/dòng width 100%, height **88–96**, padding 14–16, gap 12, icon **52×52** radius 12, icon size 22–24 | **New** | ⬜ pending |
| UI-16 | Main Content Spacing | header→title ~24, title→KPI 12–16, KPI→content 20–24 | **New** | ⬜ pending |
| UI-17 | Product Best Seller Card | Chuẩn lại theo content card listing (màn đặt hàng / lịch sử), bỏ table thô | **New** | ⬜ pending |
| UI-18 | Main menu | Row height 44–48, margin item 4–6; cùng 1 icon set, cùng stroke, size 20–22 | **New** | ⬜ pending |

> **Lưu ý status:** xlsm để UI-14..18 = **"New"** (BA chưa đánh Done). Code đã làm UI-14 (Sprint 9.15),
> còn UI-15..18 pending. Khi code 1 issue, **luôn mở lại xlsm cột G+H verbatim** — bảng này chỉ định hướng.

---

## 7. Figma mapping guide (chuẩn bị cho sync Figma↔code)

Để sau này nối Figma vào code (qua MCP/REST — xem [`figma-mcp-setup.md`](figma-mcp-setup.md))
sync sạch, **đặt tên Figma trùng tên token**:

### 7.1 Color styles / Variables
Tạo collection `wujia` trong Figma Variables, mỗi màu = 1 variable đặt tên bỏ tiền tố `--wujia-`,
đổi `-` thành `/` để Figma group lại:

| CSS token | Figma variable name |
|---|---|
| `--wujia-primary` | `wujia/primary` |
| `--wujia-primary-dark` | `wujia/primary-dark` |
| `--wujia-text-primary` | `wujia/text-primary` |
| `--wujia-bg-page` | `wujia/bg-page` |
| `--wujia-success` | `wujia/success` |
| `--wujia-danger` | `wujia/danger` |
| … (toàn bộ §2) | `wujia/<tên-token-bỏ-prefix>` |

### 7.2 Text styles
| Style Figma | Mapping |
|---|---|
| `wujia/h1` | Inter 32 / 700 |
| `wujia/h2` | Inter 24 / 600 |
| `wujia/card-title` | Inter 20 / 600 |
| `wujia/body` | Inter 15 / 400, `#374151` |
| `wujia/subtitle` | Inter 14 / 400, `#6B7280` |
| `wujia/page-title` | Inter 24 / 700, `#111827` |

### 7.3 Components
Dựng mỗi component ở §5 thành 1 Figma component đúng anatomy + đặt tên `wujia/<component>`
(vd `wujia/kpi-card`, `wujia/content-card`, `wujia/button-primary`). Dùng đúng radius/padding/gap
ở §4–§5 để khi đối chiếu Figma↔code không lệch.

> **Direction:** hiện tại code đi trước → file này + Figma styles theo code. Khi Figma thành
> source of truth, nối MCP để **đọc Figma → cập nhật `_variables.css`** (đối chiếu token theo tên).

---

## 8. Quy tắc bất di bất dịch (nhắc lại từ compact-summary)

- CSS **luôn** `var(--wujia-*)` + class `_components.css`. **Không hardcode hex.**
- Token global (color/radius/spacing/typography) bump = ảnh hưởng MỌI page → smoke test 3–5 page
  khác sau khi đổi (regression check).
- CSS đổi → bump `?v=NNNN` trong `assets.xml` (browser cache 7 ngày). CSS nằm trên **đĩa**,
  không phải DB — "local khác server" về màu = cache layer, không phải data.
- Mobile-first cho 1500 user; demo data không vào manifest (script `seed_*.py` local-only).

---

## 9. Appendix — full token reference

> Bảng đầy đủ mọi token trong `_variables.css` (tên + giá trị hiện tại) để tra cứu / map Figma 1-1.
> Các phần §2–§5 ở trên đã diễn giải theo nhóm; bảng này là danh sách phẳng đầy đủ.

### Brand / surface / text / semantic
Đã liệt kê đầy đủ ở **§2 Color palette** (token + hex).

### Layout dimensions
`--wujia-sidebar-width 300px` · `--wujia-sidebar-logo-h 200px` · `--wujia-header-height 72px` ·
`--wujia-header-padding 22px` · `--wujia-card-radius 16px` · `--wujia-card-padding 24px` ·
`--wujia-card-shadow 0 2px 6px rgba(15,23,42,.04)` · `--wujia-section-gap 28px`

### KPI card
`--wujia-kpi-card-min-height 100px` · `--wujia-kpi-card-padding 16px` · `--wujia-kpi-card-gap 12px` ·
`--wujia-kpi-icon-size 56px` · `--wujia-kpi-icon-radius 12px` · `--wujia-kpi-icon-bg var(--wujia-primary)` ·
`--wujia-kpi-icon-font 23px` · `--wujia-kpi-separator-color #D1D5DB` · `--wujia-kpi-separator-height 48px`
_(mobile <768px: `--wujia-kpi-icon-size 52px`, `--wujia-kpi-card-min-height 92px`)_

### Sidebar items
`--wujia-menu-item-height 44px` · `--wujia-menu-icon-size 20px` · `--wujia-menu-text-size 16px`

### Buttons
`--wujia-btn-height 42px` · `--wujia-btn-height-secondary 38px` · `--wujia-btn-radius 8px`

### Navbar pill (UI-03)
`--wujia-navbar-pill-bg rgba(255,255,255,.18)` · `--wujia-navbar-pill-bg-hover rgba(255,255,255,.28)` ·
`--wujia-navbar-pill-text #FFFFFF` · `--wujia-navbar-pill-icon #FFFFFF` · `--wujia-navbar-pill-radius 10px` ·
`--wujia-navbar-pill-padding 6px 16px` · `--wujia-navbar-pill-gap 10px` · `--wujia-navbar-pill-font 15px` ·
`--wujia-navbar-pill-label-size 11px` · `--wujia-navbar-pill-label-color rgba(255,255,255,.85)`

### Header right action icons (UI-13)
`--wujia-header-icon-size 20px` · `--wujia-header-icon-btn-padding 8px` · `--wujia-header-badge-size 18px`

### Mobile sub-strip (UI-04)
`--wujia-mobile-strip-bg #FFFFFF` · `--wujia-mobile-strip-label-color var(--wujia-primary)` ·
`--wujia-mobile-strip-name-color var(--wujia-text-primary)` · `--wujia-mobile-strip-padding 12px 16px` ·
`--wujia-mobile-strip-border-bottom 1px solid var(--wujia-border)`

### Typography
`--wujia-font-family 'Inter','Roboto',Arial,sans-serif` · `--wujia-font-size-body 15px` ·
`--wujia-font-size-h1 32px` · `--wujia-font-size-h2 24px` · `--wujia-font-size-card-title 20px`
Page title: `--wujia-page-title-color #111827` · `--wujia-page-title-size 24px` · `--wujia-page-title-weight 700`
Subtitle: `--wujia-text-subtitle #6B7280` · `--wujia-font-size-subtitle 14px`

### Content card (UI-12)
`--wujia-content-card-padding 22px` · `--wujia-content-card-header-icon-size 40px` ·
`--wujia-content-card-header-icon-bg var(--wujia-primary)` · `--wujia-content-card-bullet-size 8px` ·
`--wujia-content-card-bullet-color var(--wujia-primary)` · `--wujia-content-card-link-color var(--wujia-primary)` ·
`--wujia-content-card-row-gap 14px`

### Misc
`--wujia-sidebar-transition transform 0.25s ease-in-out` ·
Breakpoints: `--wujia-bp-sm 576px` · `--wujia-bp-md 768px` · `--wujia-bp-lg 992px` · `--wujia-bp-xl 1200px`

---

## 10. Kết nối Figma — verified + snapshot (Figma đang WIP)

> **Trạng thái kết nối:** ✅ **đã chạy.** Đọc file "Wujia" (key `vfVcqN5zPJvlcjZU4NYim0`) qua
> REST/MCP read-only (2026-06-02), render được frame, trích được màu (page Dashboard: 376 text +
> 284 vector = **design vector thật**). 7 page: Dashboard, Menu, Products, Add to cart, History Order,
> Order Detail, Cart.
>
> ⚠️ **BA CHƯA LÀM XONG FIGMA.** Bảng so màu dưới chỉ là **snapshot tham khảo** chứng minh pipeline
> chạy — **KHÔNG dùng để reconcile lúc này.** Hiện **theo code** (chuẩn) + xlsm spec. **Khi BA hoàn
> thiện Figma → follow theo Figma của BA** (nguồn design cuối cùng). **Không sửa Figma từ phía mình.**

### 10.1 Bảng lệch màu

> **Nhắc lại nguồn ưu tiên:** code = chuẩn hiện tại; xlsm = spec chính thức nhưng hay lag;
> Figma = chỉ đọc. Cột "Ghi chú" chỉ ra nguồn nào đang lệch để BA cập nhật.

| Vai trò | Figma dùng | BA spec (xlsm) | Code (chuẩn) | Ghi chú |
|---|---|---|---|---|
| **Cyan primary** | `#28A9DF` | `#28A9DF` (UI-11/12) | `#22A9DE` | code `#22A9DE` đang dùng; xlsm + Figma `#28A9DF` chưa khớp → BA chốt |
| **Text chính** | `#1F2933` (chủ yếu) + `#111827` | `#111827`/`#0F172A` (UI-08/12) | `#111827` | code + xlsm đã `#111827`; **Figma còn màu cũ** `#1F2933` |
| Subtitle/date | `#6B7280` | `#6B7280` (UI-09/12) | `#6B7280` | ✓ khớp cả 3 |
| Body text | (ít gặp) | `#374151` (UI-12) | `#374151` | Figma hầu như không dùng `#374151` |
| Text muted | `#8A939E` | — | `#8A9099` | lệch nhẹ Figma↔code |
| **Đỏ (danger)** | `#E84545` + `#EF4444` (2 sắc) | — (xlsm không nêu hex) | `#EC3845` | 3 sắc đỏ khác nhau |
| Warning | `#F59E0B` | — | `#F29A1F` | lệch Figma↔code |
| Primary soft | `#E8F7FC` / `#E9F7FC` | — | `#EAF7FD` | lệch nhẹ |
| Nền trang | (n/a) | `#F5F7FA`/`#F6F8FA` (UI-06) | `#E8ECEF` | code = user override đậm hơn |

### 10.2 Ghi nhận (để dành — xử lý KHI BA xong Figma)

1. **Cyan `#28A9DF` vs `#22A9DE`** — Figma + xlsm spec đều `#28A9DF`, code `#22A9DE` (dev coi là typo).
   → **BA chốt 1 giá trị.** Nếu giữ `#28A9DF` (đúng spec BA) thì code đổi `--wujia-primary` (cùng 1 dòng,
   nhưng là token global → cần smoke test + bump `?v=`).
2. **Text chính** — Figma còn dùng `#1F2933` (cũ) trong khi chính xlsm spec của BA là `#111827`.
   → Figma đang đi sau spec của chính BA; đề nghị BA cập nhật Figma về `#111827`.
3. **Đỏ** — Figma trộn `#E84545` + `#EF4444`, code `#EC3845`. → BA chọn 1 sắc đỏ chuẩn.
4. **Figma chưa có Color/Text styles + Variables** (published styles = 0) — màu hardcode trực tiếp,
   nội bộ Figma còn không nhất quán (2 text-chính, 3 đỏ, 2 cyan-soft). → đề nghị BA tạo styles/variables
   theo **§7** (đặt tên trùng token) để lần sau sync Figma↔code 1-1, không phải dò từng hex.
5. **Icon KPI 72 vs 56** — xlsm UI-11 ghi icon box `72×72` nhưng UI-14 (mới) lại yêu cầu "giảm icon box";
   code theo UI-14 → `56×56`. Đây là **mâu thuẫn nội bộ trong xlsm**, không phải bug code.

> **Tóm lại:** Figma đang WIP nên **chưa reconcile gì lúc này** — giữ **code làm chuẩn**. Khi BA
> hoàn thiện Figma, dùng MCP đọc lại → đối chiếu → cập nhật `_variables.css` **theo Figma của BA**
> (không sửa Figma). Việc cần làm bây giờ chỉ là **giữ kết nối chạy được** — đã xong.
