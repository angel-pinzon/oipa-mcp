# OIPA MCP Server - Suggested Commands (Updated)

## Development Commands

### Setup and Installation
```bash
# Initial setup
git clone https://github.com/your-org/oipa-mcp.git
cd oipa-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your OIPA connection details
```

### Development Workflow
```bash
# Run the MCP server
python -m oipa_mcp.server

# Or using the installed command
oipa-mcp

# Test database connectivity
python scripts/test_connection.py

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src/oipa_mcp --cov-report=html

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/oipa_mcp/
```

### Testing Commands
```bash
# Unit tests only
pytest tests/test_basic.py -v

# Integration tests (requires OIPA connection)
pytest tests/ -k "integration" -v

# Test specific tool
pytest tests/ -k "search_policies" -v

# Test with debug output
pytest tests/ -v -s --log-cli-level=DEBUG
```

### Database Operations
```bash
# Test OIPA database connection
python scripts/test_connection.py

# Validate configuration
python -c "from oipa_mcp.config import config; config.validate(); print('✅ Config valid')"

# Test specific query
python -c "
import asyncio
from oipa_mcp.connectors import oipa_db
async def test():
    await oipa_db.initialize()
    result = await oipa_db.execute_scalar('SELECT COUNT(*) FROM AsPolicy WHERE ROWNUM <= 1')
    print(f'Policies accessible: {result is not None}')
    await oipa_db.close()
asyncio.run(test())
"
```

### MCP Server Operations
```bash
# Start server with debug logging
LOG_LEVEL=DEBUG python -m oipa_mcp.server

# Start server with specific config
OIPA_DB_HOST=myhost OIPA_DB_SERVICE_NAME=OIPA python -m oipa_mcp.server

# Test MCP tools manually (requires MCP client)
# Use with Claude Desktop or other MCP client

# Check server health
curl -X GET http://localhost:8080/health  # If HTTP endpoint added
```

### Production Commands
```bash
# Production startup
LOG_LEVEL=INFO \
LOG_FORMAT=json \
LOG_FILE=/var/log/oipa-mcp/server.log \
python -m oipa_mcp.server

# Docker build
docker build -t oipa-mcp:latest .

# Docker run
docker run -d \
  --name oipa-mcp \
  --env-file .env \
  -p 8080:8080 \
  oipa-mcp:latest

# Check logs
docker logs oipa-mcp -f
```

### Development Tools
```bash
# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Generate documentation
sphinx-build -b html docs/ docs/_build/html

# Profile performance
python -m cProfile -o profile.stats scripts/test_connection.py
```

### Debugging Commands
```bash
# Debug database queries
LOG_LEVEL=DEBUG python -c "
import asyncio
from oipa_mcp.tools.policy_tools import SearchPoliciesQuality
async def debug():
    tool = SearchPoliciesQuality()
    result = await tool.execute({'search_term': 'test', 'limit': 1})
    print(result)
asyncio.run(debug())
"

# Test specific tool execution
python -c "
import asyncio
from oipa_mcp.tools import AVAILABLE_TOOLS
async def test_tool():
    tool = AVAILABLE_TOOLS[0]  # First tool
    print(f'Testing: {tool.name}')
    print(f'Schema: {tool.input_schema}')
asyncio.run(test_tool())
"

# Validate OIPA table structure
python -c "
import asyncio
from oipa_mcp.connectors import oipa_db
async def check_tables():
    await oipa_db.initialize()
    tables = ['AsPolicy', 'AsClient', 'AsRole', 'AsActivity']
    for table in tables:
        try:
            count = await oipa_db.execute_scalar(f'SELECT COUNT(*) FROM {table} WHERE ROWNUM <= 1')
            print(f'✅ {table}: accessible')
        except Exception as e:
            print(f'❌ {table}: {e}')
    await oipa_db.close()
asyncio.run(check_tables())
"
```

### Monitoring Commands
```bash
# Monitor server performance
tail -f logs/oipa-mcp.log | grep -E "(ERROR|WARN|execution_time)"

# Check database connection health
python -c "
import asyncio
from oipa_mcp.connectors import oipa_db
async def health():
    healthy = await oipa_db.test_connection()
    print(f'Database health: {\"✅ OK\" if healthy else \"❌ FAIL\"}')
asyncio.run(health())
"

# Memory usage monitoring
python -m memory_profiler scripts/test_connection.py
```

### Utility Commands
```bash
# Generate sample data for testing
python scripts/generate_test_data.py

# Export configuration template
python -c "
from oipa_mcp.config import Config
import yaml
config = Config()
print(yaml.dump(config.to_dict(), default_flow_style=False))
" > config_template.yaml

# Backup current configuration
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

## Oracle Database Specific Commands

### Connection Testing
```bash
# Test TNS connectivity (if using TNS)
tnsping OIPA

# Test with SQLPlus
sqlplus username/password@host:port/service_name

# Test with Python
python -c "
import cx_Oracle
try:
    conn = cx_Oracle.connect('user/pass@host:port/service')
    print('✅ Oracle connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Oracle connection failed: {e}')
"
```

### Performance Optimization
```bash
# Check Oracle session info
python -c "
import asyncio
from oipa_mcp.connectors import oipa_db
async def session_info():
    result = await oipa_db.execute_query(
        'SELECT SID, SERIAL#, USERNAME, PROGRAM FROM V\$SESSION WHERE USERNAME = USER'
    )
    print(f'Active sessions: {result}')
asyncio.run(session_info())
"

# Monitor query execution times
LOG_LEVEL=DEBUG python scripts/test_connection.py 2>&1 | grep "Query executed"
```

These commands provide comprehensive coverage for development, testing, deployment, and maintenance of the OIPA MCP Server.
