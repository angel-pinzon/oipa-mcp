#!/usr/bin/env python3
"""
Simple test to verify MCP installation and basic functionality
"""

import sys
import traceback

def test_imports():
    """Test basic imports"""
    print("=== Testing Basic Imports ===")
    
    try:
        import mcp
        print(f"✓ mcp imported successfully")
        if hasattr(mcp, '__version__'):
            print(f"  Version: {mcp.__version__}")
        else:
            print("  Version: unknown")
    except Exception as e:
        print(f"✗ Failed to import mcp: {e}")
        return False
    
    try:
        from mcp.server import Server
        print("✓ mcp.server.Server imported")
    except Exception as e:
        print(f"✗ Failed to import Server: {e}")
        return False
    
    try:
        from mcp.server.stdio import stdio_server
        print("✓ mcp.server.stdio imported")
    except Exception as e:
        print(f"✗ Failed to import stdio_server: {e}")
        return False
    
    try:
        from mcp.types import Tool as MCPTool
        print("✓ mcp.types.Tool imported")
    except Exception as e:
        print(f"✗ Failed to import Tool: {e}")
        return False
    
    try:
        import oracledb
        print(f"✓ oracledb imported - version: {oracledb.__version__}")
    except Exception as e:
        print(f"✗ Failed to import oracledb: {e}")
        return False
    
    return True

def test_config():
    """Test config import"""
    print("\n=== Testing Config ===")
    
    try:
        from src.oipa_mcp.config import config
        print("✓ Config imported successfully")
        print(f"  Server name: {config.mcp_server.name}")
        print(f"  Database host: {config.database.host}")
        return True
    except Exception as e:
        print(f"✗ Failed to import config: {e}")
        traceback.print_exc()
        return False

def test_database():
    """Test database import"""
    print("\n=== Testing Database Connector ===")
    
    try:
        from src.oipa_mcp.connectors import oipa_db
        print("✓ Database connector imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import database connector: {e}")
        traceback.print_exc()
        return False

def test_tools():
    """Test tools import"""
    print("\n=== Testing Tools ===")
    
    try:
        from src.oipa_mcp.tools import AVAILABLE_TOOLS
        print(f"✓ Tools imported successfully - {len(AVAILABLE_TOOLS)} tools")
        for tool in AVAILABLE_TOOLS:
            print(f"  - {tool.name}: {tool.description[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to import tools: {e}")
        traceback.print_exc()
        return False

def test_server_creation():
    """Test basic server creation"""
    print("\n=== Testing Server Creation ===")
    
    try:
        from mcp.server import Server
        from src.oipa_mcp.config import config
        
        server = Server(config.mcp_server.name)
        print("✓ Server created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create server: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("OIPA MCP Server - Diagnostic Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_tools,
        test_server_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
            results.append(False)
    
    print(f"\n=== Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ All tests passed - MCP server should work")
    else:
        print("✗ Some tests failed - check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()
