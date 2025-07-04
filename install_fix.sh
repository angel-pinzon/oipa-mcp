#!/bin/bash

# OIPA MCP Server - Easy Installation Script
# This script will install the python-oracledb package which doesn't require Oracle Client

echo "🔧 Installing OIPA MCP Server with modern Oracle connectivity..."

# Uninstall old cx-Oracle if present
echo "Removing old cx-Oracle package..."
pip uninstall cx-Oracle -y 2>/dev/null || true

# Install python-oracledb (modern replacement)
echo "Installing python-oracledb (no Oracle Client required)..."
pip install oracledb>=2.0.0

# Install other requirements
echo "Installing other dependencies..."
pip install -r requirements_new.txt

echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Configure your OIPA database connection in .env"
echo "3. Test connection: python scripts/test_connection.py"
echo "4. Run server: python -m oipa_mcp.server"
