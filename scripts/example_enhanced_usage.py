#!/usr/bin/env python3
"""
Example usage of enhanced OIPA MCP Server with status and state names

This example demonstrates the enhanced capabilities including:
- Human-readable status names from OIPA AsCode table
- Issue state names with full descriptions
- Improved user experience with descriptive information
"""

import asyncio
import json
from pathlib import Path
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from oipa_mcp.tools.policy_tools import SearchPoliciesQuality, GetPolicyDetailsTotal, PolicyCountsByStatusSmall
from oipa_mcp.connectors.database import oipa_db

async def example_enhanced_policy_operations():
    """Demonstrate enhanced policy operations with human-readable names"""
    
    print("🏥 OIPA MCP Server - Enhanced Policy Operations Example")
    print("=" * 60)
    
    # Initialize database
    await oipa_db.initialize()
    
    # Initialize tools
    search_tool = SearchPoliciesQuality()
    details_tool = GetPolicyDetailsTotal()
    counts_tool = PolicyCountsByStatusSmall()
    
    try:
        # Example 1: Search policies with enhanced status display
        print("\n📋 1. ENHANCED POLICY SEARCH")
        print("-" * 40)
        
        search_result = await search_tool.execute({
            "search_term": "VG01",
            "status": "all",
            "limit": 3
        })
        
        print("Search Results with Enhanced Status Names:")
        for policy in search_result.get("data", [])[:3]:
            print(f"  • {policy['policy_number']}")
            print(f"    Status: {policy['status']} (Code: {policy['status_code']})")
            print(f"    Client: {policy['client']['name']}")
            print(f"    Updated: {policy['updated_date']}")
            print()
        
        # Example 2: Get detailed policy information with state names
        print("\n🔍 2. ENHANCED POLICY DETAILS")
        print("-" * 40)
        
        if search_result.get("data"):
            policy_number = search_result["data"][0]["policy_number"]
            
            details_result = await details_tool.execute({
                "policy_number": policy_number,
                "include_roles": True
            })
            
            if details_result.get("data"):
                policy_info = details_result["data"]["policy"]
                client_info = details_result["data"]["primary_client"]
                
                print(f"Enhanced Policy Information for {policy_info['number']}:")
                print(f"  📄 Policy Details:")
                print(f"     Name: {policy_info['name']}")
                print(f"     Status: {policy_info['status']} (Code: {policy_info['status_code']})")
                if policy_info.get('status_description'):
                    print(f"     Status Description: {policy_info['status_description']}")
                print(f"     Issue State: {policy_info['issue_state']} (Code: {policy_info.get('issue_state_code', 'N/A')})")
                if policy_info.get('issue_state_description'):
                    print(f"     State Description: {policy_info['issue_state_description']}")
                print(f"     Plan Date: {policy_info['plan_date']}")
                print()
                print(f"  👤 Primary Client:")
                print(f"     Name: {client_info['name']}")
                print(f"     Tax ID: {client_info['tax_id']}")
                print(f"     Date of Birth: {client_info['date_of_birth']}")
                print()
                
                # Show roles if available
                if details_result["data"].get("roles"):
                    print(f"  👥 Policy Roles:")
                    for role in details_result["data"]["roles"][:3]:
                        print(f"     {role['role_type']}: {role['client']['name']}")
                        if role.get('percent'):
                            print(f"       Percentage: {role['percent']}%")
                    print()
        
        # Example 3: Enhanced policy counts with descriptive status names
        print("\n📊 3. ENHANCED POLICY STATUS ANALYTICS")
        print("-" * 40)
        
        counts_result = await counts_tool.execute({})
        
        if counts_result.get("data"):
            analytics = counts_result["data"]
            print(f"Total Policies: {analytics['total_policies']:,}")
            print(f"Summary: {analytics['summary']}")
            print()
            print("Status Distribution with OIPA Names:")
            
            for status_name, status_data in analytics["status_breakdown"].items():
                count = status_data["count"]
                percentage = status_data["percentage"]
                code = status_data["status_code"]
                print(f"  📈 {status_name}: {count:,} policies ({percentage}%) [Code: {code}]")
        
        print("\n✅ Enhanced Policy Operations Completed Successfully!")
        print("\nKey Enhancements Demonstrated:")
        print("  • Human-readable status names from OIPA AsCode table")
        print("  • Issue state names with full descriptions")
        print("  • Backward compatibility with original status codes")
        print("  • Enhanced user experience with descriptive information")
        print("  • Consistent with OIPA user interface terminology")
        
    except Exception as e:
        print(f"❌ Error during example execution: {e}")
        
    finally:
        await oipa_db.close()

async def example_status_code_mapping():
    """Show the difference between enhanced and basic status display"""
    
    print("\n🔄 STATUS CODE ENHANCEMENT COMPARISON")
    print("=" * 50)
    
    await oipa_db.initialize()
    
    try:
        # Query to show the enhancement
        query = """
        SELECT DISTINCT 
            p.StatusCode as code,
            status_tbl.ShortDescription as name,
            status_tbl.LongDescription as description,
            COUNT(*) as policy_count
        FROM AsPolicy p
        LEFT JOIN AsCode status_tbl ON status_tbl.CodeValue = p.StatusCode 
            AND status_tbl.CodeName = 'AsCodeStatus'
        GROUP BY p.StatusCode, status_tbl.ShortDescription, status_tbl.LongDescription
        ORDER BY policy_count DESC
        """
        
        results = await oipa_db.execute_query(query)
        
        print("Before Enhancement (Code Only) vs After Enhancement (Name + Code):")
        print()
        for row in results[:5]:
            code = row['code']
            name = row.get('name') or 'Unknown Status'
            description = row.get('description') or 'No description available'
            count = row['policy_count']
            
            print(f"  Before: Status '{code}' - {count:,} policies")
            print(f"  After:  Status '{name}' (Code: {code}) - {count:,} policies")
            if description != name:
                print(f"          Description: {description}")
            print()
            
    except Exception as e:
        print(f"❌ Error showing comparison: {e}")
    finally:
        await oipa_db.close()

if __name__ == "__main__":
    print("Starting Enhanced OIPA MCP Server Example...")
    print("This example demonstrates the new status and state name capabilities.")
    print()
    
    # Run the enhanced examples
    asyncio.run(example_enhanced_policy_operations())
    print()
    asyncio.run(example_status_code_mapping())
    
    print("\n🎉 Example completed! The OIPA MCP Server now provides")
    print("   human-readable names for better user experience.")
