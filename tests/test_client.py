"""Tests for the query client module."""

import pytest
from src.engine.client import QueryClient


class TestQueryClient:
    """Test the QueryClient class."""
    
    @pytest.fixture
    def mock_query_func(self):
        """Create a mock query function."""
        def query(question):
            if "error" in question.lower():
                raise Exception("Database error")
            if "timeout" in question.lower():
                raise TimeoutError("Query timed out")
            if "permission" in question.lower():
                raise PermissionError("Access denied")
            return f"Result for: {question}"
        
        return query
    
    @pytest.fixture
    def client(self, mock_query_func):
        """Create a QueryClient instance."""
        return QueryClient(mock_query_func, timeout_seconds=30)
    
    def test_successful_query(self, client):
        """Should execute successful queries."""
        result = client.query("How many users exist?")
        assert result['success'] is True
        assert result['error'] is None
        assert "users" in result['result']
    
    def test_empty_question(self, client):
        """Should reject empty questions."""
        result = client.query("")
        assert result['success'] is False
        assert result['error'] is not None
    
    def test_whitespace_only_question(self, client):
        """Should reject whitespace-only questions."""
        result = client.query("   ")
        assert result['success'] is False
    
    def test_timeout_error(self, client):
        """Should handle timeout errors gracefully."""
        result = client.query("This will timeout")
        assert result['success'] is False
        assert "timed out" in result['error'].lower()
    
    def test_permission_error(self, client):
        """Should handle permission errors."""
        result = client.query("This has permission issues")
        assert result['success'] is False
        assert "permission" in result['error'].lower()
    
    def test_generic_error_database(self, client):
        """Should handle generic database errors."""
        result = client.query("This will cause an error")
        assert result['success'] is False
        assert "error occurred" in result['error'].lower() or "Unable" in result['error']
    
    def test_result_structure(self, client):
        """Should return consistent result structure."""
        result = client.query("What is the data?")
        assert 'success' in result
        assert 'result' in result
        assert 'error' in result
        assert isinstance(result['success'], bool)
    
    def test_none_error_on_success(self, client):
        """Should have None error on successful queries."""
        result = client.query("How many active subscriptions?")
        assert result['error'] is None
    
    def test_none_result_on_failure(self, client):
        """Should have None result on failed queries."""
        result = client.query("This will cause an error")
        assert result['result'] is None
