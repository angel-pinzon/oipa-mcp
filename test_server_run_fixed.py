"""
Fixed test script with correct InitializationOptions
"""
import asyncio
import traceback
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities

async def test_server_run_fixed():
    """Test server run method with correct initialization options"""
    print("=== Testing Server Run Method (Fixed) ===")
    
    try:
        # Step 1: Import and create server
        print("1. Importing server...")
        from src.oipa_mcp.server import OipaMCPServer
        
        print("2. Creating server instance...")
        server = OipaMCPServer()
        
        # Step 3: Test initialization separately
        print("3. Testing server initialization...")
        await server.initialize()
        print("   ✅ Server initialization successful")
        
        # Step 4: Test the corrected stdio_server with MCP server
        print("4. Testing stdio_server with MCP server run (FIXED)...")
        
        async with stdio_server() as (read_stream, write_stream):
            print("   ✅ stdio_server context created")
            
            # Create proper InitializationOptions with capabilities
            init_options = InitializationOptions(
                server_name="oipa-mcp",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={}  # Basic capabilities
                )
            )
            
            print("   Testing MCP server.run() for 2 seconds...")
            
            # Use timeout to avoid hanging
            try:
                await asyncio.wait_for(
                    server.server.run(read_stream, write_stream, init_options),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                print("   ✅ Server ran successfully (timeout expected)")
            except Exception as e:
                print(f"   ❌ Server run failed: {e}")
                traceback.print_exc()
                return False
        
        await server.cleanup()
        print("5. ✅ All tests completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing server run method with fixed InitializationOptions...\n")
    
    try:
        result = asyncio.run(test_server_run_fixed())
        if result:
            print("\n🎉 Server run test passed!")
            print("The TaskGroup issue is resolved!")
        else:
            print("\n⚠️  Server run test failed!")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
