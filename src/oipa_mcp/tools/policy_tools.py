"""
Policy management tools for OIPA MCP Server

Provides tools for searching, retrieving, and managing insurance policies.
Based on OIPA AsPolicy table structure and common business operations.
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from .base import QueryTool
from ..connectors import OipaQueryBuilder


class SearchPoliciesQuality(QueryTool):
    """
    Search policies with intelligent filtering and ranking
    
    This tool provides natural language search capabilities for insurance policies,
    supporting various search criteria like policy number, client name, tax ID, etc.
    """
    
    @property
    def name(self) -> str:
        return "oipa_search_policies"
    
    @property
    def description(self) -> str:
        return """
        Search insurance policies using natural language queries.
        
        Supports searching by:
        - Policy number (exact or partial)
        - Client name (first name, last name, or company name)
        - Tax ID / RFC
        - Policy status (active, cancelled, pending)
        
        Examples:
        - "VG01-002-561-000001063" (exact policy number)
        - "María García" (client name)
        - "CJF950204TL0" (tax ID)
        - "active policies for ACME Corp"
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "Search term: policy number, client name, tax ID, or company name"
                },
                "status": {
                    "type": "string", 
                    "enum": ["active", "cancelled", "pending", "all"],
                    "default": "all",
                    "description": "Filter by policy status"
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                    "description": "Maximum number of results to return"
                }
            },
            "required": ["search_term"]
        }
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute policy search with intelligent ranking"""
        search_term = arguments["search_term"]
        status = arguments.get("status", "all")
        limit = arguments.get("limit", 20)
        
        logger.info(f"Searching policies: term='{search_term}', status='{status}', limit={limit}")
        
        # Build and execute query
        query, parameters = OipaQueryBuilder.search_policies(
            search_term=search_term,
            status_filter=status,
            limit=limit
        )
        
        results = await self._execute_query_tool(query, parameters)
        
        # Enhance results with additional formatting
        enhanced_results = []
        for policy in results:
            # Use database-provided status name if available, otherwise format the code
            status_display = policy.get("status_name") or self._format_status(policy["status_code"])
            
            enhanced_policy = {
                "policy_guid": policy["policy_guid"],
                "policy_number": policy["policy_number"],
                "policy_name": policy["policy_name"],
                "status": status_display,
                "status_code": policy["status_code"],
                "plan_date": policy["plan_date"].strftime("%Y-%m-%d") if policy["plan_date"] else None,
                "updated_date": policy["updated_date"].strftime("%Y-%m-%d %H:%M:%S") if policy["updated_date"] else None,
                "client": {
                    "client_guid": policy["client_guid"],
                    "name": self._format_client_name(policy),
                    "tax_id": policy["tax_id"]
                }
            }
            enhanced_results.append(enhanced_policy)
        
        return enhanced_results
    
    def _format_status(self, status_code: str) -> str:
        """Convert status code to human-readable format"""
        status_map = {
            "01": "Active",
            "08": "Pending", 
            "99": "Cancelled",
            "13": "Suspended",
            "14": "Lapsed"
        }
        return status_map.get(status_code, f"Unknown ({status_code})")
    
    def _format_client_name(self, policy: Dict[str, Any]) -> str:
        """Format client name from policy data"""
        if policy["company_name"]:
            return policy["company_name"]
        elif policy["client_first_name"] and policy["client_last_name"]:
            return f"{policy['client_first_name']} {policy['client_last_name']}"
        elif policy["client_first_name"]:
            return policy["client_first_name"]
        elif policy["client_last_name"]:
            return policy["client_last_name"]
        else:
            return "Unknown Client"


class GetPolicyDetailsTotal(QueryTool):
    """
    Get comprehensive policy information including segments, roles, and history
    
    Provides detailed view of a specific policy including all related data.
    """
    
    @property
    def name(self) -> str:
        return "oipa_get_policy_details"
    
    @property
    def description(self) -> str:
        return """
        Get comprehensive details for a specific insurance policy.
        
        Includes:
        - Basic policy information (number, name, status, dates)
        - Primary client/insured details (name, tax ID, demographics)
        - Plan information (name, GUID)
        - All policy roles with detailed client information
        - Role types (Primary Insured, Policy Owner, Beneficiary, etc.)
        - Client details for each role (name, contact info, demographics)
        - Related segments (if requested)
        
        Can search by policy GUID or policy number.
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "policy_guid": {
                    "type": "string",
                    "description": "OIPA Policy GUID"
                },
                "policy_number": {
                    "type": "string", 
                    "description": "Policy number (e.g., VG01-002-561-000001063)"
                },
                "include_segments": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include policy segments information"
                },
                "include_roles": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include all policy roles"
                }
            },
            "oneOf": [
                {"required": ["policy_guid"]},
                {"required": ["policy_number"]}
            ]
        }
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed policy information"""
        policy_guid = arguments.get("policy_guid")
        policy_number = arguments.get("policy_number")
        include_segments = arguments.get("include_segments", False)
        include_roles = arguments.get("include_roles", False)
        
        logger.info(f"Getting policy details: guid={policy_guid}, number={policy_number}")
        
        # Get basic policy information
        query, parameters = OipaQueryBuilder.get_policy_details(
            policy_guid=policy_guid,
            policy_number=policy_number
        )
        
        policy_data = await self._execute_query_tool(query, parameters, single_result=True)
        
        if not policy_data:
            return self._build_error_response("Policy not found")
        
        # Format basic policy information
        # Use database-provided names if available, otherwise format the codes
        status_display = policy_data.get("status_name") or self._format_status(policy_data["status_code"])
        state_display = policy_data.get("issue_state_name") or policy_data.get("issue_state_code", "Unknown")
        
        # Format basic policy information
        result = {
            "policy": {
                "guid": policy_data["policy_guid"],
                "number": policy_data["policy_number"],
                "name": policy_data["policy_name"],
                "status": status_display,
                "status_code": policy_data["status_code"],
                "status_description": policy_data.get("status_description"),
                "plan_date": policy_data["plan_date"].strftime("%Y-%m-%d") if policy_data["plan_date"] else None,
                "issue_state": state_display,
                "issue_state_code": policy_data.get("issue_state_code"),
                "issue_state_description": policy_data.get("issue_state_description"),
                "creation_date": policy_data["creation_date"].strftime("%Y-%m-%d") if policy_data["creation_date"] else None,
                "updated_date": policy_data["updated_date"].strftime("%Y-%m-%d %H:%M:%S") if policy_data["updated_date"] else None
            },
            "primary_client": {
                "guid": policy_data["client_guid"],
                "name": self._format_client_name(policy_data),
                "first_name": policy_data["client_first_name"],
                "last_name": policy_data["client_last_name"],
                "company_name": policy_data["company_name"],
                "tax_id": policy_data["tax_id"],
                "date_of_birth": policy_data["date_of_birth"].strftime("%Y-%m-%d") if policy_data["date_of_birth"] else None,
                "gender": policy_data["gender"]
            },
            "plan": {
                "guid": policy_data["plan_guid"],
                "name": policy_data["plan_name"]
            }
        }
        
        # Add segments if requested
        if include_segments:
            result["segments"] = await self._get_policy_segments(policy_data["policy_guid"])
        
        # Always include roles with detailed information
        result["roles"] = await self._get_policy_roles(policy_data["policy_guid"])
        
        return self._build_success_response(result)
    
    async def _get_policy_segments(self, policy_guid: str) -> List[Dict[str, Any]]:
        """Get segments for a policy"""
        # TODO: Implement segment retrieval
        # This would require AsSegment table queries
        return []
    
    async def _get_policy_roles(self, policy_guid: str) -> List[Dict[str, Any]]:
        """Get all roles for a policy with detailed client and role information"""
        query = """
            SELECT 
                r.RoleGUID as role_guid,
                r.RoleCode as role_code,
                r.RolePercent as role_percent,
                r.RoleAmount as role_amount,
                r.StatusCode as role_status_code,
                role_code_tbl.ShortDescription as role_type_name,
                role_code_tbl.LongDescription as role_type_description,
                c.ClientGUID as client_guid,
                c.FirstName as first_name,
                c.LastName as last_name,
                c.CompanyName as company_name,
                c.TaxID as tax_id,
                c.TypeCode as client_type_code,
                c.DateOfBirth as date_of_birth,
                c.Sex as gender,
                c.Email as email
            FROM AsRole r
            LEFT JOIN AsClient c ON r.ClientGUID = c.ClientGUID
            LEFT JOIN AsCode role_code_tbl ON role_code_tbl.CodeValue = r.RoleCode 
                AND role_code_tbl.CodeName = 'AsCodeRole'
            WHERE r.PolicyGUID = :policy_guid
            ORDER BY r.RoleCode
        """
        
        roles_data = await self._execute_query_tool(query, {"policy_guid": policy_guid})
        
        # Format roles with enhanced information
        formatted_roles = []
        for role in roles_data:
            # Use database-provided role type name if available, otherwise use fallback mapping
            role_type_display = role.get("role_type_name") or self._format_role_type(role["role_code"])
            
            formatted_role = {
                "role_guid": role["role_guid"],
                "role_code": role["role_code"],
                "role_type": role_type_display,
                "role_type_description": role.get("role_type_description"),
                "role_status_code": role["role_status_code"],
                "percent": float(role["role_percent"]) if role["role_percent"] else None,
                "amount": float(role["role_amount"]) if role["role_amount"] else None,
                "client": {
                    "guid": role["client_guid"],
                    "name": self._format_client_name(role),
                    "first_name": role["first_name"],
                    "last_name": role["last_name"],
                    "company_name": role["company_name"],
                    "tax_id": role["tax_id"],
                    "client_type_code": role["client_type_code"],
                    "date_of_birth": role["date_of_birth"].strftime("%Y-%m-%d") if role["date_of_birth"] else None,
                    "gender": role["gender"],
                    "email": role["email"]
                }
            }
            formatted_roles.append(formatted_role)
        
        return formatted_roles
    
    def _format_status(self, status_code: str) -> str:
        """Convert status code to human-readable format"""
        status_map = {
            "01": "Active",
            "08": "Pending",
            "99": "Cancelled", 
            "13": "Suspended",
            "14": "Lapsed"
        }
        return status_map.get(status_code, f"Unknown ({status_code})")
    
    def _format_role_type(self, role_code: str) -> str:
        """Convert role code to human-readable format based on OIPA AsCodeRole table"""
        role_map = {
            "01": "Primary Insured",
            "02": "Secondary Insured", 
            "03": "Tertiary Insured",
            "04": "Payor",
            "05": "Insured",
            "06": "Co-Insured",
            "07": "Joint Insured",
            "08": "Contingent Owner",
            "09": "Successor Owner",
            "10": "Trustee",
            "11": "Producer",
            "12": "Agent",
            "13": "Policy Owner",
            "14": "Producer Payee",
            "15": "Broker",
            "16": "Case Manager",
            "17": "Servicing Agent",
            "18": "Billing Contact",
            "19": "Alternative Payor",
            "20": "Contingent Payor",
            "21": "Premium Payor",
            "22": "Other",
            "23": "Power of Attorney",
            "24": "Guardian",
            "25": "Conservator",
            "26": "Primary Beneficiary",
            "27": "Annuitant",
            "28": "Joint Annuitant",
            "29": "Contingent Annuitant",
            "30": "Successor Annuitant",
            "31": "Beneficiary Payee",
            "32": "Contingent Beneficiary",
            "33": "Tertiary Beneficiary",
            "34": "Beneficiary",
            "35": "Estate Beneficiary",
            "36": "Trust Beneficiary",
            "37": "Corporation",
            "38": "Partnership",
            "39": "Charity",
            "40": "Other Entity"
        }
        return role_map.get(role_code, f"Role {role_code}")
    
    def _format_client_name(self, client_data: Dict[str, Any]) -> str:
        """Format client name from client data"""
        if client_data.get("company_name"):
            return client_data["company_name"]
        elif client_data.get("first_name") and client_data.get("last_name"):
            return f"{client_data['first_name']} {client_data['last_name']}"
        elif client_data.get("first_name"):
            return client_data["first_name"]
        elif client_data.get("last_name"):
            return client_data["last_name"]
        else:
            return "Unknown Client"


class PolicyCountsByStatusSmall(QueryTool):
    """
    Get policy counts grouped by status
    
    Provides quick dashboard-style overview of policy distribution.
    """
    
    @property
    def name(self) -> str:
        return "oipa_policy_counts_by_status"
    
    @property
    def description(self) -> str:
        return """
        Get count of policies grouped by status.
        
        Provides a quick overview of policy distribution across different statuses
        (active, cancelled, pending, etc.). Useful for dashboard reporting.
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get policy counts by status"""
        logger.info("Getting policy counts by status")
        
        query, parameters = OipaQueryBuilder.count_policies_by_status()
        results = await self._execute_query_tool(query, parameters)
        
        # Format results with human-readable status names
        formatted_counts = {}
        total_policies = 0
        
        for row in results:
            status_code = row["status_code"]
            count = row["policy_count"]
            # Use database-provided status name if available, otherwise format the code
            status_name = row.get("status_name") or self._format_status(status_code)
            
            formatted_counts[status_name] = {
                "count": count,
                "status_code": status_code
            }
            total_policies += count
        
        # Calculate percentages
        for status_data in formatted_counts.values():
            status_data["percentage"] = self._calculate_percentage(
                status_data["count"], 
                total_policies
            )
        
        return self._build_success_response({
            "total_policies": total_policies,
            "status_breakdown": formatted_counts,
            "summary": f"Total {total_policies} policies across {len(formatted_counts)} statuses"
        })
    
    def _format_status(self, status_code: str) -> str:
        """Convert status code to human-readable format"""
        status_map = {
            "01": "Active",
            "08": "Pending",
            "99": "Cancelled",
            "13": "Suspended", 
            "14": "Lapsed"
        }
        return status_map.get(status_code, f"Status {status_code}")
    
    def _calculate_percentage(self, part: int, total: int) -> float:
        """Calculate percentage with division by zero protection"""
        if total == 0:
            return 0.0
        return round((part / total) * 100, 2)
