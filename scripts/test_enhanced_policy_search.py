#!/usr/bin/env python3
"""
Test script for enhanced policy search with status and state names
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from oipa_mcp.connectors.database import OipaQueryBuilder, oipa_db
from oipa_mcp.config import Config
from loguru import logger

async def test_enhanced_policy_search():
    """Test the enhanced policy search with state and status names"""
    logger.info("Testing enhanced policy search functionality...")
    
    try:
        # Initialize database connection
        await oipa_db.initialize()
        
        # Test 1: Search policies query
        logger.info("Testing search_policies query...")
        query, params = OipaQueryBuilder.search_policies(
            search_term="VG01",
            status_filter="all", 
            limit=5
        )
        print("\n=== SEARCH POLICIES QUERY ===")
        print(query)
        print(f"Parameters: {params}")
        
        try:
            results = await oipa_db.execute_query(query, params)
            print(f"\nFound {len(results)} policies")
            for policy in results[:2]:  # Show first 2 results
                print(f"- {policy['policy_number']}: {policy.get('status_name', 'N/A')} (Code: {policy['status_code']})")
        except Exception as e:
            logger.error(f"Error executing search query: {e}")
        
        # Test 2: Get policy details query
        logger.info("\nTesting get_policy_details query...")
        query, params = OipaQueryBuilder.get_policy_details(
            policy_number="VG01-002-561-000001063"
        )
        print("\n=== POLICY DETAILS QUERY ===")
        print(query)
        print(f"Parameters: {params}")
        
        try:
            result = await oipa_db.execute_single_query(query, params)
            if result:
                print(f"\nPolicy Details:")
                print(f"- Number: {result['policy_number']}")
                print(f"- Status: {result.get('status_name', 'N/A')} (Code: {result['status_code']})")
                print(f"- Issue State: {result.get('issue_state_name', 'N/A')} (Code: {result.get('issue_state_code', 'N/A')})")
            else:
                print("Policy not found")
        except Exception as e:
            logger.error(f"Error executing details query: {e}")
        
        # Test 3: Count policies by status query
        logger.info("\nTesting count_policies_by_status query...")
        query, params = OipaQueryBuilder.count_policies_by_status()
        print("\n=== POLICY COUNTS QUERY ===")
        print(query)
        print(f"Parameters: {params}")
        
        try:
            results = await oipa_db.execute_query(query, params)
            print(f"\nPolicy counts by status:")
            for row in results:
                status_name = row.get('status_name') or f"Status {row['status_code']}"
                print(f"- {status_name}: {row['policy_count']} policies ({row['percentage']}%)")
        except Exception as e:
            logger.error(f"Error executing counts query: {e}")
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False
    finally:
        await oipa_db.close()
    
    logger.info("Enhanced policy search test completed!")
    return True

async def test_asCode_table_structure():
    """Test to understand AsCode table structure"""
    logger.info("Testing AsCode table structure...")
    
    try:
        await oipa_db.initialize()
        
        # Check available status codes
        status_query = """
            SELECT CodeValue, ShortDescription, LongDescription
            FROM AsCode 
            WHERE CodeName = 'AsCodeStatus'
            ORDER BY CodeValue
        """
        
        print("\n=== AVAILABLE STATUS CODES ===")
        try:
            results = await oipa_db.execute_query(status_query)
            for row in results:
                print(f"Code: {row['codevalue']} | Short: {row.get('shortdescription', 'N/A')} | Long: {row.get('longdescription', 'N/A')}")
        except Exception as e:
            logger.error(f"Error querying status codes: {e}")
        
        # Check available state codes
        state_query = """
            SELECT CodeValue, ShortDescription, LongDescription
            FROM AsCode 
            WHERE CodeName = 'AsCodeState'
            ORDER BY CodeValue
        """
        
        print("\n=== AVAILABLE STATE CODES ===")
        try:
            results = await oipa_db.execute_query(state_query)
            for row in results[:10]:  # Show first 10
                print(f"Code: {row['codevalue']} | Short: {row.get('shortdescription', 'N/A')} | Long: {row.get('longdescription', 'N/A')}")
        except Exception as e:
            logger.error(f"Error querying state codes: {e}")
            
    except Exception as e:
        logger.error(f"Database connection error: {e}")
    finally:
        await oipa_db.close()

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
    
    print("OIPA Enhanced Policy Search Test")
    print("=" * 50)
    
    # Run tests
    asyncio.run(test_asCode_table_structure())
    print("\n" + "=" * 50)
    asyncio.run(test_enhanced_policy_search())
