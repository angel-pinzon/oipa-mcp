"""
Test script for the fixed server version
"""
import asyncio
import traceback

async def test_fixed_server():
    """Test the fixed server version"""
    print("=== Testing Fixed Server Version ===")
    
    try:
        # Import the fixed server
        print("1. Importing fixed server...")
        from src.oipa_mcp.server import OipaMCPServer
        
        print("2. Creating server instance...")
        server = OipaMCPServer()
        
        print("3. Testing server initialization...")
        await server.initialize()
        print("   ✅ Server initialization successful")
        
        print("4. Testing cleanup...")
        await server.cleanup()
        print("   ✅ Server cleanup successful")
        
        print("5. ✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing fixed server version...\n")
    
    try:
        result = asyncio.run(test_fixed_server())
        if result:
            print("\n🎉 Fixed server test passed!")
            print("Ready to test full server run.")
        else:
            print("\n⚠️  Fixed server test failed!")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
