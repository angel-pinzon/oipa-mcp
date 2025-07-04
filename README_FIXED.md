# OIPA MCP Server

MCP (Model Context Protocol) server for Oracle OIPA (Insurance Policy Administration) integration.

## 🚨 **ORACLE CLIENT ERROR FIXED** 

This version solves the `DPI-1047: Cannot locate a 64-bit Oracle Client library` error by using modern `python-oracledb` which doesn't require Oracle Client installation.

## Quick Fix for Connection Issues

If you're getting Oracle Client errors, run the easy installation script:

### Windows
```cmd
install_fix.bat
```

### Linux/Mac
```bash
chmod +x install_fix.sh
./install_fix.sh
```

## Features

### Core Capabilities
- 🔍 **Intelligent Policy Search** - Natural language search across policies, clients, and products
- 📊 **Real-time Analytics** - Policy counts, status distributions, and business metrics  
- 🏢 **Client Management** - Client search, portfolio views, and relationship tracking
- ⚡ **Direct OIPA Integration** - Native Oracle database connectivity and SOAP web services

### Available Tools

#### Policy Management
- `oipa_search_policies` - Search policies by number, client name, or tax ID
- `oipa_get_policy_details` - Get comprehensive policy information including segments and roles
- `oipa_policy_counts_by_status` - Dashboard-style policy distribution overview

#### Analytics & Reporting
- Real-time policy status breakdowns
- Client portfolio summaries
- Transaction history analysis

## Installation

### Option 1: Easy Install (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-org/oipa-mcp.git
cd oipa-mcp

# Run the easy installation script
# For Windows:
install_fix.bat

# For Linux/Mac:
chmod +x install_fix.sh
./install_fix.sh
```

### Option 2: Manual Install
```bash
# Clone the repository
git clone https://github.com/your-org/oipa-mcp.git
cd oipa-mcp

# Remove old cx-Oracle (if present)
pip uninstall cx-Oracle -y

# Install modern Oracle driver (no Oracle Client required)
pip install oracledb>=2.0.0

# Install other dependencies
pip install -r requirements_new.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your OIPA connection details
```

### Important: Oracle Client Libraries
This project now uses `python-oracledb` which **does not require Oracle Client installation**. It works in "thin mode" using pure Python. This eliminates the `DPI-1047` error completely.

If you have Oracle Client installed, it will automatically use "thick mode" for better performance.

## Configuration

Edit `.env` file with your OIPA environment details:

```bash
# OIPA Database
OIPA_DB_HOST=your-oipa-host
OIPA_DB_SERVICE_NAME=OIPA
OIPA_DB_USERNAME=your-username
OIPA_DB_PASSWORD=your-password

# OIPA Web Service
OIPA_WS_ENDPOINT=http://your-oipa-server:8080/pas/services/FileReceived
OIPA_WS_USERNAME=webservice-user
OIPA_WS_PASSWORD=webservice-password
```

## Testing Connection

```bash
# Test database connectivity
python scripts/test_connection.py
```

## Running the Server

```bash
# Run the MCP server
python -m oipa_mcp.server

# Or using the installed command
oipa-mcp
```

## Usage Examples

### Searching Policies
```
User: "Find policies for María García"
MCP: Found 3 results:
1. VG01-002-561-000001063 - María García Rodríguez (Active)
2. VG01-002-561-000001128 - María García López (Active)  
3. VG01-002-561-000000987 - María García Sánchez (Cancelled)
```

### Policy Analytics
```
User: "How many policies do we have by status?"
MCP: Total 15,847 policies across 4 statuses:
- Active: 14,203 policies (89.6%)
- Pending: 1,234 policies (7.8%)
- Cancelled: 380 policies (2.4%)
- Suspended: 30 policies (0.2%)
```

### Detailed Policy Information
```
User: "Get details for policy VG01-002-561-000001063"
MCP: Policy Details:
- Number: VG01-002-561-000001063
- Name: Term Life Policy
- Status: Active
- Client: María García Rodríguez (Tax ID: RFC123456789)
- Plan: Standard Term Life 20 Year
- Issue Date: 2023-03-15
```

## Troubleshooting

### Oracle Connection Issues

**Problem**: `DPI-1047: Cannot locate a 64-bit Oracle Client library`

**Solution**: This error is completely eliminated with the new `python-oracledb` package. Run the installation script.

**Problem**: Connection timeout or authentication errors

**Solution**: 
1. Verify your `.env` configuration
2. Test with: `python scripts/test_connection.py`
3. Check OIPA database accessibility

### Performance Issues

**Problem**: Slow query responses

**Solution**:
1. Adjust connection pool settings in `.env`
2. Enable query result limits
3. Check database index performance

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/oipa_mcp/
```

## Architecture

- **MCP Server**: Implements Model Context Protocol for AI integration
- **Oracle Connector**: Direct database access using modern `python-oracledb`
- **Tool Framework**: Extensible tool system for OIPA operations
- **Query Builder**: Optimized queries for OIPA table structure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review OIPA documentation
