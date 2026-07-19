"""
test_detector.py

Unit tests for src/detector.py -- the combined risk-scoring and
classification logic. Run with:
    pytest tests/test_detector.py -v
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import detector


def make_email(sender="test@example.com", subject="Test", body="", links=None, images=None):
    return {
        "sender": sender,
        "subject": subject,
        "body": body,
        "links": links or [],
        "images": images or [],
    }


class TestWhalingDetection:
    def test_detects_whaling(self):
        email = make_email(
            sender="ceo.company@gmail.com",
            body="Hi Sarah, this is the CEO, please wire transfer $5,000 immediately.",
        )
        result = detector.analyze_email(email, claimed_org="company")
        assert result["attack_type"] == "Whaling (Executive Impersonation)"
        assert result["risk_score"] >= 70
        assert result["threat_level"] == "HIGH"


class TestBECDetection:
    def test_detects_bec(self):
        email = make_email(
            sender="ceo.company@gmail.com",
            body="As requested by the Finance Department, please wire transfer $5,000 immediately before 5 PM today.",
            links=["http://192.168.1.1/login"],
        )
        result = detector.analyze_email(email, claimed_org="company")
        assert result["attack_type"] == "Business Email Compromise (BEC)"


class TestDeviceCodePhishing:
    def test_detects_device_code_attack(self):
        email = make_email(
            body="Please go to https://microsoft.com/devicelogin and enter code XYZ-789 to authenticate this device.",
            links=["https://microsoft.com/devicelogin"],
        )
        result = detector.analyze_email(email)
        assert result["attack_type"] == "Device Code Phishing (OAuth Token Theft)"
        assert result["risk_score"] > 0


class TestFalsePositiveReduction:
    """These are the real false positives found during testing on a
    personal inbox -- regression tests to make sure they stay fixed."""

    def test_trusted_domain_login_email_not_flagged(self):
        email = make_email(
            sender="no-reply@mail.anthropic.com",
            body="Click here to log in. This link expires soon.",
            links=["https://claude.ai/login"],
        )
        result = detector.analyze_email(email)
        assert result["attack_type"] == "No Clear Threat Detected"
        assert result["risk_score"] <= 20

    def test_job_notification_not_flagged_as_spear_phishing(self):
        email = make_email(
            sender="jobs@noreply12.jobs2web.com",
            body="New management and engineering positions have been published on our career portal.",
        )
        result = detector.analyze_email(email)
        assert result["attack_type"] == "No Clear Threat Detected"


class TestTyposquattingClassification:
    def test_typosquat_domain_flagged(self):
        email = make_email(sender="security@amaz0n.com", body="Please verify your account.")
        result = detector.analyze_email(email)
        assert "Typosquatting" in result["attack_type"]


class TestNoFalseAlarmOnCleanEmail:
    def test_clean_email_scores_low(self):
        email = make_email(
            sender="colleague@company.com",
            body="Hi, just a reminder about tomorrow's meeting at 10am. See you there!",
        )
        result = detector.analyze_email(email)
        assert result["risk_score"] <= 20
        assert result["threat_level"] in ("MINIMAL", "LOW")


class TestExplanationGeneration:
    def test_explanation_is_nonempty_for_threats(self):
        email = make_email(
            sender="ceo.company@gmail.com",
            body="Hi Sarah, this is the CEO, please wire transfer $5,000 immediately.",
        )
        result = detector.analyze_email(email, claimed_org="company")
        explanation = detector.build_explanation(result)
        assert len(explanation) > 20
        assert "CEO" in explanation or "authority" in explanation.lower()

    def test_explanation_for_clean_email(self):
        email = make_email(body="Hi, how are you doing today?")
        result = detector.analyze_email(email)
        explanation = detector.build_explanation(result)
        assert len(explanation) > 0
