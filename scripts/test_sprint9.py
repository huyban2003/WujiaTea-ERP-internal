"""Smoke test for Sprint 9 — Issue List UI refactor (UI-18 + empty state + cleanup).

Run via odoo shell (ORM-level, same style as test_sprint5.py):
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/test_sprint9.py

Covers the non-CSS-visual parts that are assertable from the ORM:
  - UI-18 sidebar icon consistency (no Font Awesome left in the menu)
  - empty states standardized to .wujia-empty-state
  - wujia_account stub removed (never a real module)

Visual spacing / 301 redirect behaviour are checked separately
(browser smoke + curl) — see Sprint 9.22.
"""
print("=== SPRINT 9 SMOKE TEST ===")

PASS, FAIL = 0, 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


View = env['ir.ui.view']


def all_arch():
    """Concatenated arch of every stored view — cheap global scan."""
    chunks = []
    for v in View.search([]):
        try:
            chunks.append(v.arch or '')
        except Exception:
            pass
    return "\n".join(chunks)

ARCH = all_arch()

# -----------------------------------------------------------------
# A) UI-18 — sidebar menu icon consistency (feather, no Font Awesome)
#    Scope is the SIDEBAR MENU only: page-body fa-* icons (page headers,
#    modals, backend admin) are explicitly out of scope for UI-18.
# -----------------------------------------------------------------
print("\n[A] UI-18 sidebar icon consistency")
menu_franchises = env.ref('wujia_portal_base.layout_sidenav_franchises',
                          raise_if_not_found=False)
menu_info = env.ref('wujia_portal_base.sidenav_franchise_information',
                    raise_if_not_found=False)
fa_arch = (menu_franchises.arch if menu_franchises else '') + \
          (menu_info.arch if menu_info else '')
check(menu_info and 'feather icon-info' in menu_info.arch,
      "'Thông tin nhượng quyền' menu item uses feather icon-info")
check(menu_franchises and 'feather icon-shopping-bag' in menu_franchises.arch,
      "'Cửa hàng' menu item uses feather icon-shopping-bag")
check('fa fa-building' not in fa_arch,
      "no 'fa fa-building' left in the sidebar menu items")
check('fa fa-info-circle' not in fa_arch,
      "no 'fa fa-info-circle' left in the sidebar menu items")

# -----------------------------------------------------------------
# B) 9.20 — empty states standardized to .wujia-empty-state
# -----------------------------------------------------------------
print("\n[B] Empty state standardization")
empty_views = View.search([]).filtered(
    lambda v: 'wujia-empty-state' in (v.arch or ''))
check(len(empty_views) >= 8,
      f"at least 8 views use .wujia-empty-state (found {len(empty_views)})")
check('class="alert alert-info">Bạn chưa có kết quả thi nào' not in ARCH,
      "exam result empty no longer uses raw alert-info block")

# -----------------------------------------------------------------
# C) 9.21 — wujia_account stub removed
# -----------------------------------------------------------------
print("\n[C] Cleanup — wujia_account stub")
mod = env['ir.module.module'].search([('name', '=', 'wujia_account')])
check(not mod,
      "wujia_account is not a registered module (stub removed)")

# -----------------------------------------------------------------
print(f"\n=== RESULT: {PASS} passed, {FAIL} failed ===")
if FAIL:
    print("[ERROR] some assertions failed — see FAIL lines above.")
else:
    print("[OK] all assertions passed.")
