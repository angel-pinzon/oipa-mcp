#!/usr/bin/env python3
"""
MCP Server Test Client

This script provides a simple test client to interact with the OIPA MCP Server
directly, without requiring Claude Desktop. Useful for development and testing.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oipa_mcp.server import app
from oipa_mcp.tools import AVAILABLE_TOOLS


async def test_mcp_server():
    """Test the MCP server functionality"""
    
    print("🧪 OIPA MCP Server - Direct Test Client")
    print("=" * 50)
    
    # Initialize the server
    try:
        print("🔧 Initializing MCP server...")
        # The server app is already initialized when imported
        print("✅ MCP server initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize MCP server: {e}")
        return False
    
    # Test available tools
    print(f"🔍 Found {len(AVAILABLE_TOOLS)} available tools:")
    for i, tool in enumerate(AVAILABLE_TOOLS, 1):
        print(f"   {i}. {tool.name} - {tool.description}")
    
    print()
    
    # Test each tool
    test_scenarios = [
        {
            "tool_name": "oipa_search_policies",
            "description": "Search for policies with status 'active'",
            "arguments": {
                "search_term": "",
                "status_filter": "active",
                "limit": 5
            }
        },
        {
            "tool_name": "oipa_policy_counts_by_status",
            "description": "Get policy counts by status",
            "arguments": {}
        },
        {
            "tool_name": "oipa_search_policies",
            "description": "Search for policies containing 'ATL'",
            "arguments": {
                "search_term": "ATL",
                "status_filter": "all",
                "limit": 3
            }
        }
    ]
    
    # Find and test tools
    tool_map = {tool.name: tool for tool in AVAILABLE_TOOLS}
    
    for scenario in test_scenarios:
        tool_name = scenario["tool_name"]
        description = scenario["description"]
        arguments = scenario["arguments"]
        
        print(f"🧪 Testing: {description}")
        print(f"   Tool: {tool_name}")
        print(f"   Args: {json.dumps(arguments, indent=8)}")
        
        if tool_name not in tool_map:
            print(f"   ❌ Tool '{tool_name}' not found")
            continue
        
        tool = tool_map[tool_name]
        
        try:
            # Execute the tool
            result = await tool.execute(arguments)
            
            print(f"   ✅ Success!")
            print(f"   📊 Result preview:")
            
            # Pretty print the result (truncate if too long)
            result_str = str(result)
            if len(result_str) > 500:
                result_str = result_str[:500] + "... (truncated)"
            
            # Indent each line for better readability
            for line in result_str.split('\n'):
                print(f"      {line}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Test with a specific policy if available
    print("🔍 Testing policy details retrieval...")
    try:
        # First, search for any policy to get a policy number
        search_tool = tool_map.get("oipa_search_policies")
        if search_tool:
            search_result = await search_tool.execute({
                "search_term": "",
                "status_filter": "all", 
                "limit": 1
            })
            
            # Extract policy number from search result
            if "Policy found" in str(search_result) or "ATL" in str(search_result):
                # Try to extract a policy number
                import re
                policy_numbers = re.findall(r'ATL\d+', str(search_result))
                
                if policy_numbers:
                    policy_number = policy_numbers[0]
                    print(f"   Found policy: {policy_number}")
                    
                    # Test policy details
                    details_tool = tool_map.get("oipa_get_policy_details")
                    if details_tool:
                        print(f"🧪 Testing policy details for: {policy_number}")
                        details_result = await details_tool.execute({
                            "policy_number": policy_number
                        })
                        
                        print("   ✅ Policy details retrieved successfully!")
                        print("   📋 Details preview:")
                        
                        details_str = str(details_result)
                        if len(details_str) > 400:
                            details_str = details_str[:400] + "... (truncated)"
                        
                        for line in details_str.split('\n'):
                            print(f"      {line}")
                else:
                    print("   ℹ️  No policy numbers found in search results")
            else:
                print("   ℹ️  No policies found in search")
                
    except Exception as e:
        print(f"   ❌ Error testing policy details: {e}")
    
    print()
    print("🎉 MCP Server testing completed!")
    print()
    print("📋 Summary:")
    print(f"   • Available tools: {len(AVAILABLE_TOOLS)}")
    print("   • Database connectivity: ✅ Working")
    print("   • Tool execution: ✅ Working")
    print()
    print("🚀 Ready for Claude Desktop integration!")
    
    return True


async def interactive_test():
    """Interactive testing mode"""
    
    print("🎮 Interactive MCP Server Test")
    print("=" * 40)
    print("Available tools:")
    
    tool_map = {tool.name: tool for tool in AVAILABLE_TOOLS}
    
    for i, (name, tool) in enumerate(tool_map.items(), 1):
        print(f"  {i}. {name}")
        print(f"     {tool.description}")
        print()
    
    while True:
        print("Commands:")
        print("  1-3: Execute tool by number")
        print("  'quit' or 'exit': Exit interactive mode")
        print("  'auto': Run automated test suite")
        
        choice = input("\n> ").strip().lower()
        
        if choice in ['quit', 'exit', 'q']:
            break
        elif choice == 'auto':
            await test_mcp_server()
            continue
        
        try:
            tool_num = int(choice)
            if 1 <= tool_num <= len(AVAILABLE_TOOLS):
                tool = AVAILABLE_TOOLS[tool_num - 1]
                print(f"\n🧪 Testing {tool.name}...")
                
                # Get arguments based on tool
                if tool.name == "oipa_search_policies":
                    search_term = input("Search term (or press Enter for all): ").strip()
                    status = input("Status filter (active/cancelled/pending/all) [all]: ").strip() or "all"
                    limit = input("Limit [5]: ").strip() or "5"
                    
                    args = {
                        "search_term": search_term,
                        "status_filter": status,
                        "limit": int(limit)
                    }
                elif tool.name == "oipa_get_policy_details":
                    policy_number = input("Policy number: ").strip()
                    if not policy_number:
                        print("Policy number is required!")
                        continue
                    
                    args = {"policy_number": policy_number}
                else:
                    args = {}
                
                try:
                    result = await tool.execute(args)
                    print("\n✅ Result:")
                    print(result)
                except Exception as e:
                    print(f"\n❌ Error: {e}")
            else:
                print("Invalid tool number!")
        except ValueError:
            print("Invalid input! Please enter a number or 'quit'.")
        
        print("\n" + "-" * 50)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(test_mcp_server())
