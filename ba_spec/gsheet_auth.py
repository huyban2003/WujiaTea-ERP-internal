#!/usr/bin/env python3
"""OAuth (installed-app) cho Google Sheets — tài khoản user, dev-only, gitignored.

Một lần: đặt `client_secret.json` (OAuth Desktop client) cạnh file này rồi chạy
    python3 gsheet_auth.py            # mở consent -> sinh token.json (refresh token)
    python3 gsheet_auth.py --check    # kiểm token còn dùng được không

token.json sau đó được qa_sync.py / task_sync.py / cron tái dùng (tự refresh access
token, KHÔNG cần consent lại) cho tới khi user thu hồi quyền.

KHÔNG commit client_secret.json / token.json (thư mục scripts/ba_spec/ đã gitignore).
"""
import os
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Read + write giá trị ô. (Không cần scope Drive.)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(HERE, "client_secret.json")
TOKEN = os.path.join(HERE, "token.json")


def get_credentials(interactive=True):
    """Trả Credentials hợp lệ (refresh nếu hết hạn). interactive=False -> không mở
    consent (dùng trong cron: chỉ chấp nhận creds đã có + refresh được).

    Ưu tiên: (0) gcloud ADC (application-default login) -> (1) token.json -> (2) consent."""
    # (0) Application Default Credentials — `gcloud auth application-default login`
    #     (cách bật gọn nhất: 1 lệnh, không cần tạo OAuth client trong GCP console).
    try:
        import google.auth
        adc, _ = google.auth.default(scopes=SCOPES)
        if not adc.valid:
            adc.refresh(Request())
        if adc.valid:
            return adc
    except Exception:
        pass  # chưa có ADC -> thử token.json bên dưới

    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save(creds)
        return creds

    if not interactive:
        raise RuntimeError(
            "token.json thiếu/không refresh được. Chạy tay `python3 gsheet_auth.py` "
            "(có browser) để consent trước khi cron dùng."
        )

    if not os.path.exists(CLIENT_SECRET):
        raise FileNotFoundError(
            f"Thiếu {CLIENT_SECRET}. Tạo OAuth Desktop client trong Google Cloud "
            "Console, tải JSON về đổi tên thành client_secret.json đặt cạnh script."
        )

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
    # port=0: tự chọn cổng trống; mở browser trên MÁY NÀY (hoặc port-forward qua SSH/VSCode).
    creds = flow.run_local_server(port=0, prompt="consent")
    _save(creds)
    return creds


def _save(creds):
    with open(TOKEN, "w") as fh:
        fh.write(creds.to_json())
    os.chmod(TOKEN, 0o600)


def _check():
    from googleapiclient.discovery import build
    creds = get_credentials(interactive=False)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    from sheet_io import SPREADSHEET_ID
    meta = svc.spreadsheets().get(spreadsheetId=SPREADSHEET_ID,
                                  fields="properties.title,sheets.properties.title").execute()
    print("OK — mở được:", meta["properties"]["title"])
    print("Tabs:", ", ".join(s["properties"]["title"] for s in meta["sheets"]))


if __name__ == "__main__":
    if "--check" in sys.argv:
        _check()
    else:
        get_credentials(interactive=True)
        print(f"Đã lưu {TOKEN}. Cron/scripts giờ dùng được (tự refresh).")
