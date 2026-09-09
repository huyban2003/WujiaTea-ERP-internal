# -*- coding: utf-8 -*-
import io
import json
import logging
import os
import threading

_logger = logging.getLogger(__name__)

# Scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveClient:
    """
    Utility client for Google Drive API operations:
    - Supports Service Account (preferred for headless production)
    - Supports OAuth2 credentials with automatic token refresh and DB persistence
    - Managing folders (wujia media / <store_code>)
    - Uploading inspection media streams / files directly to Google Drive
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, env=None, token_path=None, credentials_path=None):
        self.env = env
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, '..', 'data')
        self.token_path = token_path or os.path.join(data_dir, 'token.json')
        self.credentials_path = credentials_path or os.path.join(data_dir, 'credentials.json')
        self._service = None

    def _get_credentials_from_db(self):
        """Attempts to load credentials / tokens from ir.config_parameter."""
        if not self.env:
            return None, None
        try:
            Param = self.env['ir.config_parameter'].sudo()
            cred_str = Param.get_param('wujia_franchise_inspection.google_drive_credentials_json')
            token_str = Param.get_param('wujia_franchise_inspection.google_drive_token_json')
            cred_data = json.loads(cred_str) if cred_str else None
            token_data = json.loads(token_str) if token_str else None
            return cred_data, token_data
        except Exception as e:
            _logger.warning("Could not load Google Drive config from DB: %s", e)
            return None, None

    def _save_token_to_db(self, token_json_str):
        """Saves refreshed token back to DB if env is available."""
        if self.env:
            try:
                self.env['ir.config_parameter'].sudo().set_param(
                    'wujia_franchise_inspection.google_drive_token_json',
                    token_json_str
                )
                _logger.info("Persisted refreshed Google Drive token to ir.config_parameter.")
            except Exception as e:
                _logger.warning("Could not save refreshed token to DB: %s", e)

    def _get_credentials(self):
        """Loads and refreshes Google API credentials safely in headless environments."""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
            from google.oauth2.credentials import Credentials
        except ImportError:
            _logger.error(
                "Google Drive API libraries are not installed. "
                "Please run: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2"
            )
            raise RuntimeError(
                "Google Drive API libraries are not installed (missing google-api-python-client or google-auth)."
            )

        cred_data, token_data = self._get_credentials_from_db()

        # 1. Check if Service Account JSON is provided (either from DB or file)
        if cred_data and cred_data.get('type') == 'service_account':
            try:
                return service_account.Credentials.from_service_account_info(cred_data, scopes=SCOPES)
            except Exception as e:
                _logger.error("Failed to load service account credentials from DB: %s", e)
                raise RuntimeError(f"Service account error: {e}")

        if os.path.exists(self.credentials_path):
            try:
                with open(self.credentials_path, 'r', encoding='utf-8') as f:
                    file_cred = json.load(f)
                if file_cred.get('type') == 'service_account':
                    return service_account.Credentials.from_service_account_file(self.credentials_path, scopes=SCOPES)
            except Exception as e:
                _logger.warning("Failed to check file credentials: %s", e)

        # 2. Check if OAuth2 User Token is provided
        creds = None
        if token_data:
            try:
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            except Exception as e:
                _logger.warning("Error reading token from DB: %s", e)
                creds = None
        elif os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                _logger.warning("Error reading token.json: %s", e)
                creds = None

        if creds and creds.valid:
            return creds

        # 3. Refresh expired OAuth2 token
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                token_str = creds.to_json()
                self._save_token_to_db(token_str)
                if os.path.exists(os.path.dirname(self.token_path)):
                    try:
                        with open(self.token_path, 'w', encoding='utf-8') as token_file:
                            token_file.write(token_str)
                    except Exception:
                        pass
                _logger.info("Google Drive OAuth token refreshed successfully.")
                return creds
            except Exception as e:
                _logger.error("Failed to refresh Google Drive token: %s", e)
                raise RuntimeError(f"Failed to refresh Google Drive token: {e}")

        # 4. If credentials/token missing, raise informative error instead of running local server in headless
        raise RuntimeError(
            "Google Drive credentials or token not configured or expired. "
            "Please upload credentials.json / token.json in Settings > Survey & Google Drive."
        )

    def get_service(self):
        """Returns the Google Drive service instance (thread-safe build)."""
        try:
            from googleapiclient.discovery import build
        except ImportError:
            raise RuntimeError("googleapiclient is not installed.")

        with self._lock:
            if not self._service:
                creds = self._get_credentials()
                self._service = build('drive', 'v3', credentials=creds, cache_discovery=False)
            return self._service

    def get_or_create_folder(self, folder_name, parent_folder_id=None):
        """Finds or creates a folder on Google Drive."""
        service = self.get_service()
        query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"

        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        files = response.get('files', [])

        if files:
            folder_id = files[0].get('id')
            _logger.info("Found existing Google Drive folder '%s' (ID: %s)", folder_name, folder_id)
            return folder_id

        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        folder = service.files().create(
            body=folder_metadata,
            fields='id, name'
        ).execute()

        folder_id = folder.get('id')
        _logger.info("Created new Google Drive folder '%s' (ID: %s)", folder_name, folder_id)
        return folder_id

    def upload_inspection_video(self, video_data, store_code, date_str, original_filename=None):
        """
        Uploads inspection video directly to Google Drive under: 'wujia media/<store_code>/ks<date_str>.mp4'
        """
        try:
            from googleapiclient.http import MediaIoBaseUpload
        except ImportError:
            raise RuntimeError("googleapiclient is not installed.")

        service = self.get_service()

        root_folder_id = self.get_or_create_folder('wujia media')
        store_folder_name = store_code.strip() if store_code else 'UNKNOWN_STORE'
        store_folder_id = self.get_or_create_folder(store_folder_name, parent_folder_id=root_folder_id)

        clean_date = date_str.replace('-', '').replace('/', '') if date_str else 'UNKNOWN_DATE'
        dest_filename = f"ks{clean_date}.mp4"

        file_metadata = {
            'name': dest_filename,
            'parents': [store_folder_id],
            'description': f"Wujia Franchise Inspection Video - Store: {store_code} - Date: {date_str}"
        }

        media_stream = io.BytesIO(video_data)
        media = MediaIoBaseUpload(
            media_stream,
            mimetype='video/mp4',
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, webContentLink, size'
        ).execute()

        _logger.info(
            "Uploaded inspection video to Google Drive: %s (ID: %s, URL: %s)",
            dest_filename, file.get('id'), file.get('webViewLink')
        )
        return file
