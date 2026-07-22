# Sprint Summary — Portal Order + Shell/Layout (2026-07-23)

**Branch integration:** all work merged to `main` (HEAD `1d80ef0`), 8 commits ahead of `origin/main`.
**Build:** `-u wujia_portal_sale,wujia_portal_layout,wujia_portal_base --stop-after-init` → 94 modules loaded, **no ERROR/CRITICAL/Traceback**.
**Sheet:** 28 issues set **Ready for Retest** via `qa_sync` (verified 28/28).
**Dev handoff rule:** Dev max state = Ready for Retest. BA retests → Done.

---

## Batches (git)

| Batch | Branch | Fix commit | Ledger commit | Merge |
|-------|--------|-----------|---------------|-------|
| A — order logic | dev/2026-07-22-orderA-logic | `bd55ef9` | `37f35a6` | `8cea51b` |
| B — order UI a11y | dev/2026-07-22-orderB-ui | `cd1025d` | `af51fd5` | `8cea51b` |
| C — shell/layout | dev/2026-07-23-shellC | `2e2e70d` | `e2dc33e` | `1d80ef0` |

## Issues completed (28 → Ready for Retest)

**Batch A — order logic (6):** WJ-ORD-001, -002, -003, -004, -017, -020
Qty validation (reject -1/0/non-int), atomic ±min_qty step, BFCache fix, unaccent search.

**Batch B — order UI / a11y / order-window (15):** WJ-ORD-005, -006, -009, -010, -011, -012, -013, -014, -015, -018, -019, -021, -022, FUNC-MOB-ORDER-005, -006
Mobile H1 "Đặt hàng" + SP counter, real order-window banner, conditional Quy-cách column,
aria-labels on cart buttons, larger touch targets, CTA-dark token `#0F7CA8` (AA 4.71:1),
safe-area padding, detail-image cap, overnight order-window label, cart horizontal-scroll,
focus rings, list-row stepper morph, item-vs-quantity count labels, mobile order note, mobile search submit.

**Batch C — shell/layout/typography (7):** UI-01, UI-02, UI-03, UI-04, UI-06, UI-MOB-HOME-002, UI-PC-SHELL-001
Navbar float-offset override (specificity + position:fixed), PC language pill 118×40,
account pill 202×52, mobile header actions 44→38px, font-smoothing + Inter broaden + weight cap ≤700,
Home mobile section-title 18/24/700, sidebar width 300px + content margin (close 40px gap).

## Needs on-server visual retest (headless can't measure computed-style)

- **UI-01 / UI-PC-SHELL-001** — Vuexy cascade resolves at runtime; verify Top Bar anchors x=300,y=0,w=1620,h=72 and sidebar background is continuous 0–300 at 1920×1080. If still off, send computed-style of `.header-navbar` / `.main-menu`.
- **UI-02** — control shows "English" **correctly** because the test account (Administrator) is `lang=en_US` in DB. To see "Việt Nam": set account language = Tiếng Việt (Settings → Users → Preferences → Language) or click the VN flag on portal.
- **UI-06** — "nhòe/răng cưa" is a rendering perception; confirm by eye on server (fix added `-webkit-font-smoothing`).
- **UI-01 store block** — `margin-left:10px` was calibrated against the (previously broken) navbar; re-measure once navbar anchors correctly.

## Deferred (documented in ledger, not this sprint)

- **UI-MOB-SHELL-001** — needs BA to supply a mobile logo asset at ratio 100:34 (container ready, `object-fit:contain` preserves source ratio).
- **RESP-MOB-SHELL-003** — page-header y=168 normalization spans ~10 pages (wide regression risk); needs browser verification.

---

## Deploy (server)

All work is on local `main`, **not yet on origin**. Two steps:

1. Push `main` → `origin/main` (only after user consent — see guardrail).
2. On the server: `git pull` then restart Odoo **with `-u` to rebuild CSS asset bundles**:

```
python odoo-bin -c config/odoo.conf -d wujia_tea_19 \
  -u wujia_portal_sale,wujia_portal_layout,wujia_portal_base
```

> A plain reload (`--dev=reload`) does **not** rebuild compiled CSS asset bundles — the `-u` on these 3 modules is required for the new CSS/tokens to take effect.

## Logo not showing (fleet/franchise)

Portal logos do **not** come from static files. All portal logos render from **`res.company.logo_web`** (navbar/sidebar/mobile) and the favicon from **`res.company.logo`** — base64 DB fields on `res.company`.

**Fix on server:** backend → **Settings → Companies → [the company] → Logo** field → upload the image. Do this per company (fleet + each franchise company). Uploading files into `static/` folders has no effect on the portal logo.
