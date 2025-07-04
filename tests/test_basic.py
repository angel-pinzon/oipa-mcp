"""
Basic unit tests for OIPA MCP Server

Tests core functionality including tools, connectors, and configuration.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Test imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oipa_mcp.config import Config, DatabaseConfig
from oipa_mcp.tools.policy_tools import SearchPoliciesQuality, GetPolicyDetailsTotal, PolicyCountsByStatusSmall


class TestConfiguration:
    """Test configuration management"""
    
    def test_database_config_creation(self):
        """Test database configuration"""
        db_config = DatabaseConfig(
            host="testhost",
            port=1521,
            service_name="TEST",
            username="testuser",
            password="testpass"
        )
        
        assert db_config.host == "testhost"
        assert db_config.port == 1521
        assert db_config.dsn == "testhost:1521/TEST"
        assert "testuser/testpass@testhost:1521/TEST" in db_config.connection_string
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = Config()
        
        # Should fail with empty credentials
        with pytest.raises(ValueError):
            config.validate()


class TestPolicyTools:
    """Test policy management tools"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database for testing"""
        mock_db = AsyncMock()
        mock_db.test_connection.return_value = True
        return mock_db
    
    @pytest.fixture
    def search_tool(self, mock_db):
        """Create search tool with mocked database"""
        tool = SearchPoliciesQuality()
        tool.db = mock_db
        return tool
    
    @pytest.fixture
    def sample_policy_data(self):
        """Sample policy data for testing"""
        return [
            {
                "policy_guid": "6CCA0B15-EFAC-471F-A698-27949AB9B9C4",
                "policy_number": "VG01-002-561-000001063",
                "policy_name": "Seguro de Vida Individual",
                "status_code": "01",
                "plan_date": datetime(2023, 1, 15),
                "updated_date": datetime(2023, 6, 1, 10, 30),
                "client_guid": "12345678-1234-1234-1234-123456789012",
                "client_first_name": "María",
                "client_last_name": "García",
                "company_name": None,
                "tax_id": "GARM850101ABC"
            }
        ]
    
    def test_search_tool_properties(self, search_tool):
        """Test search tool basic properties"""
        assert search_tool.name == "oipa_search_policies"
        assert "Search insurance policies" in search_tool.description
        assert "search_term" in search_tool.input_schema["properties"]
    
    @pytest.mark.asyncio
    async def test_search_policies_execution(self, search_tool, sample_policy_data):
        """Test policy search execution"""
        # Mock database response
        search_tool.db.execute_query.return_value = sample_policy_data
        
        # Execute search
        result = await search_tool._execute_impl({
            "search_term": "María García",
            "status": "active",
            "limit": 20
        })
        
        # Verify results
        assert len(result) == 1
        assert result[0]["policy_number"] == "VG01-002-561-000001063"
        assert result[0]["client"]["name"] == "María García"
        assert result[0]["status"] == "Active"
    
    @pytest.mark.asyncio
    async def test_search_policies_empty_result(self, search_tool):
        """Test search with no results"""
        # Mock empty database response
        search_tool.db.execute_query.return_value = []
        
        # Execute search
        result = await search_tool._execute_impl({
            "search_term": "NonexistentPolicy",
            "status": "all",
            "limit": 20
        })
        
        # Verify empty results
        assert len(result) == 0
    
    def test_policy_details_tool(self):
        """Test policy details tool properties"""
        tool = GetPolicyDetailsTotal()
        
        assert tool.name == "oipa_get_policy_details"
        assert "comprehensive details" in tool.description.lower()
        
        # Test schema validation
        schema = tool.input_schema
        assert "oneOf" in schema  # Should allow either policy_guid or policy_number
    
    def test_policy_counts_tool(self):
        """Test policy counts tool properties"""
        tool = PolicyCountsByStatusSmall()
        
        assert tool.name == "oipa_policy_counts_by_status"
        assert "count of policies" in tool.description.lower()


class TestToolIntegration:
    """Integration tests for tools"""
    
    @pytest.fixture
    def mock_query_results(self):
        """Mock query results for integration testing"""
        return [
            {"status_code": "01", "policy_count": 15000},
            {"status_code": "08", "policy_count": 1200},
            {"status_code": "99", "policy_count": 800}
        ]
    
    @pytest.mark.asyncio
    async def test_policy_counts_integration(self, mock_query_results):
        """Test policy counts with realistic data"""
        tool = PolicyCountsByStatusSmall()
        tool.db = AsyncMock()
        tool.db.test_connection.return_value = True
        tool.db.execute_query.return_value = mock_query_results
        
        # Execute tool
        result = await tool.execute({})
        
        # Verify response structure
        assert result["success"] is True
        assert "data" in result
        assert "total_policies" in result["data"]
        assert result["data"]["total_policies"] == 17000
        
        # Verify status breakdown
        breakdown = result["data"]["status_breakdown"]
        assert "Active" in breakdown
        assert breakdown["Active"]["count"] == 15000
        assert breakdown["Active"]["percentage"] == 88.24  # 15000/17000 * 100


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Test handling of database connection errors"""
        tool = SearchPoliciesQuality()
        tool.db = AsyncMock()
        tool.db.test_connection.return_value = False
        
        # Should raise DatabaseToolError
        from oipa_mcp.tools.base import DatabaseToolError
        with pytest.raises(DatabaseToolError):
            await tool._ensure_db_connection()
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """Test handling of invalid tool inputs"""
        tool = SearchPoliciesQuality()
        tool.db = AsyncMock()
        tool.db.test_connection.return_value = True
        
        # Test with missing required field
        try:
            result = await tool.execute({})  # Missing search_term
            # Tool should handle gracefully or raise ValidationToolError
            assert "error" in result or "success" in result
        except Exception as e:
            # Should be a ValidationToolError or similar
            assert "validation" in str(e).lower() or "required" in str(e).lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
