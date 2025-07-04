#!/usr/bin/env python3
"""
Debug version of OIPA MCP Server
Simplified version to identify the TaskGroup error
"""

import asyncio
import sys
import traceback
from typing import Any, Sequence
from loguru import logger

# Configure simple logging
logger.remove()
logger.add(sys.stderr, level="DEBUG", format="{time} | {level} | {message}")

async def debug_server():
    """Debug version of server startup"""
    try:
        logger.info("=== OIPA MCP Server Debug Mode ===")
        
        # Step 1: Import basic modules
        logger.info("Step 1: Importing basic modules...")
        from mcp.server import Server
        from mcp.server.models import InitializationOptions
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool as MCPTool
        logger.success("✓ Basic MCP modules imported successfully")
        
        # Step 2: Import config
        logger.info("Step 2: Importing config...")
        from src.oipa_mcp.config import config
        logger.success("✓ Config imported successfully")
        
        # Step 3: Import connectors
        logger.info("Step 3: Importing database connector...")
        from src.oipa_mcp.connectors import oipa_db
        logger.success("✓ Database connector imported successfully")
        
        # Step 4: Import tools
        logger.info("Step 4: Importing tools...")
        from src.oipa_mcp.tools import AVAILABLE_TOOLS
        logger.success(f"✓ Tools imported successfully - {len(AVAILABLE_TOOLS)} tools available")
        
        # Step 5: Create server
        logger.info("Step 5: Creating MCP server...")
        server = Server(config.mcp_server.name)
        logger.success("✓ MCP server created successfully")
        
        # Step 6: Register minimal handlers
        logger.info("Step 6: Registering handlers...")
        
        @server.list_tools()
        async def handle_list_tools() -> list[MCPTool]:
            """List all available tools"""
            logger.info("Handler: list_tools called")
            mcp_tools = []
            
            for tool in AVAILABLE_TOOLS:
                mcp_tool = MCPTool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.input_schema
                )
                mcp_tools.append(mcp_tool)
            
            logger.info(f"Returning {len(mcp_tools)} tools")
            return mcp_tools
        
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> Sequence[Any]:
            """Execute a tool with given arguments"""
            logger.info(f"Handler: call_tool called - name={name}")
            return [{"type": "text", "text": f"Tool {name} executed successfully"}]
        
        logger.success("✓ Handlers registered successfully")
        
        # Step 7: Initialize database (optional)
        logger.info("Step 7: Testing database connection...")
        try:
            await oipa_db.initialize()
            if await oipa_db.test_connection():
                logger.success("✓ Database connection test passed")
            else:
                logger.warning("⚠ Database connection test failed - continuing anyway")
        except Exception as e:
            logger.warning(f"⚠ Database initialization failed: {e} - continuing anyway")
        
        # Step 8: Start MCP server
        logger.info("Step 8: Starting MCP server...")
        logger.info("Attempting to start stdio_server...")
        
        async with stdio_server() as streams:
            logger.success("✓ stdio_server context entered")
            
            initialization_options = InitializationOptions(
                server_name=config.mcp_server.name,
                server_version=config.mcp_server.version
            )
            logger.info(f"Created initialization options: {initialization_options}")
            
            logger.info("About to call server.run()...")
            await server.run(
                streams[0], 
                streams[1], 
                initialization_options
            )
            logger.success("✓ Server.run() completed")
            
    except Exception as e:
        logger.error(f"Error in debug_server: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise
    finally:
        logger.info("Cleaning up...")
        try:
            await oipa_db.close()
        except:
            pass

def main():
    """Main entry point"""
    try:
        logger.info("Starting debug server...")
        asyncio.run(debug_server())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
