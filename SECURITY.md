# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in OIPA MCP Server, please report it by emailing security@example.com. Please do not report security vulnerabilities through public GitHub issues.

## Security Best Practices

### Environment Variables

1. **Never commit `.env` files** to version control
2. Use strong, unique passwords for database connections
3. Rotate credentials regularly
4. Use environment-specific configurations

### Database Security

1. **Principle of Least Privilege**
   - Grant only necessary permissions to database users
   - Use read-only accounts where possible
   - Restrict network access to database servers

2. **Connection Security**
   - Use SSL/TLS for database connections in production
   - Consider using Oracle Cloud Wallet for credential management
   - Enable connection pooling with appropriate timeouts

### Configuration Security

```bash
# Good - Using environment variables
OIPA_DB_PASSWORD=${DB_PASSWORD}

# Bad - Hardcoded credentials
OIPA_DB_PASSWORD=mysecretpassword
```

### Sensitive Data Handling

1. **PII Protection**
   - Never log personally identifiable information
   - Mask sensitive data in logs and error messages
   - Use data retention policies

2. **Audit Logging**
   - Log access to sensitive operations
   - Store audit logs securely
   - Monitor for suspicious activities

### Production Deployment

1. **Network Security**
   - Use firewalls to restrict access
   - Deploy behind a reverse proxy
   - Enable rate limiting

2. **Monitoring**
   - Set up alerts for failed authentication attempts
   - Monitor resource usage
   - Track API usage patterns

### Example Secure Configuration

```bash
# .env.production (example)
# Database
OIPA_DB_HOST=${DB_HOST}
OIPA_DB_PORT=${DB_PORT}
OIPA_DB_SERVICE_NAME=${DB_SERVICE}
OIPA_DB_USERNAME=${DB_USER}
OIPA_DB_PASSWORD=${DB_PASSWORD}

# Use Cloud Wallet for production
OIPA_DB_CONNECTION_TYPE=cloud_wallet
OIPA_DB_WALLET_LOCATION=/secure/path/to/wallet

# Enable SSL
ENABLE_SSL=true
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# Logging (no sensitive data)
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security headers
ENABLE_CORS=false
ALLOWED_ORIGINS=https://your-domain.com
```

## Dependencies

We regularly update dependencies to patch security vulnerabilities. Run:

```bash
# Check for security vulnerabilities
pip audit

# Update dependencies
pip install --upgrade -r requirements.txt
```

## Compliance

This project follows security best practices aligned with:
- OWASP Top 10
- PCI DSS (for handling insurance data)
- GDPR (for EU data protection)

## Security Checklist

Before deploying to production:

- [ ] All secrets are in environment variables
- [ ] Database connections use SSL
- [ ] Logging doesn't contain PII
- [ ] Dependencies are up to date
- [ ] Access controls are configured
- [ ] Monitoring is enabled
- [ ] Backup and recovery procedures are tested
- [ ] Security headers are configured
- [ ] Rate limiting is enabled
- [ ] Input validation is implemented

## Resources

- [OWASP Security Guidelines](https://owasp.org/)
- [Oracle Database Security Best Practices](https://docs.oracle.com/en/database/oracle/oracle-database/19/dbseg/)
- [Python Security Best Practices](https://python.org/dev/security/)
