# 🚀 Proxmox Manager - Proxmox MCP Server

![ProxmoxMCP](https://github.com/user-attachments/assets/e32ab79f-be8a-420c-ab2d-475612150534)

## 🚨 CRITICAL SECURITY NOTICE

**This MCP server provides direct access to your Proxmox virtualization infrastructure. Improper configuration can expose your entire virtual environment to security risks.**

**⚠️ BEFORE INSTALLATION: READ [SECURITY.md](SECURITY.md)**

**🔒 REQUIRED SECURITY ACTIONS:**
- **Change ALL default credentials** before first use
- **Enable SSL verification** (`verify_ssl: true`) for production
- **Use dedicated service accounts** (not root@pam)
- **Generate strong API tokens** with expiration dates
- **Never commit credentials** to version control

---

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

4. **🔒 SECURITY: Use the secure configuration template:**
   ```bash
   # Copy secure template with validation
   cp config-secure-template.json proxmox-config/config.json
   ```

   **⚠️ CRITICAL: Replace ALL placeholder values marked with "CHANGE-THIS"**
   
   **🚨 INSECURE EXAMPLE (DO NOT USE AS-IS):**
   ```json
   {
       "proxmox": {
           "host": "CHANGE-THIS-PROXMOX-HOST-VALUE",
           "verify_ssl": true,            // ⚠️ REQUIRED: Always true in production
           "service": "PVE"
       },
       "auth": {
           "user": "CHANGE-THIS-USER-VALUE@pam",     // ⚠️ Use dedicated service account
           "token_name": "CHANGE-THIS-TOKEN-NAME",   // ⚠️ Use descriptive names
           "token_value": "CHANGE-THIS-TOKEN-VALUE"  // ⚠️ Generate strong token
       }
   }
   ```

   **✅ SECURE PRODUCTION EXAMPLE:**
   ```json
   {
       "proxmox": {
           "host": "proxmox.internal.company.com",  // ✅ Your actual server
           "verify_ssl": true,                      // ✅ ALWAYS true
           "service": "PVE"
       },
       "auth": {
           "user": "mcp-service@pam",               // ✅ Dedicated account
           "token_name": "mcp-prod-2024-q4",       // ✅ Descriptive name
           "token_value": "a8f5c2d9-4e7b-4c3a"    // ✅ Strong generated token
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

**🚨 WARNING: This example contains insecure settings for demonstration only**

```json
{
  "proxmox": {
    "host": "proxmox.internal.company.com",     // ✅ Use your actual server
    "port": 8006,
    "verify_ssl": true,                         // ⚠️ CRITICAL: Always true in production
    "service": "PVE"
  },
  "auth": {
    "user": "mcp-service@pam",                  // ✅ Dedicated service account (not root)
    "token_name": "mcp-prod-2024-q4",          // ✅ Descriptive, versioned name
    "token_value": "REPLACE-WITH-GENERATED-TOKEN-VALUE"  // ⚠️ Generate secure token
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s",
    "file": "proxmox_mcp_security.log"         // ✅ Enable file logging
  },
  "transport": {
    "type": "stdio"
  },
  "authorization": {
    "enabled": false
  }
}
```

**🔒 SECURITY REQUIREMENTS:**
- Replace `REPLACE-WITH-GENERATED-TOKEN-VALUE` with actual secure token
- Ensure `verify_ssl: true` for production deployments
- Use dedicated service account with minimal permissions

#### HTTP with OAuth Configuration (`config-http-auth.json`)

**🚨 CRITICAL: This configuration requires additional security hardening**

```json
{
  "proxmox": {
    "host": "proxmox.internal.company.com",     // ✅ Use FQDN with valid cert
    "port": 8006,
    "verify_ssl": true,                         // ⚠️ CRITICAL: Must be true
    "service": "PVE"
  },
  "auth": {
    "user": "mcp-service@pam",                  // ✅ Dedicated service account
    "token_name": "mcp-oauth-prod-2024",       // ✅ Descriptive name
    "token_value": "REPLACE-WITH-SECURE-TOKEN" // ⚠️ Generate strong token
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s",
    "file": "proxmox_mcp_security.log"
  },
  "transport": {
    "type": "http",
    "host": "127.0.0.1",                       // ✅ SECURE: Localhost only
    "port": 8443                               // ✅ Non-standard port
  },
  "authorization": {
    "enabled": true,
    "issuer": "https://auth.internal.company.com",  // ✅ HTTPS only
    "audience": "proxmox-mcp-production",
    "scopes": [
      "proxmox:nodes:read"                     // ✅ Minimal required scope
    ],
    "token_expiry": 3600,                      // ✅ 1 hour maximum
    "dynamic_client_registration": false,     // ✅ Disabled for production
    "secret_key": "REPLACE-WITH-64-CHAR-CRYPTOGRAPHICALLY-SECURE-SECRET-KEY"
  }
}
```

**🚨 CRITICAL SECURITY WARNINGS:**
- **Replace ALL placeholder values** before deployment
- **Generate 64+ character secret key** for JWT signing
- **Use HTTPS only** for issuer and redirect URIs
- **Bind to localhost** (127.0.0.1) unless reverse proxy configured
- **Minimize OAuth scopes** to required permissions only
- **Disable dynamic client registration** in production

### OAuth 2.1 Scopes

When authorization is enabled, the following scopes control access:

- 🖥️ `proxmox:nodes:read` - List and view node information
- 🗃️ `proxmox:vms:read` - List and view VM information  
- ⚡ `proxmox:vms:execute` - Execute commands in VMs
- 💾 `proxmox:storage:read` - View storage information
- ⚙️ `proxmox:cluster:read` - View cluster status
- 📸 `proxmox:snapshots:read` - List and view VM snapshots
- 📸 `proxmox:snapshots:manage` - Create, delete, and rollback VM snapshots
- 📦 `proxmox:containers:read` - List and view LXC container information
- 📦 `proxmox:containers:control` - Start, stop, and manage LXC containers

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

## 🔌 Client Integration

This section covers adding and removing the Proxmox MCP server across all supported MCP clients.

### 📋 Quick Reference

| Client | Config File Location | Transport | Notes |
|--------|---------------------|-----------|-------|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)<br>`%APPDATA%/Claude/claude_desktop_config.json` (Windows)<br>`~/.config/Claude/claude_desktop_config.json` (Linux) | stdio | Restart required |
| **Claude Code CLI** | `~/.claude/settings.local.json` | stdio | Built-in MCP support |
| **Cline (VS Code)** | `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | stdio | VS Code extension |
| **Cursor** | `~/Library/Application Support/Cursor/User/globalStorage/anysphere.cursor/config.json` (macOS)<br>`%APPDATA%/Cursor/User/globalStorage/anysphere.cursor/config.json` (Windows) | stdio | IDE integration |
| **Windsurf** | `~/.windsurf/mcp_servers.json` | stdio | Codeium IDE |
| **Continue** | `~/.continue/config.json` | stdio | VS Code extension |

### 🖥️ Claude Desktop

**Add Server:**
```bash
# Generate configuration automatically
python3 -c "
import os
import json

# Get absolute paths for current directory
base_path = os.getcwd()
config = {
    'mcpServers': {
        'proxmox-mcp': {
            'command': os.path.join(base_path, 'venv/bin/python'),
            'args': ['-m', 'proxmox_mcp.server'],
            'cwd': os.path.join(base_path, 'src'),
            'env': {
                'PROXMOX_MCP_CONFIG': os.path.join(base_path, 'config.json')
            }
        }
    }
}

print('Add this to your Claude Desktop configuration:')
print(json.dumps(config, indent=2))
"
```

**Manual Configuration:**
```json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/path/to/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/path/to/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/path/to/ProxmoxMCP/config.json"
      }
    }
  }
}
```

**Remove Server:**
```bash
# Remove the "proxmox-mcp" key from mcpServers object
# Restart Claude Desktop
```

### 💻 Claude Code CLI

**Add Server:**
```bash
# Add to ~/.claude/settings.local.json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/path/to/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/path/to/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/path/to/ProxmoxMCP/config.json"
      }
    }
  }
}
```

**Remove Server:**
```bash
# Remove the "proxmox-mcp" entry from mcpServers
# Restart Claude Code CLI session
```

### 🤖 Cline (VS Code Extension)

**Add Server:**
```json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/path/to/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/path/to/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/path/to/ProxmoxMCP/config.json"
      }
    }
  }
}
```

**Configuration File Location:**
- **macOS/Linux**: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Windows**: `%APPDATA%/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**Remove Server:**
```bash
# Remove the "proxmox-mcp" entry from the configuration file
# Restart VS Code or reload the Cline extension
```

### 🎯 Cursor

**Add Server:**
```json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/path/to/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/path/to/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/path/to/ProxmoxMCP/config.json"
      }
    }
  }
}
```

**Configuration File Location:**
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/anysphere.cursor/config.json`
- **Windows**: `%APPDATA%/Cursor/User/globalStorage/anysphere.cursor/config.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/anysphere.cursor/config.json`

**Remove Server:**
```bash
# Remove the "proxmox-mcp" entry from mcpServers
# Restart Cursor
```

### 🌊 Windsurf

**Add Server:**
```json
{
  "servers": {
    "proxmox-mcp": {
      "command": "/path/to/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/path/to/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/path/to/ProxmoxMCP/config.json"
      }
    }
  }
}
```

**Configuration File Location:**
- **All Platforms**: `~/.windsurf/mcp_servers.json`

**Remove Server:**
```bash
# Remove the "proxmox-mcp" entry from servers
# Restart Windsurf
```

### ⏭️ Continue (VS Code Extension)

**Add Server:**
```json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/path/to/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/path/to/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/path/to/ProxmoxMCP/config.json"
      }
    }
  }
}
```

**Configuration File Location:**
- **All Platforms**: `~/.continue/config.json`

**Remove Server:**
```bash
# Remove the "proxmox-mcp" entry from mcpServers
# Restart VS Code or reload Continue extension
```

### 🔧 Universal Setup Script

Use this script to automatically configure the correct paths for any client:

```bash
#!/bin/bash
# universal_setup.sh - Generate MCP configuration for any client

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
SRC_DIR="$SCRIPT_DIR/src"
CONFIG_FILE="$SCRIPT_DIR/config.json"

echo "=== Proxmox MCP Universal Configuration ==="
echo "Base Path: $SCRIPT_DIR"
echo "Python: $VENV_PYTHON"
echo "Config: $CONFIG_FILE"
echo ""

cat <<EOF
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "$VENV_PYTHON",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "$SRC_DIR",
      "env": {
        "PROXMOX_MCP_CONFIG": "$CONFIG_FILE"
      }
    }
  }
}
EOF

echo ""
echo "Copy the JSON above to your MCP client configuration file."
echo "Remember to restart your client after making changes!"
```

### 🚨 Troubleshooting Client Integration

#### Common Issues

1. **Server Not Starting**
   - ✅ Verify Python virtual environment path is correct
   - ✅ Check that `config.json` exists and has proper Proxmox credentials
   - ✅ Ensure `cwd` points to the `src` directory

2. **Permission Errors**
   - ✅ Make sure the Python executable is executable
   - ✅ Check file permissions on configuration files
   - ✅ Verify virtual environment was created properly

3. **Configuration Not Loading**
   - ✅ Use absolute paths (not relative)
   - ✅ Check JSON syntax with a validator
   - ✅ Restart the client application completely

4. **Connection Timeouts**
   - ✅ Set logging level to `"ERROR"` in config.json
   - ✅ Verify Proxmox server is accessible
   - ✅ Check firewall settings

#### Verification Commands

```bash
# Test Python environment
source venv/bin/activate
python -c "import proxmox_mcp; print('✅ Module loads correctly')"

# Test configuration
python -c "
from proxmox_mcp.config.loader import load_config
config = load_config('config.json')
print(f'✅ Config loaded: {config.proxmox.host}')
"

# Test server startup
cd src
python -m proxmox_mcp.server --help
```

### 📝 Configuration Notes

**Important Setup Requirements:**
- ✅ **Use absolute paths** - Relative paths may not work across all clients
- ✅ **Set logging level to ERROR** - Reduces noise in client logs  
- ✅ **Point cwd to src directory** - Required for Python module loading
- ✅ **Restart client after changes** - Configuration changes require restart
- ✅ **Use config.json** - Not config-stdio.json or other variants

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

### create_vm_snapshot
Create a snapshot of a virtual machine.

- Parameters:
  - `node` (string, required): Host node name where the VM is located
  - `vmid` (string, required): VM ID number
  - `snapname` (string, required): Name for the new snapshot (alphanumeric, no spaces)
  - `description` (string, optional): Optional description for the snapshot
- Example Response:
  ```
  📸 VM Snapshot Creation
    • VM ID: 100
    • Node: pve1
    • Snapshot Name: pre-update
    • Description: Before system updates
    • Task ID: UPID:pve1:00001234:snapshot_task
    • Status: Snapshot creation initiated
  ```
- Requirements:
  - VM must be accessible on the specified node
  - Sufficient storage space for snapshot
  - Valid snapshot name (no special characters or spaces)

### list_vm_snapshots
List all snapshots for a specific virtual machine.

- Parameters:
  - `node` (string, required): Host node name where the VM is located
  - `vmid` (string, required): VM ID number
- Example Response:
  ```
  📸 VM Snapshots: 100
    • Node: pve1
    • Total Snapshots: 3

  📋 Snapshot List:
   1. pre-update-2024
      • Created: 2024-01-15 14:30:22
      • Description: Before critical updates
      • Parent: current
      
   2. stable-config
      • Created: 2024-01-10 09:15:10
      • Description: Working configuration
      • Parent: current
  ```

### delete_vm_snapshot
Delete a specific snapshot from a virtual machine.

- Parameters:
  - `node` (string, required): Host node name where the VM is located
  - `vmid` (string, required): VM ID number
  - `snapname` (string, required): Name of the snapshot to delete
  - `force` (boolean, optional): Force deletion even if snapshot has children (default: false)
- Example Response:
  ```
  🗑️ VM Snapshot Deletion
    • VM ID: 100
    • Node: pve1
    • Snapshot: old-snapshot
    • Force Mode: No
    • Task ID: UPID:pve1:00001235:delete_task
    • Status: Deletion initiated

  ⚠️ Warning: This operation is irreversible!
  ```
- Error Handling:
  - Returns error if snapshot does not exist
  - Returns error if snapshot has children and force=false
  - Includes list of available snapshots if target not found

### rollback_vm_snapshot
Rollback a virtual machine to a specific snapshot.

- Parameters:
  - `node` (string, required): Host node name where the VM is located
  - `vmid` (string, required): VM ID number
  - `snapname` (string, required): Name of the snapshot to rollback to
- Example Response:
  ```
  ⏪ VM Snapshot Rollback
    • VM ID: 100
    • Node: pve1
    • Target Snapshot: stable-config
    • Snapshot Date: 2024-01-10 09:15:10
    • Description: Working configuration
    • Task ID: UPID:pve1:00001236:rollback_task
    • Status: Rollback initiated

  ⚠️ Important:
     • All changes made since this snapshot will be LOST
     • This operation cannot be undone
  ```
- Requirements:
  - Target snapshot must exist
  - VM will be stopped during rollback if currently running
  - All data since snapshot creation will be permanently lost

### get_containers
List all LXC containers across the cluster with their status and configuration.

- Parameters:
  - `proxmox_node` (string, optional): Proxmox instance to query for multi-node setups
- Example Response:
  ```
  📦 LXC Containers
    • Total Containers: 3
    • Cluster-wide Status: 2 running, 1 stopped

  📋 Container List:

  🖥️ Node: pve1
     🟢 CT 200 - web-server
        • Status: running
        • Template: ubuntu-22.04
        • CPU: 15.2% (2 cores)
        • Memory: 512.0 MB / 2048.0 MB
        • Disk: 1.5 GB / 20.0 GB
        • Uptime: 1d 5h 30m
  ```
- Requirements:
  - Access to Proxmox cluster resources
  - OAuth scope: `proxmox:containers:read`

### start_container
Start an LXC container.

- Parameters:
  - `node` (string, required): Host node name where the container is located
  - `vmid` (string, required): Container ID number
  - `proxmox_node` (string, optional): Proxmox instance to query
- Example Response:
  ```
  🚀 Container Start Operation
    • Container ID: 200
    • Node: pve1
    • Previous Status: stopped
    • Operation: START
    • Task ID: UPID:pve1:00001234:start_task
    • Status: Start operation initiated

  ⏳ The container is now starting up. This typically takes 10-30 seconds
  ```
- Requirements:
  - Container must exist and be in stopped state
  - OAuth scope: `proxmox:containers:control`

### stop_container
Stop an LXC container.

- Parameters:
  - `node` (string, required): Host node name where the container is located
  - `vmid` (string, required): Container ID number
  - `proxmox_node` (string, optional): Proxmox instance to query
- Example Response:
  ```
  🛑 Container Stop Operation
    • Container ID: 200
    • Node: pve1
    • Previous Status: running
    • Operation: STOP
    • Task ID: UPID:pve1:00001235:stop_task
    • Status: Stop operation initiated

  ⏳ The container is now shutting down gracefully.
  ```
- Requirements:
  - Container must exist and be in running state
  - OAuth scope: `proxmox:containers:control`

### get_container_status
Get detailed status information for a specific LXC container.

- Parameters:
  - `node` (string, required): Host node name where the container is located
  - `vmid` (string, required): Container ID number
  - `proxmox_node` (string, optional): Proxmox instance to query
- Example Response:
  ```
  🟢 Container Status: CT 200
    • Name: web-server
    • Node: pve1
    • Status: RUNNING
    • Uptime: 1d 5h 30m

  📊 Resource Usage:
    • CPU: 15.2% (2 cores allocated)
    • Memory: 512.0 MB / 2048.0 MB (25.0%)
    • Disk: 1.5 GB / 20.0 GB (7.5%)

  ⚙️ Configuration:
    • Template: ubuntu-22.04-standard_22.04-1_amd64.tar.xz
    • Description: Web server container
  ```
- Requirements:
  - Container must exist on the specified node
  - OAuth scope: `proxmox:containers:read`

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

### 🚨 MANDATORY Production Security Checklist

**⚠️ CRITICAL: Complete ALL items before production deployment**

- [ ] **🔑 Changed ALL default credentials** and placeholder values
- [ ] **🔒 Enabled SSL verification** (`verify_ssl: true`)
- [ ] **👤 Created dedicated service account** (not root@pam)
- [ ] **🎫 Generated strong API tokens** with expiration dates
- [ ] **🔐 Set 64+ character JWT secret key** for authorization
- [ ] **🌐 Used HTTPS only** for all OAuth endpoints
- [ ] **🏠 Bound to specific IP** (not 0.0.0.0) or localhost only
- [ ] **📝 Enabled comprehensive logging** with security monitoring
- [ ] **🔥 Configured firewall rules** restricting access
- [ ] **⏰ Set token expiration** policies (1-4 hours max)
- [ ] **🎯 Minimized OAuth scopes** to required permissions only
- [ ] **📊 Implemented log monitoring** for security events

### 🛡️ Security Validation Script

**Run this before deployment to check for security issues:**

```bash
# Download and run security validation
curl -s https://raw.githubusercontent.com/canvrno/ProxmoxMCP/main/scripts/security-check.sh | bash

# Or manually check configuration
python3 -c "
import json
with open('config.json') as f:
    config = json.load(f)
    
# Check for placeholder values
config_str = json.dumps(config)
if any(placeholder in config_str for placeholder in ['CHANGE-THIS', 'your-token', 'localhost', 'example']):
    print('❌ CRITICAL: Placeholder values detected')
    exit(1)

# Check SSL verification
if not config.get('proxmox', {}).get('verify_ssl', False):
    print('❌ CRITICAL: SSL verification disabled')
    exit(1)

print('✅ Basic security validation passed')
"
```

### Default Test Client

A default client is pre-registered for testing:
- **Client ID**: `proxmox-mcp-client`
- **Client Type**: Public (no secret required)
- **Redirect URIs**: `http://localhost:3000/callback`
- **Allowed Scopes**: All configured scopes

See [AUTHORIZATION.md](AUTHORIZATION.md) for complete security documentation.

## 🐳 Docker Deployment

ProxmoxMCP supports containerized deployment with Docker and Docker Compose for both development and production environments.

### Quick Docker Start

```bash
# Clone and setup
git clone https://github.com/canvrno/ProxmoxMCP.git
cd ProxmoxMCP/src

# Development deployment
./scripts/setup/docker-setup.sh deploy --mode development

# Production deployment with monitoring
./scripts/setup/docker-setup.sh deploy --mode production
```

### Docker Services

| Service | Description | Port | Purpose |
|---------|-------------|------|---------|
| **proxmox-mcp** | Main MCP server | 8080 | Core application |
| **redis** | Cache & sessions | 6379 | OAuth session storage |
| **prometheus** | Metrics collection | 9090 | Performance monitoring |
| **grafana** | Dashboards | 3000 | Visualization |
| **nginx** | Reverse proxy | 80/443 | SSL termination (optional) |

### Deployment Modes

- **🔧 Development**: Live reloading, debug logging
- **🚀 Production**: Full monitoring stack, health checks
- **🌐 Production + Proxy**: Nginx reverse proxy with SSL

For complete Docker deployment instructions, see [**Docker Deployment Guide**](src/docs/DOCKER_DEPLOYMENT.md).

## 📁 Project Structure

```
proxmox-mcp/
├── src/
│   ├── proxmox_mcp/           # Core Python package
│   │   ├── server.py          # Main MCP server implementation
│   │   ├── auth/              # OAuth 2.1 authorization module
│   │   ├── config/            # Configuration handling
│   │   ├── core/              # Core functionality
│   │   ├── formatting/        # Output formatting and themes
│   │   ├── tools/             # Tool implementations
│   │   └── utils/             # Utilities (auth, logging)
│   ├── config/                # Configuration files
│   │   ├── examples/          # Example configurations
│   │   ├── prometheus.yml     # Metrics configuration
│   │   └── nginx/             # Proxy configuration
│   ├── docs/                  # Documentation
│   │   ├── DOCKER_DEPLOYMENT.md  # Docker guide
│   │   ├── SECURITY.md        # Security documentation
│   │   └── api/               # API documentation
│   ├── examples/              # Demo scripts and tutorials
│   ├── tests/                 # Test suite
│   ├── scripts/               # Setup and maintenance scripts
│   ├── Dockerfile             # Container definition
│   └── docker-compose.yml     # Multi-service deployment
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # This file
└── LICENSE                   # MIT License
```

## 📄 License

MIT License
