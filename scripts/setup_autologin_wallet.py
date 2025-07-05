#!/usr/bin/env python3
"""
Oracle Cloud Wallet Auto-Login Setup Script

This script creates a clean auto-login wallet directory by copying only the necessary
files and excluding the PEM file that causes password prompts.
"""

import os
import shutil
from pathlib import Path

def create_autologin_wallet(source_wallet: str, target_wallet: str = None) -> bool:
    """Create a clean auto-login wallet directory"""
    
    source_path = Path(source_wallet)
    if not source_path.exists():
        print(f"❌ Source wallet directory does not exist: {source_wallet}")
        return False
    
    # Default target path
    if target_wallet is None:
        target_wallet = str(source_path.parent / f"{source_path.name}_autologin")
    
    target_path = Path(target_wallet)
    
    print(f"🔧 Creating auto-login wallet:")
    print(f"   Source: {source_path}")
    print(f"   Target: {target_path}")
    
    # Create target directory
    target_path.mkdir(exist_ok=True)
    
    # Files needed for auto-login wallet (exclude PEM files)
    required_files = [
        'cwallet.sso',      # Auto-login wallet (most important)
        'ewallet.p12',      # Encrypted wallet (backup)
        'sqlnet.ora',       # Network configuration
        'tnsnames.ora',     # Service definitions
        'ojdbc.properties', # JDBC properties
        'keystore.jks',     # Java keystore (optional)
        'truststore.jks',   # Java truststore (optional)
        'README'            # Documentation
    ]
    
    # Copy only required files (skip PEM files)
    copied_files = []
    for file_name in required_files:
        source_file = source_path / file_name
        target_file = target_path / file_name
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                copied_files.append(file_name)
                print(f"✅ Copied: {file_name}")
            except Exception as e:
                print(f"❌ Failed to copy {file_name}: {e}")
        else:
            print(f"⚠️  File not found: {file_name}")
    
    # Check for PEM files (these cause password prompts)
    pem_files = list(source_path.glob("*.pem"))
    if pem_files:
        print(f"🔒 Excluded PEM files to avoid password prompts:")
        for pem_file in pem_files:
            print(f"   - {pem_file.name}")
    
    # Verify essential files
    essential_files = ['cwallet.sso', 'tnsnames.ora', 'sqlnet.ora']
    missing_essential = []
    for file_name in essential_files:
        if not (target_path / file_name).exists():
            missing_essential.append(file_name)
    
    if missing_essential:
        print(f"❌ Missing essential files: {', '.join(missing_essential)}")
        return False
    
    print(f"✅ Auto-login wallet created successfully!")
    print(f"📁 Location: {target_path}")
    print(f"📋 Files copied: {len(copied_files)}")
    
    return True

def update_env_file(new_wallet_location: str) -> bool:
    """Update .env file with new wallet location"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    try:
        # Read current content
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Update wallet location
        lines = content.split('\n')
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('OIPA_DB_WALLET_LOCATION='):
                lines[i] = f'OIPA_DB_WALLET_LOCATION={new_wallet_location}'
                updated = True
                break
        
        if not updated:
            print("❌ OIPA_DB_WALLET_LOCATION not found in .env file")
            return False
        
        # Write updated content
        with open(env_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated .env file with new wallet location: {new_wallet_location}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Oracle Cloud Wallet Auto-Login Setup")
    print("=" * 50)
    
    # Current wallet location from .env or user input
    current_wallet = "C:\\Tmp\\gnp\\Sbox\\wallet"
    
    print(f"Current wallet location: {current_wallet}")
    
    # Create auto-login wallet
    autologin_wallet = current_wallet + "_autologin"
    
    if create_autologin_wallet(current_wallet, autologin_wallet):
        # Update .env file
        if update_env_file(autologin_wallet):
            print("\n🎉 Setup completed successfully!")
            print(f"📁 New wallet location: {autologin_wallet}")
            print(f"🔧 Updated .env file")
            print("\n🚀 Next steps:")
            print("1. Test the connection: python scripts/test_connection.py")
            print("2. The new wallet should connect without password prompts")
        else:
            print("\n⚠️  Wallet created but failed to update .env file")
            print(f"Please manually update OIPA_DB_WALLET_LOCATION to: {autologin_wallet}")
    else:
        print("\n❌ Failed to create auto-login wallet")
        print("Please check the source wallet directory and try again")

if __name__ == "__main__":
    main()
