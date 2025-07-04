"""
Test script to identify the TaskGroup issue in server.run()
"""
import asyncio
import traceback
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions

async def test_server_run_step_by_step():
    """Test server run method step by step"""
    print("=== Testing Server Run Method ===")
    
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
        
        # Step 4: Test the problematic part - stdio_server with MCP server
        print("4. Testing stdio_server with MCP server run...")
        
        # This is likely where the TaskGroup issue occurs
        async with stdio_server() as (read_stream, write_stream):
            print("   ✅ stdio_server context created")
            
            # Try to run the server for a very short time
            print("   Testing MCP server.run() for 2 seconds...")
            
            # Use timeout to avoid hanging
            try:
                await asyncio.wait_for(
                    server.server.run(
                        read_stream, 
                        write_stream, 
                        InitializationOptions(
                            server_name="oipa-mcp",
                            server_version="1.0.0"
                        )
                    ),
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
    print("Testing server run method to identify TaskGroup issue...\n")
    
    try:
        result = asyncio.run(test_server_run_step_by_step())
        if result:
            print("\n🎉 Server run test passed!")
            print("The TaskGroup issue might be in a different area.")
        else:
            print("\n⚠️  Server run test failed - TaskGroup issue identified!")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
