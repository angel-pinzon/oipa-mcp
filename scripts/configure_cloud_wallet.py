#!/usr/bin/env python3
"""
Cloud Wallet Configuration Script for OIPA MCP Server

Helps configure Oracle Cloud Wallet connection for OIPA MCP Server.
This script validates wallet files and creates proper .env configuration.
"""

import os
import sys
import zipfile
from pathlib import Path
from typing import Optional

def validate_wallet_files(wallet_path: str) -> bool:
    """Validate that all required wallet files are present"""
    required_files = [
        'cwallet.sso',
        'ewallet.p12', 
        'sqlnet.ora',
        'tnsnames.ora',
        'ojdbc.properties'
    ]
    
    wallet_dir = Path(wallet_path)
    if not wallet_dir.exists():
        print(f"❌ Wallet directory does not exist: {wallet_path}")
        return False
    
    missing_files = []
    for file in required_files:
        file_path = wallet_dir / file
        if not file_path.exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing wallet files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required wallet files found")
    return True

def extract_wallet_if_needed(wallet_path: str) -> Optional[str]:
    """Extract wallet zip file if provided"""
    wallet_file = Path(wallet_path)
    
    if wallet_file.is_file() and wallet_file.suffix.lower() == '.zip':
        print(f"📦 Extracting wallet from: {wallet_path}")
        
        # Create extraction directory
        extract_dir = wallet_file.parent / wallet_file.stem
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(wallet_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print(f"✅ Wallet extracted to: {extract_dir}")
            return str(extract_dir)
        except Exception as e:
            print(f"❌ Failed to extract wallet: {e}")
            return None
    
    return wallet_path

def get_service_names(wallet_path: str) -> list:
    """Parse tnsnames.ora to get available service names"""
    tnsnames_path = Path(wallet_path) / 'tnsnames.ora'
    service_names = []
    
    if tnsnames_path.exists():
        try:
            with open(tnsnames_path, 'r') as f:
                content = f.read()
                # Simple parsing - look for service names (text before =)
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        service_name = line.split('=')[0].strip()
                        if service_name and service_name not in service_names:
                            service_names.append(service_name)
        except Exception as e:
            print(f"⚠️  Could not parse tnsnames.ora: {e}")
    
    return service_names

def create_env_configuration(wallet_path: str, service_name: str, username: str, password: str, wallet_password: str = None) -> str:
    """Create .env configuration for Cloud Wallet"""
    
    env_content = f"""# OIPA Database Configuration - Oracle Cloud Wallet
# Connection Type: Cloud Wallet
OIPA_DB_CONNECTION_TYPE=cloud_wallet

# Cloud Wallet Settings
OIPA_DB_WALLET_LOCATION={wallet_path}
OIPA_DB_SERVICE_NAME={service_name}
OIPA_DB_USERNAME={username}
OIPA_DB_PASSWORD={password}
"""
    
    if wallet_password:
        env_content += f"OIPA_DB_WALLET_PASSWORD={wallet_password}\n"
    
    env_content += """
# Traditional settings (not used with Cloud Wallet)
OIPA_DB_HOST=not_used_with_cloud_wallet
OIPA_DB_PORT=not_used_with_cloud_wallet

# OIPA Web Service Configuration  
OIPA_WS_ENDPOINT=http://oipa-server:8080/pas/services/FileReceived
OIPA_WS_USERNAME=webservice_user
OIPA_WS_PASSWORD=your_ws_password

# MCP Server Configuration
MCP_SERVER_NAME=oipa-mcp
MCP_SERVER_VERSION=1.0.0
MCP_SERVER_DESCRIPTION="MCP Server for Oracle OIPA integration"

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/oipa-mcp.log

# Connection Pool Settings
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=10
DB_POOL_TIMEOUT=30

# SOAP/HTTP Settings
HTTP_TIMEOUT=30
SOAP_TIMEOUT=60
MAX_RETRIES=3

# Security Settings
ENABLE_SSL=false
SSL_CERT_PATH=""
SSL_KEY_PATH=""

# Performance Settings
CACHE_TTL=300
MAX_QUERY_RESULTS=1000
QUERY_TIMEOUT=30

# Feature Flags
ENABLE_PUSH_FRAMEWORK=true
ENABLE_ANALYTICS=true
ENABLE_CACHING=true
ENABLE_MONITORING=true
"""
    
    return env_content

def main():
    """Main configuration wizard"""
    print("🔧 OIPA MCP Server - Cloud Wallet Configuration")
    print("=" * 50)
    
    # Get wallet path
    wallet_path = input("📁 Enter path to wallet (directory or .zip file): ").strip()
    if not wallet_path:
        print("❌ Wallet path is required")
        sys.exit(1)
    
    # Extract wallet if needed
    wallet_path = extract_wallet_if_needed(wallet_path)
    if not wallet_path:
        sys.exit(1)
    
    # Validate wallet files
    if not validate_wallet_files(wallet_path):
        sys.exit(1)
    
    # Get available service names
    service_names = get_service_names(wallet_path)
    if service_names:
        print(f"🔍 Available service names: {', '.join(service_names)}")
        default_service = service_names[0] if service_names else None
    else:
        default_service = None
    
    # Get database credentials
    service_name = input(f"🌐 Service name [{default_service}]: ").strip() or default_service
    if not service_name:
        print("❌ Service name is required")
        sys.exit(1)
    
    username = input("👤 Database username: ").strip()
    if not username:
        print("❌ Username is required")
        sys.exit(1)
    
    password = input("🔒 Database password: ").strip()
    if not password:
        print("❌ Password is required")
        sys.exit(1)
    
    wallet_password = input("🔐 Wallet password (optional): ").strip() or None
    
    # Create configuration
    env_content = create_env_configuration(
        wallet_path=os.path.abspath(wallet_path),
        service_name=service_name,
        username=username,
        password=password,
        wallet_password=wallet_password
    )
    
    # Write .env file
    env_path = Path('.env')
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Configuration saved to: {env_path.absolute()}")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        sys.exit(1)
    
    print("\n🎉 Cloud Wallet configuration completed!")
    print(f"📁 Wallet location: {wallet_path}")
    print(f"🌐 Service name: {service_name}")
    print(f"👤 Username: {username}")
    print(f"📝 Configuration file: {env_path.absolute()}")
    
    print("\n🚀 Next steps:")
    print("1. Test the connection: python scripts/test_connection.py")
    print("2. Run the MCP server: python -m oipa_mcp.server")

if __name__ == "__main__":
    main()
