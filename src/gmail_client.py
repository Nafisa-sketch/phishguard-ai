"""
gmail_client.py

Connects to a real Gmail inbox (read-only) and converts each fetched
message into the same dict format our parser.py produces, so it can
be fed straight into detector.analyze_email() -- no duplicate logic.

First run: opens a browser window asking you to log in and approve
read-only access. After that, a token.json file is saved so you don't
have to log in again every time.

Requires credentials.json (from Google Cloud Console) in this folder.
"""

import os
import base64
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only scope -- this script can never send, delete, or modify email,
# only read it. Worth keeping this narrow on purpose.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"


def get_gmail_service():
    """Authenticates (via browser popup on first run) and returns a Gmail API client."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} not found. Download it from Google Cloud "
                    f"Console (APIs & Services > Credentials) and place it in this folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


def fetch_recent_messages(service, max_results: int = 10) -> list:
    """Returns the most recent messages in the inbox (read or unread)."""
    results = service.users().messages().list(
        userId="me", maxResults=max_results, labelIds=["INBOX"]
    ).execute()
    return results.get("messages", [])


def gmail_message_to_parsed(service, message_id: str) -> dict:
    """
    Fetches one full message and converts it into the same dict shape
    parser.py produces: {sender, subject, body, links, images}.
    """
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = msg.get("payload", {})
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

    body = _extract_body(payload)
    images = _extract_images(service, message_id, payload)

    import re
    links = re.findall(r"https?://[^\s\"'<>]+", body) if body else []

    return {
        "sender": headers.get("from"),
        "subject": headers.get("subject"),
        "body": body,
        "links": links,
        "images": images,
    }


def _extract_body(payload: dict) -> str:
    """Walks the (possibly nested) MIME parts to find the plain-text body."""
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return _decode_base64url(payload["body"]["data"])

    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result

    # Fall back to HTML if no plain-text part exists
    if payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
        html = _decode_base64url(payload["body"]["data"])
        import re
        return re.sub(r"<[^>]+>", " ", html)

    return ""


def _extract_images(service, message_id: str, payload: dict) -> list:
    """Downloads any image attachments (needed for QR detection)."""
    images = []

    def walk(part):
        filename = part.get("filename", "")
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})

        if mime_type.startswith("image/") and filename:
            attachment_id = body.get("attachmentId")
            if attachment_id:
                attachment = service.users().messages().attachments().get(
                    userId="me", messageId=message_id, id=attachment_id
                ).execute()
                data = _decode_base64url(attachment["data"], as_bytes=True)
                images.append({"filename": filename, "content_type": mime_type, "data": data})

        for sub_part in part.get("parts", []):
            walk(sub_part)

    walk(payload)
    return images


def _decode_base64url(data: str, as_bytes: bool = False):
    decoded = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
    return decoded if as_bytes else decoded.decode("utf-8", errors="ignore")
