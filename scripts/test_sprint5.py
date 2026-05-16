"""Smoke test for Sprint 5 — batch_id + knowledge + support full BA.

Run AFTER all seed scripts:
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/test_sprint5.py

Exits with non-zero count if any assertion fails — main runner can
grep "FAIL:" in stdout for CI-style use.
"""
print("=== SPRINT 5 SMOKE TEST ===")

PASS, FAIL = 0, 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


# -----------------------------------------------------------------
# A) sale.order.batch_id
# -----------------------------------------------------------------
print("\n[A] sale.order.batch_id")
SO = env['sale.order']
Batch = env['stock.picking.batch']
Picking = env['stock.picking']

so_with_batch = SO.search([('batch_id', '!=', False)], limit=1)
if so_with_batch:
    so = so_with_batch
    pickings = so.picking_ids.filtered(
        lambda p: p.state != 'cancel' and p.batch_id
    ).sorted('id')
    expected_batch = pickings[:1].batch_id
    check(so.batch_id == expected_batch,
          f"SO {so.name} batch_id == first non-cancel picking's batch")
else:
    # Manufacture: find a picking with batch, ensure SO compute populates.
    pick_with_batch = Picking.search([('batch_id', '!=', False)], limit=1)
    if pick_with_batch and pick_with_batch.sale_id:
        so = pick_with_batch.sale_id
        so.invalidate_recordset(['batch_id'])
        check(so.batch_id == pick_with_batch.batch_id,
              f"SO {so.name} batch_id auto = picking.batch_id ({pick_with_batch.batch_id.name})")
    else:
        print("  SKIP: no SO with batch_id and no picking with batch found.")

# -----------------------------------------------------------------
# B) wujia.knowledge — state, tag, is_published_portal, cron
# -----------------------------------------------------------------
print("\n[B] wujia.knowledge")
Article = env['wujia.knowledge.article']
Tag = env['wujia.knowledge.tag']

published = Article.search([('state', '=', 'published')])
check(len(published) > 0, f"At least one published article ({len(published)} found)")

# is_published_portal must match (state=published AND expired in future).
from datetime import datetime
now = datetime.now()
visible_expected = published.filtered(
    lambda a: not a.expired_date or a.expired_date > now
)
visible_actual = Article.search([('is_published_portal', '=', True)])
check(set(visible_actual.ids) == set(visible_expected.ids),
      f"is_published_portal matches state=published AND not expired "
      f"(expected {len(visible_expected)}, got {len(visible_actual)})")

expired = Article.search([('expired_date', '<=', now), ('state', '=', 'published')])
if expired:
    check(all(not a.is_published_portal for a in expired),
          f"Expired articles ({len(expired)}) excluded from portal")

# Tag M2m search.
tag = Tag.search([], limit=1)
if tag:
    tagged = Article.search([('tag_ids', 'in', [tag.id])])
    direct = Article.search([]).filtered(lambda a: tag in a.tag_ids)
    check(set(tagged.ids) == set(direct.ids),
          f"Tag M2m search works ({len(tagged)} articles for tag '{tag.name}')")

# Sequence — at least one article has KNW- code.
coded = Article.search([('code', 'like', 'KNW-%')])
check(len(coded) > 0, f"Sequence assigned KNW- prefix ({len(coded)} articles)")

# Cron exists.
cron = env.ref('wujia_portal_knowledge.cron_recompute_is_published', raise_if_not_found=False)
check(bool(cron), "Cron recompute_is_published exists")

# -----------------------------------------------------------------
# C) wujia.support.ticket — rename, state, analytics
# -----------------------------------------------------------------
print("\n[C] wujia.support.ticket")
Ticket = env['wujia.support.ticket']
Category = env['wujia.support.category']

# Categories seeded from XML
default_codes = {'order', 'delivery', 'product', 'pos', 'operation', 'account', 'other'}
seeded_codes = set(Category.search([('code', 'in', list(default_codes))]).mapped('code'))
check(default_codes == seeded_codes,
      f"All 7 default categories seeded (missing: {default_codes - seeded_codes})")

tickets = Ticket.search([])
check(len(tickets) > 0, f"Tickets seeded ({len(tickets)})")

if tickets:
    t = tickets[0]
    check(bool(t.title), f"Ticket {t.name} has title")
    check(bool(t.category_id), f"Ticket {t.name} has category_id (M2o)")
    check(bool(t.created_by_id), f"Ticket {t.name} has created_by_id")
    check(t.priority in ('normal', 'urgent'), f"Priority in BA spec values: {t.priority}")

# created_by_role snapshot (only if franchise has membership).
with_role = Ticket.search([('created_by_role', '!=', False)])
print(f"  INFO: tickets with created_by_role={len(with_role)} (depends on membership)")

# 6-state coverage.
states = set(tickets.mapped('state'))
check('cancelled' in states, "At least one cancelled ticket in seed")
check('waiting_customer' in states, "At least one waiting_customer ticket in seed")

# Cancel constraint.
from odoo.exceptions import ValidationError
cancelled = tickets.filtered(lambda t: t.state == 'cancelled')
if cancelled:
    check(all((tc.cancel_reason or '').strip() for tc in cancelled),
          "All cancelled tickets have cancel_reason")
    try:
        nt = Ticket.create({
            'title': '_test_cancel_no_reason',
            'franchise_id': tickets[0].franchise_id.id,
            'category_id': tickets[0].category_id.id,
            'state': 'cancelled',
        })
        check(False, "Cancel without reason should raise ValidationError")
    except ValidationError:
        check(True, "Cancel without cancel_reason raises ValidationError")

# State transition stamps in_progress_date.
draft_t = Ticket.search([('state', '=', 'new')], limit=1)
if draft_t:
    draft_t.action_set_in_progress()
    check(bool(draft_t.in_progress_date), "action_set_in_progress stamps in_progress_date")
    draft_t.action_set_resolved()
    check(bool(draft_t.resolved_date), "action_set_resolved stamps resolved_date")

# message_post updates analytics.
if tickets:
    t = tickets[0]
    t.with_user(env.user).message_post(body='Test reply from internal HQ',
                                       message_type='comment',
                                       subtype_xmlid='mail.mt_comment')
    t.invalidate_recordset(['last_message_date', 'last_response_by'])
    check(bool(t.last_message_date),
          "message_post updates last_message_date")
    check(t.last_response_by == 'hq',
          f"message_post by internal user → last_response_by='hq' (got {t.last_response_by})")

# -----------------------------------------------------------------
# Result
# -----------------------------------------------------------------
print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
if FAIL:
    print("[ERROR] some assertions failed — see FAIL lines above.")
else:
    print("[OK] all assertions passed.")
