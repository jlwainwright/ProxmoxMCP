# 🖥️ Local Development Setup

This guide covers running ProxmoxMCP locally for development and testing.

## ✅ Prerequisites Verified

The local environment has been tested and confirmed working:

- ✅ **Configuration Loading**: Loads Proxmox settings correctly
- ✅ **Server Initialization**: All tools and components load properly
- ✅ **Proxmox Connection**: Successfully connects to Proxmox VE 8.4.1

## 🚀 Quick Start

### 1. Configuration Setup

The project is already configured with a working configuration file:

```bash
# Configuration location
/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json

# Current settings
Host: 192.168.0.200:8006
User: mcp@pve
Transport: stdio (MCP client mode)
SSL Verify: false (development only)
```

### 2. Running the Server

**Option A: Using the convenience script**
```bash
cd /Users/jacques/DevFolder/ProxmoxMCP/src
./run_local.sh
```

**Option B: Manual execution**
```bash
cd /Users/jacques/DevFolder/ProxmoxMCP/src
export PROXMOX_MCP_CONFIG="/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
python -m proxmox_mcp.server
```

### 3. Testing the Setup

Run the comprehensive test suite:
```bash
cd /Users/jacques/DevFolder/ProxmoxMCP/src
python test_local_run.py
```

## 🔌 MCP Client Integration

The server is configured for **stdio transport** mode, perfect for MCP clients like:

- **Claude Desktop**
- **Claude Code CLI** 
- **Cline (VS Code)**
- **Cursor IDE**
- **Windsurf**

### Claude Desktop Configuration

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "proxmox-mcp": {
      "command": "/Users/jacques/DevFolder/ProxmoxMCP/venv/bin/python",
      "args": ["-m", "proxmox_mcp.server"],
      "cwd": "/Users/jacques/DevFolder/ProxmoxMCP/src",
      "env": {
        "PROXMOX_MCP_CONFIG": "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
      }
    }
  }
}
```

## 🛠️ Available Tools

The server provides **31 comprehensive MCP tools** across multiple phases:

### 📊 **Tool Categories**
- **Core Infrastructure** (11 tools): Node/VM/storage/cluster management
- **Deep Analysis** (4 tools): OS detection, system info, services, network
- **Container Management** (4 tools): Docker/Podman runtime control
- **Application Discovery** (4 tools): Web services, databases, APIs, stack analysis
- **Monitoring Automation** (4 tools): Grafana, Prometheus, alerting, logs
- **Backup Automation** (4 tools): Intelligent scheduling, verification, DR planning

### 🚀 **Key Tools Examples**
| Tool | Description | Category |
|------|-------------|----------|
| `get_cluster_status` | Complete cluster overview | Core Infrastructure |
| `analyze_application_stack` | Full technology stack analysis | Application Discovery |
| `generate_grafana_dashboard` | Auto-create monitoring dashboards | Monitoring Automation |
| `create_intelligent_backup_schedule` | Smart backup by VM criticality | Backup Automation |
| `manage_docker_container` | Control containers within VMs | Container Management |

For complete tool documentation, see [**Tools Summary**](TOOLS_SUMMARY.md).

## 🔧 Development Features

### Live Configuration Reloading

The server loads configuration on startup. To change settings:

1. Edit `config/config.json`
2. Restart the server
3. Configuration changes take effect immediately

### Debug Mode

For detailed logging, modify the config:

```json
{
  "logging": {
    "level": "DEBUG",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "proxmox_mcp_debug.log"
  }
}
```

### Security Warnings

The current configuration shows these security warnings:

```
SECURITY WARNING: SSL verification disabled (verify_ssl: false) - Enable for production
```

This is normal for development environments. For production:

```json
{
  "proxmox": {
    "verify_ssl": true
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Module Import Warnings**
   ```
   RuntimeWarning: 'proxmox_mcp.server' found in sys.modules
   ```
   This is a harmless Python import warning and doesn't affect functionality.

2. **Connection Errors**
   ```
   HTTPSConnectionPool(...): Max retries exceeded
   ```
   - Verify Proxmox server is accessible at `192.168.0.200:8006`
   - Check network connectivity
   - Ensure Proxmox web interface is running

3. **Authentication Errors**
   ```
   401 Unauthorized
   ```
   - Verify API token is valid in Proxmox
   - Check user permissions
   - Ensure token hasn't expired

### Verification Commands

```bash
# Test configuration loading
python -c "from proxmox_mcp.config.loader import load_config; print('Config OK')"

# Test Proxmox connection
python -c "
from proxmox_mcp.config.loader import load_config
from proxmox_mcp.core.proxmox import ProxmoxManager
config = load_config('/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json')
manager = ProxmoxManager(config.proxmox, config.auth)
api = manager.get_api()
print(f'Connected to Proxmox {api.version.get()[\"version\"]}')
"
```

## 📈 Performance Monitoring

### Resource Usage

Monitor the server's resource consumption:

```bash
# Memory usage
ps aux | grep proxmox_mcp

# CPU usage
top -p $(pgrep -f proxmox_mcp)
```

### API Call Monitoring

The server logs all Proxmox API calls. Enable detailed logging to track:

- API response times
- Error rates
- Tool usage patterns

## 🚀 Next Steps

### Production Deployment

For production use, consider:

1. **Docker Deployment**: Use the provided Docker setup
2. **SSL Certificates**: Enable SSL verification
3. **Monitoring**: Set up Prometheus/Grafana stack
4. **Authentication**: Configure OAuth 2.1 for HTTP mode

### Development Extensions

The server architecture supports:

- Custom tool development
- Additional Proxmox API integrations
- Enhanced formatting and themes
- Multi-node cluster management

---

**Status**: ✅ **Ready for Development**
**Last Tested**: Proxmox VE 8.4.1
**Environment**: macOS with Python 3.13.5