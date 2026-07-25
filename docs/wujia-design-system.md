# Wujia Portal — Design System (chuẩn giao diện hiện tại)

> **Mục đích.** Bản **người-đọc** của design system đang chạy trong code, để designer dựng Figma
> cho khớp và BA/dev có 1 nguồn thống nhất khi bàn UI.
>
> **Source of truth = code, KHÔNG phải file này:**
> - Token: [`_variables.css`](../custom/wujia_portal_layout/static/assets/css/_variables.css)
> - Component class: [`_components.css`](../custom/wujia_portal_layout/static/assets/css/_components.css)
>   · PC: [`_pc_components.css`](../custom/wujia_portal_layout/static/assets/css/_pc_components.css)
>   · [`_pc_account.css`](../custom/wujia_portal_layout/static/assets/css/_pc_account.css)
>   · Auth: [`_auth.css`](../custom/wujia_portal_layout/static/assets/css/_auth.css)
> - Design rule theo issue: Google Sheet `5. Issue List` (compact-summary §7 có gid).
>
> Doc này sinh từ các nguồn trên, cập nhật cuối mỗi sprint (`/wujia-end-sprint`).
> **Đừng** sửa giá trị ở đây rồi mong code đổi theo — chiều ngược lại.
>
> **Cập nhật:** 2026-07-25 (reconcile toàn bộ token với `_variables.css` @ Sprint 39).
>
> 📄 **Bản gửi BA:** `docs/wujia-figma-brief.tex` → `scripts/build-brief.sh` → `wujia-figma-brief.pdf`
> (self-contained, có swatch màu + **Phụ lục A: bảng lệch code vs BA spec sheet "2. FE - Portal"**).
> Doc `.md` này là bản nội bộ chi tiết hơn.

---

## 1. Cách dùng (cho designer build Figma)

> **Thứ tự ưu tiên nguồn:** **code (`_variables.css`) = giá trị đúng hiện tại** > sheet BA
> (chính thức nhưng hay lag) > Figma (chỉ đọc, BA chưa hoàn thiện — §9).

1. Đọc §2–§5 để lấy **palette + typography + spacing + components**.
2. Trong Figma: tạo Color/Text styles + Variables **trùng tên token** theo §7 (vd `wujia/primary`)
   → sau này sync Figma↔code khớp 1-1, không map tay.
3. Mỗi component (§5) có **anatomy + token + class CSS thật** — dựng Figma theo đúng cấu trúc đó.
4. Design rule theo issue (§6) là nguyên tắc BA đã chốt — bám theo, đừng tự đổi.

---

## 2. Color palette

> Mọi màu là CSS variable trong `:root`. Template **không hardcode hex** — luôn `var(--wujia-*)`.

### 2.0 Ba tầng token (quan trọng — đừng nhầm)

| Tầng | Prefix | Vai trò |
|---|---|---|
| Gốc | `--wujia-*` | Nguồn duy nhất định nghĩa hex thật. Đổi màu = đổi ở đây. |
| Alias | `--wj-*` | Bí danh ngắn, **trỏ vào `--wujia-*`** (`--wj-primary: var(--wujia-primary)`). Dùng trong component `wj-*` đời mới. **Không** định nghĩa hex mới. |
| PC | `--wj-pc-*` | Lớp riêng cho desktop rework. Đa số alias, chỉ vài giá trị PC-only (`--wj-pc-primary-dark #168FBE`, `--wj-pc-blue #2563EB`, các `*-soft` badge). |

⇒ Sửa màu **luôn ở tầng gốc**; sửa ở alias = lệch giữa mobile và PC.

### Brand / primary
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-primary` | `#28A9DF` | Màu thương hiệu (cyan) — button, icon KPI, link, bullet |
| `--wujia-primary-dark` | `#168FC2` | Hover của primary |
| `--wujia-primary-light` | `#E0F7FF` | Nền nhạt |
| `--wujia-primary-soft` | `#EAF7FD` | Nền active menu; nền badge info |
| `--wujia-active-text` | `#28A9DF` | Icon + text menu đang active |

> ⚠️ **`#28A9DF` là giá trị BA chốt.** `#22A9DE` **cấm dùng** (comment ngay trong `_variables.css`).
> Hai hex chỉ lệch 4 ký tự nên rất dễ chép nhầm — thấy `#22A9DE` ở đâu là sai, sửa về token.

### CTA (Sprint 38 — accessibility)
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-cta` | `#0F7CA8` | Nút hành động chính trên nền trắng — **đạt contrast AA**, thay `--wujia-primary` ở chỗ chữ trắng trên nền cyan bị fail |
| `--wujia-cta-dark` | `#0C6688` | Hover của CTA |

### Surface / layout
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-bg-page` | `#F3F6F8` | Nền trang |
| `--wujia-bg-sidebar` / `--wujia-bg-card` | `#FFFFFF` | Nền sidebar / card |
| `--wujia-border` | `#E5E7EB` | Viền card / divider |
| `--wujia-border-soft` | `#EEF2F5` | Viền nhạt hơn |
| `--wujia-table-header-line` | `#9AA0A6` | Vạch header bảng |

### Text (Tailwind gray scale)
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-text-primary` | `#111827` | Tiêu đề, text đậm (gray-900) |
| `--wujia-text-secondary` | `#374151` | Body text (gray-700) |
| `--wujia-text-subtitle` | `#6B7280` | Subtitle / mô tả / ngày |
| `--wujia-text-muted` | `#8A939E` | Text mờ, badge muted |

### State / semantic
| Token | Hex | Vai trò |
|---|---|---|
| `--wujia-success` / `-bg` | `#16A34A` / `#EAF8EF` | Thành công |
| `--wujia-warning` / `-bg` | `#F29A1F` / `#FFF3E0` | Cảnh báo |
| `--wujia-danger` / `-bg` | `#EF4444` / `#FEECEC` | Lỗi; badge đỏ header cart/bell |
| `--wujia-info` / `-text` / `-bg` | `#1FC160` / `#1FC160` / `#D6F4E0` | Info |
| `--wujia-muted-bg` | `#F1F3F6` | Nền badge muted |

---

## 3. Typography

| Thuộc tính | Token | Giá trị |
|---|---|---|
| Font family | `--wujia-font-family` | `'Inter', sans-serif` (Inter self-host, không CDN) |
| Body | `--wujia-font-size-body` | `15px` |
| H1 | `--wujia-font-size-h1` | `32px`, weight 700 |
| H2 | `--wujia-font-size-h2` | `24px`, weight 600 |
| Card title | `--wujia-font-size-card-title` | `20px` |
| Page title | `--wujia-page-title-*` | size `24px`, weight `700`, color `#111827` |
| Subtitle | `--wujia-font-size-subtitle` | `14px`, color `#6B7280` |

**Fluid scaling:** `html` font-size scale theo viewport → mọi giá trị `rem` co giãn, không cần
media query riêng từng form:

| Breakpoint | `html` font-size |
|---|---|
| < 768px | 14px |
| ≥ 768px | 15px |
| ≥ 992px / ≥ 1200px | 16px |

> ⚠️ Shell Vuexy có rule **tag-level `!important`** đè mọi class (`h1/h2` font-size, `table th`,
> `select`, `label`) → xem compact-summary §10 L4 trước khi chỉnh typography.

---

## 4. Spacing & dimensions

| Token | Giá trị | Vai trò |
|---|---|---|
| `--wujia-sidebar-width` | `300px` | Bề rộng sidebar |
| `--wujia-sidebar-logo-h` | `200px` | Chiều cao vùng logo |
| `--wujia-header-height` | `72px` | Chiều cao navbar (Vuexy default) |
| `--wujia-header-padding` | `22px` | Padding header |
| `--wujia-card-radius` | `16px` | Bo góc card |
| `--wujia-card-padding` | `24px` | Padding card |
| `--wujia-card-shadow` | `0 2px 6px rgba(15,23,42,.04)` | Shadow nhẹ |
| `--wujia-section-gap` | `28px` | Khoảng cách giữa section |
| `--wujia-page-content-top` | `24px` | Header → nội dung |
| `--wujia-page-title-gap` | `14px` | Title → khối kế |
| `--wujia-kpi-content-gap` | `22px` | KPI → content |
| `--wujia-btn-height` / `-secondary` / `-radius` | `42px` / `38px` / `8px` | Button |
| `--wujia-menu-item-height` / `-icon-size` / `-text-size` | `44px` / `20px` / `16px` | Item sidebar |

**Breakpoints (Bootstrap-aligned)** — KHÔNG dùng số ad-hoc 550/770/850:
`--wujia-bp-sm 576px` · `--wujia-bp-md 768px` · `--wujia-bp-lg 992px` · `--wujia-bp-xl 1200px`

### Token con theo component

- **KPI card:** `min-height 100px` · `padding 16px` · `gap 12px` · `icon-size 56px` ·
  `icon-radius 12px` · `icon-bg var(--wujia-primary)` · `icon-font 23px` ·
  `separator-color #D1D5DB` · `separator-height 48px`
  _(override **<992px**: icon `52px`, min-height `92px`, padding `14px` — UI-15)_
- **Content card:** `padding 22px` · `header-icon-size 40px` · `bullet-size 8px` ·
  `row-gap 14px` · icon/bullet/link đều `var(--wujia-primary)`
- **Navbar pill:** `bg rgba(255,255,255,.18)` (hover `.28`) · text/icon trắng · `radius 10px` ·
  `padding 6px 16px` · `gap 10px` · `font 15px` · `label-size 11px` · `label-color rgba(255,255,255,.85)`
- **Header right icons:** `icon-size 20px` · `btn-padding 8px` · `badge-size 18px`
- **Mobile sub-strip:** nền trắng · label = primary · name = text-primary · `padding 12px 16px` ·
  `border-bottom 1px solid var(--wujia-border)`
- **Filter:** `--wujia-filter-field-bg #F8FAFC` (fill ô search / date pill)
- **PC:** `--wj-pc-card-radius 18px` · `component-radius 12px` · `input-radius 10px` ·
  `pill-radius 999px` · `content-padding 24px` · `btn-h/input-h 42px` · `filter-input-h 38px` ·
  `table-header-h 50px` · `table-row-h 58px` · `metric-h 96px` · `metric-icon 52px` · `pagebtn 36px`

### Họ token mobile theo màn

Mỗi màn mobile có namespace riêng trong `_variables.css` — **tra thẳng file**, không chép ở đây
(chúng đổi theo từng sprint Figma):
`--wujia-mhome-*` (Home) · `--wujia-morder-*` (Đặt hàng — cũng là base cho nhiều component `wj-*`
dùng chung) · `--wujia-mshell-*` / `--wujia-mheader-*` / `--wujia-mnav-*` (shell mobile) ·
`--wujia-msheet-*` (More sheet) · `--wujia-mknow-*` (Kiến thức) · `--wujia-mdash-*` (Dashboard) ·
`--wujia-mticket-*` (Hỗ trợ) · `--wujia-maccount-*` (Tài khoản).

---

## 5. Components

Mỗi component = **1 class trong `_components.css`** để mọi page tái dùng cùng look.

### 5.A Nhóm canonical `wj-*` (dùng cho trang MỚI)

Đây là bộ chuẩn hiện hành — trang mới **bắt buộc** dùng nhóm này thay vì tự viết lại.

#### 5.A.1 Page header — `.wj-page-header` (+ `__title`, `__back`, `__actions`, `__create`, `--m`)
Chuẩn header mọi trang (rollout ~40 site/11 module từ Sprint 33).
- Base: flex ngang, `min-height 44px`, nền trong suốt; title `flex:1` + ellipsis + weight 700.
- `__back`: nút vuông nền `--wj-surface`, viền `--wj-border`, radius `12px`, icon `24px` màu primary.
- `__create`: nền `--wj-primary`, chữ trắng `14px/700`, radius `12px`, gap `8px`, hover → `primary-dark`.
- **`--m` (mobile):** margin `16px 0 12px` (bằng 0 khi nằm trong `.wujia-mpage` — mpage tự lo spacing);
  title `22px !important` (**phải** `!important` để thắng global `h1{font-size !important}`);
  back/create `40px`, create `112px` rộng; back có `::after` 44×44 để **tap target ≥44** dù visual 40.

#### 5.A.2 Filter — `.wj-filter-card` + `.wj-filter-chip[--soft|--clear]` / `.wj-filter-chips[--wrap]`
Canonical filter (Figma 4785:498 — 5 biến thể: search / date-range / chip-slide / period).
- `wj-filter-card`: cột, gap `10px`, nền card, viền `--wujia-border-soft`, radius `--wujia-morder-radius`,
  padding `12px`, margin-bottom `16px`.
- `wj-filter-chip`: pill `h32`, padding `0 14px`, viền `--wujia-morder-border`, `13px/600`,
  `white-space:nowrap`; `--soft` = active nền nhạt, `--clear` = nút xoá lọc.
- `wj-filter-chips` scroll ngang (ẩn scrollbar); `--wrap` cho xuống dòng.
- Phụ trợ: `wj-filter-search[-btn|-field]`, `wj-filter-dates[--compact]`, `wj-filter-date-sep`,
  `wj-filter-period`; ô nhập dùng `--wujia-filter-field-bg`.

#### 5.A.3 Đếm kết quả — `.wj-count-meta[--bold|--primary]`
Dòng "N kết quả" dưới filter: `13px`, màu `--wujia-morder-text-sub`; `--bold` weight 700;
`--primary` weight 700 + màu primary.

#### 5.A.4 Empty state — `.wj-empty-state[--card|--compact|--rich]`
**Canonical.** (`.wujia-empty-state` ở §5.B là bản cũ — trang cũ còn dùng, **đừng dùng cho trang mới**.)
- Base: căn giữa, padding `48px 24px`, màu `--wujia-text-muted`.
- `--card`: bọc trong card trắng viền + radius, padding `32px 16px`.
- `--compact`: padding `14px 0`, `13px` — cho khối nhỏ trong trang.
- `--rich`: no-data card chung (Figma 4788:974 — card 359×253, icon 76, nút "Tải lại"), cột căn giữa
  gap `6px`, padding `24px 18px 17px`. Nút phụ: `.wj-empty-state-btn`, icon: `.wj-empty-state-icon`.

#### 5.A.5 PC components — `.wj-pc-*` (`_pc_components.css`)
Bộ desktop rework (Sprint 28 / PC-1..3). Nhóm chính:
`wj-pc-card[__head|__title(--sm)|__subtitle|__count]` · `wj-pc-btn[--primary|--secondary|--ghost|--danger|--disabled]` ·
`wj-pc-badge[--pending|--confirmed|--sent|--transit|--done|--cancel|--warn|--area|--staff]` ·
`wj-pc-page-header[__title|__crumb|__actions]` · `wj-pc-filterbar[__row|__grow|__actions|__title]` +
`wj-pc-filter-control/-search` · `wj-pc-table` · `wj-pc-pagination[__count|__size]` + `wj-pc-page-btn` ·
`wj-pc-kv-grid[--single]` + `wj-pc-kv[__label|__value(--primary|--warning)]` ·
`wj-pc-field[__label]` + `wj-pc-control` · `wj-pc-modal[__backdrop|__panel|__title|__body|__divider|__note]` ·
`wj-pc-empty[__icon|__title|__sub]` · `wj-pc-two-col` · `wj-pc-order-head*` · `wj-pc-link`.
Trang Tài khoản PC có bộ riêng `wj-pc-acct-*` (`_pc_account.css`): `headcard`, `nav`, `menu`,
`kv-grid`, `pw-*` (đổi mật khẩu), `staff`, `members`, `sec-list`.

#### 5.A.6 Auth — `.wj-auth*` (`_auth.css`, Sprint 39)
4 màn Login/Quên mật khẩu × PC+Mobile (thay boilerplate Vuexy EN):
`wj-auth` (shell) + `__brand`/`__eyebrow`/`__features`/`__flag`/`__decor[--1|--2]` (nền trái PC) ·
`wj-auth-card[--forgot]` + `__title`/`__sub` · `wj-auth-field[__label]` + `wj-auth-control` ·
`wj-auth-alert[--error|--success]` · `wj-auth-back` · `wj-auth-foot`.

### 5.B Nhóm `wujia-*` (đời đầu — trang cũ còn dùng)

#### 5.B.1 Buttons — `.wujia-btn`, `-primary`, `-secondary`
- **Primary**: nền `--wujia-primary`, chữ trắng, `h42`, radius `8px`, hover → `primary-dark`.
  (Nút CTA trên nền trắng dùng `--wujia-cta` để đạt contrast AA — §2.)
- **Secondary**: nền trắng, viền `1px --wujia-border`, chữ text-primary, `h38`.
- Icon trong button: flex-center, `line-height:1`, `gap 6px` (fix lệch baseline Font Awesome).
- Variant: `.btn-sm` h32, `.btn-lg` h48.

#### 5.B.2 Status badge — `.wujia-badge` + `-{success,warning,danger,info,muted}`
Pill `999px`, padding `4px 10px`, `12px/600`, nền soft + chữ đậm theo state.
Legacy `.state-*` tự upgrade theo cùng look.

#### 5.B.3 KPI card — `.wujia-kpi-card` (+ `-link`, `-icon-*`, `-separator`, `-content`, `-arrow`)
Layout ngang: **icon vuông trái → vạch dọc 1px → content → chevron phải (optional)**.
- Card trắng radius `16px`, shadow nhẹ, `min-height 100px`, padding `16px`, gap `12px`. Hover nhấc `-2px`.
- Icon box `56×56` radius `12px` nền primary, icon trắng `23px`; đổi màu qua `-icon-{primary,success,warning,danger,info}`.
- Separator `1px × 48px` `#D1D5DB`. Content: label `14px` + value `28px/700` + desc `12px`.
- Chevron neo phải (`margin-left:auto`) `18px`. **<992px:** icon `52×52`, min-h `92px`, 1 card/dòng.

#### 5.B.4 Content card — `.wujia-content-card` (+ `-header[-icon,-title,-link]`, `-body`, `-row[-bullet,-content,-date]`, `-empty`)
Card "Xem tất cả" cho home + listing.
- Card trắng radius `16px`, shadow, padding `22px`.
- Header: icon tròn cyan `40px` + title bold `17px` + link "Xem tất cả" cyan neo phải.
- Row: grid `auto 1fr auto auto` = bullet cyan `8px` + content + date `#6B7280` + badge, có border-bottom.
  Mobile <576px ẩn cột date.
- `--flush` + `.wujia-content-card-table` (negative-margin edge-to-edge) cho trang listing full.

#### 5.B.5 Layout utility
- `.wujia-empty-state` — bản cũ, xem 5.A.4 để biết bản canonical.
- `.wujia-two-pane` — 2 cột (list + detail); <992px stack dọc full-width.
- `.wujia-container` — `padding-inline clamp(12px,3vw,32px)`, max-width `1400px`.
- `.wujia-grid-responsive` — `auto-fit minmax(280px,1fr)`, gap `clamp(12px,2vw,24px)` (thay `col-md-X`).
- `.wujia-stack-mobile[.wujia-row-md]` — flex column mobile, chuyển row ở ≥768px.
- `.pagination.wujia-pagination` — trả dáng chữ nhật Bootstrap (Vuexy bo 5rem làm vỡ pager).

#### 5.B.6 Shell — Current Store + header actions
- **Navbar pill (PC)**: pill 2 dòng sát trái navbar cyan, nền frosted, label uppercase `11px`.
  Token `--wujia-navbar-pill-*`.
- **Mobile sub-strip (<768px)**: dải dưới navbar nền trắng, label cyan uppercase, name đậm,
  role badge stacked. Token `--wujia-mobile-strip-*`.
- **Header right actions**: Language + Cart + Bell + Account. Icon `20px` padding `8px`;
  badge tròn đỏ `--wujia-danger` góc trên-phải, `18px`, hiện qua `.is-active` (count load AJAX
  sau page-ready — perf 1500 user).
  ⚠️ Badge bị Vuexy `.badge` chèn → phải scope `.header-navbar … .wujia-header-badge` + `!important`
  cho bg + color (compact-summary §9 gotcha **#4**).

### 5.C Component mobile theo màn

#### 5.C.1 More Sheet — `.wujia-msheet*` (Figma WJ_MoreBottom 4477:242)
Bottom sheet "Thêm chức năng" mở từ tab footer "Thêm". Markup trong
`wujia_portal_layout.mobile_bottomnav` (`d-lg-none`), toggle `wujia_mobile_more_sheet.js`
(tab/backdrop/close/ESC; body `.wujia-msheet-open` = scroll lock).
- Sheet trắng fixed `bottom: var(--wujia-mnav-height)` (83px — footer vẫn bấm được), bo trên `20px`,
  handle `67×5`, slide-up `.25s`. z-index: backdrop 1028 / sheet 1029 / footer 1030.
- Title Inter Bold `18px` + subtitle `12.5px`, close tròn `32×32`.
- Row `min-height 62px`: icon tile `40×40` tròn nền `--wujia-msheet-icon-bg` + title `15px` bold +
  sub `12px` + chevron.
- 7 item: Đổi trả / Đăng ký thi / Kiến thức / Hỗ trợ / Hồ sơ cửa hàng / **Báo cáo** (ngoài Figma —
  user chốt 2026-06-11) / Tài khoản.

#### 5.C.2 Content wrapper — `.wujia-mpage` (Figma WJ_Mobile_BlankShell 4447:11)
Chuẩn content area cho **trang mobile MỚI** (trong shell header 104 / strip 48 / footer 83):
flex column, gap `--wujia-mshell-content-gap` (14px), padding `14px 16px 0` — **KHÔNG pad-bottom**
(footer-clearance ≥96px đã do rule `.app-content.content` lo; giữ cả hai = 192px trống đáy).
**Đặt block `d-lg-none .wujia-mpage` NGOÀI `.content-wrapper`** — lồng vào = double pad ngang.
Trang đã ship (Home/Order/History) giữ layout riêng, **không retrofit**.

#### 5.C.3 Kiến thức — `.wujia-mknow-*` (Figma WJ_Knowledge_Mobile 4475:2)
List + Detail `/portal/knowledge[/<slug>]`, scoped trong `.wujia-mpage`.
- Chip danh mục: `h32` pill scroll ngang; active = **SOLID** cyan chữ trắng — khác chip **soft**
  của mhist. Cả 2 style đều hợp lệ, chọn theo Figma từng trang.
- Icon tile `40×40` bo `10` (vuông bo, ≠ tile tròn msheet), icon feather cyan `18`.
- Featured card: card trắng + accent cyan 4px mép trái (`::before`).
- Row bài viết: mỗi bài 1 card riêng (gap 10) — KHÔNG list liền-divider như mhist.
- Badge: reuse `.wujia-badge-*`; map MOBILE mandatory/important → **danger** (theo Figma; desktop
  important = warning — drift chủ đích), new → info.
- Body bài viết: `ul/li` marker cyan, `blockquote` → card xám, `div.wujia-note` → card cam.
- Attachment: tile + tên truncate + "EXT • size", route `/portal/knowledge/<slug>/attachment/<id>`
  (stream thật, ACL theo bài).

---

## 6. Design rules theo issue (`5. Issue List` UI-01..UI-18)

> Cột **Impl** = trạng thái code thực tế. ⚠️ BA cập nhật sheet liên tục và đã từng re-number —
> khi code 1 issue **luôn mở lại sheet cột G+H verbatim**, bảng này chỉ định hướng.

| ID | Vùng | Kết quả mong muốn (rút gọn) | Impl (code) |
|---|---|---|---|
| UI-01 | Sidebar | Icon 20–22, text 16, item height 44–48, gap 12; active icon+text trắng | ✅ |
| UI-02 | Sidebar | Bỏ block thông tin user | ✅ |
| UI-03 | Header PC | Current Store `[H000] Cửa hàng…` + role badge + language + avatar | ✅ (container 430px) |
| UI-04 | Header mobile | Như UI-03 cho mobile → sub-strip dưới navbar; action `38×38` gap 16 | ✅ |
| UI-05 | Button | Primary xanh/chữ trắng h40–44; Secondary trắng/viền xám h36–40; đồng nhất mọi page | ✅ (h42/h38) |
| UI-06 | Card/nền | Background chung sáng, card trắng | ✅ (`#F3F6F8`) |
| UI-07 | Top Bar | Height ~64–72px, căn giữa item theo chiều dọc | ✅ (72px) |
| UI-08 | Page Title | `#111827`, ~24px, weight 700 | ✅ |
| UI-09 | Page Subtitle | `#6B7280`, 14–15px, weight 400 | ✅ |
| UI-10 | Font | Đồng nhất 1 font mọi trang | ✅ (Inter) |
| UI-11 | KPI card | Card trắng radius 16, shadow, height ~100, padding 20–24; icon box nền primary; vạch dọc 1px | ✅ (icon 56 theo UI-14, radius 12, sep h48) |
| UI-12 | Content Card | Header icon tròn + title đậm + "Xem tất cả"; row bullet + nội dung + thời gian + badge | ✅ |
| UI-13 | Header Right Actions | Language + cart + notification + account | ✅ (badge đỏ `--wujia-danger`) |
| UI-14 | KPI Card Height | Tăng content, giảm icon box, chuẩn hoá height 100–108 | ✅ |
| UI-15 | KPI Card Mobile | 1 card/dòng, height 88–96, padding 14–16, icon 52×52 | ✅ (override <992px trong `_variables.css`) |
| UI-16 | Main Content Spacing | header→title ~24, title→KPI 12–16, KPI→content 20–24 | ✅ (3 token áp ở `_wujia_theme.css`) |
| UI-17 | Product Best Seller Card | Chuẩn lại theo content card listing, bỏ table thô | ⬜ chưa có (grep `best.seller` = rỗng) |
| UI-18 | Main menu | Row height 44–48, margin 4–6; cùng icon set/stroke, size 20–22 | 🟡 height/icon-size ✅ (`_wujia_theme.css`); "cùng 1 icon set/stroke" chưa rà |

> Trạng thái BA-side (Ready for Retest / Done / Need BA Confirm) nằm ở `qa-issue-ledger.yaml`
> + sheet — **không** duplicate ở đây (sẽ lệch ngay).

---

## 7. Figma mapping guide

Để sync Figma↔code sạch (qua MCP — [`figma-mcp-setup.md`](figma-mcp-setup.md)), **đặt tên Figma
trùng tên token**: bỏ tiền tố `--wujia-`, đổi `-` thành `/` để Figma group lại.

| CSS token | Figma variable |
|---|---|
| `--wujia-primary` | `wujia/primary` |
| `--wujia-text-primary` | `wujia/text-primary` |
| `--wujia-bg-page` | `wujia/bg-page` |
| … (toàn bộ §2) | `wujia/<tên-token-bỏ-prefix>` |

**Text styles:** `wujia/h1` Inter 32/700 · `wujia/h2` 24/600 · `wujia/card-title` 20/600 ·
`wujia/body` 15/400 `#374151` · `wujia/subtitle` 14/400 `#6B7280` · `wujia/page-title` 24/700 `#111827`.

**Components:** dựng mỗi component §5 thành 1 Figma component đúng anatomy, đặt tên
`wujia/<component>` (vd `wujia/kpi-card`), dùng đúng radius/padding/gap ở §4–§5.

---

## 8. Quy tắc bất di bất dịch

Không chép lại ở đây — nguồn duy nhất là **compact-summary §5** (non-negotiable rules: bắt buộc
`var(--wujia-*)`, regression check trước khi sửa token global, bump `?v=` khi đổi CSS) và
**§9 + §10 L4** (gotchas: cache 7 ngày, CSS nằm trên đĩa không phải DB, `!important` tag-level của
shell Vuexy, cách đo computed-style bằng Playwright).

---

## 9. Kết nối Figma — trạng thái

- **File hiện hành = BẢN COPY** team Pro `aoeiDYlg6vlhJZg2w6Q7o5` ("Wujia (Copy)"). Bản gốc
  `vfVcqN5zPJvlcjZU4NYim0` **bị throttle, không dùng nữa** (gặp key này ở chapter tex cũ là lý do đó).
  BA edit trực tiếp vào bản copy.
- Kết nối qua Framelink MCP (`.mcp.json` ở root, gitignored) — **READ-ONLY, không sửa Figma**.
- **BA chưa hoàn thiện Figma** → hiện **theo code** (§2–§5). Khi BA xong: đọc lại qua MCP → đối chiếu
  → cập nhật `_variables.css` **theo Figma của BA**.
- Figma đang **PHẲNG** (card không phải container thật) → gom bằng geometry grouping;
  cách làm ở [`figma-mcp-setup.md`](figma-mcp-setup.md) §8.

**Drift còn sống, cần BA xử lý khi hoàn thiện Figma:**
1. Figma còn dùng text chính `#1F2933` (cũ) trong khi spec của chính BA là `#111827`.
2. Figma trộn 2 sắc đỏ (`#E84545`, `#EF4444`); code chuẩn `--wujia-danger #EF4444`.
3. Figma **chưa có Color/Text styles + Variables** (published styles = 0) — màu hardcode, nội bộ
   không nhất quán → đề nghị BA tạo styles theo §7 để lần sau sync 1-1.
