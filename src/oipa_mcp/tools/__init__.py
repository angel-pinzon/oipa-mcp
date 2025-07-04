"""
Tools package for OIPA MCP Server

Contains all MCP tools organized by functional area:
- policy_tools.py: Policy search, details, and management
- client_tools.py: Client search and portfolio management  
- transaction_tools.py: Transaction execution and history
- query_tools.py: Generic query and reporting tools
- analytics_tools.py: Business intelligence and analytics
"""

from .base import BaseTool, QueryTool, TransactionTool, AnalyticsTool
from .policy_tools import (
    SearchPoliciesQuality,
    GetPolicyDetailsTotal, 
    PolicyCountsByStatusSmall
)

# Registry of all available tools
AVAILABLE_TOOLS = [
    SearchPoliciesQuality(),
    GetPolicyDetailsTotal(),
    PolicyCountsByStatusSmall()
]

__all__ = [
    "BaseTool",
    "QueryTool", 
    "TransactionTool",
    "AnalyticsTool",
    "SearchPoliciesQuality",
    "GetPolicyDetailsTotal",
    "PolicyCountsByStatusSmall",
    "AVAILABLE_TOOLS"
]
