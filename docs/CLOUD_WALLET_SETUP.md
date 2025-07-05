# Oracle Cloud Wallet Configuration Guide

This guide explains how to configure the OIPA MCP Server to connect to Oracle Autonomous Database using Oracle Cloud Wallet.

## Prerequisites

- Oracle Autonomous Database instance
- Downloaded wallet from Oracle Cloud Console
- Python 3.8+ with oracledb library

## Quick Setup

### 1. Download Your Wallet

1. Go to Oracle Cloud Console
2. Navigate to your Autonomous Database instance
3. Click "Database connection" 
4. Click "Download wallet"
5. Save the wallet zip file (e.g., `Wallet_VITALNPROD.zip`)

### 2. Run Configuration Script

```bash
python scripts/configure_cloud_wallet.py
```

The script will:
- Extract the wallet if needed
- Validate all required files
- Show available service names
- Create proper `.env` configuration

### 3. Test Connection

```bash
python scripts/test_connection.py
```

## Manual Configuration

### 1. Extract Wallet

```bash
# Create wallet directory
mkdir -p /path/to/wallet

# Extract wallet files
unzip Wallet_VITALNPROD.zip -d /path/to/wallet
```

### 2. Configure Environment Variables

Create `.env` file with:

```env
# Connection Type
OIPA_DB_CONNECTION_TYPE=cloud_wallet

# Cloud Wallet Settings
OIPA_DB_WALLET_LOCATION=/path/to/wallet
OIPA_DB_SERVICE_NAME=vitalnprod_high
OIPA_DB_USERNAME=EQ_SPINZON
OIPA_DB_PASSWORD=your_password
OIPA_DB_WALLET_PASSWORD=wallet_password_if_required

# Traditional settings (not used with Cloud Wallet)
OIPA_DB_HOST=not_used_with_cloud_wallet
OIPA_DB_PORT=not_used_with_cloud_wallet
```

### 3. Required Wallet Files

Your wallet directory must contain:
- `cwallet.sso` - Auto-login wallet
- `ewallet.p12` - Encrypted wallet  
- `sqlnet.ora` - Network configuration
- `tnsnames.ora` - Service definitions
- `ojdbc.properties` - JDBC properties
- `keystore.jks` - Java keystore (optional)
- `truststore.jks` - Java truststore (optional)

## Service Names

Common Oracle Autonomous Database service names:
- `{db_name}_high` - High priority, parallel execution
- `{db_name}_medium` - Medium priority, limited parallelism
- `{db_name}_low` - Low priority, serial execution
- `{db_name}_tp` - Transaction processing
- `{db_name}_tpurgent` - Transaction processing urgent

From your example: `vitalnprod_high`

## Configuration Details

### Connection Parameters

For Cloud Wallet connections, the MCP server uses:

```python
# Database connection with Cloud Wallet
oracledb.create_pool_async(
    user=username,
    password=password,
    dsn=service_name,  # Uses service name directly
    config_dir=wallet_location,
    wallet_location=wallet_location,
    wallet_password=wallet_password,  # If required
    # ... other pool settings
)
```

### Thin Mode vs Thick Mode

Cloud Wallet connections **must** use thin mode:
- ✅ **Thin Mode**: Pure Python, no Oracle Client required
- ❌ **Thick Mode**: Not supported with Cloud Wallet

The MCP server automatically uses thin mode for Cloud Wallet connections.

## Security Best Practices

### 1. File Permissions

```bash
# Secure wallet directory
chmod 700 /path/to/wallet
chmod 600 /path/to/wallet/*
```

### 2. Environment Variables

- Never commit `.env` files to version control
- Use secure credential storage in production
- Consider using encrypted wallet passwords

### 3. Network Security

- Cloud Wallet connections use mTLS automatically
- No additional SSL configuration needed
- Connections are encrypted end-to-end

## Troubleshooting

### Common Issues

**1. "Wallet location not found"**
```bash
# Check wallet path
ls -la /path/to/wallet
# Should show cwallet.sso, ewallet.p12, etc.
```

**2. "Invalid service name"**
```bash
# Check available services
grep -i "=" /path/to/wallet/tnsnames.ora
```

**3. "Authentication failed"**
```bash
# Verify credentials
# Check if user has proper database permissions
```

**4. "Connection timeout"**
```bash
# Check network connectivity
# Verify firewall rules
```

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
```

This will show detailed connection information and help diagnose issues.

## Testing

### 1. Basic Connection Test

```bash
python scripts/test_connection.py
```

Expected output:
```
📋 Connection Type: Oracle Cloud Wallet
Wallet Location: /path/to/wallet
Service Name: vitalnprod_high
Username: EQ_SPINZON
✅ Database pool initialized
✅ Database connection test passed
```

### 2. MCP Server Test

```bash
python -m oipa_mcp.server
```

Should show:
```
Using thin mode for Cloud Wallet (no Oracle Client required)
Cloud Wallet connection initialized from: /path/to/wallet
Async database pool initialized: vitalnprod_high
```

## Production Deployment

### Docker Configuration

```dockerfile
# Copy wallet to container
COPY wallet/ /app/wallet/

# Set environment variables
ENV OIPA_DB_CONNECTION_TYPE=cloud_wallet
ENV OIPA_DB_WALLET_LOCATION=/app/wallet
ENV OIPA_DB_SERVICE_NAME=vitalnprod_high
```

### Kubernetes

```yaml
# ConfigMap for wallet files
apiVersion: v1
kind: ConfigMap
metadata:
  name: oracle-wallet
data:
  # ... wallet files (base64 encoded)

# Secret for credentials
apiVersion: v1
kind: Secret
metadata:
  name: oracle-credentials
type: Opaque
data:
  username: <base64-encoded-username>
  password: <base64-encoded-password>
```

## Migration from Traditional Connection

If migrating from traditional Oracle connection:

1. **Backup current configuration**
   ```bash
   cp .env .env.backup
   ```

2. **Update connection type**
   ```env
   OIPA_DB_CONNECTION_TYPE=cloud_wallet
   ```

3. **Add wallet settings**
   ```env
   OIPA_DB_WALLET_LOCATION=/path/to/wallet
   ```

4. **Test new configuration**
   ```bash
   python scripts/test_connection.py
   ```

5. **Update deployment** (if applicable)

The MCP server will automatically detect the connection type and use the appropriate connection method.

## Performance Considerations

### Connection Pooling

Cloud Wallet supports the same connection pooling as traditional connections:

```env
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=10
DB_POOL_TIMEOUT=30
```

### Network Latency

Cloud connections may have higher latency:
- Use connection pooling to minimize connection overhead
- Consider adjusting query timeouts
- Use batch operations for bulk data

### Resource Limits

Autonomous Database has resource limits:
- Monitor concurrent connections
- Adjust pool sizes based on workload
- Consider using different service names for different workloads

## Support

For issues:
1. Check the troubleshooting section
2. Review Oracle Cloud documentation
3. Verify network connectivity
4. Check database user permissions

Oracle Autonomous Database documentation:
- [Oracle Database Cloud Service](https://docs.oracle.com/en/cloud/paas/autonomous-database/)
- [Python-oracledb Documentation](https://python-oracledb.readthedocs.io/)
