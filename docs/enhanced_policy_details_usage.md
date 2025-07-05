# Enhanced Policy Details with Roles - Usage Examples

## Overview

The `oipa_get_policy_details` tool has been enhanced to provide comprehensive role information for insurance policies. This includes detailed client information for each role and proper role type descriptions.

## Key Enhancements

### 1. **Always Includes Roles**
- Roles are now included by default (no need to set `include_roles: true`)
- Comprehensive role information with client details

### 2. **Enhanced Role Information**
- Role type names from OIPA database (when available)
- Role type descriptions
- Role status codes
- Percentage and amount allocations
- Complete client information for each role

### 3. **Expanded Role Mapping**
- 40+ role types supported (vs 6 previously)
- Includes all common OIPA role codes
- Fallback to database descriptions when available

## Usage Examples

### Basic Policy Lookup
```json
{
  "policy_number": "VG01-002-561-000001063"
}
```

### Response Structure (Enhanced)
```json
{
  "success": true,
  "data": {
    "policy": {
      "guid": "12345678-1234-1234-1234-123456789012",
      "number": "VG01-002-561-000001063",
      "name": "Life Insurance Policy",
      "status": "Active",
      "status_code": "01",
      "status_description": "Policy is active and in force",
      "plan_date": "2021-07-31",
      "issue_state": "Mexico City",
      "issue_state_code": "09",
      "creation_date": "2021-07-31",
      "updated_date": "2021-12-21 15:40:19"
    },
    "primary_client": {
      "guid": "87654321-4321-4321-4321-210987654321",
      "name": "Juan Pérez García",
      "first_name": "Juan",
      "last_name": "Pérez García",
      "company_name": null,
      "tax_id": "PEGJ850204TL0",
      "date_of_birth": "1985-02-04",
      "gender": "01"
    },
    "plan": {
      "guid": "ABCDEF12-3456-7890-ABCD-EF1234567890",
      "name": "Term Life Insurance Plan"
    },
    "roles": [
      {
        "role_guid": "ROLE1234-5678-9012-3456-789012345678",
        "role_code": "01",
        "role_type": "Primary Insured",
        "role_type_description": "The primary person covered by the insurance policy",
        "role_status_code": "01",
        "percent": 100.0,
        "amount": null,
        "client": {
          "guid": "87654321-4321-4321-4321-210987654321",
          "name": "Juan Pérez García",
          "first_name": "Juan",
          "last_name": "Pérez García",
          "company_name": null,
          "tax_id": "PEGJ850204TL0",
          "client_type_code": "01",
          "date_of_birth": "1985-02-04",
          "gender": "01",
          "email": "juan.perez@email.com"
        }
      },
      {
        "role_guid": "ROLE2345-6789-0123-4567-890123456789",
        "role_code": "13",
        "role_type": "Policy Owner",
        "role_type_description": "The entity that owns the policy and has control rights",
        "role_status_code": "01",
        "percent": null,
        "amount": null,
        "client": {
          "guid": "87654321-4321-4321-4321-210987654321",
          "name": "Juan Pérez García",
          "first_name": "Juan",
          "last_name": "Pérez García",
          "company_name": null,
          "tax_id": "PEGJ850204TL0",
          "client_type_code": "01",
          "date_of_birth": "1985-02-04",
          "gender": "01",
          "email": "juan.perez@email.com"
        }
      },
      {
        "role_guid": "ROLE3456-7890-1234-5678-901234567890",
        "role_code": "34",
        "role_type": "Beneficiary",
        "role_type_description": "Person or entity designated to receive benefits",
        "role_status_code": "01",
        "percent": 100.0,
        "amount": 500000.00,
        "client": {
          "guid": "BENEF123-4567-8901-2345-678901234567",
          "name": "María Pérez López",
          "first_name": "María",
          "last_name": "Pérez López",
          "company_name": null,
          "tax_id": "PELM900315AB1",
          "client_type_code": "01",
          "date_of_birth": "1990-03-15",
          "gender": "02",
          "email": "maria.perez@email.com"
        }
      }
    ]
  }
}
```

## Role Types Supported

The enhanced tool now supports 40+ role types including:

### Primary Roles
- **01**: Primary Insured
- **13**: Policy Owner  
- **27**: Annuitant
- **34**: Beneficiary

### Beneficiary Types
- **26**: Primary Beneficiary
- **32**: Contingent Beneficiary
- **33**: Tertiary Beneficiary
- **35**: Estate Beneficiary
- **36**: Trust Beneficiary

### Business Roles
- **11**: Producer
- **12**: Agent
- **15**: Broker
- **17**: Servicing Agent

### Payment Roles
- **04**: Payor
- **19**: Alternative Payor
- **20**: Contingent Payor
- **21**: Premium Payor

### Legal Roles
- **23**: Power of Attorney
- **24**: Guardian
- **25**: Conservator
- **10**: Trustee

### Entity Types
- **37**: Corporation
- **38**: Partnership
- **39**: Charity
- **40**: Other Entity

## Business Value

### For Agents/CSRs
- **Complete Role View**: See all parties involved in a policy
- **Client Details**: Access contact information for each role
- **Relationship Understanding**: Clear role types and descriptions

### For Underwriters
- **Risk Assessment**: Full view of all involved parties
- **Beneficiary Analysis**: Complete beneficiary information
- **Ownership Structure**: Clear policy ownership details

### For Claims Processing
- **Beneficiary Identification**: Quick access to beneficiary details
- **Contact Information**: Email and demographic data for communications
- **Role Verification**: Confirm role types and percentages

### For Compliance
- **Complete Documentation**: Full role and client information
- **Audit Trail**: All relationships clearly documented
- **Regulatory Reporting**: Complete policy participant data

## Integration Examples

### Natural Language Queries
```
User: "Show me all details for policy VG01-002-561-000001063"
System: Returns complete policy with all roles and client information

User: "Who are the beneficiaries for policy ATL20055008?"
System: Extracts and highlights beneficiary roles from the response

User: "Get contact details for all parties on policy number 123456"
System: Returns all role information with complete client details
```

### API Integration
```python
# Get policy details with enhanced roles
result = await oipa_get_policy_details({
    "policy_number": "VG01-002-561-000001063"
})

# Extract specific role types
beneficiaries = [
    role for role in result["data"]["roles"] 
    if role["role_code"] in ["26", "32", "33", "34"]
]

# Get all contact information
contacts = [
    {
        "role": role["role_type"],
        "name": role["client"]["name"],
        "email": role["client"]["email"],
        "tax_id": role["client"]["tax_id"]
    }
    for role in result["data"]["roles"]
    if role["client"]["email"]
]
```

This enhancement significantly improves the business value of the OIPA MCP Server by providing comprehensive relationship and contact information in a single query.
