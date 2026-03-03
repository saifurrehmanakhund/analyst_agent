"""Tests for the output formatter module."""

import pytest
from src.output.formatter import (
    format_result_for_slack,
    format_error_message,
    _truncate_message,
    _format_data_structure,
)


class TestFormatResult:
    """Test result formatting for Slack."""
    
    def test_format_string_result(self):
        """Should return string results as-is."""
        result = "There are 150 active users"
        formatted = format_result_for_slack(result)
        assert formatted == result
    
    def test_format_empty_string(self):
        """Should handle empty strings."""
        result = ""
        formatted = format_result_for_slack(result)
        assert isinstance(formatted, str)
    
    def test_format_long_string(self):
        """Should truncate long messages."""
        result = "x" * 4000
        formatted = format_result_for_slack(result)
        assert len(formatted) <= 3100
        assert "truncated" in formatted.lower()
    
    def test_format_list_result(self):
        """Should format lists with bullets."""
        result = ["item1", "item2", "item3"]
        formatted = format_result_for_slack(result)
        assert "•" in formatted
        assert "item1" in formatted
    
    def test_format_dict_result(self):
        """Should format dicts key-value pairs."""
        result = {"name": "John", "age": 30, "status": "active"}
        formatted = format_result_for_slack(result)
        assert "name" in formatted
        assert "John" in formatted
    
    def test_format_empty_list(self):
        """Should handle empty lists."""
        result = []
        formatted = format_result_for_slack(result)
        assert "No results" in formatted
    
    def test_format_large_list(self):
        """Should truncate large lists to 20 items."""
        result = [f"item_{i}" for i in range(50)]
        formatted = format_result_for_slack(result)
        assert "item_0" in formatted
        assert "Showing first 20" in formatted or "Showing first 20" in formatted.lower()


class TestTruncateMessage:
    """Test message truncation."""
    
    def test_short_message_not_truncated(self):
        """Should not truncate short messages."""
        msg = "Short message"
        truncated = _truncate_message(msg)
        assert truncated == msg
    
    def test_long_message_truncated(self):
        """Should truncate messages longer than limit."""
        msg = "x" * 3500
        truncated = _truncate_message(msg, max_length=3000)
        assert len(truncated) <= 3000
        assert "truncated" in truncated.lower()
    
    def test_custom_max_length(self):
        """Should respect custom max_length."""
        msg = "x" * 1000
        truncated = _truncate_message(msg, max_length=500)
        assert len(truncated) <= 550  # 500 + 50 for the message


class TestFormatDataStructure:
    """Test data structure formatting."""
    
    def test_format_dict_items(self):
        """Should format dict items."""
        data = {"key1": "value1", "key2": "value2"}
        formatted = _format_data_structure(data)
        assert "key1" in formatted
        assert "value1" in formatted
    
    def test_format_list_items(self):
        """Should format list items with bullets."""
        data = ["first", "second", "third"]
        formatted = _format_data_structure(data)
        assert "•" in formatted
        assert "first" in formatted


class TestErrorFormatting:
    """Test error message formatting."""
    
    def test_string_error(self):
        """Should format string errors."""
        error = "Something went wrong"
        formatted = format_error_message(error)
        assert "❌" in formatted
        assert "Something went wrong" in formatted
    
    def test_database_error(self):
        """Should map database errors to user-friendly message."""
        error = Exception("database connection refused")
        formatted = format_error_message(error)
        assert "Unable to connect to the database" in formatted
    
    def test_timeout_error(self):
        """Should map timeout errors."""
        error = Exception("Query timeout after 30 seconds")
        formatted = format_error_message(error)
        assert "timed out" in formatted.lower()
    
    def test_connection_error(self):
        """Should map connection errors."""
        error = Exception("Connection refused")
        formatted = format_error_message(error)
        assert "Unable to connect" in formatted or "database" in formatted.lower()
    
    def test_generic_error(self):
        """Should provide generic message for unknown errors."""
        error = Exception("Some random error that shouldn't leak")
        formatted = format_error_message(error)
        assert "Something went wrong" in formatted or "error occurred" in formatted.lower()
        assert "Some random error" not in formatted
