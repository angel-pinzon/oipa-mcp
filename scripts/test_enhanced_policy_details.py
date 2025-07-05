#!/usr/bin/env python3
"""
Test script for enhanced policy details with roles information

This script tests the improved oipa_get_policy_details tool to verify
that it properly returns detailed role information.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from oipa_mcp.tools.policy_tools import GetPolicyDetailsTotal
from oipa_mcp.connectors import oipa_db


async def test_policy_details_with_roles():
    """Test the enhanced policy details functionality"""
    
    # Initialize the tool
    tool = GetPolicyDetailsTotal()
    
    # Test with a known policy number (you may need to adjust this)
    test_policy_number = "VG01-002-561-000001063"
    
    print(f"🔍 Testing enhanced policy details for policy: {test_policy_number}")
    print("=" * 80)
    
    try:
        # Test database connection first
        print("📡 Testing database connection...")
        connection_ok = await oipa_db.test_connection()
        if not connection_ok:
            print("❌ Database connection failed")
            return
        print("✅ Database connection successful")
        
        # Test the enhanced policy details
        print(f"\n🏛️ Getting detailed policy information with roles...")
        
        # Execute the tool
        result = await tool._execute_impl({
            "policy_number": test_policy_number,
            "include_segments": False,
            "include_roles": True
        })
        
        if result.get("success"):
            data = result["data"]
            
            # Display basic policy info
            policy = data["policy"]
            print(f"\n📋 Policy Information:")
            print(f"   Number: {policy['number']}")
            print(f"   Name: {policy['name']}")
            print(f"   Status: {policy['status']}")
            print(f"   Plan Date: {policy['plan_date']}")
            print(f"   Issue State: {policy['issue_state']}")
            
            # Display primary client info
            client = data["primary_client"]
            print(f"\n👤 Primary Client:")
            print(f"   Name: {client['name']}")
            print(f"   Tax ID: {client['tax_id']}")
            print(f"   Date of Birth: {client['date_of_birth']}")
            print(f"   Gender: {client['gender']}")
            
            # Display plan info
            plan = data["plan"]
            print(f"\n📊 Plan Information:")
            print(f"   Name: {plan['name']}")
            print(f"   GUID: {plan['guid']}")
            
            # Display enhanced roles information
            roles = data.get("roles", [])
            print(f"\n👥 Policy Roles ({len(roles)} roles found):")
            print("-" * 60)
            
            for i, role in enumerate(roles, 1):
                print(f"\n   {i}. Role: {role['role_type']} (Code: {role['role_code']})")
                if role.get('role_type_description'):
                    print(f"      Description: {role['role_type_description']}")
                
                # Role details
                if role['percent']:
                    print(f"      Percentage: {role['percent']}%")
                if role['amount']:
                    print(f"      Amount: ${role['amount']:,.2f}")
                
                # Client details for this role
                role_client = role['client']
                print(f"      Client: {role_client['name']}")
                if role_client['tax_id']:
                    print(f"      Tax ID: {role_client['tax_id']}")
                if role_client['date_of_birth']:
                    print(f"      Date of Birth: {role_client['date_of_birth']}")
                if role_client['gender']:
                    print(f"      Gender: {role_client['gender']}")
                if role_client['email']:
                    print(f"      Email: {role_client['email']}")
                if role_client['company_name']:
                    print(f"      Company: {role_client['company_name']}")
            
            print(f"\n✅ Enhanced policy details retrieved successfully!")
            print(f"📊 Summary: {len(roles)} roles found with detailed client information")
            
        else:
            print(f"❌ Error retrieving policy details: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up database connection
        await oipa_db.close()


async def test_role_mapping():
    """Test the enhanced role mapping functionality"""
    print("\n🎭 Testing Role Type Mapping:")
    print("=" * 50)
    
    tool = GetPolicyDetailsTotal()
    
    # Test common role codes
    test_codes = ["01", "13", "27", "34", "26", "32", "11", "12", "99"]
    
    for code in test_codes:
        role_name = tool._format_role_type(code)
        print(f"   Role {code}: {role_name}")


if __name__ == "__main__":
    print("🧪 Testing Enhanced OIPA Policy Details with Roles")
    print("=" * 80)
    
    # Run the tests
    asyncio.run(test_policy_details_with_roles())
    asyncio.run(test_role_mapping())
    
    print("\n🎉 Test completed!")
