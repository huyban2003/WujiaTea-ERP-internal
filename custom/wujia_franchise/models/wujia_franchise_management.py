import re

from odoo import _, api, fields, models
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


class WujiaFranchiseManagement(models.Model):
    _name = 'wujia.franchise.management'
    _description = 'Wujia Franchise Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'code, name'

    code = fields.Char(
        string='Store code',
        required=True,
        index=True,
        tracking=True,
        help='Franchise store code, e.g. H010 or HN-01.',
    )
    name = fields.Char(
        string='Store name',
        required=True,
        tracking=True,
        help='Display name, e.g. "[H010] 219 Vinh Vien store".',
    )
    display_name = fields.Char(compute='_compute_display_name', store=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        ondelete='restrict',
        index=True,
        tracking=True,
        help='Link to the res.partner representing the store — the transactional entity for '
             'sale.order, account.move, membership.',
    )

    opening_date = fields.Date(string='Opening date', tracking=True)
    address = fields.Text(string='Address', tracking=True)
    state_id = fields.Many2one(
        'res.country.state',
        string='Province',
        tracking=True,
    )
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    franchise_start_date = fields.Date(
        string='Franchise start date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    franchise_end_date = fields.Date(
        string='Franchise end date',
        required=True,
        tracking=True,
    )
    remaining_days = fields.Integer(
        string='Days remaining',
        compute='_compute_remaining_days',
        store=True,
    )
    is_expired = fields.Boolean(
        string='Contract expired',
        compute='_compute_remaining_days',
        store=True,
    )

    area_id = fields.Many2one(
        'res.area',
        string='Area',
        tracking=True,
        ondelete='restrict',
    )
    area_name = fields.Char(related='area_id.name', store=True, readonly=True)

    description = fields.Text(
        string='Operating description',
        help='Operating notes: delivery, loading bans, parking bans...',
    )
    note = fields.Text(string='Internal note')

    portal_locked = fields.Boolean(
        string='Portal locked',
        default=False,
        tracking=True,
        help='Block every portal access of this store (e.g. contract breach).',
    )
    invoiced = fields.Boolean(
        string='Invoiced',
        default=False,
        help='Flag tracking whether the related invoices have been issued.',
    )

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('locked', 'Locked'),
            ('closed', 'Closed'),
            ('expired', 'Expired'),
        ],
        string='Status',
        required=True,
        default='draft',
        tracking=True,
    )

    member_ids = fields.One2many(
        'wujia.franchise.member',
        'franchise_id',
        string='Members',
    )
    member_count = fields.Integer(
        string='Member count',
        compute='_compute_member_count',
    )
    main_owner_member_id = fields.Many2one(
        'wujia.franchise.member',
        string='Primary owner',
        compute='_compute_main_owner_member',
        help='The active member with role=owner for this store (BA spec).',
    )

    supervision_user_id = fields.Many2one(
        'res.users',
        string='Supervisor',
        tracking=True,
    )

    area_manager_user_id = fields.Many2one(
        related='area_id.manager_user_id',
        string='Area Manager',
        readonly=True,
        store=False
    )

    effective_supervision_user_id = fields.Many2one(
        'res.users',
        string='Assigned Supervisor',
        compute='_compute_effective_supervision_user',
        store=True,
        help='Franchise supervisor. If not assigned, defaults to Area Manager.',
    )

    next_supervision_date = fields.Date(
        string='Next Inspection Date',
        compute='_compute_next_supervision_date',
        store=True,
        search='_search_next_supervision_date',
        help='Nearest upcoming inspection date (>= today), excluding past and cancelled schedules.',
    )

    inspection_ids = fields.One2many(
        'wujia.franchise.inspection',
        'franchise_id',
        string='Inspection Sheets',
    )
    document_ids = fields.One2many(
        'wujia.franchise.document',
        'franchise_id',
        string='Documents',
        copy=False,
    )
    inspection_chart_data = fields.Text(
        string='Inspection Chart Data',
        compute='_compute_inspection_chart_data',
    )

    latest_inspection_id = fields.Many2one(
        'wujia.franchise.inspection',
        string='Latest Inspection Sheet',
        compute='_compute_latest_inspection_info',
        store=True,
    )
    latest_total_score = fields.Float(
        string='Latest Inspection Score',
        compute='_compute_latest_inspection_info',
        store=True,
    )
    latest_grade_id = fields.Many2one(
        'wujia.franchise.inspection.grade',
        string='Latest Inspection Grade',
        compute='_compute_latest_inspection_info',
        store=True,
    )
    latest_inspection_date = fields.Date(
        string='Latest Inspection Date',
        compute='_compute_latest_inspection_info',
        store=True,
    )
    consecutive_c_count = fields.Integer(
        string='Consecutive C Count',
        compute='_compute_latest_inspection_info',
        store=True,
        help='Number of consecutive completed inspections with grade C from the latest round.',
    )
    consecutive_d_count = fields.Integer(
        string='Consecutive D Count',
        compute='_compute_latest_inspection_info',
        store=True,
        help='Number of consecutive completed inspections with grade D from the latest round.',
    )
    consecutive_cd_count = fields.Integer(
        string='Consecutive C/D Count',
        compute='_compute_latest_inspection_info',
        store=True,
        help='Consecutive count of grade C if latest is C, or consecutive count of grade D if latest is D.',
    )
    google_map_url = fields.Char(string='Google Map URL')

    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint(
        'UNIQUE (code)',
        'Store code must be unique.',
    )

    # ===========================================================
    # Compute / depends
    # ===========================================================
    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            if rec.code and rec.name:
                rec.display_name = f'[{rec.code}] {rec.name}'
            else:
                rec.display_name = rec.name or rec.code or _('New Franchise')

    @api.depends('franchise_end_date')
    def _compute_remaining_days(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.franchise_end_date:
                delta = (rec.franchise_end_date - today).days
                rec.remaining_days = delta
                rec.is_expired = delta < 0
            else:
                rec.remaining_days = 0
                rec.is_expired = False

    @api.depends('member_ids.is_currently_valid')
    def _compute_member_count(self):
        for rec in self:
            rec.member_count = len(
                rec.member_ids.filtered('is_currently_valid')
            )

    @api.depends('member_ids.role', 'member_ids.is_currently_valid')
    def _compute_main_owner_member(self):
        for rec in self:
            owner = rec.member_ids.filtered(
                lambda m: m.role == 'owner' and m.is_currently_valid
            )[:1]
            rec.main_owner_member_id = owner

    @api.depends('supervision_user_id', 'area_id.manager_user_id')
    def _compute_effective_supervision_user(self):
        for rec in self:
            rec.effective_supervision_user_id = (
                rec.supervision_user_id or rec.area_id.manager_user_id
            )

    @api.depends()
    def _compute_next_supervision_date(self):
        if not self:
            return
        today = fields.Date.context_today(self)
        groups = self.env['wujia.supervision.schedule']._read_group(
            domain=[
                ('store_id', 'in', self.ids),
                ('date', '>=', today),
                ('state', '!=', 'cancel'),
            ],
            groupby=['store_id'],
            aggregates=['date:min'],
        )
        min_date_by_store = {store.id: min_date for store, min_date in groups if store and min_date}
        for rec in self:
            rec.next_supervision_date = min_date_by_store.get(rec.id, False)

    def _search_next_supervision_date(self, operator, value):
        today = fields.Date.context_today(self)
        schedules = self.env['wujia.supervision.schedule'].search([
            ('date', '>=', today),
            ('date', operator, value),
            ('state', '!=', 'cancel'),
        ])
        return [('id', 'in', schedules.mapped('store_id').ids)]

    @api.depends('inspection_ids.total_score', 'inspection_ids.grade_id', 'inspection_ids.planned_date', 'inspection_ids.state')
    def _compute_latest_inspection_info(self):
        if not self:
            return

        for rec in self:
            done_inspections = rec.inspection_ids.filtered(
                lambda i: i.state == 'done' and i.planned_date
            ).sorted(
                key=lambda i: (i.planned_date, i.id),
                reverse=True
            )
            if done_inspections:
                latest = done_inspections[0]
                rec.latest_inspection_id = latest
                rec.latest_total_score = latest.total_score
                rec.latest_grade_id = latest.grade_id
                rec.latest_inspection_date = latest.planned_date

                # Separate consecutive counts for grade C and grade D
                count_c = 0
                count_d = 0
                latest_grade_name = latest.grade_id.name if latest.grade_id else ''

                if latest_grade_name == 'C':
                    for insp in done_inspections:
                        if insp.grade_id and insp.grade_id.name == 'C':
                            count_c += 1
                        else:
                            break
                elif latest_grade_name == 'D':
                    for insp in done_inspections:
                        if insp.grade_id and insp.grade_id.name == 'D':
                            count_d += 1
                        else:
                            break

                rec.consecutive_c_count = count_c
                rec.consecutive_d_count = count_d
                rec.consecutive_cd_count = count_c if latest_grade_name == 'C' else (count_d if latest_grade_name == 'D' else 0)
            else:
                rec.latest_inspection_id = False
                rec.latest_total_score = 0.0
                rec.latest_grade_id = False
                rec.latest_inspection_date = False
                rec.consecutive_c_count = 0
                rec.consecutive_d_count = 0
                rec.consecutive_cd_count = 0

    @api.depends('inspection_ids.total_score', 'inspection_ids.grade_id', 'inspection_ids.planned_date', 'inspection_ids.state')
    def _compute_inspection_chart_data(self):
        import json
        for rec in self:
            inspections = rec.inspection_ids.filtered(
                lambda i: i.state in ('done', 'need_remediation') and i.planned_date
            ).sorted(
                key=lambda i: (i.planned_date, i.id)
            )

            # Take last 10 rounds
            if len(inspections) > 10:
                inspections = inspections[-10:]

            labels = []
            scores = []
            grades = []
            display_scores = []
            avg_scores = []

            if inspections:
                total_sum = sum(ins.total_score for ins in inspections)
                overall_avg = total_sum / len(inspections)

                for ins in inspections:
                    date_str = ins.planned_date.strftime('%d/%m/%Y') if ins.planned_date else ''
                    labels.append(date_str)
                    scores.append(ins.total_score)
                    grade_name = (ins.grade_id.name if ins.grade_id else '').strip()
                    grades.append(grade_name)

                    score_val = ins.total_score
                    score_str = f"{int(score_val)}" if score_val.is_integer() else f"{score_val:.1f}"
                    display_text = f"{score_str} ({grade_name})" if grade_name else score_str
                    display_scores.append(display_text)
                    avg_scores.append(round(overall_avg, 2))

            rec.inspection_chart_data = json.dumps({
                'labels': labels,
                'scores': scores,
                'grades': grades,
                'display_scores': display_scores,
                'avg_scores': avg_scores,
                'title': _("Supervision Score History (Last 10 Rounds)"),
                'single_label': _("Score per Round"),
                'avg_label': _("Average Score"),
                'no_data_title': _("No Historical Data Yet!"),
                'no_data_desc': _("This store has no completed/remediation inspection sheets yet."),
            })

    # ===========================================================
    # Constraints
    # ===========================================================
    @api.constrains('franchise_start_date', 'franchise_end_date')
    def _check_franchise_dates(self):
        for rec in self:
            if (rec.franchise_end_date and rec.franchise_start_date
                    and rec.franchise_end_date < rec.franchise_start_date):
                raise ValidationError(_(
                    "Franchise end date must be >= start date."
                ))

    @api.constrains('email')
    def _check_email_format(self):
        for rec in self:
            if rec.email and not EMAIL_RE.match(rec.email):
                raise ValidationError(_("Email '%s' is invalid.", rec.email))

    @api.constrains('status', 'partner_id')
    def _check_partner_required_when_active(self):
        for rec in self:
            if rec.status == 'active' and not rec.partner_id:
                raise ValidationError(_(
                    "Active store '%s' must have an associated Partner for sales orders/invoicing.", rec.display_name,
                ))

    # ===========================================================
    # Onchange / Actions
    # ===========================================================
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.name or self.partner_id.name
            self.phone = self.phone or self.partner_id.phone
            self.email = self.email or self.partner_id.email
            self.state_id = self.state_id or self.partner_id.state_id

    def action_view_members(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Members of %s', self.display_name),
            'res_model': 'wujia.franchise.member',
            'view_mode': 'list,form',
            'domain': [('franchise_id', '=', self.id)],
            'context': {'default_franchise_id': self.id},
        }

    def _onboarding_action(self, mode):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'wujia_franchise.action_franchise_onboarding_wizard'
        )
        action['context'] = {
            'default_franchise_id': self.id,
            'default_mode': mode,
            'default_partner_mode': 'existing' if self.partner_id else 'new',
        }
        return action

    def action_open_onboarding(self):
        return self._onboarding_action('store')

    def action_open_add_members(self):
        return self._onboarding_action('member')

    def action_set_active(self):
        for rec in self:
            rec._assert_ready_to_activate()
            rec.status = 'active'
            rec.portal_locked = False

    def _assert_ready_to_activate(self):
        self.ensure_one()
        missing = []
        if not self.partner_id:
            missing.append(_("a Store Partner"))
        if not self.main_owner_member_id:
            missing.append(_("at least one valid Owner membership"))
        if missing:
            raise ValidationError(_(
                "Store '%(store)s' cannot be activated yet — it still needs %(missing)s. "
                "Run store onboarding to complete it; the store stays in Draft meanwhile.",
                store=self.display_name, missing=', '.join(missing),
            ))

    def action_lock_portal(self):
        for rec in self:
            rec.status = 'locked'
            rec.portal_locked = True

    def action_close(self):
        for rec in self:
            rec.status = 'closed'
            rec.portal_locked = True

    @api.model
    def _cron_check_expired(self):
        """Tự động set status='expired' khi đến hạn (ir.cron daily)."""
        today = fields.Date.context_today(self)
        expired = self.search([
            ('franchise_end_date', '<', today),
            ('status', 'not in', ['expired', 'closed']),
            ('active', '=', True),
        ])
        expired.write({'status': 'expired'})


class WujiaFranchiseDocument(models.Model):
    _name = 'wujia.franchise.document'
    _description = 'Franchise Store Document'
    _order = 'create_date desc, id desc'

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Franchise Store',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Document Name',
    )
    file = fields.Binary(
        string='Download',
        required=True,
        attachment=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') and vals.get('file'):
                vals['name'] = _('Document')
        return super().create(vals_list)
