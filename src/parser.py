"""
parser.py

Takes a raw email (either a .eml file's contents, or plain pasted text)
and turns it into a simple, structured dictionary that the rest of the
pipeline can work with.
"""

import email
from email import policy
from email.parser import BytesParser, Parser
import re


def parse_eml_bytes(eml_bytes: bytes) -> dict:
    """Parse a real .eml file (uploaded email) into structured fields."""
    msg = BytesParser(policy=policy.default).parsebytes(eml_bytes)
    return _extract_fields(msg)


def parse_raw_text(raw_text: str) -> dict:
    """
    Parse plain pasted email text (not a real .eml file).
    Falls back to simple pattern matching for sender/subject if the
    text isn't a properly formatted email.
    """
    try:
        msg = Parser(policy=policy.default).parsestr(raw_text)
        fields = _extract_fields(msg)
        if fields["body"]:
            return fields
    except Exception:
        pass

    # Fallback: treat the whole thing as the body, try to guess sender/subject
    sender_match = re.search(r"[Ff]rom:\s*(.+)", raw_text)
    subject_match = re.search(r"[Ss]ubject:\s*(.+)", raw_text)

    return {
        "sender": sender_match.group(1).strip() if sender_match else None,
        "subject": subject_match.group(1).strip() if subject_match else None,
        "body": raw_text.strip(),
        "links": _extract_links(raw_text),
        "images": [],  # no real attachments possible from plain pasted text
    }


def _extract_fields(msg) -> dict:
    sender = msg.get("From")
    subject = msg.get("Subject")
    body = _get_body(msg)
    images = _get_images(msg)

    return {
        "sender": sender,
        "subject": subject,
        "body": body,
        "links": _extract_links(body),
        "images": images,
    }


def _get_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_content()
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return part.get_content()
        return ""
    else:
        return msg.get_content()


def _get_images(msg) -> list:
    """Pull out embedded/attached images as raw bytes, for the QR module."""
    images = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type.startswith("image/"):
                try:
                    images.append({
                        "filename": part.get_filename() or "unnamed_image",
                        "content_type": content_type,
                        "data": part.get_content(),
                    })
                except Exception:
                    continue
    return images


def _extract_links(text: str) -> list:
    if not text:
        return []
    url_pattern = r"https?://[^\s\"'<>]+"
    return re.findall(url_pattern, text)


if __name__ == "__main__":
    # Quick manual test
    sample = """From: ceo.company@gmail.com
Subject: Urgent wire transfer needed

Hi Sarah, please transfer $5,000 before 5 PM today.
Click here to confirm: http://fake-bank-login.com
"""
    result = parse_raw_text(sample)
    print(result)
