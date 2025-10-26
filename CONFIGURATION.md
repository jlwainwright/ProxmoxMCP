# Proxmox MCP Server Configuration

## Changes Made (September 5, 2025)

### 1. Deleted Mock Server
- **Removed**: `main_fastmcp.py` (renamed to `main_fastmcp.py.deprecated`)
- **Reason**: Was a mock implementation that didn't connect to real Proxmox instances

### 2. Updated to Real Implementation
- **Active File**: `/src/proxmox_mcp/server.py`
- **Features**: Full Proxmox API integration with real connection capabilities

### 3. Created Multi-Node Configuration

#### Configuration Files Created:
```
proxmox-config/
├── config.json                 # Primary config (points to 192.168.0.200)
├── config-node-200.json        # HP ProDesk 400 G5 (pve1)
├── config-node-201.json        # Intel NUC11ATK
├── config-node-202.json        # Intel NUC10i5FNH
└── config.example.json         # Template for new nodes
```

### 4. MCP Server Entries

The Claude Desktop configuration now has 4 Proxmox entries:

1. **proxmox-mcp** - Primary cluster connection (192.168.0.200)
2. **proxmox-node-200** - HP ProDesk 400 G5 (192.168.0.200)
3. **proxmox-node-201** - Intel NUC11ATK (192.168.0.201)  
4. **proxmox-node-202** - Intel NUC10i5FNH (192.168.0.202)

## Node Details

### Node 200 - HP ProDesk 400 G5
- **IP**: 192.168.0.200:8006
- **Hardware**: i3-9100T, 16GB RAM, 512GB NVMe
- **Role**: Primary node with most VMs
- **VMs**: 101, 102, 103, 104, 106, 110, 600, 601, 800

### Node 201 - Intel NUC11ATK
- **IP**: 192.168.0.201:8006
- **Hardware**: Celeron N4505, 12GB RAM, 954GB NVMe
- **Role**: Container host
- **VMs**: 100, 101, 102, 103, 999

### Node 202 - Intel NUC10i5FNH
- **IP**: 192.168.0.202:8006
- **Hardware**: i5-10210U, 12GB RAM, 128GB NVMe
- **Role**: Lightweight node
- **VMs**: 100, 101

## Authentication
All nodes use the same authentication token:
- **User**: root@pam
- **Token Name**: mcp-token
- **Token Value**: f536e122-8fd1-4bb7-b028-cdd2ae312633

## Usage

After restarting Claude Desktop, you can:
1. Use `proxmox-mcp` for general cluster operations (connects to primary node)
2. Use `proxmox-node-200/201/202` to connect to specific nodes
3. All connections use the real Proxmox API, not mock data

## File Structure
```
/Users/jacques/DevFolder/mcp_servers/proxmox-mcp-server/
├── src/proxmox_mcp/server.py           # Main server implementation
├── proxmox-config/                     # Configuration files
│   ├── config.json                     # Primary (192.168.0.200)
│   ├── config-node-200.json            # HP ProDesk
│   ├── config-node-201.json            # NUC11ATK
│   └── config-node-202.json            # NUC10i5FNH
├── main_fastmcp.py.deprecated           # Old mock server (removed)
└── venv/                                # Python virtual environment
```