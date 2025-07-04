"""
OIPA MCP Server - Fixed Version

Main MCP server implementation for Oracle OIPA integration.
Provides intelligent tools for insurance policy administration.
"""

import asyncio
import sys
from typing import Any, Sequence
from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool as MCPTool

from .config import config
from .connectors import oipa_db
from .tools import AVAILABLE_TOOLS


class OipaMCPServer:
    """
    OIPA MCP Server implementation
    
    Manages the MCP server lifecycle, tool registration, and request handling.
    """
    
    def __init__(self):
        self.server = Server(config.mcp_server.name)
        self.tools = AVAILABLE_TOOLS
        self._setup_logging()
        self._register_handlers()
    
    def _setup_logging(self):
        """Configure logging based on config"""
        logger.remove()  # Remove default handler
        
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        if config.logging.format == "json":
            log_format = "{time} | {level} | {name}:{function}:{line} | {message}"
        
        # Console logging
        logger.add(
            sys.stderr,
            format=log_format,
            level=config.logging.level,
            colorize=True
        )
        
        # File logging (if configured)
        if config.logging.file:
            logger.add(
                config.logging.file,
                format=log_format,
                level=config.logging.level,
                rotation="1 day",
                retention="30 days"
            )
        
        logger.info(f"OIPA MCP Server starting - version {config.mcp_server.version}")
    
    def _register_handlers(self):
        """Register MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[MCPTool]:
            """List all available tools"""
            try:
                mcp_tools = []
                
                for tool in self.tools:
                    mcp_tool = MCPTool(
                        name=tool.name,
                        description=tool.description,
                        inputSchema=tool.input_schema
                    )
                    mcp_tools.append(mcp_tool)
                
                logger.info(f"Listed {len(mcp_tools)} available tools")
                return mcp_tools
                
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return []
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> Sequence[Any]:
            """Execute a tool with given arguments"""
            try:
                logger.info(f"Executing tool: {name} with arguments: {arguments}")
                
                # Find the tool
                tool = None
                for available_tool in self.tools:
                    if available_tool.name == name:
                        tool = available_tool
                        break
                
                if not tool:
                    error_msg = f"Tool '{name}' not found"
                    logger.error(error_msg)
                    return [{"type": "text", "text": f"Error: {error_msg}"}]
                
                # Execute the tool
                result = await tool.execute(arguments)
                
                # Format response for MCP
                if isinstance(result, dict) and result.get("success") is False:
                    # Error response
                    error_text = f"Tool execution failed: {result.get('error', 'Unknown error')}"
                    if result.get("details"):
                        error_text += f"\nDetails: {result['details']}"
                    return [{"type": "text", "text": error_text}]
                else:
                    # Success response
                    return [{"type": "text", "text": self._format_tool_response(result)}]
                        
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [{"type": "text", "text": f"Error: {error_msg}"}]
    
    def _format_tool_response(self, result: Any) -> str:
        """Format tool response for display"""
        try:
            if isinstance(result, dict):
                if "data" in result:
                    return self._format_data_response(result["data"])
                else:
                    return str(result)
            elif isinstance(result, list):
                return self._format_list_response(result)
            else:
                return str(result)
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return f"Response formatting error: {str(e)}"
    
    def _format_data_response(self, data: Any) -> str:
        """Format data response with nice formatting"""
        if isinstance(data, list):
            return self._format_list_response(data)
        elif isinstance(data, dict):
            return self._format_dict_response(data)
        else:
            return str(data)
    
    def _format_list_response(self, data: list) -> str:
        """Format list response (e.g., search results)"""
        if not data:
            return "No results found."
        
        if len(data) == 1:
            return f"Found 1 result:\n{self._format_dict_response(data[0])}"
        else:
            formatted_items = []
            for i, item in enumerate(data[:10], 1):  # Limit to first 10 items
                formatted_items.append(f"{i}. {self._format_dict_response(item, compact=True)}")
            
            result = f"Found {len(data)} results:\n" + "\n".join(formatted_items)
            if len(data) > 10:
                result += f"\n... and {len(data) - 10} more results"
            return result
    
    def _format_dict_response(self, data: dict, compact: bool = False) -> str:
        """Format dictionary response"""
        if compact:
            # Compact format for list items
            if "policy_number" in data:
                client_name = data.get("client", {}).get("name", "Unknown")
                status = data.get("status", "Unknown")
                return f"{data['policy_number']} - {client_name} ({status})"
            elif "name" in data and "count" in data:
                return f"{data['name']}: {data['count']}"
            else:
                # Generic compact format
                key_fields = ["name", "number", "id", "guid"]
                for field in key_fields:
                    if field in data:
                        return f"{data[field]}"
                return str(data)
        else:
            # Full format for single items
            formatted_lines = []
            for key, value in data.items():
                if isinstance(value, dict):
                    formatted_lines.append(f"{key.title()}:")
                    for sub_key, sub_value in value.items():
                        formatted_lines.append(f"  {sub_key.replace('_', ' ').title()}: {sub_value}")
                elif isinstance(value, list):
                    formatted_lines.append(f"{key.title()}: {len(value)} items")
                else:
                    formatted_lines.append(f"{key.replace('_', ' ').title()}: {value}")
            return "\n".join(formatted_lines)
    
    async def initialize(self):
        """Initialize the server and its dependencies"""
        try:
            # Validate configuration
            config.validate()
            logger.info("Configuration validated successfully")
            
            # Initialize database connection
            await oipa_db.initialize()
            logger.info("Database connection initialized")
            
            # Test database connectivity
            if await oipa_db.test_connection():
                logger.info("Database connection test passed")
            else:
                logger.warning("Database connection test failed - some tools may not work")
                
        except Exception as e:
            logger.error(f"Server initialization failed: {e}")
            raise
    
    async def run(self):
        """Run the MCP server with proper error handling"""
        try:
            # Initialize server components
            await self.initialize()
            
            # Start MCP server
            logger.info(f"Starting MCP server: {config.mcp_server.name}")
            
            # Use the stdio server properly
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream, 
                    write_stream, 
                    InitializationOptions(
                        server_name=config.mcp_server.name,
                        server_version=config.mcp_server.version
                    )
                )
                
        except Exception as e:
            logger.error(f"Server runtime error: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up server resources")
            await oipa_db.close()
            logger.info("Server shutdown complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global server instance
app = OipaMCPServer()


async def main_async():
    """Async main entry point"""
    try:
        await app.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point for the MCP server"""
    try:
        # Use asyncio.run with proper exception handling
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
