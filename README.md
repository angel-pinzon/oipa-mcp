# OIPA MCP Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)

A Model Context Protocol (MCP) server that enables AI assistants to interact with Oracle OIPA (Insurance Policy Administration) systems using natural language.

## 🌟 What is this?

This project provides a bridge between AI assistants (like Claude) and Oracle OIPA insurance systems. It allows you to:

- Search insurance policies using natural language
- Get detailed policy information with a simple query
- View real-time analytics and dashboards
- Execute OIPA transactions through conversational interfaces

No more complex SQL queries or navigating through multiple OIPA screens - just ask in plain language!

## 🚀 Features

### Core Capabilities
- **🔍 Natural Language Policy Search** - Search by policy number, client name, tax ID, or status
- **📋 Comprehensive Policy Details** - View complete policy information including clients, plans, and coverage
- **📊 Real-time Analytics** - Instant dashboards showing policy distributions and metrics
- **🔗 Direct OIPA Integration** - Native connection to OIPA database with no intermediaries
- **⚡ High Performance** - Async architecture with connection pooling for fast responses

### Available Tools

| Tool | Description | Example Query |
|------|-------------|---------------|
| `oipa_search_policies` | Search policies with intelligent filtering | "Find all active policies for John Smith" |
| `oipa_get_policy_details` | Get comprehensive policy information | "Show me details for policy VG01-002-561-000001063" |
| `oipa_policy_counts_by_status` | View policy distribution analytics | "How many policies do we have by status?" |

## 📋 Prerequisites

- Python 3.8 or higher
- Access to an Oracle OIPA database
- MCP-compatible client (e.g., Claude Desktop, custom MCP client)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/oipa-mcp-server.git
cd oipa-mcp-server
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: This project uses the modern `oracledb` library which doesn't require Oracle Client installation!

### 4. Configure Environment

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your OIPA connection details
```

## ⚙️ Configuration

### Basic Configuration (.env file)

```bash
# OIPA Database Connection
OIPA_DB_HOST=your-oipa-host.com
OIPA_DB_PORT=1521
OIPA_DB_SERVICE_NAME=OIPA
OIPA_DB_USERNAME=your_username
OIPA_DB_PASSWORD=your_password

# Optional: Default Schema (if different from username)
OIPA_DB_DEFAULT_SCHEMA=OIPA_SCHEMA

# Connection Pool Settings
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=5

# Logging
LOG_LEVEL=INFO
```

### Oracle Cloud Wallet Configuration

If using Oracle Autonomous Database or Cloud:

```bash
# Connection Type
OIPA_DB_CONNECTION_TYPE=cloud_wallet

# Wallet Configuration
OIPA_DB_WALLET_LOCATION=/path/to/wallet
OIPA_DB_SERVICE_NAME=oipa_high

# Optional: Wallet Password (for encrypted wallets)
OIPA_DB_WALLET_PASSWORD=wallet_password
```

## 🏃‍♂️ Running the Server

### Quick Start

```bash
# Run the MCP server
python -m oipa_mcp.server
```

### Testing Connection

```bash
# Verify OIPA database connectivity
python scripts/test_connection.py
```

### Integration with Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "oipa": {
      "command": "python",
      "args": ["-m", "oipa_mcp.server"],
      "cwd": "/path/to/oipa-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/oipa-mcp-server"
      }
    }
  }
}
```

## 💬 Usage Examples

### Policy Search
```
User: "Find policies for María García"
Assistant: I found 3 policies for María García:

1. **VG01-002-561-000001063** - María García Rodríguez
   - Status: Active
   - Plan: Vida Universal
   - Created: 2023-01-15

2. **VG01-002-561-000001128** - María García López
   - Status: Active
   - Plan: Seguro Temporal
   - Created: 2023-03-20

3. **VG01-002-561-000000987** - María García Sánchez
   - Status: Cancelled
   - Plan: Vida Entera
   - Created: 2022-11-10
```

### Policy Details
```
User: "Show me details for policy VG01-002-561-000001063"
Assistant: Here are the details for policy VG01-002-561-000001063:

**Policy Information**
- Policy Number: VG01-002-561-000001063
- Policy Name: Seguro de Vida Individual
- Status: Active
- Creation Date: 2023-01-15

**Primary Insured**
- Name: María García Rodríguez
- Tax ID: GARM850101ABC
- Birth Date: 1985-01-01
- Gender: Female

**Plan Details**
- Plan Name: Vida Universal
- Plan Code: VU-001
- Coverage Amount: $1,000,000 MXN
```

### Analytics Dashboard
```
User: "How many policies do we have by status?"
Assistant: Here's the current policy distribution:

📊 **Total Policies: 15,847**

- ✅ Active: 14,203 (89.6%)
- ⏳ Pending: 1,234 (7.8%)
- ❌ Cancelled: 380 (2.4%)
- ⚠️ Suspended: 30 (0.2%)
```

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   AI Assistant  │────▶│  OIPA MCP Server │────▶│   Oracle OIPA   │
│    (Claude)     │◀────│                  │◀────│    Database     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         │                       ├── Policy Tools         │
         │                       ├── Client Tools         │
         │                       └── Analytics Tools      │
         │                                                │
         └────────── Natural Language ────────────────────┘
```

### Project Structure

```
oipa-mcp-server/
├── src/oipa_mcp/
│   ├── server.py           # Main MCP server implementation
│   ├── config.py           # Configuration management
│   ├── connectors/         # OIPA integration layer
│   │   ├── database.py     # Oracle database connector
│   │   └── query_builder.py # SQL query construction
│   └── tools/              # MCP tool implementations
│       ├── base.py         # Base tool classes
│       └── policy_tools.py # Policy management tools
├── scripts/
│   └── test_connection.py  # Database connectivity test
├── tests/                  # Unit and integration tests
├── .env.example           # Example configuration
└── requirements.txt       # Python dependencies
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/oipa_mcp --cov-report=html

# Code formatting
black src/ tests/

# Linting
ruff check src/ tests/

# Type checking
mypy src/oipa_mcp/
```

### Adding New Tools

1. Create a new tool class in `src/oipa_mcp/tools/`:

```python
from typing import Any, Dict
from .base import QueryTool

class MyNewTool(QueryTool):
    """Description of what your tool does"""
    
    @property
    def name(self) -> str:
        return "oipa_my_new_tool"
    
    @property
    def description(self) -> str:
        return """
        Detailed description of your tool's functionality.
        Include examples of how to use it.
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of parameter"
                }
            },
            "required": ["param1"]
        }
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Any:
        # Implement your tool logic here
        param1 = arguments["param1"]
        
        # Use query builder for database operations
        query, params = OipaQueryBuilder.your_query_method(param1)
        results = await self._execute_query(query, params)
        
        return results
```

2. Register the tool in `src/oipa_mcp/tools/__init__.py`:

```python
from .my_new_tool import MyNewTool

AVAILABLE_TOOLS = [
    # ... existing tools
    MyNewTool()
]
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check your connection settings
python scripts/test_connection.py

# Verify environment variables
python -c "from oipa_mcp.config import config; print(config.database.dsn)"
```

#### Oracle Client Not Found

This project uses `oracledb` in thin mode - no Oracle Client needed! If you see this error, ensure you're using the latest version:

```bash
pip install --upgrade oracledb
```

#### Permission Denied on OIPA Tables

Ensure your database user has SELECT permissions on these OIPA tables:
- AsPolicy
- AsClient
- AsRole
- AsSegment
- AsPlan
- AsCode

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Run with debug output
python -m oipa_mcp.server
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `pytest tests/`
5. **Commit**: `git commit -m 'Add amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 and use Black for formatting
- Add tests for new functionality
- Update documentation for API changes
- Keep commits focused and atomic
- Write clear commit messages

## 📈 Roadmap

### Current Release (v1.0) ✅
- Core MCP server infrastructure
- Basic policy search and details
- Real-time analytics
- Oracle database integration

### Next Release (v1.1) 🚧
- Client portfolio management
- Transaction history search
- Advanced filtering options
- Performance optimizations

### Future Plans (v2.0) 📋
- OIPA Web Service integration
- Transaction execution capabilities
- Batch operations support
- Multi-language support

### Long Term Vision 🔮
- AI-powered insights
- Predictive analytics
- Workflow automation
- Custom reporting tools

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Oracle OIPA development team for the comprehensive insurance platform
- Anthropic for the MCP specification and Claude AI
- The open-source community for invaluable tools and libraries

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/oipa-mcp-server/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/oipa-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/oipa-mcp-server/discussions)

---

**Made with ❤️ for the Insurance Technology Community**

*Disclaimer: This is an independent project and is not officially affiliated with or endorsed by Oracle Corporation.*
