#!/usr/bin/env python3
"""
Claude Desktop Configuration Script for OIPA MCP Server

This script helps configure Claude Desktop to use the OIPA MCP Server.
It creates the necessary configuration files and provides setup instructions.
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, Any

def get_claude_desktop_config_path() -> Path:
    """Get the Claude Desktop configuration directory path based on OS"""
    system = platform.system()
    
    if system == "Windows":
        # Windows: %APPDATA%\Claude\claude_desktop_config.json
        appdata = os.environ.get('APPDATA', '')
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":
        # macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
        home = Path.home()
        return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        # Linux: ~/.config/claude/claude_desktop_config.json
        home = Path.home()
        return home / ".config" / "claude" / "claude_desktop_config.json"

def create_mcp_config(
    db_host: str = "192.168.1.50",
    db_port: str = "1521",
    db_service: str = "oipadev",
    db_username: str = "oipa",
    db_password: str = "your_password_here",
    project_path: str = None
) -> Dict[str, Any]:
    """Create MCP server configuration for Claude Desktop"""
    
    if project_path is None:
        project_path = str(Path(__file__).parent.parent.absolute())
    
    config = {
        "mcpServers": {
            "oipa-mcp": {
                "command": "python",
                "args": ["-m", "oipa_mcp.server"],
                "cwd": project_path,
                "env": {
                    "OIPA_DB_HOST": db_host,
                    "OIPA_DB_PORT": db_port,
                    "OIPA_DB_SERVICE_NAME": db_service,
                    "OIPA_DB_USERNAME": db_username,
                    "OIPA_DB_PASSWORD": db_password,
                    "LOG_LEVEL": "INFO",
                    "LOG_FORMAT": "text"
                }
            }
        }
    }
    
    return config

def setup_claude_desktop_integration():
    """Main setup function for Claude Desktop integration"""
    
    print("🚀 OIPA MCP Server - Claude Desktop Integration Setup")
    print("=" * 60)
    
    # Get current project path
    current_path = Path(__file__).parent.parent.absolute()
    print(f"📁 Project Path: {current_path}")
    
    # Get Claude Desktop config path
    config_path = get_claude_desktop_config_path()
    print(f"📁 Claude Desktop Config: {config_path}")
    
    # Check if Claude Desktop is installed
    if not config_path.parent.exists():
        print("⚠️  Claude Desktop configuration directory not found.")
        print(f"   Expected at: {config_path.parent}")
        print("   Please ensure Claude Desktop is installed.")
        print()
        print("📥 Download Claude Desktop:")
        print("   https://claude.ai/desktop")
        return False
    
    # Get database credentials
    print()
    print("🔧 Database Configuration")
    print("-" * 30)
    
    # Try to read from .env file
    env_file = current_path / ".env"
    db_config = {}
    
    if env_file.exists():
        print("✅ Found .env file, reading database configuration...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    if key == 'OIPA_DB_HOST':
                        db_config['host'] = value
                    elif key == 'OIPA_DB_PORT':
                        db_config['port'] = value
                    elif key == 'OIPA_DB_SERVICE_NAME':
                        db_config['service'] = value
                    elif key == 'OIPA_DB_USERNAME':
                        db_config['username'] = value
                    elif key == 'OIPA_DB_PASSWORD':
                        db_config['password'] = value
    
    # Use defaults or prompt for missing values
    db_host = db_config.get('host', '192.168.1.50')
    db_port = db_config.get('port', '1521')
    db_service = db_config.get('service', 'oipadev')
    db_username = db_config.get('username', 'oipa')
    db_password = db_config.get('password', 'your_password_here')
    
    print(f"   Host: {db_host}:{db_port}")
    print(f"   Service: {db_service}")
    print(f"   Username: {db_username}")
    print(f"   Password: {'*' * len(db_password) if db_password != 'your_password_here' else '⚠️  NOT SET'}")
    
    if db_password == 'your_password_here':
        print()
        print("⚠️  Database password not configured!")
        print("   Please update your .env file with the correct OIPA_DB_PASSWORD")
        return False
    
    # Create MCP configuration
    print()
    print("🔧 Creating MCP Configuration")
    print("-" * 30)
    
    mcp_config = create_mcp_config(
        db_host=db_host,
        db_port=db_port,
        db_service=db_service,
        db_username=db_username,
        db_password=db_password,
        project_path=str(current_path)
    )
    
    # Check if config file already exists
    existing_config = {}
    if config_path.exists():
        print(f"✅ Found existing Claude Desktop config")
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Existing config file has invalid JSON, creating backup...")
            backup_path = config_path.with_suffix('.backup.json')
            if config_path.exists():
                config_path.rename(backup_path)
                print(f"   Backup saved to: {backup_path}")
    
    # Merge configurations
    if 'mcpServers' not in existing_config:
        existing_config['mcpServers'] = {}
    
    existing_config['mcpServers'].update(mcp_config['mcpServers'])
    
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write configuration
    with open(config_path, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    print(f"✅ Configuration written to: {config_path}")
    
    # Test the MCP server
    print()
    print("🧪 Testing MCP Server")
    print("-" * 30)
    
    test_command = f'cd "{current_path}" && python scripts/test_connection.py'
    print(f"Running: {test_command}")
    
    import subprocess
    try:
        result = subprocess.run([
            "python", "scripts/test_connection.py"
        ], cwd=current_path, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ OIPA MCP Server test passed!")
        else:
            print("❌ OIPA MCP Server test failed!")
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Test timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    # Success instructions
    print()
    print("🎉 Claude Desktop Integration Setup Complete!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Restart Claude Desktop application")
    print("2. Open a new conversation in Claude Desktop")
    print("3. Try using OIPA commands like:")
    print('   • "Search for policies with status active"')
    print('   • "How many policies do we have by status?"')
    print('   • "Show details for policy ATL20055008"')
    print()
    print("🔧 Available OIPA MCP Tools:")
    print("   • oipa_search_policies - Search policies by various criteria")
    print("   • oipa_get_policy_details - Get comprehensive policy information")
    print("   • oipa_policy_counts_by_status - Get policy distribution analytics")
    print()
    print("📁 Configuration saved to:")
    print(f"   {config_path}")
    print()
    print("🐛 Troubleshooting:")
    print("   • Check Claude Desktop logs if tools don't appear")
    print("   • Verify database connection with: python scripts/test_connection.py")
    print("   • Ensure Claude Desktop has permission to execute Python scripts")
    
    return True

if __name__ == "__main__":
    success = setup_claude_desktop_integration()
    exit(0 if success else 1)
