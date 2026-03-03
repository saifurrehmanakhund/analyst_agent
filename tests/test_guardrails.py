"""Tests for the guardrails module."""

import pytest
from src.guardrails import check_pii_columns, check_pii_in_question


class TestPIIColumns:
    """Test PII column detection."""
    
    def test_detect_email_column(self):
        """Should detect email columns."""
        columns = ["user_id", "email", "name"]
        pii_cols = check_pii_columns(columns)
        assert "email" in pii_cols
        assert len(pii_cols) == 1
    
    def test_detect_phone_column(self):
        """Should detect phone columns."""
        columns = ["user_id", "phone_number", "address"]
        pii_cols = check_pii_columns(columns)
        assert "phone_number" in pii_cols
    
    def test_detect_ssn_column(self):
        """Should detect SSN columns."""
        columns = ["user_id", "ssn", "name"]
        pii_cols = check_pii_columns(columns)
        assert "ssn" in pii_cols
    
    def test_detect_multiple_pii_columns(self):
        """Should detect multiple PII columns."""
        columns = ["user_id", "email", "phone_number", "ssn"]
        pii_cols = check_pii_columns(columns)
        assert len(pii_cols) == 3
        assert "email" in pii_cols
        assert "phone_number" in pii_cols
        assert "ssn" in pii_cols
    
    def test_no_pii_columns(self):
        """Should return empty list if no PII columns."""
        columns = ["user_id", "name", "subscription_status"]
        pii_cols = check_pii_columns(columns)
        assert len(pii_cols) == 0
    
    def test_case_insensitive(self):
        """Should detect PII columns case-insensitively."""
        columns = ["user_id", "EMAIL", "Phone"]
        pii_cols = check_pii_columns(columns)
        assert "EMAIL" in pii_cols
        assert "Phone" in pii_cols


class TestPIIInQuestion:
    """Test PII detection in user questions."""
    
    def test_explicit_email_request(self):
        """Should block email requests."""
        has_pii, msg = check_pii_in_question("Show me all user emails")
        assert has_pii is True
        assert msg is not None
        assert "personal information" in msg.lower()
    
    def test_explicit_phone_request(self):
        """Should block phone requests."""
        has_pii, msg = check_pii_in_question("Get all phone numbers")
        assert has_pii is True
    
    def test_ssn_request(self):
        """Should block SSN requests."""
        has_pii, msg = check_pii_in_question("What are the SSN values?")
        assert has_pii is True
    
    def test_safe_question(self):
        """Should allow safe questions."""
        has_pii, msg = check_pii_in_question("How many active annual subscriptions do we have?")
        assert has_pii is False
        assert msg is None
    
    def test_export_email_request(self):
        """Should block export of email data."""
        has_pii, msg = check_pii_in_question("Export all user emails to CSV")
        assert has_pii is True
    
    def test_empty_question(self):
        """Should handle empty questions."""
        has_pii, msg = check_pii_in_question("")
        assert has_pii is False
        assert msg is None
    
    def test_case_insensitive_pii_detection(self):
        """Should detect PII case-insensitively."""
        has_pii, msg = check_pii_in_question("Show me all EMAIL addresses")
        assert has_pii is True
    
    def test_dob_request(self):
        """Should block date of birth requests."""
        has_pii, msg = check_pii_in_question("What are the date of birth values?")
        assert has_pii is True
    
    def test_credit_card_request(self):
        """Should block credit card requests."""
        has_pii, msg = check_pii_in_question("Show credit card numbers")
        assert has_pii is True
