# lay_email.py
import os
import base64
import re
import pandas as pd
from dateutil import parser
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def xac_thuc():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def lay_email_gmail(maxResults=50, save_csv=True):
    service = xac_thuc()
    results = service.users().messages().list(userId='me', maxResults=maxResults).execute()
    messages = results.get('messages', [])

    danh_sach_email = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()
        headers = msg_data['payload']['headers']

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender_raw = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date_raw = next((h['value'] for h in headers if h['name'] == 'Date'), '')

        # Lấy email từ trường From
        match = re.search(r'[\w\.-]+@[\w\.-]+', sender_raw)
        sender = match.group(0) if match else sender_raw

        # Chuẩn hoá thời gian
        try:
            dt = parser.parse(date_raw)
            vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
            date = dt.astimezone(vn_tz).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            date = date_raw

        # Lấy nội dung
        body = ''
        parts = msg_data['payload'].get('parts')
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode(errors="ignore")
                    break
        else:
            if 'data' in msg_data['payload']['body']:
                body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode(errors="ignore")

        body_sach = re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', body)).strip()

        danh_sach_email.append({
            'EmailNguoiGui': sender,
            'ThoiGianGui': date,
            'TieuDe': subject,
            'NoiDung': body_sach
        })

    if save_csv:
        df = pd.DataFrame(danh_sach_email)
        df.to_csv('email_gmail_sach.csv', index=False, encoding='utf-8')
        print(f"✅ Đã lưu {len(danh_sach_email)} email vào 'email_gmail_sach.csv'")

    return danh_sach_email
