# 🔒 Security Hardening Guide

## ⚠️ CRITICAL SECURITY NOTICE

**This MCP server provides direct access to your Proxmox infrastructure. Improper configuration can expose your virtualization environment to security risks.**

## 🚨 Pre-Deployment Security Checklist

### Required Actions Before Production Deployment

- [ ] **Change ALL default credentials and tokens**
- [ ] **Enable SSL/TLS verification (`verify_ssl: true`)**  
- [ ] **Use strong, unique JWT signing keys (minimum 32 characters)**
- [ ] **Bind HTTP transport to specific interfaces (not `0.0.0.0`)**
- [ ] **Configure proper firewall rules**
- [ ] **Enable comprehensive logging and monitoring**
- [ ] **Review and restrict OAuth scopes to minimum required**
- [ ] **Implement secure token rotation policies**

## 🛡️ Configuration Security

### 1. SSL/TLS Configuration

**❌ INSECURE - DO NOT USE IN PRODUCTION:**
```json
{
  "proxmox": {
    "verify_ssl": false  // ⚠️ DANGEROUS: Disables certificate validation
  }
}
```

**✅ SECURE - PRODUCTION CONFIGURATION:**
```json
{
  "proxmox": {
    "host": "proxmox.yourdomain.com",
    "port": 8006,
    "verify_ssl": true,  // ✅ REQUIRED: Always verify SSL certificates
    "service": "PVE"
  }
}
```

**SSL Certificate Setup:**
1. **Use Valid Certificates**: Deploy proper SSL certificates on your Proxmox server
2. **Certificate Authority**: Use certificates from trusted CAs or proper internal CA
3. **Self-Signed Certificates**: If unavoidable, add to system trust store instead of disabling verification

### 2. Authentication Security

**❌ INSECURE PLACEHOLDER VALUES:**
```json
{
  "auth": {
    "user": "root@pam",
    "token_name": "mcp-token",  // ⚠️ Generic name
    "token_value": "your-token-secret-here"  // ⚠️ Placeholder
  }
}
```

**✅ SECURE AUTHENTICATION:**
```json
{
  "auth": {
    "user": "mcp-service@pam",  // ✅ Dedicated service account
    "token_name": "mcp-prod-2024-q4",  // ✅ Descriptive, versioned
    "token_value": "a8f5c2d9-4e7b-4c3a-9d8e-1f2a3b4c5d6e"  // ✅ Strong UUID
  }
}
```

**Token Security Best Practices:**
- **Dedicated Service Account**: Create specific user for MCP server (not root)
- **Principle of Least Privilege**: Grant only necessary permissions
- **Token Rotation**: Rotate tokens quarterly or after security incidents
- **Token Storage**: Store tokens securely, never in version control

### 3. Network Security

**❌ INSECURE NETWORK BINDING:**
```json
{
  "transport": {
    "type": "http",
    "host": "0.0.0.0",  // ⚠️ DANGEROUS: Binds to all interfaces
    "port": 8080
  }
}
```

**✅ SECURE NETWORK CONFIGURATION:**
```json
{
  "transport": {
    "type": "http",
    "host": "127.0.0.1",  // ✅ LOCALHOST ONLY
    "port": 8080
  }
}
```

**Or for controlled external access:**
```json
{
  "transport": {
    "type": "http",
    "host": "10.0.1.100",  // ✅ SPECIFIC INTERNAL IP
    "port": 8443  // ✅ Non-standard port
  }
}
```

### 4. OAuth Security

**❌ WEAK OAUTH CONFIGURATION:**
```json
{
  "authorization": {
    "enabled": true,
    "secret_key": "change-this-secret",  // ⚠️ Weak secret
    "token_expiry": 86400  // ⚠️ 24 hour tokens
  }
}
```

**✅ STRONG OAUTH CONFIGURATION:**
```json
{
  "authorization": {
    "enabled": true,
    "issuer": "https://auth.yourdomain.com",  // ✅ HTTPS only
    "audience": "proxmox-mcp-production",
    "secret_key": "7K9mP#vL2@qR8$nE5*wT1!xC6^zF4&jH3%dS0+bA9-gY2",  // ✅ Strong 64-char key
    "token_expiry": 3600,  // ✅ 1 hour maximum
    "scopes": [
      "proxmox:nodes:read"  // ✅ Minimal required scopes only
    ],
    "dynamic_client_registration": false  // ✅ Disable for production
  }
}
```

## 🔐 Proxmox Security Configuration

### 1. Create Dedicated Service Account

```bash
# Create dedicated user for MCP
pveum user add mcp-service@pam --comment "MCP Server Service Account"

# Create role with minimal permissions
pveum role add MCPServerRole -privs "VM.Monitor,VM.Console,Sys.Audit,Datastore.Audit"

# Assign role to user
pveum aclmod / -user mcp-service@pam -role MCPServerRole
```

### 2. Generate Secure API Token

```bash
# Generate token with expiration
pveum user token add mcp-service@pam mcp-prod-token --expire 1577836800 --comment "MCP Server Production Token"
```

**Token Security Requirements:**
- **Expiration Date**: Set reasonable expiration (90-365 days)
- **Privilege Separation**: Enable unless full admin access required
- **Documentation**: Record token purpose and scope

### 3. Network Security

**Proxmox Firewall Rules:**
```bash
# Allow MCP server access only from specific IPs
iptables -A INPUT -p tcp -s 10.0.1.0/24 --dport 8006 -j ACCEPT
iptables -A INPUT -p tcp --dport 8006 -j DROP
```

## 🔍 Security Monitoring

### 1. Enable Comprehensive Logging

**Secure Logging Configuration:**
```json
{
  "logging": {
    "level": "INFO",  // ✅ Capture security events
    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s",
    "file": "/var/log/proxmox-mcp/security.log"  // ✅ Dedicated log file
  }
}
```

### 2. Monitor Security Events

**Critical Events to Monitor:**
- Authentication failures
- Invalid token usage
- Privilege escalation attempts
- Unusual command execution patterns
- Failed SSL handshakes

### 3. Log Analysis

**Set up log monitoring for:**
```bash
# Failed authentication attempts
grep "Authentication failed" /var/log/proxmox-mcp/security.log

# Token validation failures  
grep "Token validation failed" /var/log/proxmox-mcp/security.log

# Suspicious commands
grep "execute_vm_command" /var/log/proxmox-mcp/security.log | grep -E "(rm|dd|format|mkfs)"
```

## 🏢 Production Deployment Architecture

### 1. Recommended Network Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │────│   Reverse Proxy  │────│  Proxmox MCP    │
│ (Claude Desktop)│    │     (nginx)      │    │     Server      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              │                          │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   SSL/TLS Cert   │    │ Proxmox Cluster │
                       │   Management     │    │                 │
                       └──────────────────┘    └─────────────────┘
```

### 2. Reverse Proxy Configuration (nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name mcp.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚨 Incident Response

### 1. Security Incident Checklist

**Immediate Actions:**
- [ ] **Disable compromised tokens** immediately
- [ ] **Check access logs** for unauthorized activities  
- [ ] **Rotate all secrets** (tokens, JWT keys)
- [ ] **Review user permissions** and revoke unnecessary access
- [ ] **Analyze system logs** for breach indicators
- [ ] **Document incident** for post-mortem analysis

### 2. Recovery Procedures

**Token Compromise:**
```bash
# Revoke compromised token
pveum user token remove mcp-service@pam compromised-token

# Generate new token
pveum user token add mcp-service@pam mcp-recovery-token --expire $(date -d "+90 days" +%s)

# Update MCP server configuration
# Restart MCP server with new token
```

## 📋 Security Validation

### Pre-Production Security Test

```bash
#!/bin/bash
# security-validation.sh

echo "🔒 ProxmoxMCP Security Validation"
echo "================================="

# Check SSL verification
if grep -q '"verify_ssl": false' config.json; then
    echo "❌ CRITICAL: SSL verification disabled"
    exit 1
else
    echo "✅ SSL verification enabled"
fi

# Check for default tokens
if grep -q "your-token\|change-this\|example" config.json; then
    echo "❌ CRITICAL: Default/placeholder tokens detected"
    exit 1
else
    echo "✅ No placeholder tokens found"
fi

# Check network binding
if grep -q '"host": "0.0.0.0"' config.json; then
    echo "⚠️  WARNING: Binding to all interfaces (0.0.0.0)"
    echo "   Consider using 127.0.0.1 or specific IP"
fi

# Check JWT secret strength
SECRET_LENGTH=$(grep -o '"secret_key": "[^"]*"' config.json | sed 's/.*": "//;s/".*//' | wc -c)
if [ "$SECRET_LENGTH" -lt 32 ]; then
    echo "❌ CRITICAL: JWT secret key too short (< 32 characters)"
    exit 1
else
    echo "✅ JWT secret key meets minimum length"
fi

echo "✅ Security validation completed"
```

## 📖 Additional Resources

- **Proxmox Security Guide**: https://pve.proxmox.com/wiki/Security
- **OAuth 2.1 Security Best Practices**: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics
- **JWT Security Best Practices**: https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/

## 🆘 Support

For security-related questions or to report vulnerabilities:
- **Security Issues**: Create issue with `[SECURITY]` prefix
- **Best Practices**: Consult this guide and official Proxmox documentation
- **Emergency**: Follow incident response procedures above

---

**Remember: Security is not a one-time setup. Regularly review and update your security configuration, monitor logs, and stay informed about security best practices.**