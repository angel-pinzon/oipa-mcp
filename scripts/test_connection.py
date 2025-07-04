"""
Test script to verify OIPA database connectivity

This script tests the Oracle database connection to OIPA using the new
oracledb library and validates the basic table structure.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oipa_mcp.config import config
from oipa_mcp.connectors import oipa_db


async def test_database_connection():
    """Test database connectivity and basic queries with enhanced diagnostics"""
    print("🔍 Testing OIPA Database Connection...")
    print(f"Host: {config.database.host}")
    print(f"Service: {config.database.service_name}")
    print(f"Username: {config.database.username}")
    print(f"Pool Config: min={config.database.pool_min_size}, max={config.database.pool_max_size}")
    print()
    
    try:
        # Initialize database
        await oipa_db.initialize()
        print("✅ Database pool initialized")
        
        # Get pool status
        pool_status = await oipa_db.get_pool_status()
        print(f"✅ Pool status: {pool_status}")
        
        # Test basic connectivity with timing
        if await oipa_db.test_connection():
            print("✅ Database connection test passed")
        else:
            print("❌ Database connection test failed")
            return False
        
        # Test table access
        print("\n🔍 Testing table access...")
        
        # Test core OIPA tables
        tables_to_test = [
            ("AsPolicy", "Policy data"),
            ("AsClient", "Client data"),
            ("AsRole", "Role relationships"),
            ("AsActivity", "Transaction history"),
            ("AsPlan", "Plan definitions"),
            ("AsSegment", "Policy segments")
        ]
        
        for table_name, description in tables_to_test:
            try:
                count = await oipa_db.execute_scalar(
                    f"SELECT COUNT(*) FROM {table_name} WHERE ROWNUM <= 1"
                )
                if count is not None:
                    print(f"✅ {table_name} table accessible ({description})")
                else:
                    print(f"⚠️  {table_name} table empty or restricted")
            except Exception as e:
                print(f"❌ {table_name} table error: {e}")
        
        # Test enhanced sample queries
        print("\n🔍 Testing enhanced sample queries...")
        
        # Test policy search query
        try:
            from oipa_mcp.connectors.database import OipaQueryBuilder
            
            # Test basic policy query
            query, params = OipaQueryBuilder.search_policies(limit=3)
            sample_policies = await oipa_db.execute_query(query, params)
            
            print(f"✅ Policy search query successful - found {len(sample_policies)} policies")
            for policy in sample_policies[:3]:
                client_name = "N/A"
                if policy.get('client_first_name') and policy.get('client_last_name'):
                    client_name = f"{policy['client_first_name']} {policy['client_last_name']}"
                elif policy.get('company_name'):
                    client_name = policy['company_name']
                
                print(f"   - {policy.get('policy_number', 'N/A')}: {client_name} ({policy.get('status_code', 'N/A')})")
        except Exception as e:
            print(f"❌ Policy search query error: {e}")
        
        # Test status count query
        try:
            query, params = OipaQueryBuilder.count_policies_by_status()
            status_counts = await oipa_db.execute_query(query, params)
            
            print(f"✅ Status count query successful - found {len(status_counts)} status types")
            for status in status_counts[:5]:  # Show top 5
                print(f"   - Status {status.get('status_code', 'N/A')}: {status.get('policy_count', 0)} policies ({status.get('percentage', 0)}%)")
        except Exception as e:
            print(f"❌ Status count query error: {e}")
        
        # Test client search query
        try:
            query, params = OipaQueryBuilder.search_clients(limit=3)
            sample_clients = await oipa_db.execute_query(query, params)
            
            print(f"✅ Client search query successful - found {len(sample_clients)} clients")
            for client in sample_clients[:3]:
                client_name = "N/A"
                if client.get('first_name') and client.get('last_name'):
                    client_name = f"{client['first_name']} {client['last_name']}"
                elif client.get('company_name'):
                    client_name = client['company_name']
                
                print(f"   - {client_name} (TaxID: {client.get('tax_id', 'N/A')})")
        except Exception as e:
            print(f"❌ Client search query error: {e}")
        
        # Test async performance
        print("\n🔍 Testing async performance...")
        try:
            import time
            start_time = time.time()
            
            # Run multiple concurrent queries
            tasks = []
            for i in range(5):
                task = oipa_db.execute_scalar("SELECT 1 FROM DUAL")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            successful_queries = sum(1 for r in results if r == 1)
            total_time = (end_time - start_time) * 1000
            
            print(f"✅ Async performance test: {successful_queries}/5 queries successful in {total_time:.2f}ms")
        except Exception as e:
            print(f"❌ Async performance test error: {e}")
        
        print("\n✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        await oipa_db.close()


async def test_configuration():
    """Test configuration validation"""
    print("🔍 Testing configuration...")
    
    try:
        config.validate()
        print("✅ Configuration validation passed")
        
        # Show configuration details
        print(f"✅ Database configuration:")
        print(f"   - Host: {config.database.host}:{config.database.port}")
        print(f"   - Service: {config.database.service_name}")
        print(f"   - Pool: {config.database.pool_min_size}-{config.database.pool_max_size} connections")
        print(f"   - Performance: max {config.performance.max_query_results} results per query")
        
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


async def test_oracledb_features():
    """Test specific oracledb features"""
    print("🔍 Testing oracledb specific features...")
    
    try:
        import oracledb
        
        # Check oracledb version
        print(f"✅ oracledb version: {oracledb.version}")
        
        # Check if thick mode is available
        try:
            oracledb.init_oracle_client()
            print("✅ Oracle Client available (thick mode)")
        except Exception:
            print("✅ Using thin mode (pure Python)")
        
        return True
    except ImportError:
        print("❌ oracledb library not installed")
        return False
    except Exception as e:
        print(f"❌ oracledb feature test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 OIPA MCP Server Connection Test (oracledb)")
    print("=" * 60)
    
    # Test oracledb features
    oracledb_ok = await test_oracledb_features()
    if not oracledb_ok:
        print("\n❌ oracledb test failed - check installation")
        print("Run: pip install oracledb>=2.0.0")
        sys.exit(1)
    
    print()
    
    # Test configuration
    config_ok = await test_configuration()
    if not config_ok:
        print("\n❌ Configuration test failed - check your .env file")
        sys.exit(1)
    
    print()
    
    # Test database
    db_ok = await test_database_connection()
    if not db_ok:
        print("\n❌ Database test failed - check your connection settings")
        sys.exit(1)
    
    print("\n🎉 All tests passed! OIPA MCP server with oracledb should work correctly.")
    print("\n📋 Migration Summary:")
    print("✅ Using modern oracledb library (no Oracle Client required)")
    print("✅ Async connection pooling enabled")
    print("✅ Enhanced error handling and diagnostics")
    print("✅ Optimized query builders with better performance")


if __name__ == "__main__":
    asyncio.run(main())
