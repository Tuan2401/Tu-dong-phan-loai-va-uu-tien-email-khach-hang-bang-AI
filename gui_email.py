# gui_email.py
import os
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# -----------------------------
# Cấu hình
# -----------------------------
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE = "token_send.json"
CREDENTIALS_FILE = "credentials.json"

# -----------------------------
# Lấy service Gmail
# -----------------------------
def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print("Lỗi refresh token:", e)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Lưu token mới
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

# -----------------------------
# Hàm gửi email
# -----------------------------
def send_email(to, subject, body_html, body_text=None):
    """
    to: email nhận
    subject: tiêu đề
    body_html: nội dung HTML
    body_text: fallback text (nếu None sẽ strip HTML)
    Trả về (success: bool, message: str)
    """
    try:
        service = get_gmail_service()

        # Chuẩn bị email Multipart
        message = MIMEMultipart("alternative")
        message['to'] = to
        message['subject'] = subject

        if body_text is None:
            import re
            body_text = re.sub(r'<[^>]+>', '', body_html)

        message.attach(MIMEText(body_text, 'plain', 'utf-8'))
        message.attach(MIMEText(body_html, 'html', 'utf-8'))

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        sent = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        return True, f"Đã gửi email đến {to} (ID: {sent['id']})"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    # Thử tạo Gmail service
    try:
        service = get_gmail_service()
        print("✅ Gmail service đã sẵn sàng. Token lưu ở:", TOKEN_FILE)

        # Thử gửi email test (thay bằng email của bạn)
        to = "email_cua_ban@gmail.com"
        subject = "Test Gmail API"
        body_html = "<h3>Đây là email test từ Gmail API</h3><p>Chúc bạn thành công!</p>"

        success, msg = send_email(to, subject, body_html)
        if success:
            print("✅", msg)
        else:
            print("❌ Lỗi gửi email:", msg)
    except Exception as e:
        print("❌ Lỗi khi tạo Gmail service:", e)

