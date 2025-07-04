"""
OIPA MCP Server

MCP (Model Context Protocol) server for Oracle OIPA (Insurance Policy Administration)
integration. Provides intelligent tools for policy management, client operations,
transaction execution, and analytics.

Based on OIPA documentation analysis and real-world integration patterns.
"""

__version__ = "1.0.0"
__author__ = "OIPA MCP Team"
__email__ = "oipa-mcp@company.com"

from .server import app
from .config import Config

__all__ = ["app", "Config"]
