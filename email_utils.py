import os
import base64
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build




SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Absolute paths ensure Odoo and pytest can both locate these files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")


def gmail_service():
    print("BASE_DIR:", BASE_DIR)
    print("CREDENTIALS_PATH:", CREDENTIALS_PATH)

    creds = None
    
    # Try to load an existing token
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception:
            pass  # Token broken/expired, fall through to re-auth

    # If no token or token is invalid, run authorization flow
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"Missing credentials.json file. Please place your DESKTOP credentials file at: {CREDENTIALS_PATH}"
            )

        # Load the new Desktop App credentials file
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        
        # NOTE: flow.redirect_uri override is removed for Desktop App credentials.
        # Google handles the desktop loopback natively.
        
        creds = flow.run_local_server(
            host="localhost",
            port=5001,
            authorization_prompt_message="請登入 Gmail 授權",
            success_message="授權成功，可以關閉視窗",
            open_browser=True
        )
        
        # Save the valid token file so you only have to log in once
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
            
    return build("gmail", "v1", credentials=creds)

 
def gmail_send(message: dict):
    """
    Sends an email via the Gmail API.
    Expects a dictionary with 'raw' (base64 MIME) and optional 'threadId'.
    """
    service = gmail_service()

    body = {"raw": message["raw"]}
    if "threadId" in message:
        body["threadId"] = message["threadId"]

    send_result = service.users().messages().send(
        userId="me", body=body
    ).execute()

    print(f"Gmail API send result: {send_result['id']}")
    return send_result



def gmail_send_with_attachment(message: dict, attachment_path: str):
    """
    Sends an HTML email via Gmail API with a PDF attachment.
    message dict: { "to": ..., "subject": ..., "html": ... }
    attachment_path: local file path to PDF
    """
    service = gmail_service()

    # 建立 multipart message
    mime_msg = MIMEMultipart()
    mime_msg["to"] = message["to"]
    mime_msg["subject"] = message["subject"]

    # HTML body
    mime_msg.attach(MIMEText(message["html"], "html"))

    # PDF attachment
    with open(attachment_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment_path)}"')
        mime_msg.attach(part)

    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
    send_result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    print(f"Gmail API send result: {send_result['id']}")
    return send_result
