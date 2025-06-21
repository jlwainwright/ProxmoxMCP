# 🚀 Proxmox Manager - Proxmox MCP Server

![ProxmoxMCP](https://github.com/user-attachments/assets/e32ab79f-be8a-420c-ab2d-475612150534)

A Python-based Model Context Protocol (MCP) server for interacting with Proxmox hypervisors, providing a clean interface for managing nodes, VMs, and containers. Now with **OAuth 2.1 authorization** support!

## 🏗️ Built With

- [Cline](https://github.com/cline/cline) - Autonomous coding agent - Go faster with Cline.
- [Proxmoxer](https://github.com/proxmoxer/proxmoxer) - Python wrapper for Proxmox API
- [MCP SDK](https://github.com/modelcontextprotocol/sdk) - Model Context Protocol SDK
- [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type annotations
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for HTTP transport
- [Authlib](https://authlib.org/) - OAuth 2.1 implementation
- [python-jose](https://python-jose.readthedocs.io/) - JWT token handling

## ✨ Features

- 🤖 Full integration with Cline
- 🛠️ Built with the official MCP SDK
- 🔒 Secure token-based authentication with Proxmox
- 🛡️ **NEW: OAuth 2.1 authorization with scope-based permissions**
- 🌐 **NEW: Dual transport support (stdio/HTTP)**
- 🖥️ Tools for managing nodes and VMs
- 💻 VM console command execution
- 📝 Configurable logging system
- ✅ Type-safe implementation with Pydantic
- 🎨 Rich output formatting with customizable themes
- 🔐 **NEW: JWT-based access tokens with PKCE support**
- 🎯 **NEW: Granular scope-based access control**

## 📹 Demo Video

https://github.com/user-attachments/assets/1b5f42f7-85d5-4918-aca4-d38413b0e82b

## 📦 Installation

### Prerequisites
- UV package manager (recommended)
- Python 3.10 or higher
- Git
- Access to a Proxmox server with API token credentials

Before starting, ensure you have:

- [ ] Proxmox server hostname or IP
- [ ] Proxmox API token (see [API Token Setup](#proxmox-api-token-setup))
- [ ] UV installed (`pip install uv`)

### Option 1: Quick Install (Recommended)

1. Clone and set up environment:

   ```bash
   # Clone repository
   cd ~/Documents/Cline/MCP  # For Cline users
   # OR
   cd your/preferred/directory  # For manual installation
   
   git clone https://github.com/canvrno/ProxmoxMCP.git
   cd ProxmoxMCP

   # Create and activate virtual environment
   uv venv
   source venv/bin/activate  # Linux/macOS
   # OR
   .\venv\Scripts\Activate.ps1  # Windows
   ```

2. Install dependencies:

   ```bash
   # Install with development dependencies
   uv pip install -e ".[dev]"
   ```

3. Create configuration:

   ```bash
   # Create config directory and copy template
   mkdir -p proxmox-config
   cp config/config.example.json proxmox-config/config.json
   ```

4. Edit `proxmox-config/config.json`:
   ```json
   {
       "proxmox": {
           "host": "PROXMOX_HOST",        # Required: Your Proxmox server address
           "port": 8006,                  # Optional: Default is 8006
           "verify_ssl": false,           # Optional: Set false for self-signed certs
           "service": "PVE"               # Optional: Default is PVE
       },
       "auth": {
           "user": "USER@pve",            # Required: Your Proxmox username
           "token_name": "TOKEN_NAME",    # Required: API token ID
           "token_value": "TOKEN_VALUE"   # Required: API token value
       },
       "logging": {
           "level": "INFO",               # Optional: DEBUG for more detail
           "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
           "file": "proxmox_mcp.log"      # Optional: Log to file
       }
   }
   ```

### Verifying Installation

1. Check Python environment:
   ```bash
   python -c "import proxmox_mcp; print('Installation OK')"
   ```

2. Run the tests:
   ```bash
   pytest
   ```

3. Verify configuration:
   ```bash
   # Linux/macOS
   PROXMOX_MCP_CONFIG="proxmox-config/config.json" python -m proxmox_mcp.server

   # Windows (PowerShell)
   $env:PROXMOX_MCP_CONFIG="proxmox-config\config.json"; python -m proxmox_mcp.server
   ```

   You should see either:
   - A successful connection to your Proxmox server
   - Or a connection error (if Proxmox details are incorrect)

   **Note:** Make sure to activate your virtual environment and run from the `src` directory:
   ```bash
   source venv/bin/activate
   export PROXMOX_MCP_CONFIG="$(pwd)/proxmox-config/config.json"
   cd src
   python -m proxmox_mcp.server
   ```

## ⚙️ Configuration

The server supports two transport modes and optional OAuth 2.1 authorization:

### Transport Modes

#### Stdio Mode (Default)
- **Use case**: Direct integration with MCP clients (Cline, Claude Code CLI)
- **Security**: Basic Proxmox token authentication
- **Setup**: Minimal configuration required

#### HTTP Mode 
- **Use case**: Web applications, REST API access, OAuth-based integrations
- **Security**: Optional OAuth 2.1 with JWT tokens and scope-based permissions
- **Setup**: HTTP server on configurable host/port

### Configuration Examples

#### Basic Stdio Configuration (`config-stdio.json`)
```json
{
  "proxmox": {
    "host": "192.168.1.100",
    "port": 8006,
    "verify_ssl": false,
    "service": "PVE"
  },
  "auth": {
    "user": "root@pam",
    "token_name": "mcp-token",
    "token_value": "your-token-secret-here"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": null
  },
  "transport": {
    "type": "stdio"
  },
  "authorization": {
    "enabled": false
  }
}
```

#### HTTP with OAuth Configuration (`config-http-auth.json`)
```json
{
  "proxmox": {
    "host": "192.168.1.100",
    "port": 8006,
    "verify_ssl": false,
    "service": "PVE"
  },
  "auth": {
    "user": "root@pam",
    "token_name": "mcp-token",
    "token_value": "your-token-secret-here"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "proxmox_mcp.log"
  },
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
    "secret_key": "your-secret-key-for-jwt-signing-change-this-in-production"
  }
}
```

### OAuth 2.1 Scopes

When authorization is enabled, the following scopes control access:

- 🖥️ `proxmox:nodes:read` - List and view node information
- 🗃️ `proxmox:vms:read` - List and view VM information  
- ⚡ `proxmox:vms:execute` - Execute commands in VMs
- 💾 `proxmox:storage:read` - View storage information
- ⚙️ `proxmox:cluster:read` - View cluster status

### Proxmox API Token Setup
1. Log into your Proxmox web interface
2. Navigate to Datacenter -> Permissions -> API Tokens
3. Create a new API token:
   - Select a user (e.g., root@pam)
   - Enter a token ID (e.g., "mcp-token")
   - Uncheck "Privilege Separation" if you want full access
   - Save and copy both the token ID and secret


## 🚀 Running the Server

### Stdio Mode (Default)
For direct MCP client integration:
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Set configuration and run
export PROXMOX_MCP_CONFIG="config-stdio.json"
cd src
python -m proxmox_mcp.server
```

### HTTP Mode with OAuth
For web applications and OAuth-secured access:
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS

# Set configuration and run HTTP server
export PROXMOX_MCP_CONFIG="config-http-auth.json"
cd src
python -m proxmox_mcp.server

# Server will be available at http://localhost:8080
# OAuth endpoints:
# - Authorization: http://localhost:8080/authorize
# - Token: http://localhost:8080/token
# - Metadata: http://localhost:8080/.well-known/oauth-authorization-server
# - MCP Tools: http://localhost:8080/mcp/tools
```

### OAuth Authorization Flow

1. **Get authorization code**:
   ```
   GET /authorize?response_type=code&client_id=proxmox-mcp-client&redirect_uri=http://localhost:3000/callback&scope=proxmox:nodes:read&code_challenge=CHALLENGE&code_challenge_method=S256
   ```

2. **Exchange for access token**:
   ```bash
   curl -X POST http://localhost:8080/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&code=AUTH_CODE&redirect_uri=http://localhost:3000/callback&client_id=proxmox-mcp-client&code_verifier=VERIFIER"
   ```

3. **Use access token**:
   ```bash
   curl -X POST http://localhost:8080/mcp/tools/call \
     -H "Authorization: Bearer ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"tool": "get_nodes", "parameters": {}}'
   ```

### Claude Desktop Integration

To add Proxmox MCP to Claude Desktop, update your configuration file:

**Configuration File Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Generate Your Configuration:**
```bash
# Run this from your ProxmoxMCP directory to get the correct paths
python3 -c "
import os
import json

config = {
    'mcpServers': {
        'proxmox-mcp': {
            'command': os.path.abspath('venv/bin/python'),
            'args': ['-m', 'proxmox_mcp.server'],
            'cwd': os.path.abspath('src'),
            'env': {
                'PROXMOX_MCP_CONFIG': os.path.abspath('config-stdio.json')
            }
        }
    }
}

print('Add this to your Claude Desktop configuration:')
print(json.dumps(config, indent=2))
"
```

**Example Configuration:**
```json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/Users/your-username/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/Users/your-username/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/Users/your-username/ProxmoxMCP/config-stdio.json"
      }
    }
  }
}
```

**Important Setup Notes:**
- ✅ Use `config-stdio.json` (not `proxmox-config/config.json`)
- ✅ Ensure all paths are absolute
- ✅ Set logging level to `"ERROR"` to reduce noise in Claude logs
- ✅ Restart Claude Desktop after configuration changes

### Cline/VS Code Integration

For Cline users, add to your MCP settings file (`~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/absolute/path/to/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/absolute/path/to/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/absolute/path/to/ProxmoxMCP/config-stdio.json"
      }
    }
  }
}
```

# 🔧 Available Tools

The server provides the following MCP tools for interacting with Proxmox:

### get_nodes
Lists all nodes in the Proxmox cluster.

- Parameters: None
- Example Response:
  ```
  🖥️ Proxmox Nodes

  🖥️ pve-compute-01
    • Status: ONLINE
    • Uptime: ⏳ 156d 12h
    • CPU Cores: 64
    • Memory: 186.5 GB / 512.0 GB (36.4%)

  🖥️ pve-compute-02
    • Status: ONLINE
    • Uptime: ⏳ 156d 11h
    • CPU Cores: 64
    • Memory: 201.3 GB / 512.0 GB (39.3%)
  ```

### get_node_status
Get detailed status of a specific node.

- Parameters:
  - `node` (string, required): Name of the node
- Example Response:
  ```
  🖥️ Node: pve-compute-01
    • Status: ONLINE
    • Uptime: ⏳ 156d 12h
    • CPU Usage: 42.3%
    • CPU Cores: 64 (AMD EPYC 7763)
    • Memory: 186.5 GB / 512.0 GB (36.4%)
    • Network: ⬆️ 12.8 GB/s ⬇️ 9.2 GB/s
    • Temperature: 38°C
  ```

### get_vms
List all VMs across the cluster.

- Parameters: None
- Example Response:
  ```
  🗃️ Virtual Machines

  🗃️ prod-db-master (ID: 100)
    • Status: RUNNING
    • Node: pve-compute-01
    • CPU Cores: 16
    • Memory: 92.3 GB / 128.0 GB (72.1%)

  🗃️ prod-web-01 (ID: 102)
    • Status: RUNNING
    • Node: pve-compute-01
    • CPU Cores: 8
    • Memory: 12.8 GB / 32.0 GB (40.0%)
  ```

### get_storage
List available storage.

- Parameters: None
- Example Response:
  ```
  💾 Storage Pools

  💾 ceph-prod
    • Status: ONLINE
    • Type: rbd
    • Usage: 12.8 TB / 20.0 TB (64.0%)
    • IOPS: ⬆️ 15.2k ⬇️ 12.8k

  💾 local-zfs
    • Status: ONLINE
    • Type: zfspool
    • Usage: 3.2 TB / 8.0 TB (40.0%)
    • IOPS: ⬆️ 42.8k ⬇️ 35.6k
  ```

### get_cluster_status
Get overall cluster status.

- Parameters: None
- Example Response:
  ```
  ⚙️ Proxmox Cluster

    • Name: enterprise-cloud
    • Status: HEALTHY
    • Quorum: OK
    • Nodes: 4 ONLINE
    • Version: 8.1.3
    • HA Status: ACTIVE
    • Resources:
      - Total CPU Cores: 192
      - Total Memory: 1536 GB
      - Total Storage: 70 TB
    • Workload:
      - Running VMs: 7
      - Total VMs: 8
      - Average CPU Usage: 38.6%
      - Average Memory Usage: 42.8%
  ```

### execute_vm_command
Execute a command in a VM's console using QEMU Guest Agent.

- Parameters:
  - `node` (string, required): Name of the node where VM is running
  - `vmid` (string, required): ID of the VM
  - `command` (string, required): Command to execute
- Example Response:
  ```
  🔧 Console Command Result
    • Status: SUCCESS
    • Command: systemctl status nginx
    • Node: pve-compute-01
    • VM: prod-web-01 (ID: 102)

  Output:
  ● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2025-02-18 15:23:45 UTC; 2 months 3 days ago
  ```
- Requirements:
  - VM must be running
  - QEMU Guest Agent must be installed and running in the VM
  - Command execution permissions must be enabled in the Guest Agent
- Error Handling:
  - Returns error if VM is not running
  - Returns error if VM is not found
  - Returns error if command execution fails
  - Includes command output even if command returns non-zero exit code

## 👨‍💻 Development

After activating your virtual environment:

- Run tests: `pytest`
- Format code: `black .`
- Type checking: `mypy .`
- Lint: `ruff .`

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. **Claude Desktop Connection Timeout**
```
ERROR - Failed to connect to Proxmox: HTTPSConnectionPool(...): Max retries exceeded
```

**Solutions:**
- ✅ **Check Proxmox host**: Ensure the IP/hostname in `config-stdio.json` is correct
- ✅ **Verify network access**: Try pinging your Proxmox server
- ✅ **Check firewall**: Ensure port 8006 is accessible
- ✅ **Test manually**: Run the connection test script below

#### 2. **Authentication Errors**
```
401 Unauthorized: no such user
```

**Solutions:**
- ✅ **Check token format**: Use only the token name (e.g., `"MCP-Server"`) not the full identifier
- ✅ **Verify credentials**: Ensure token exists in Proxmox and has proper permissions
- ✅ **Service name**: Must be `"PVE"` exactly (case-sensitive)

#### 3. **JSON Parse Errors in Claude Desktop**
```
Unexpected token 'E', "Error: Fai"... is not valid JSON
```

**Solutions:**
- ✅ **Set log level**: Use `"ERROR"` instead of `"DEBUG"` in logging configuration
- ✅ **Fix connection**: Resolve underlying Proxmox connection issues first
- ✅ **Restart Claude**: Restart Claude Desktop after config changes

#### 4. **Module Not Found Errors**
```
ModuleNotFoundError: No module named 'proxmox_mcp'
```

**Solutions:**
- ✅ **Activate venv**: Always use `source venv/bin/activate`
- ✅ **Install dependencies**: Run `pip install -e .` in the project root
- ✅ **Check paths**: Ensure `cwd` points to the `src` directory

### Test Your Connection

Run this script to verify your Proxmox connection before using with Claude:

```bash
source venv/bin/activate
cd src
python -c "
import sys
sys.path.insert(0, '.')
from proxmox_mcp.config.loader import load_config
from proxmox_mcp.core.proxmox import ProxmoxManager

try:
    config = load_config('../config-stdio.json')
    print(f'Config loaded: {config.proxmox.host}:{config.proxmox.port}')
    
    manager = ProxmoxManager(config.proxmox, config.auth)
    api = manager.get_api()
    
    version = api.version.get()
    print(f'✅ Connected to Proxmox {version[\"version\"]}')
    
    nodes = api.nodes.get()
    print(f'✅ Found {len(nodes)} nodes')
    for node in nodes:
        print(f'  - {node[\"node\"]}: {node[\"status\"]}')
        
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### Configuration Validation

Ensure your `config-stdio.json` follows this format:

```json
{
  "proxmox": {
    "host": "192.168.0.200",     // Your Proxmox server IP
    "port": 8006,                // Usually 8006
    "verify_ssl": false,         // Set true if using valid SSL cert
    "service": "PVE"             // Must be exactly "PVE"
  },
  "auth": {
    "user": "root@pam",          // Your Proxmox user
    "token_name": "MCP-Server",  // Token name only (not user!tokenname)
    "token_value": "uuid-here"   // The actual token secret
  },
  "logging": {
    "level": "ERROR",            // Use ERROR for Claude Desktop
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "proxmox_mcp.log"
  },
  "transport": {
    "type": "stdio"
  },
  "authorization": {
    "enabled": false
  }
}
```

### Success Indicators

When everything is working correctly, you should see:

#### ✅ **Connection Test Success**
```bash
Config loaded: 192.168.0.200:8006
✅ Connected to Proxmox 8.4.1
✅ Found 1 nodes
  - pve1: online
```

#### ✅ **Claude Desktop Logs (Clean)**
```
[proxmox-mcp] [info] Initializing server...
[proxmox-mcp] [info] Server started and connected successfully
[proxmox-mcp] [info] Message from client: {"method":"initialize"...}
```

#### ✅ **Claude Desktop Usage**
Ask Claude: *"Can you show me the Proxmox nodes in my cluster?"*

Expected response with formatted node information showing status, uptime, CPU, memory, etc.

## 🔐 Security & Authorization

### Production Security Checklist

For production deployments with OAuth authorization:

- ✅ **Set a strong secret key** for JWT signing
- ✅ **Use HTTPS** for all OAuth endpoints  
- ✅ **Configure appropriate CORS** origins
- ✅ **Use secure redirect URIs**
- ✅ **Monitor and log** authorization events
- ✅ **Rotate tokens** regularly
- ✅ **Review scope permissions** for least privilege

### Default Test Client

A default client is pre-registered for testing:
- **Client ID**: `proxmox-mcp-client`
- **Client Type**: Public (no secret required)
- **Redirect URIs**: `http://localhost:3000/callback`
- **Allowed Scopes**: All configured scopes

See [AUTHORIZATION.md](AUTHORIZATION.md) for complete security documentation.

## 📁 Project Structure

```
proxmox-mcp/
├── src/
│   └── proxmox_mcp/
│       ├── server.py          # Main MCP server implementation
│       ├── auth/              # OAuth 2.1 authorization module
│       │   ├── models.py      # OAuth data models
│       │   ├── middleware.py  # Token validation middleware
│       │   ├── server.py      # Authorization server
│       │   └── exceptions.py  # Auth-specific exceptions
│       ├── config/            # Configuration handling
│       ├── core/              # Core functionality
│       ├── formatting/        # Output formatting and themes
│       ├── tools/             # Tool implementations
│       │   └── console/       # VM console operations
│       └── utils/             # Utilities (auth, logging)
├── tests/                     # Test suite
├── config-stdio.json         # Stdio mode configuration example
├── config-http-auth.json     # HTTP with OAuth configuration example
├── AUTHORIZATION.md           # Complete authorization documentation
├── pyproject.toml            # Project metadata and dependencies
└── LICENSE                   # MIT License
```

## 📄 License

MIT License
