"""
Diagnostic script to identify initialization issues
"""
import sys
import traceback

def test_imports():
    """Test imports step by step to identify the problem"""
    print("=== Diagnostic Import Test ===")
    
    # Test 1: Basic mcp import
    try:
        print("1. Testing MCP import...")
        import mcp
        print("   ✅ MCP import successful")
    except Exception as e:
        print(f"   ❌ MCP import failed: {e}")
        return False
    
    # Test 2: MCP server import
    try:
        print("2. Testing MCP server import...")
        from mcp.server import Server
        print("   ✅ MCP Server import successful")
    except Exception as e:
        print(f"   ❌ MCP Server import failed: {e}")
        return False
    
    # Test 3: Config import (we know this triggers something)
    try:
        print("3. Testing config import...")
        print("   (This may show initialization logs)")
        from src.oipa_mcp.config import config
        print("   ✅ Config import successful")
    except Exception as e:
        print(f"   ❌ Config import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 4: Database connector import
    try:
        print("4. Testing database connector import...")
        from src.oipa_mcp.connectors import oipa_db
        print("   ✅ Database connector import successful")
    except Exception as e:
        print(f"   ❌ Database connector import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 5: Tools import (we know this triggers something)
    try:
        print("5. Testing tools import...")
        print("   (This may show initialization logs)")
        from src.oipa_mcp.tools import AVAILABLE_TOOLS
        print(f"   ✅ Tools import successful ({len(AVAILABLE_TOOLS)} tools)")
    except Exception as e:
        print(f"   ❌ Tools import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 6: Server class import (this is likely where the problem is)
    try:
        print("6. Testing server class import...")
        from src.oipa_mcp.server import OipaMCPServer
        print("   ✅ Server class import successful")
    except Exception as e:
        print(f"   ❌ Server class import failed: {e}")
        traceback.print_exc()
        return False
    
    print("\n=== All imports successful ===")
    return True

def test_server_creation():
    """Test server creation without running it"""
    print("\n=== Server Creation Test ===")
    try:
        from src.oipa_mcp.server import OipaMCPServer
        print("Creating server instance...")
        server = OipaMCPServer()
        print("✅ Server instance created successfully")
        print(f"   Server name: {server.server.name}")
        print(f"   Tools count: {len(server.tools)}")
        return True
    except Exception as e:
        print(f"❌ Server creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main diagnostic function"""
    print("Starting OIPA MCP Server diagnostics...\n")
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test server creation
        server_ok = test_server_creation()
        
        if server_ok:
            print("\n🎉 All basic tests passed!")
            print("The issue is likely in the server.run() method or stdio_server usage.")
        else:
            print("\n⚠️  Server creation failed")
    else:
        print("\n⚠️  Import tests failed")

if __name__ == "__main__":
    main()
