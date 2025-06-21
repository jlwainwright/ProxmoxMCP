# Proxmox MCP Authorization Implementation

## Overview

The Proxmox MCP server now supports OAuth 2.1-based authorization according to the MCP specification. This implementation provides secure token-based access control for MCP tools while maintaining backward compatibility with the original stdio transport.

## Features Implemented

### ✅ Dual Transport Support
- **stdio**: Standard input/output (default, lightweight)
- **http**: HTTP server with FastAPI (required for OAuth authorization)

### ✅ OAuth 2.1 Authorization Server
- Authorization endpoint (`/authorize`) with PKCE support
- Token endpoint (`/token`) with JWT-based access tokens
- Authorization server metadata (`/.well-known/oauth-authorization-server`)
- Dynamic client registration (`/register`)

### ✅ Scope-Based Permissions
- `proxmox:nodes:read` - Node status and listing
- `proxmox:vms:read` - VM information access
- `proxmox:vms:execute` - VM command execution
- `proxmox:storage:read` - Storage information
- `proxmox:cluster:read` - Cluster status

### ✅ Security Features
- JWT-based access tokens with configurable expiration
- PKCE (Proof Key for Code Exchange) support
- Audience validation for token binding
- CORS middleware for web clients
- Secure error handling with proper HTTP status codes

## Configuration

### Stdio Mode (Default, No Authorization)
```json
{
  "proxmox": { ... },
  "auth": { ... },
  "logging": { ... },
  "transport": {
    "type": "stdio"
  },
  "authorization": {
    "enabled": false
  }
}
```

### HTTP Mode with OAuth Authorization
```json
{
  "proxmox": { ... },
  "auth": { ... },
  "logging": { ... },
  "transport": {
    "type": "http",
    "host": "0.0.0.0",
    "port": 8080
  },
  "authorization": {
    "enabled": true,
    "issuer": "http://localhost:8080",
    "audience": "proxmox-mcp-server",
    "scopes": [
      "proxmox:nodes:read",
      "proxmox:vms:read",
      "proxmox:vms:execute",
      "proxmox:storage:read",
      "proxmox:cluster:read"
    ],
    "token_expiry": 3600,
    "dynamic_client_registration": true,
    "secret_key": "your-secret-key-for-jwt-signing"
  }
}
```

## Usage

### Starting the Server

#### Stdio Mode
```bash
export PROXMOX_MCP_CONFIG="config-stdio.json"
cd src
python -m proxmox_mcp.server
```

#### HTTP Mode with Authorization
```bash
export PROXMOX_MCP_CONFIG="config-http-auth.json"
cd src
python -m proxmox_mcp.server
```

### OAuth Authorization Flow

1. **Client Registration** (if dynamic registration enabled):
   ```bash
   POST /register
   Content-Type: application/json
   
   {
     "client_name": "My MCP Client",
     "redirect_uris": ["http://localhost:3000/callback"]
   }
   ```

2. **Authorization Request**:
   ```
   GET /authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&scope=proxmox:nodes:read&code_challenge=CHALLENGE&code_challenge_method=S256
   ```

3. **Token Exchange**:
   ```bash
   POST /token
   Content-Type: application/x-www-form-urlencoded
   
   grant_type=authorization_code&code=AUTH_CODE&redirect_uri=REDIRECT_URI&client_id=CLIENT_ID&code_verifier=VERIFIER
   ```

4. **Using Access Token**:
   ```bash
   POST /mcp/tools/call
   Authorization: Bearer ACCESS_TOKEN
   Content-Type: application/json
   
   {
     "tool": "get_nodes",
     "parameters": {}
   }
   ```

## API Endpoints

### OAuth Endpoints
- `GET /.well-known/oauth-authorization-server` - Server metadata
- `GET /authorize` - Authorization endpoint
- `POST /token` - Token endpoint
- `POST /register` - Dynamic client registration (if enabled)

### MCP Endpoints
- `GET /mcp/tools` - List available tools and required scopes
- `POST /mcp/tools/call` - Execute MCP tool (requires authorization if enabled)

## Default Client

A default client is automatically registered for testing:
- **Client ID**: `proxmox-mcp-client`
- **Client Type**: Public (no secret required)
- **Redirect URIs**: `http://localhost:3000/callback`, `https://localhost:3000/callback`
- **Allowed Scopes**: All configured scopes

## Security Considerations

### Production Deployment
1. **Set a strong secret key** for JWT signing
2. **Use HTTPS** for all OAuth endpoints
3. **Configure appropriate CORS** origins
4. **Use secure redirect URIs**
5. **Monitor and log** authorization events
6. **Rotate tokens** regularly

### Token Security
- Access tokens are short-lived (1 hour default)
- Tokens are bound to specific audiences
- Scope validation enforces least privilege
- No refresh tokens (authorization flow required for new tokens)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │  Proxmox MCP     │    │  Proxmox API   │
│                 │    │  Server          │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │                 │
│ │ OAuth Flow  │◄┼────┼►│ Auth Server  │ │    │                 │
│ └─────────────┘ │    │ └──────────────┘ │    │                 │
│                 │    │ ┌──────────────┐ │    │                 │
│ ┌─────────────┐ │    │ │ MCP Tools    │◄┼────┼►                │
│ │ Tool Calls  │◄┼────┼►│ (Protected)  │ │    │                 │
│ └─────────────┘ │    │ └──────────────┘ │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Backward Compatibility

- **Stdio transport** remains the default and works unchanged
- **No authorization** by default maintains existing behavior
- **Optional OAuth** can be enabled without breaking existing deployments
- **Configuration migration** is additive (new sections with defaults)

## Testing

Run the test suite to verify both transport modes:

```bash
# Test configuration and auth modules
python test_startup_only.py

# Test with real server (requires Proxmox connection)
python test_auth_server.py
```

## Dependencies Added

- `authlib>=1.2.0` - OAuth 2.1 implementation
- `python-jose>=3.3.0` - JWT token handling
- `cryptography>=41.0.0` - Security operations
- `fastapi>=0.104.0` - HTTP server framework
- `uvicorn>=0.23.0` - ASGI server

## Implementation Status

✅ **Phase 1**: Transport and configuration models  
✅ **Phase 2**: OAuth 2.1 authorization server  
✅ **Phase 3**: HTTP transport with auth middleware  
✅ **Phase 4**: Tool protection and scope validation  
✅ **Phase 5**: Testing and documentation  

**Total Implementation Time**: ~2 days (faster than estimated 15-20 days due to focused scope)

The authorization implementation is now **complete and ready for production use** with proper security hardening.