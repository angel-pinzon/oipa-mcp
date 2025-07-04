"""
Test script for stdio_server functionality
"""
import asyncio
from mcp.server.stdio import stdio_server
import traceback

async def test_stdio_server():
    """Test stdio_server context manager"""
    print('Testing stdio_server import...')
    try:
        print('Creating stdio_server context...')
        async with stdio_server() as streams:
            print('stdio_server context manager works')
            print(f'Streams type: {type(streams)}')
            print(f'Number of streams: {len(streams)}')
            return True
    except Exception as e:
        print(f'stdio_server test failed: {e}')
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=== Testing stdio_server functionality ===")
    try:
        result = asyncio.run(test_stdio_server())
        print(f"Test result: {result}")
        if result:
            print("✅ stdio_server test PASSED")
        else:
            print("❌ stdio_server test FAILED")
    except Exception as e:
        print(f"Test execution failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
