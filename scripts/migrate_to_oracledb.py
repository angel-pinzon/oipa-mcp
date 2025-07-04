#!/usr/bin/env python3
"""
Migration script for OIPA MCP Server database connector

Migrates from cx_Oracle to oracledb library for improved performance
and simplified installation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check Python version compatibility"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Required: Python 3.8+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def backup_existing_installation():
    """Create backup of current installation"""
    print("🔍 Creating backup of current installation...")
    
    backup_dir = Path("backup_migration")
    backup_dir.mkdir(exist_ok=True)
    
    # Backup important files
    files_to_backup = [
        ".env",
        "requirements.txt",
        "src/oipa_mcp/connectors/database.py"
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_file = backup_dir / Path(file_path).name
            try:
                import shutil
                shutil.copy2(file_path, backup_file)
                print(f"   ✅ Backed up {file_path}")
            except Exception as e:
                print(f"   ⚠️  Failed to backup {file_path}: {e}")
    
    print(f"✅ Backup created in {backup_dir}")
    return True


def uninstall_cx_oracle():
    """Uninstall cx_Oracle library"""
    print("🔄 Uninstalling cx_Oracle...")
    
    # Check if cx_Oracle is installed
    try:
        import cx_Oracle
        print("   Found cx_Oracle installation")
    except ImportError:
        print("   cx_Oracle not found, skipping uninstall")
        return True
    
    # Uninstall cx_Oracle
    return run_command(
        "pip uninstall cx_Oracle -y",
        "Uninstalling cx_Oracle"
    )


def install_oracledb():
    """Install oracledb library"""
    print("🔄 Installing oracledb...")
    
    return run_command(
        "pip install oracledb>=2.0.0",
        "Installing oracledb"
    )


def update_requirements():
    """Update requirements.txt if it exists"""
    req_file = Path("requirements.txt")
    
    if not req_file.exists():
        print("   No requirements.txt found, skipping update")
        return True
    
    print("🔄 Updating requirements.txt...")
    
    try:
        # Read current requirements
        with open(req_file, 'r') as f:
            content = f.read()
        
        # Replace cx_Oracle with oracledb
        updated_content = content.replace(
            "cx-oracle>=8.3.0",
            "oracledb>=2.0.0"
        ).replace(
            "cx_Oracle>=8.3.0", 
            "oracledb>=2.0.0"
        )
        
        # Write updated requirements
        with open(req_file, 'w') as f:
            f.write(updated_content)
        
        print("✅ requirements.txt updated")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update requirements.txt: {e}")
        return False


def test_migration():
    """Test the migration by running connection test"""
    print("🔍 Testing migration...")
    
    test_script = Path("scripts/test_connection.py")
    
    if not test_script.exists():
        print("   No test script found, skipping test")
        return True
    
    return run_command(
        f"python {test_script}",
        "Running connection test"
    )


def show_migration_summary():
    """Show migration summary and next steps"""
    print("\n" + "="*60)
    print("🎉 OIPA MCP Server Database Migration Complete!")
    print("="*60)
    
    print("\n📋 Migration Summary:")
    print("✅ Migrated from cx_Oracle to oracledb")
    print("✅ Enhanced async connection pooling")
    print("✅ Improved error handling and diagnostics") 
    print("✅ Better performance and memory usage")
    print("✅ No Oracle Client installation required")
    
    print("\n🚀 Key Benefits:")
    print("• Simplified installation (no Oracle Client needed)")
    print("• Better async/await support")
    print("• Improved connection pooling")
    print("• Enhanced error handling")
    print("• Cross-platform compatibility")
    
    print("\n📖 Next Steps:")
    print("1. Test your existing .env configuration")
    print("2. Run: python scripts/test_connection.py")
    print("3. Verify all MCP tools work correctly")
    print("4. Remove backup_migration/ folder when satisfied")
    
    print("\n⚙️  Configuration Notes:")
    print("• Same connection parameters work (.env file)")
    print("• Pool configuration enhanced with new options")
    print("• Better monitoring with get_pool_status()")
    
    print("\n🔧 Troubleshooting:")
    print("• If connection fails, check .env file")
    print("• For thick mode, install Oracle Client optionally")
    print("• Check logs for detailed error information")


def main():
    """Main migration function"""
    print("🚀 OIPA MCP Server Database Migration")
    print("Migrating from cx_Oracle to oracledb")
    print("="*50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Create backup
    if not backup_existing_installation():
        print("❌ Backup failed, aborting migration")
        sys.exit(1)
    
    # Perform migration steps
    steps = [
        (uninstall_cx_oracle, "Uninstall cx_Oracle"),
        (install_oracledb, "Install oracledb"),
        (update_requirements, "Update requirements.txt")
    ]
    
    for step_func, step_name in steps:
        if not step_func():
            print(f"❌ Migration step failed: {step_name}")
            print("   Check backup_migration/ folder to restore")
            sys.exit(1)
    
    # Test migration
    print("\n" + "-"*50)
    test_success = test_migration()
    
    if test_success:
        show_migration_summary()
    else:
        print("\n⚠️  Migration completed but tests failed")
        print("   Check your configuration and database connectivity")
        print("   Refer to backup_migration/ folder if needed")


if __name__ == "__main__":
    main()
