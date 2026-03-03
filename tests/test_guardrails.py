"""Tests for the guardrails module."""

import pytest
from src.guardrails import check_pii_columns, check_pii_in_question, check_malicious_input


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


class TestMaliciousInput:
    """Test malicious code injection detection."""
    
    def test_exec_injection(self):
        """Should block exec() attempts."""
        is_malicious, msg = check_malicious_input("What is exec('import os')?")
        assert is_malicious is True
        assert msg is not None
    
    def test_eval_injection(self):
        """Should block eval() attempts."""
        is_malicious, msg = check_malicious_input("Calculate eval(open('/etc/passwd').read())")
        assert is_malicious is True
    
    def test_import_injection(self):
        """Should block __import__ attempts."""
        is_malicious, msg = check_malicious_input("Use __import__('os').system('ls')")
        assert is_malicious is True
    
    def test_os_system_injection(self):
        """Should block os.system attempts."""
        is_malicious, msg = check_malicious_input("Run os.system('rm -rf /')")
        assert is_malicious is True
    
    def test_subprocess_injection(self):
        """Should block subprocess attempts."""
        is_malicious, msg = check_malicious_input("Execute using subprocess.call")
        assert is_malicious is True
    
    def test_sql_drop_injection(self):
        """Should block DROP TABLE attempts."""
        is_malicious, msg = check_malicious_input("DROP TABLE users")
        assert is_malicious is True
    
    def test_sql_delete_injection(self):
        """Should block DELETE FROM attempts."""
        is_malicious, msg = check_malicious_input("DELETE FROM subscriptions WHERE 1=1")
        assert is_malicious is True
    
    def test_sql_update_injection(self):
        """Should block UPDATE SET attempts."""
        is_malicious, msg = check_malicious_input("UPDATE users SET password='hacked'")
        assert is_malicious is True
    
    def test_network_requests_injection(self):
        """Should block requests library usage."""
        is_malicious, msg = check_malicious_input("Use requests.get to fetch data")
        assert is_malicious is True
    
    def test_file_operations_injection(self):
        """Should block file write attempts."""
        is_malicious, msg = check_malicious_input("Write this to a file using write()")
        assert is_malicious is True
    
    def test_safe_question(self):
        """Should allow safe data questions."""
        is_malicious, msg = check_malicious_input("How many active users do we have?")
        assert is_malicious is False
        assert msg is None
    
    def test_safe_aggregation(self):
        """Should allow safe aggregation queries."""
        is_malicious, msg = check_malicious_input("What is the total revenue from annual subscriptions?")
        assert is_malicious is False
    
    def test_excessive_length(self):
        """Should block excessively long questions."""
        long_question = "A" * 1500
        is_malicious, msg = check_malicious_input(long_question)
        assert is_malicious is True
        assert "too long" in msg.lower()
    
    def test_empty_question(self):
        """Should handle empty questions."""
        is_malicious, msg = check_malicious_input("")
        assert is_malicious is False
        assert msg is None
    
    def test_case_insensitive_detection(self):
        """Should detect malicious patterns case-insensitively."""
        is_malicious, msg = check_malicious_input("Show me EXEC('malicious code')")
        assert is_malicious is True
