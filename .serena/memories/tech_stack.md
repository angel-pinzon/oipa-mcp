# OIPA MCP Server - Technology Stack (Updated)

## Core Technology Stack

### MCP Server Framework
- **MCP Protocol**: Latest MCP (Model Context Protocol) implementation
- **Python**: 3.8+ with full async/await support
- **Pydantic**: 2.0+ for data validation and type safety
- **aiohttp**: 3.8+ for async HTTP operations

### Database & Connectivity
- **Oracle Database**: Direct connection to OIPA database
- **cx-oracle**: 8.3+ Oracle database driver with connection pooling
- **Connection Pooling**: Async connection pool management
- **Query Builder**: Custom query builder for OIPA table structure

### OIPA Integration
- **AsXML Format**: Support for OIPA's native XML format
- **FileReceived Web Service**: SOAP web service integration (structure ready)
- **Push Framework**: Async messaging integration (structure ready)
- **OIPA Tables**: Direct access to AsPolicy, AsClient, AsRole, AsActivity, etc.

### Configuration & Environment
- **python-dotenv**: Environment variable management
- **PyYAML**: YAML configuration file support
- **Dataclasses**: Type-safe configuration objects
- **Environment Validation**: Automatic configuration validation

### Logging & Monitoring
- **Loguru**: Advanced logging with structured output
- **JSON Logging**: Structured logging for production
- **Performance Metrics**: Query timing and execution metrics
- **Health Checks**: Database connectivity monitoring

### Development & Testing
- **pytest**: Testing framework with async support
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking framework for testing
- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **MyPy**: Static type checking

### XML & Data Processing
- **lxml**: XML processing for AsXML and SOAP
- **Jinja2**: Template engine for XML generation
- **Data Transformation**: OIPA-specific data formatters

### Deployment & Production
- **Docker Ready**: Container deployment configuration
- **Environment Management**: Multi-environment support
- **SSL/TLS Support**: Secure connections
- **Connection Pooling**: Production-grade database pooling

## Architecture Patterns

### Async First Design
- Full async/await implementation
- Non-blocking database operations
- Concurrent request handling
- Async context managers for resource management

### Type Safety
- Complete Pydantic models for data validation
- Type hints throughout codebase
- Runtime type checking
- Schema validation for tool inputs

### Error Handling
- Custom exception hierarchy
- Graceful error recovery
- Structured error responses
- Comprehensive logging

### Extensibility
- Plugin-based tool architecture
- Base classes for easy extension
- Configuration-driven tool registration
- Modular connector system

## OIPA-Specific Technologies

### Database Schema Knowledge
- AsPolicy, AsClient, AsRole table structures
- AsActivity transaction history
- AsSegment policy segments
- AsPlan product definitions

### Integration Protocols
- **SOAP/XML**: FileReceived web service protocol
- **AsXML**: OIPA native data exchange format
- **Math Variables**: OIPA calculation engine integration
- **Transaction XML**: OIPA transaction execution format

### Business Logic Integration
- Insurance policy lifecycle management
- Client relationship handling
- Transaction processing workflows
- Premium and claims calculations

## Performance Considerations

### Database Optimization
- Connection pooling with configurable limits
- Query optimization for OIPA schema
- Prepared statements and parameter binding
- Result set pagination

### Memory Management
- Async generators for large result sets
- Streaming data processing
- Resource cleanup with context managers
- Configurable cache TTL

### Scalability Features
- Horizontal scaling ready
- Stateless server design
- Database connection sharing
- Configurable resource limits

## Development Environment
- **IDE Agnostic**: Works with VS Code, PyCharm, etc.
- **Environment Isolation**: Virtual environment support
- **Hot Reload**: Development server with auto-reload
- **Debug Support**: Full debugging capabilities with proper logging

This technology stack provides a robust, scalable, and maintainable foundation for OIPA integration while ensuring high performance and reliability.
