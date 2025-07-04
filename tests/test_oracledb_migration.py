"""
Tests for Oracle database migration from cx_Oracle to oracledb

Tests the new oracledb connector functionality and migration aspects.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Test imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oipa_mcp.config import Config, DatabaseConfig
from oipa_mcp.connectors.database import OipaDatabase, OipaQueryBuilder


class TestOracleDBMigration:
    """Test oracledb library functionality"""
    
    def test_oracledb_import(self):
        """Test that oracledb library can be imported"""
        try:
            import oracledb
            assert hasattr(oracledb, 'create_pool_async')
            assert hasattr(oracledb, 'init_oracle_client')
            print(f"✅ oracledb version: {oracledb.version}")
        except ImportError:
            pytest.fail("oracledb library not available - run: pip install oracledb>=2.0.0")
    
    def test_database_config_dsn_format(self):
        """Test DSN format for oracledb"""
        db_config = DatabaseConfig(
            host="oipa-db.example.com",
            port=1521,
            service_name="OIPA",
            username="oipa_user",
            password="secure_password"
        )
        
        # Test DSN format
        assert db_config.dsn == "oipa-db.example.com:1521/OIPA"
        
        # Test connection string (should not include password in logs)
        conn_str = db_config.connection_string
        assert "oipa_user" in conn_str
        assert "oipa-db.example.com:1521/OIPA" in conn_str
    
    @pytest.mark.asyncio
    async def test_async_pool_creation(self):
        """Test async connection pool creation"""
        # Mock oracledb
        with patch('oracledb.create_pool_async') as mock_create_pool, \
             patch('oracledb.init_oracle_client') as mock_init_client:
            
            # Mock pool object
            mock_pool = AsyncMock()
            mock_pool.opened = 2
            mock_pool.busy = 1
            mock_pool.max = 10
            mock_pool.min = 2
            mock_pool.increment = 1
            mock_pool.timeout = 30
            mock_create_pool.return_value = mock_pool
            
            # Create database instance
            config = Config()
            config.database.host = "testhost"
            config.database.service_name = "TEST"
            config.database.username = "testuser"
            config.database.password = "testpass"
            
            db = OipaDatabase(config)
            
            # Initialize should create async pool
            await db.initialize()
            
            # Verify pool creation was called with correct parameters
            mock_create_pool.assert_called_once()
            call_args = mock_create_pool.call_args[1]  # keyword arguments
            assert call_args['user'] == 'testuser'
            assert call_args['password'] == 'testpass'
            assert call_args['dsn'] == 'testhost:1521/TEST'
            assert call_args['min'] == config.database.pool_min_size
            assert call_args['max'] == config.database.pool_max_size
            
            # Test pool status
            status = await db.get_pool_status()
            assert status['status'] == 'active'
            assert status['opened'] == 2
            assert status['busy'] == 1
            
            await db.close()


class TestAsyncDatabaseOperations:
    """Test async database operations with oracledb"""
    
    @pytest.fixture
    def mock_database(self):
        """Create mock database with async support"""
        config = Config()
        config.database.host = "mockhost"
        config.database.service_name = "MOCK"
        config.database.username = "mockuser"
        config.database.password = "mockpass"
        
        db = OipaDatabase(config)
        return db
    
    @pytest.mark.asyncio
    async def test_async_query_execution(self, mock_database):
        """Test async query execution"""
        # Mock the pool and connection
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_cursor = AsyncMock()
        
        # Setup cursor mock
        mock_cursor.description = [('POLICY_GUID', None), ('POLICY_NUMBER', None)]
        mock_cursor.fetchall.return_value = [
            ('6CCA0B15-EFAC-471F-A698-27949AB9B9C4', 'VG01-002-561-000001063'),
            ('7CCA0B15-EFAC-471F-A698-27949AB9B9C5', 'VG01-002-561-000001064')
        ]
        
        # Setup connection mock
        mock_connection.cursor.return_value = mock_cursor
        mock_pool.acquire.return_value = mock_connection
        
        # Setup database mock
        mock_database._pool = mock_pool
        mock_database._initialized = True
        
        # Execute query
        results = await mock_database.execute_query(
            "SELECT PolicyGUID, PolicyNumber FROM AsPolicy WHERE ROWNUM <= 2"
        )
        
        # Verify results
        assert len(results) == 2
        assert results[0]['policy_guid'] == '6CCA0B15-EFAC-471F-A698-27949AB9B9C4'
        assert results[0]['policy_number'] == 'VG01-002-561-000001063'
        assert results[1]['policy_guid'] == '7CCA0B15-EFAC-471F-A698-27949AB9B9C5'
        
        # Verify async operations were called
        mock_pool.acquire.assert_called_once()
        mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_pool.release.assert_called_once_with(mock_connection)
    
    @pytest.mark.asyncio
    async def test_async_scalar_query(self, mock_database):
        """Test async scalar query execution"""
        # Mock for scalar result
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_cursor = AsyncMock()
        
        mock_cursor.description = [('COUNT', None)]
        mock_cursor.fetchall.return_value = [(15847,)]
        
        mock_connection.cursor.return_value = mock_cursor
        mock_pool.acquire.return_value = mock_connection
        
        mock_database._pool = mock_pool
        mock_database._initialized = True
        
        # Execute scalar query
        result = await mock_database.execute_scalar("SELECT COUNT(*) FROM AsPolicy")
        
        # Verify scalar result
        assert result == 15847
    
    @pytest.mark.asyncio
    async def test_async_batch_operations(self, mock_database):
        """Test async batch operations"""
        # Mock for batch execution
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_cursor = AsyncMock()
        
        mock_connection.cursor.return_value = mock_cursor
        mock_pool.acquire.return_value = mock_connection
        
        mock_database._pool = mock_pool
        mock_database._initialized = True
        
        # Execute batch operation
        parameters_list = [
            {'policy_id': '1', 'status': 'active'},
            {'policy_id': '2', 'status': 'pending'},
            {'policy_id': '3', 'status': 'cancelled'}
        ]
        
        await mock_database.execute_many(
            "UPDATE AsPolicy SET StatusCode = :status WHERE PolicyGUID = :policy_id",
            parameters_list
        )
        
        # Verify batch execution
        mock_cursor.executemany.assert_called_once_with(
            "UPDATE AsPolicy SET StatusCode = :status WHERE PolicyGUID = :policy_id",
            parameters_list
        )
        mock_connection.commit.assert_called_once()


class TestEnhancedQueryBuilder:
    """Test enhanced query builder functionality"""
    
    def test_optimized_policy_search_query(self):
        """Test enhanced policy search query"""
        query, params = OipaQueryBuilder.search_policies(
            search_term="María García",
            status_filter="active",
            limit=10
        )
        
        # Verify query structure
        assert "UPPER(" in query  # Case-insensitive search
        assert "FETCH FIRST 10 ROWS ONLY" in query  # Modern Oracle syntax
        assert "ORDER BY p.UpdatedGmt DESC" in query  # Proper ordering
        
        # Verify parameters
        assert params['search_term'] == "%María García%"
        assert params['status_code'] == "01"  # Active status
    
    def test_enhanced_policy_details_query(self):
        """Test enhanced policy details query"""
        query, params = OipaQueryBuilder.get_policy_details(
            policy_number="VG01-002-561-000001063"
        )
        
        # Verify enhanced fields
        assert "pl.PlanDescription" in query  # Added plan description
        assert "LEFT JOIN AsPlan pl" in query  # Proper plan join
        assert "c.DateOfBirth" in query  # Client demographics
        
        # Verify parameters
        assert params['policy_number'] == "VG01-002-561-000001063"
    
    def test_client_search_query(self):
        """Test new client search functionality"""
        query, params = OipaQueryBuilder.search_clients(
            search_term="García",
            client_type="01",
            limit=25
        )
        
        # Verify client search structure
        assert "AsClient c" in query
        assert "UPPER(c.FirstName) LIKE UPPER(:search_term)" in query
        assert "c.TypeCode = :client_type" in query
        assert "FETCH FIRST 25 ROWS ONLY" in query
        
        # Verify parameters
        assert params['search_term'] == "%García%"
        assert params['client_type'] == "01"
    
    def test_enhanced_status_count_query(self):
        """Test enhanced status count with percentages"""
        query, params = OipaQueryBuilder.count_policies_by_status()
        
        # Verify percentage calculation
        assert "ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage" in query
        assert "GROUP BY p.StatusCode" in query
        assert "ORDER BY policy_count DESC" in query
    
    def test_client_portfolio_query(self):
        """Test client portfolio query"""
        client_guid = "12345678-1234-1234-1234-123456789012"
        query, params = OipaQueryBuilder.get_client_portfolio(client_guid)
        
        # Verify portfolio query structure
        assert "AsRole r" in query
        assert "JOIN AsPolicy p ON r.PolicyGUID = p.PolicyGUID" in query
        assert "LEFT JOIN AsPlan pl" in query  # Include plan information
        assert "r.ClientGUID = :client_guid" in query
        
        # Verify parameters
        assert params['client_guid'] == client_guid


class TestPerformanceImprovements:
    """Test performance improvements with oracledb"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_status_monitoring(self):
        """Test connection pool monitoring"""
        config = Config()
        config.database.host = "testhost"
        config.database.service_name = "TEST"
        config.database.username = "testuser"
        config.database.password = "testpass"
        
        db = OipaDatabase(config)
        
        # Test status when not initialized
        status = await db.get_pool_status()
        assert status['status'] == 'not_initialized'
        
        # Mock initialized pool
        mock_pool = AsyncMock()
        mock_pool.opened = 5
        mock_pool.busy = 2
        mock_pool.max = 10
        mock_pool.min = 2
        mock_pool.increment = 1
        mock_pool.timeout = 30
        
        db._pool = mock_pool
        
        # Test status when initialized
        status = await db.get_pool_status()
        assert status['status'] == 'active'
        assert status['opened'] == 5
        assert status['busy'] == 2
        assert status['max_size'] == 10
    
    @pytest.mark.asyncio
    async def test_enhanced_connection_test(self):
        """Test enhanced connection test with timing"""
        config = Config()
        db = OipaDatabase(config)
        
        # Mock successful connection test
        with patch.object(db, 'execute_scalar') as mock_execute:
            mock_execute.return_value = 1
            
            result = await db.test_connection()
            assert result is True
            mock_execute.assert_called_once_with("SELECT 1 FROM DUAL")
    
    def test_batch_size_configuration(self):
        """Test configurable batch sizes for performance"""
        config = Config()
        db = OipaDatabase(config)
        
        # Test that performance settings are accessible
        assert hasattr(config.performance, 'max_query_results')
        assert config.performance.max_query_results > 0


class TestErrorHandlingImprovements:
    """Test improved error handling with oracledb"""
    
    @pytest.mark.asyncio
    async def test_connection_retry_logic(self):
        """Test connection retry and error handling"""
        config = Config()
        db = OipaDatabase(config)
        
        with patch('oracledb.create_pool_async') as mock_create_pool:
            # Mock connection failure then success
            mock_create_pool.side_effect = [
                Exception("Connection failed"),
                Exception("Still failing")
            ]
            
            # Should raise exception after retries
            with pytest.raises(Exception):
                await db.initialize()
    
    @pytest.mark.asyncio
    async def test_graceful_pool_closure(self):
        """Test graceful connection pool closure"""
        config = Config()
        db = OipaDatabase(config)
        
        # Mock pool
        mock_pool = AsyncMock()
        db._pool = mock_pool
        db._initialized = True
        
        # Close should be graceful
        await db.close()
        
        mock_pool.close.assert_called_once()
        assert db._pool is None
        assert db._initialized is False
    
    @pytest.mark.asyncio
    async def test_query_error_handling(self, mock_database):
        """Test query error handling and logging"""
        # Mock database error
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_cursor = AsyncMock()
        
        # Setup error scenario
        import oracledb
        mock_cursor.execute.side_effect = oracledb.DatabaseError("ORA-00942: table or view does not exist")
        
        mock_connection.cursor.return_value = mock_cursor
        mock_pool.acquire.return_value = mock_connection
        
        mock_database._pool = mock_pool
        mock_database._initialized = True
        
        # Should raise database error
        with pytest.raises(oracledb.DatabaseError):
            await mock_database.execute_query("SELECT * FROM NonExistentTable")
        
        # Verify cleanup was called
        mock_cursor.close.assert_called_once()
        mock_pool.release.assert_called_once_with(mock_connection)


class TestBackwardCompatibility:
    """Test backward compatibility after migration"""
    
    def test_api_compatibility(self):
        """Test that public API remains compatible"""
        # Import should work the same way
        from oipa_mcp.connectors import oipa_db
        
        # Methods should exist
        assert hasattr(oipa_db, 'initialize')
        assert hasattr(oipa_db, 'execute_query')
        assert hasattr(oipa_db, 'execute_scalar')
        assert hasattr(oipa_db, 'test_connection')
        assert hasattr(oipa_db, 'close')
        
        # Query builder should be available
        assert hasattr(OipaQueryBuilder, 'search_policies')
        assert hasattr(OipaQueryBuilder, 'get_policy_details')
        assert hasattr(OipaQueryBuilder, 'count_policies_by_status')
    
    def test_configuration_compatibility(self):
        """Test that configuration remains compatible"""
        config = Config()
        
        # Database config should have same structure
        assert hasattr(config.database, 'host')
        assert hasattr(config.database, 'port')
        assert hasattr(config.database, 'service_name')
        assert hasattr(config.database, 'username')
        assert hasattr(config.database, 'password')
        assert hasattr(config.database, 'dsn')
        assert hasattr(config.database, 'connection_string')


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
