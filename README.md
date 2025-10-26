# 🚀 Proxmox Manager - Proxmox MCP Server

**Status:** ✅ **OPERATIONAL** *(Last tested: 2025-10-26)*
**MCP SDK:** FastMCP (latest)
**Tools Available:** 6 (nodes, VMs, storage, cluster management)

[![CI](https://github.com/jlwainwright/ProxmoxMCP/workflows/CI/badge.svg)](https://github.com/jlwainwright/ProxmoxMCP/actions/workflows/ci.yml)
[![Docker](https://github.com/jlwainwright/ProxmoxMCP/workflows/Docker%20Build/badge.svg)](https://github.com/jlwainwright/ProxmoxMCP/actions/workflows/docker.yml)
[![Security](https://github.com/jlwainwright/ProxmoxMCP/workflows/Security/badge.svg)](https://github.com/jlwainwright/ProxmoxMCP/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/jlwainwright/ProxmoxMCP/branch/main/graph/badge.svg)](https://codecov.io/gh/jlwainwright/ProxmoxMCP)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![ProxmoxMCP](https://github.com/user-attachments/assets/e32ab79f-be8a-420c-ab2d-475612150534)

A Python-based Model Context Protocol (MCP) server for interacting with Proxmox hypervisors, providing a clean interface for managing nodes, VMs, and containers.

## 🏗️ Built With

- [Cline](https://github.com/cline/cline) - Autonomous coding agent - Go faster with Cline.
- [Proxmoxer](https://github.com/proxmoxer/proxmoxer) - Python wrapper for Proxmox API
- [MCP SDK](https://github.com/modelcontextprotocol/sdk) - Model Context Protocol SDK
- [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type annotations

## ✨ Features

- 🤖 Full integration with Cline
- 🛠️ Built with the official MCP SDK
- 🔒 Secure token-based authentication with Proxmox
- 🖥️ Tools for managing nodes and VMs
- 💻 VM console command execution
- 📝 Configurable logging system
- ✅ Type-safe implementation with Pydantic
- 🎨 Rich output formatting with customizable themes



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
   source .venv/bin/activate  # Linux/macOS
   # OR
   .\.venv\Scripts\Activate.ps1  # Windows
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

## ⚙️ Configuration

### Proxmox API Token Setup
1. Log into your Proxmox web interface
2. Navigate to Datacenter -> Permissions -> API Tokens
3. Create a new API token:
   - Select a user (e.g., root@pam)
   - Enter a token ID (e.g., "mcp-token")
   - Uncheck "Privilege Separation" if you want full access
   - Save and copy both the token ID and secret


## 🚀 Running the Server

### Development Mode
For testing and development:
```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/macOS
# OR
.\.venv\Scripts\Activate.ps1  # Windows

# Run the server
python -m proxmox_mcp.server
```

### Cline Desktop Integration

For Cline users, add this configuration to your MCP settings file (typically at `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

```json
{
    "mcpServers": {
        "github.com/canvrno/ProxmoxMCP": {
            "command": "/absolute/path/to/ProxmoxMCP/.venv/bin/python",
            "args": ["-m", "proxmox_mcp.server"],
            "cwd": "/absolute/path/to/ProxmoxMCP",
            "env": {
                "PYTHONPATH": "/absolute/path/to/ProxmoxMCP/src",
                "PROXMOX_MCP_CONFIG": "/absolute/path/to/ProxmoxMCP/proxmox-config/config.json",
                "PROXMOX_HOST": "your-proxmox-host",
                "PROXMOX_USER": "username@pve",
                "PROXMOX_TOKEN_NAME": "token-name",
                "PROXMOX_TOKEN_VALUE": "token-value",
                "PROXMOX_PORT": "8006",
                "PROXMOX_VERIFY_SSL": "false",
                "PROXMOX_SERVICE": "PVE",
                "LOG_LEVEL": "DEBUG"
            },
            "disabled": false,
            "autoApprove": []
        }
    }
}
```

To help generate the correct paths, you can use this command:
```bash
# This will print the MCP settings with your absolute paths filled in
python -c "import os; print(f'''{{
    \"mcpServers\": {{
        \"github.com/canvrno/ProxmoxMCP\": {{
            \"command\": \"{os.path.abspath('.venv/bin/python')}\",
            \"args\": [\"-m\", \"proxmox_mcp.server\"],
            \"cwd\": \"{os.getcwd()}\",
            \"env\": {{
                \"PYTHONPATH\": \"{os.path.abspath('src')}\",
                \"PROXMOX_MCP_CONFIG\": \"{os.path.abspath('proxmox-config/config.json')}\",
                ...
            }}
        }}
    }}
}}''')"
```

Important:
- All paths must be absolute
- The Python interpreter must be from your virtual environment
- The PYTHONPATH must point to the src directory
- Restart VSCode after updating MCP settings

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

## 📁 Project Structure

```
proxmox-mcp/
├── src/
│   └── proxmox_mcp/
│       ├── server.py          # Main MCP server implementation
│       ├── config/            # Configuration handling
│       ├── core/              # Core functionality
│       ├── formatting/        # Output formatting and themes
│       ├── tools/             # Tool implementations
│       │   └── console/       # VM console operations
│       └── utils/             # Utilities (auth, logging)
├── tests/                     # Test suite
├── proxmox-config/
│   └── config.example.json    # Configuration template
├── pyproject.toml            # Project metadata and dependencies
└── LICENSE                   # MIT License
```

## 🐳 Docker Deployment

The ProxmoxMCP server is available as a Docker container for easy deployment:

### Quick Start with Docker

```bash
# Pull the latest image
docker pull ghcr.io/jlwainwright/proxmoxmcp:latest

# Create config file
mkdir -p $(pwd)/config
cat > $(pwd)/config/config.json << 'EOF'
{
  "proxmox": {
    "host": "your-proxmox-host.com",
    "port": 8006,
    "verify_ssl": false,
    "service": "PVE"
  },
  "auth": {
    "user": "your-user@pam",
    "token_name": "your-token-name",
    "token_value": "your-token-value"
  },
  "logging": {
    "level": "INFO"
  }
}
EOF

# Run container
docker run -d \
  --name proxmox-mcp \
  -v $(pwd)/config/config.json:/app/config.json:ro \
  -p 8080:8080 \
  ghcr.io/jlwainwright/proxmoxmcp:latest
```

### Docker Compose Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  proxmox-mcp:
    image: ghcr.io/jlwainwright/proxmoxmcp:latest
    container_name: proxmox-mcp
    ports:
      - "8080:8080"
    volumes:
      - ./config/config.json:/app/config.json:ro
    restart: unless-stopped
    environment:
      - PROXMOX_MCP_CONFIG=/app/config.json
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Multi-Architecture Support

The Docker images support multiple architectures:
- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (ARM 64-bit, Apple Silicon, ARM servers)

### Available Tags

| Tag | Description |
|-----|-------------|
| `latest` | Latest stable release |
| `dev` | Development build with additional tools |
| `v1.x.x` | Specific version tags |
| `main` | Latest commit from main branch |

### Building from Source

```bash
# Clone repository
git clone https://github.com/jlwainwright/ProxmoxMCP.git
cd ProxmoxMCP

# Build Docker image
docker build -t proxmox-mcp:local .

# Run locally built image
docker run -v $(pwd)/config.json:/app/config.json proxmox-mcp:local
```

## 🚀 Automated Deployment

### GitHub Actions CI/CD

This repository includes comprehensive GitHub Actions workflows:

- **🔄 Continuous Integration**: Runs tests, linting, and security scans on every push
- **🐳 Docker Build**: Automatically builds and publishes Docker images
- **🔒 Security Scanning**: Daily security scans with CodeQL, Trivy, and dependency audits
- **📦 Release Automation**: Automated releases with changelog generation
- **⬆️ Dependabot**: Automated dependency updates with security monitoring

### Manual Release Process

To create a new release:

```bash
# Tag the release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Run full test suite
# 2. Build and publish Docker images
# 3. Create GitHub release with changelog
# 4. Generate release artifacts
```

### Server-Side Deployment

For server deployment, you can now:

1. **Pull from GitHub**: `git pull origin main`
2. **Rebuild automatically**: GitHub Actions will trigger on push
3. **Use Docker**: `docker pull ghcr.io/jlwainwright/proxmoxmcp:latest`
4. **Monitor builds**: Check [Actions tab](https://github.com/jlwainwright/ProxmoxMCP/actions) for build status

## 📄 License

MIT License
