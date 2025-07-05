#!/usr/bin/env python3
"""
Quick test script to verify schema configuration is working
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oipa_mcp.config import config
from oipa_mcp.connectors import oipa_db

async def test_schema_config():
    """Test that schema configuration is working"""
    print("🔍 Testing Schema Configuration...")
    
    # Show current configuration
    print(f"📋 Default schema configured: {config.database.default_schema}")
    
    if not config.database.default_schema:
        print("⚠️  No default schema configured - this might cause table access issues")
        return False
    
    try:
        # Initialize database
        await oipa_db.initialize()
        print("✅ Database pool initialized with schema support")
        
        # Test schema information
        async with oipa_db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Check current schema
                await cursor.execute("SELECT USER, SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
                result = await cursor.fetchone()
                if result:
                    current_user = result[0]
                    current_schema = result[1]
                    print(f"✅ Connected as user: {current_user}")
                    print(f"✅ Current schema: {current_schema}")
                    
                    if current_schema == config.database.default_schema:
                        print(f"✅ Schema correctly set to: {config.database.default_schema}")
                    else:
                        print(f"⚠️  Expected schema: {config.database.default_schema}, got: {current_schema}")
                
                # Test table access
                print("\n🔍 Testing table access with schema...")
                await cursor.execute("SELECT COUNT(*) FROM AsPolicy WHERE ROWNUM <= 1")
                count = await cursor.fetchone()
                if count:
                    print(f"✅ AsPolicy table accessible (found {count[0]} record check)")
                else:
                    print("⚠️  AsPolicy table returned no results")
                
            except Exception as e:
                print(f"❌ Schema test error: {e}")
                return False
            finally:
                cursor.close()
        
        print("\n✅ Schema configuration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema configuration test failed: {e}")
        return False
    finally:
        await oipa_db.close()


async def main():
    """Main test function"""
    print("🚀 OIPA MCP Server Schema Test")
    print("=" * 40)
    
    success = await test_schema_config()
    
    if success:
        print("\n🎉 Schema configuration is working correctly!")
        print("You can now run the full test: python scripts/test_connection.py")
    else:
        print("\n❌ Schema configuration test failed!")
        print("Check your .env file and ensure OIPA_DB_DEFAULT_SCHEMA is set correctly")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
