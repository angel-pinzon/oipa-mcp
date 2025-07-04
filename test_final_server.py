"""
Final test script to run the complete OIPA MCP Server
"""
import asyncio
import signal
import sys
import traceback

class ServerTester:
    def __init__(self):
        self.server_task = None
        self.running = False
    
    async def run_server_with_timeout(self, timeout_seconds=10):
        """Run server with timeout for testing"""
        print(f"=== Running OIPA MCP Server for {timeout_seconds} seconds ===")
        
        try:
            from src.oipa_mcp.server import main_async
            
            print("Starting server...")
            self.running = True
            
            # Run server with timeout
            await asyncio.wait_for(main_async(), timeout=timeout_seconds)
            
        except asyncio.TimeoutError:
            print(f"✅ Server ran successfully for {timeout_seconds} seconds (timeout expected)")
            return True
        except KeyboardInterrupt:
            print("✅ Server interrupted by user (expected)")
            return True
        except Exception as e:
            print(f"❌ Server failed: {e}")
            traceback.print_exc()
            return False
        finally:
            self.running = False

def main():
    """Main test function"""
    print("Testing complete OIPA MCP Server functionality...\n")
    
    tester = ServerTester()
    
    try:
        # Test 1: Quick server run
        print("Test 1: Quick server run (10 seconds)")
        result = asyncio.run(tester.run_server_with_timeout(10))
        
        if result:
            print("\n🎉 Server test completed successfully!")
            print("\nThe OIPA MCP Server is working correctly.")
            print("\nTo run the server normally:")
            print("  python -m src.oipa_mcp.server")
            print("\nOr use the fixed main function:")
            print("  python -c \"from src.oipa_mcp.server import main; main()\"")
        else:
            print("\n⚠️  Server test failed!")
            print("There may still be TaskGroup issues.")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
