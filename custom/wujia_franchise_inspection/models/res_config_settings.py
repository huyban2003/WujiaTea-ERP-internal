# -*- coding: utf-8 -*-
import base64
import json
import logging
import os
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wujia_inspection_use_google_drive = fields.Boolean(
        string='Store Inspection Videos on Google Drive',
        help='If enabled, inspection videos will be automatically uploaded to Google Drive (wujia media -> [Store Code] -> ksYYYYMMDD.mp4) instead of storing on Odoo server disk.',
        config_parameter='wujia_franchise_inspection.use_google_drive_video',
        default=False,
    )

    google_drive_credentials_file = fields.Binary(
        string='credentials.json File',
        help='Select credentials.json (OAuth Client Secrets or Service Account Key) downloaded from Google Cloud Console.',
    )
    google_drive_credentials_filename = fields.Char(
        string='Credentials Filename',
        default='credentials.json',
    )

    google_drive_token_file = fields.Binary(
        string='token.json File',
        help='Select token.json containing OAuth access/refresh token.',
    )
    google_drive_token_filename = fields.Char(
        string='Token Filename',
        default='token.json',
    )

    google_drive_has_credentials = fields.Boolean(
        string='Has credentials.json',
        compute='_compute_drive_auth_status',
    )
    google_drive_has_token = fields.Boolean(
        string='Has token.json',
        compute='_compute_drive_auth_status',
    )
    google_drive_status_message = fields.Char(
        string='Authentication Status',
        compute='_compute_drive_auth_status',
    )

    @api.depends('wujia_inspection_use_google_drive')
    def _compute_drive_auth_status(self):
        Param = self.env['ir.config_parameter'].sudo()
        cred_str = Param.get_param('wujia_franchise_inspection.google_drive_credentials_json')
        token_str = Param.get_param('wujia_franchise_inspection.google_drive_token_json')

        base_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(base_dir, '..', 'data', 'credentials.json')
        token_path = os.path.join(base_dir, '..', 'data', 'token.json')

        has_cred = bool(cred_str) or os.path.exists(cred_path)
        has_token = bool(token_str) or os.path.exists(token_path)

        for rec in self:
            rec.google_drive_has_credentials = has_cred
            rec.google_drive_has_token = has_token

            # Check if Service Account
            is_service_account = False
            if cred_str:
                try:
                    c_dict = json.loads(cred_str)
                    if c_dict.get('type') == 'service_account':
                        is_service_account = True
                except Exception:
                    pass

            if is_service_account:
                rec.google_drive_status_message = _('Configured with Google Service Account (Headless ready)')
            elif has_cred and has_token:
                rec.google_drive_status_message = _('Fully configured with credentials.json and token.json')
            elif has_cred:
                rec.google_drive_status_message = _('credentials.json loaded (token.json required for OAuth)')
            else:
                rec.google_drive_status_message = _('No Google Drive authentication file configured')

    def set_values(self):
        super().set_values()
        Param = self.env['ir.config_parameter'].sudo()

        for rec in self:
            # 1. Save credentials.json if uploaded
            if rec.google_drive_credentials_file:
                try:
                    raw_data = base64.b64decode(rec.google_drive_credentials_file).decode('utf-8')
                    # Validate JSON
                    json.loads(raw_data)
                    Param.set_param('wujia_franchise_inspection.google_drive_credentials_json', raw_data)
                    _logger.info("Successfully updated credentials JSON in ir.config_parameter.")
                except Exception as e:
                    raise UserError(_("Invalid JSON format in credentials file: %s") % str(e))

            # 2. Save token.json if uploaded
            if rec.google_drive_token_file:
                try:
                    raw_data = base64.b64decode(rec.google_drive_token_file).decode('utf-8')
                    # Validate JSON
                    json.loads(raw_data)
                    Param.set_param('wujia_franchise_inspection.google_drive_token_json', raw_data)
                    _logger.info("Successfully updated token JSON in ir.config_parameter.")
                except Exception as e:
                    raise UserError(_("Invalid JSON format in token file: %s") % str(e))

    def action_test_google_drive_connection(self):
        """Tests connection and folder structure on Google Drive."""
        self.ensure_one()
        from .google_drive_client import GoogleDriveClient

        client = GoogleDriveClient(env=self.env)
        try:
            folder_id = client.get_or_create_folder('wujia media')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Google Drive Connection Successful!'),
                    'message': _("Authentication successful. Folder 'wujia media' is ready (Folder ID: %s).") % folder_id,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_("Google Drive connection test failed: %s") % str(e))
