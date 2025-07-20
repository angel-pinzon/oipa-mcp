# Contributing to OIPA MCP Server

Thank you for your interest in contributing to the OIPA MCP Server! This document provides guidelines and instructions for contributing to the project.

## 🎯 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Prioritize the project's best interests

## 🚀 Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/oipa-mcp-server.git
cd oipa-mcp-server
```

### 3. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Development Guidelines

### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Run these before committing:

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type checking
mypy src/oipa_mcp/
```

### Writing Tests

All new features should include tests:

```python
# tests/test_your_feature.py
import pytest
from oipa_mcp.your_module import YourClass

class TestYourFeature:
    @pytest.mark.asyncio
    async def test_feature_behavior(self):
        # Arrange
        instance = YourClass()
        
        # Act
        result = await instance.your_method()
        
        # Assert
        assert result == expected_value
```

Run tests:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_your_feature.py -v

# Run with coverage
pytest tests/ --cov=src/oipa_mcp --cov-report=html
```

### Documentation

- Add docstrings to all public functions and classes
- Update README.md if adding new features
- Include usage examples in docstrings

Example docstring:

```python
async def search_policies(
    self,
    search_term: str,
    status: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for insurance policies using various criteria.
    
    Args:
        search_term: Policy number, client name, or tax ID to search for
        status: Optional status filter ('active', 'cancelled', 'pending')
        limit: Maximum number of results to return (default: 20)
    
    Returns:
        List of policy dictionaries containing policy information
    
    Example:
        >>> results = await db.search_policies("John Smith", status="active")
        >>> print(f"Found {len(results)} active policies")
    """
```

## 🔧 Making Changes

### Adding a New Tool

1. Create the tool class in `src/oipa_mcp/tools/`:

```python
# src/oipa_mcp/tools/your_tool.py
from typing import Any, Dict
from .base import QueryTool

class YourNewTool(QueryTool):
    """Tool description"""
    
    @property
    def name(self) -> str:
        return "oipa_your_tool_name"
    
    @property
    def description(self) -> str:
        return "Detailed description with examples"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                # Define parameters
            },
            "required": ["required_params"]
        }
    
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Any:
        # Implementation
        pass
```

2. Register in `src/oipa_mcp/tools/__init__.py`
3. Add tests in `tests/test_your_tool.py`
4. Update README.md with usage examples

### Database Query Patterns

When adding database queries:

```python
# Use the query builder pattern
from ..connectors import OipaQueryBuilder

# In your tool
query, params = OipaQueryBuilder.your_query_method(
    param1=value1,
    param2=value2
)
results = await self._execute_query(query, params)
```

### Error Handling

Always handle errors gracefully:

```python
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return {
        "success": False,
        "error": "User-friendly error message",
        "details": str(e)
    }
```

## 📤 Submitting Changes

### 1. Commit Your Changes

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add fuzzy search support to policy search tool"

# Bad
git commit -m "Update code"
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template with:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if applicable)

### Pull Request Checklist

- [ ] Code follows the project's style guidelines
- [ ] All tests pass (`pytest tests/`)
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main

## 🐛 Reporting Issues

### Before Creating an Issue

1. Check existing issues to avoid duplicates
2. Try to reproduce the issue
3. Collect relevant information:
   - Python version
   - OIPA version
   - Error messages
   - Steps to reproduce

### Issue Template

```markdown
**Description**
Clear description of the issue

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Python version: 
- OIPA version:
- OS:
- Database: Oracle version

**Error Messages**
```
Paste any error messages here
```
```

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check if the feature has already been requested
2. Clearly describe the use case
3. Provide examples of how it would work
4. Explain why existing functionality doesn't meet your needs

## 🔍 Code Review Process

All submissions require review:

1. Automated checks must pass (tests, linting, type checking)
2. At least one maintainer approval required
3. Changes may be requested - please be patient and responsive
4. Once approved, a maintainer will merge your PR

## 📚 Resources

### OIPA Documentation
- [OIPA Database Schema](docs/oipa_schema.md)
- [AsXML Format](docs/asxml_format.md)
- [Transaction Types](docs/transactions.md)

### Python Resources
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
- [Type Hints](https://docs.python.org/3/library/typing.html)
- [MCP Protocol](https://modelcontextprotocol.io)

### Testing Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Asyncio](https://pytest-asyncio.readthedocs.io/)

## 🏆 Recognition

Contributors will be:
- Listed in the project's contributors file
- Mentioned in release notes
- Given credit in relevant documentation

## ❓ Questions?

If you have questions:

1. Check the [FAQ](https://github.com/yourusername/oipa-mcp-server/wiki/FAQ)
2. Ask in [Discussions](https://github.com/yourusername/oipa-mcp-server/discussions)
3. Reach out to maintainers

Thank you for contributing to OIPA MCP Server! 🎉
