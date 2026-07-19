"""
test_features.py

Unit tests for src/features.py -- the rule-based signal extraction
functions. Run with:
    pytest tests/test_features.py -v
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import features


class TestUrgencyDetection:
    def test_detects_urgency_words(self):
        result = features.check_urgency("Please act immediately, this account will expire soon.")
        assert result["urgency_detected"] is True

    def test_no_urgency_in_normal_text(self):
        result = features.check_urgency("Hi, just wanted to check in about the project.")
        assert result["urgency_detected"] is False


class TestSenderDomain:
    def test_free_email_domain_flagged(self):
        result = features.check_sender_domain("ceo.company@gmail.com")
        assert result["domain_suspicious"] is True

    def test_corporate_domain_not_flagged(self):
        result = features.check_sender_domain("hr@company.com")
        assert result["domain_suspicious"] is False

    def test_claimed_org_mismatch(self):
        result = features.check_sender_domain("ceo@totallydifferent.com", claimed_org="mycompany")
        assert result["domain_suspicious"] is True

    def test_trusted_domain_skips_org_mismatch(self):
        result = features.check_sender_domain("no-reply@google.com", claimed_org="mycompany")
        assert result["domain_suspicious"] is False


class TestTyposquatting:
    def test_detects_lookalike_domain(self):
        result = features.check_typosquatting("security@amaz0n.com")
        assert result["typosquatting_detected"] is True
        assert result["impersonated_domain"] == "amazon.com"

    def test_legitimate_domain_not_flagged(self):
        result = features.check_typosquatting("security@amazon.com")
        assert result["typosquatting_detected"] is False

    def test_unrelated_domain_not_flagged(self):
        result = features.check_typosquatting("hello@myrandomsite.com")
        assert result["typosquatting_detected"] is False


class TestDisplayNameSpoofing:
    def test_detects_brand_mismatch(self):
        result = features.check_display_name_spoofing("PayPal Security <alerts@random-xyz.com>")
        assert result["display_name_spoofing_detected"] is True
        assert result["claimed_brand"] == "paypal"

    def test_legitimate_sender_not_flagged(self):
        result = features.check_display_name_spoofing("PayPal <service@paypal.com>")
        assert result["display_name_spoofing_detected"] is False


class TestAttachmentScanning:
    def test_flags_dangerous_extension(self):
        result = features.check_attachments([{"filename": "invoice.docm"}])
        assert result["dangerous_attachment_found"] is True

    def test_allows_safe_extension(self):
        result = features.check_attachments([{"filename": "invoice.pdf"}])
        assert result["dangerous_attachment_found"] is False


class TestReplyToMismatch:
    def test_detects_mismatch(self):
        headers = "From: ceo@realcompany.com\nReply-To: attacker@fake.com\n"
        result = features.check_reply_to_mismatch(headers)
        assert result["reply_to_mismatch_detected"] is True

    def test_no_mismatch_when_domains_match(self):
        headers = "From: ceo@company.com\nReply-To: assistant@company.com\n"
        result = features.check_reply_to_mismatch(headers)
        assert result["reply_to_mismatch_detected"] is False

    def test_no_headers_available(self):
        result = features.check_reply_to_mismatch("")
        assert result["checked"] is False


class TestDeviceCodePhishing:
    def test_detects_device_code_pattern(self):
        body = "Please go to https://microsoft.com/devicelogin and enter the code XYZ-789."
        result = features.check_device_code_phishing(body, ["https://microsoft.com/devicelogin"])
        assert result["device_code_phishing_detected"] is True

    def test_normal_email_not_flagged(self):
        body = "Hi, let's meet for coffee tomorrow."
        result = features.check_device_code_phishing(body, [])
        assert result["device_code_phishing_detected"] is False


class TestCallbackPhishing:
    def test_detects_phone_plus_callback_phrase(self):
        body = "Your account has been suspended. Please call us at 800-555-0199 immediately."
        result = features.check_callback_phishing(body)
        assert result["callback_detected"] is True

    def test_phone_number_alone_not_enough(self):
        body = "You can reach our office at 800-555-0199 during business hours."
        result = features.check_callback_phishing(body)
        assert result["callback_detected"] is False
