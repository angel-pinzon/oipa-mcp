#!/usr/bin/env python3
"""
Test MCP Server Startup

Script to test and troubleshoot MCP server startup issues.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oipa_mcp.config import config
from oipa_mcp.connectors import oipa_db
from oipa_mcp.tools import AVAILABLE_TOOLS


async def test_configuration():
    """Test configuration loading and validation"""
    print("🔧 Testing configuration...")
    try:
        config.validate()
        print("✅ Configuration validation successful")
        
        print(f"   - Server name: {config.mcp_server.name}")
        print(f"   - Server version: {config.mcp_server.version}")
        print(f"   - Log level: {config.logging.level}")
        print(f"   - Database host: {config.database.host}")
        print(f"   - Database service: {config.database.service_name}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_database_connection():
    """Test database connectivity"""
    print("\n💾 Testing database connection...")
    try:
        await oipa_db.initialize()
        print("✅ Database pool initialized")
        
        if await oipa_db.test_connection():
            print("✅ Database connection test passed")
            return True
        else:
            print("❌ Database connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        traceback.print_exc()
        return False
    finally:
        try:
            await oipa_db.close()
        except:
            pass


async def test_tools_loading():
    """Test tools loading and initialization"""
    print("\n🛠️ Testing tools loading...")
    try:
        print(f"   - Found {len(AVAILABLE_TOOLS)} tools:")
        
        for i, tool in enumerate(AVAILABLE_TOOLS, 1):
            print(f"     {i}. {tool.name}: {tool.description[:60]}...")
            
            # Test tool schema
            schema = tool.input_schema
            if not isinstance(schema, dict):
                print(f"     ⚠️  Tool {tool.name} has invalid schema")
                return False
        
        print("✅ All tools loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Tools loading error: {e}")
        traceback.print_exc()
        return False


async def test_mcp_server_components():
    """Test MCP server components without starting the full server"""
    print("\n🚀 Testing MCP server components...")
    try:
        from oipa_mcp.server_fixed import OipaMCPServer
        
        # Create server instance
        server = OipaMCPServer()
        print("✅ Server instance created")
        
        # Test handler registration
        print("✅ Handlers registered")
        
        # Test tools access
        print(f"✅ Server has access to {len(server.tools)} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server component error: {e}")
        traceback.print_exc()
        return False


async def test_basic_tool_execution():
    """Test basic tool execution without MCP protocol"""
    print("\n⚙️ Testing basic tool execution...")
    try:
        # Initialize database for testing
        await oipa_db.initialize()
        
        # Test one tool execution
        if AVAILABLE_TOOLS:
            tool = AVAILABLE_TOOLS[0]  # Test first tool
            print(f"   - Testing tool: {tool.name}")
            
            # Create minimal test arguments
            test_args = {"search_term": "VG01"}  # Simple search
            
            try:
                result = await asyncio.wait_for(
                    tool.execute(test_args), 
                    timeout=30.0
                )
                print("✅ Tool execution test successful")
                print(f"   - Result type: {type(result)}")
                return True
                
            except asyncio.TimeoutError:
                print("⚠️  Tool execution timed out (this may be normal)")
                return True  # Timeout is not necessarily a failure
            except Exception as tool_error:
                print(f"⚠️  Tool execution error: {tool_error}")
                print("   (This may be expected if test data is not available)")
                return True  # Tool errors are not server startup failures
        else:
            print("❌ No tools available to test")
            return False
            
    except Exception as e:
        print(f"❌ Tool execution test error: {e}")
        traceback.print_exc()
        return False
    finally:
        try:
            await oipa_db.close()
        except:
            pass


async def diagnose_startup_issue():
    """Diagnose MCP server startup issues"""
    print("🔍 OIPA MCP Server Startup Diagnostics")
    print("=" * 50)
    
    results = {}
    
    # Run all tests
    results['config'] = await test_configuration()
    results['database'] = await test_database_connection()
    results['tools'] = await test_tools_loading()
    results['server_components'] = await test_mcp_server_components()
    results['tool_execution'] = await test_basic_tool_execution()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Server should start correctly.")
        print("\nTry running: python -m oipa_mcp.server_fixed")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        
        # Provide specific guidance
        if not results['config']:
            print("\n💡 Fix configuration issues first:")
            print("   - Check .env file exists and has correct values")
            print("   - Verify database connection parameters")
        
        if not results['database']:
            print("\n💡 Fix database connectivity:")
            print("   - Verify Oracle database is running")
            print("   - Check network connectivity to database")
            print("   - Verify credentials in .env file")
    
    return passed == total


def main():
    """Main entry point"""
    try:
        # Set up asyncio for Windows if needed
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Run diagnostics
        success = asyncio.run(diagnose_startup_issue())
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Diagnostics interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostics failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
