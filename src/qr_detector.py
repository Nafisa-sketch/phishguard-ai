"""
qr_detector.py

Scans images found in an email (attachments or embedded images) for
QR codes. Attackers hide malicious links inside QR codes specifically
to bypass normal link/URL scanners -- the victim scans it with their
phone instead, which is usually unprotected by company security tools.

This module answers: "Does this email contain a QR code, and if so,
where does it actually point to?"

Uses OpenCV's built-in QR detector (no extra system libraries needed,
works reliably on Windows/Mac/Linux without separate DLL installs).
"""

import io
import numpy as np
import cv2
from PIL import Image


_qr_detector = cv2.QRCodeDetector()


def scan_images_for_qr(images: list) -> list:
    """
    Takes the list of images produced by parser.py (each a dict with
    'filename', 'content_type', 'data') and returns a list of findings,
    one per QR code detected.
    """
    findings = []

    for image_info in images:
        try:
            pil_img = Image.open(io.BytesIO(image_info["data"])).convert("RGB")
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception:
            # Not a readable image, skip it
            continue

        # detectAndDecodeMulti handles images with more than one QR code
        retval, decoded_texts, points, _ = _qr_detector.detectAndDecodeMulti(cv_img)

        if not retval:
            continue

        for text in decoded_texts:
            if not text:
                continue  # a QR-like shape was found but couldn't be decoded

            findings.append({
                "source_filename": image_info["filename"],
                "qr_content": text,
                "is_url": text.strip().lower().startswith(("http://", "https://")),
            })

    return findings


def build_qr_risk_signal(qr_findings: list, has_visible_links: bool) -> dict:
    """
    Turns raw QR findings into a risk signal the detector/explainer can use.
    """
    if not qr_findings:
        return {
            "qr_detected": False,
            "risk_note": None,
        }

    urls_found = [f["qr_content"] for f in qr_findings if f["is_url"]]

    note = (
        "This email contains a QR code. Attackers use QR codes to hide "
        "malicious links from normal email security scanners, moving the "
        "attack to your phone camera instead."
    )

    if not has_visible_links and urls_found:
        note += (
            " This email has no visible clickable link, only a QR code -- "
            "a common sign of this evasion technique."
        )

    return {
        "qr_detected": True,
        "qr_urls": urls_found,
        "risk_note": note,
    }


if __name__ == "__main__":
    # Quick manual test: generate a fake QR code pointing to a fake
    # phishing URL, then confirm our own detector catches it.
    import qrcode

    test_url = "http://fake-bank-login.example.com/verify"
    qr_img = qrcode.make(test_url)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")

    fake_email_images = [{
        "filename": "signature_logo.png",
        "content_type": "image/png",
        "data": buffer.getvalue(),
    }]

    results = scan_images_for_qr(fake_email_images)
    print("QR findings:", results)

    signal = build_qr_risk_signal(results, has_visible_links=False)
    print("Risk signal:", signal)
