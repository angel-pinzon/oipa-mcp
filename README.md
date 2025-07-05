# OIPA MCP Server

MCP (Model Context Protocol) server for Oracle OIPA (Insurance Policy Administration) integration.

## Features

### Core Capabilities
- 🔍 **Intelligent Policy Search** - Natural language search across policies, clients, and products
- 📊 **Real-time Analytics** - Policy counts, status distributions, and business metrics  
- 🏢 **Client Management** - Client search, portfolio views, and relationship tracking
- ⚡ **Direct OIPA Integration** - Native Oracle database connectivity and SOAP web services
- 🏷️ **Enhanced Data Display** - Human-readable status and state names from OIPA AsCode lookups

### Available Tools

#### Policy Management
- `oipa_search_policies` - Search policies by number, client name, or tax ID with human-readable status names
- `oipa_get_policy_details` - Get comprehensive policy information including segments, roles, and descriptive state/status names
- `oipa_policy_counts_by_status` - Dashboard-style policy distribution overview with OIPA-configured status descriptions

#### Analytics & Reporting
- Real-time policy status breakdowns
- Client portfolio summaries
- Transaction history analysis

## Quick Start

### Prerequisites
- Python 3.8+
- Oracle Database access to OIPA
- OIPA FileReceived Web Service access

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/oipa-mcp.git
cd oipa-mcp

# Install dependencies (uses modern oracledb - no Oracle Client required!)
pip install -r requirements.txt
# Copy and configure environment
cp .env.example .env
# Edit .env with your OIPA connection details
```

### Configuration

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

### Running the Server

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

### Policy Details
```
User: "Get details for policy VG01-002-561-000001063"
MCP: Policy Number: VG01-002-561-000001063
Policy Name: Seguro de Vida Individual
Status: Active
Primary Client: María García Rodríguez
Tax ID: GARM850101ABC
Plan: Vida Universal
Creation Date: 2023-01-15
```

### Analytics Dashboard
```
User: "How many policies do we have by status?"
MCP: Total 15,847 policies across 4 statuses
Active: 14,203 (89.6%)
Pending: 1,234 (7.8%)
Cancelled: 380 (2.4%)
Suspended: 30 (0.2%)
```

## Architecture

### Components
```
src/oipa_mcp/
├── server.py           # Main MCP server
├── config.py           # Configuration management
├── connectors/         # OIPA integration layer
│   ├── database.py     # Oracle database connector
│   ├── web_service.py  # FileReceived SOAP client
│   └── push_framework.py # Push framework integration
└── tools/              # MCP tools implementation
    ├── policy_tools.py # Policy management tools
    ├── client_tools.py # Client management tools
    └── analytics_tools.py # Analytics and reporting
```

### Integration Methods

1. **Direct Database Access** - Fast queries for read operations
2. **FileReceived Web Service** - Transaction execution and data updates
3. **Push Framework** - Async messaging and notifications

## Development

### Adding New Tools

1. Create tool class inheriting from `BaseTool`:

```python
from .base import QueryTool

class MyNewTool(QueryTool):
    @property
    def name(self) -> str:
        return "oipa_my_new_tool"
    
    @property
    def description(self) -> str:
        return "Description of what this tool does"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Parameter description"}
            },
            "required": ["param1"]
        }
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Any:
        # Implement tool logic
        return {"result": "success"}
```

2. Register in `tools/__init__.py`:

```python
from .my_module import MyNewTool

AVAILABLE_TOOLS = [
    # existing tools...
    MyNewTool()
]
```

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/oipa_mcp --cov-report=html

# Test specific component
pytest tests/test_policy_tools.py -v
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

## OIPA Integration Details

### Supported OIPA Tables
- `AsPolicy` - Policy master data
- `AsClient` - Client/insured information
- `AsRole` - Policy-client relationships
- `AsActivity` - Transaction history
- `AsSegment` - Policy segments/coverages
- `AsPlan` - Product/plan definitions

### Supported Transactions
Based on documented OIPA transaction examples:
- `INTPrintAvisoCobro` - Print billing notices
- `INTPrintCertificado` - Print certificates
- `INTPrintConsentimiento` - Print consent forms

### AsXML Support
Full support for OIPA's AsXML format for data exchange:
```xml
<AsXml>
  <AsPolicy>
    <PolicyGuid>6CCA0B15-EFAC-471F-A698-27949AB9B9C4</PolicyGuid>
    <PolicyNumber>VG01-002-561-000001063</PolicyNumber>
    <PolicyName>Seguro de Vida Individual</PolicyName>
    <!-- ... -->
  </AsPolicy>
</AsXml>
```

## Deployment

### Production Configuration

```bash
# Production environment variables
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/oipa-mcp/server.log

# Database connection pooling
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
DB_POOL_TIMEOUT=30

# Performance tuning
CACHE_TTL=300
MAX_QUERY_RESULTS=1000
QUERY_TIMEOUT=30
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8080
CMD ["python", "-m", "oipa_mcp.server"]
```

### Monitoring

The server includes built-in logging and monitoring:
- Structured JSON logging
- Database connection health checks
- Tool execution metrics
- Error tracking and alerting

## Database Migration (cx_Oracle → oracledb)

🚀 **New in this version**: We've migrated from `cx_Oracle` to the modern `oracledb` library for improved performance and simplified installation.

### Migration Benefits

- ✅ **No Oracle Client Required** - Pure Python implementation
- ✅ **Simplified Installation** - Single `pip install` command  
- ✅ **Better Performance** - Optimized async connection pooling
- ✅ **Enhanced Error Handling** - Improved diagnostics and logging
- ✅ **Cross-Platform** - Works consistently across OS platforms

### Automatic Migration

For existing installations, run the migration script:

```bash
# Run automated migration
python scripts/migrate_to_oracledb.py

# Test the migration
python scripts/test_connection.py
```

### Manual Migration Steps

If you prefer manual migration:

```bash
# 1. Uninstall old dependency
pip uninstall cx_Oracle

# 2. Install new dependency  
pip install oracledb>=2.0.0

# 3. Update requirements.txt (if exists)
sed -i 's/cx-oracle>=8.3.0/oracledb>=2.0.0/g' requirements.txt

# 4. Test connection
python scripts/test_connection.py
```

### Configuration Compatibility

Your existing `.env` configuration remains the same:
- Same connection parameters
- Same database credentials
- Same performance settings

The migration is **backward compatible** - no configuration changes needed!

### Performance Improvements

After migration, you'll benefit from:
- Faster connection establishment
- Better memory usage
- Enhanced async performance
- Improved error reporting
- Optional thick mode for maximum performance


## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   ```bash
   # Test Oracle connectivity
   python scripts/test_connection.py
   
   # Check TNS configuration
   echo $TNS_ADMIN
   tnsping OIPA
   ```

2. **SOAP Web Service Errors**
   ```bash
   # Test FileReceived endpoint
   curl -X POST $OIPA_WS_ENDPOINT \
     -H "Content-Type: text/xml" \
     -d @test_message.xml
   ```

3. **Tool Execution Timeouts**
   ```bash
   # Increase query timeout
   export QUERY_TIMEOUT=60
   
   # Enable query debugging
   export LOG_LEVEL=DEBUG
   ```

### Debugging

Enable debug logging for detailed troubleshooting:

```bash
export LOG_LEVEL=DEBUG
python -m oipa_mcp.server
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Guidelines
- Follow existing code style (Black formatting)
- Add tests for new functionality
- Update documentation for new tools
- Ensure all tests pass before submitting

## Roadmap

### Phase 1 ✅ (Current)
- [x] Core MCP server infrastructure
- [x] Oracle database connectivity
- [x] Basic policy search and details
- [x] Status analytics

### Phase 2 🚧 (In Progress)
- [ ] Client management tools
- [ ] FileReceived web service integration
- [ ] Transaction execution support
- [ ] Enhanced search with fuzzy matching

### Phase 3 📋 (Planned)
- [ ] Push framework integration
- [ ] Advanced analytics and ML insights
- [ ] Workflow automation tools
- [ ] Real-time notifications

### Phase 4 🔮 (Future)
- [ ] External data integration
- [ ] Predictive analytics
- [ ] Automated underwriting support
- [ ] Full workflow orchestration

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: oipa-mcp@company.com
- 📖 Documentation: [GitHub Wiki](https://github.com/your-org/oipa-mcp/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/oipa-mcp/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/oipa-mcp/discussions)

---

**Built with ❤️ for the Insurance Technology Community**
