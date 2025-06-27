#!/bin/bash
# ProxmoxMCP Local Runner Script
# Easy script to start the server locally

echo "🚀 Starting ProxmoxMCP Server Locally"
echo "======================================"

# Set configuration path
export PROXMOX_MCP_CONFIG="/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"

# Check if config exists
if [[ ! -f "$PROXMOX_MCP_CONFIG" ]]; then
    echo "❌ Configuration file not found: $PROXMOX_MCP_CONFIG"
    echo "   Please ensure config.json exists with valid Proxmox settings"
    exit 1
fi

echo "📁 Using config: $PROXMOX_MCP_CONFIG"
echo "🔧 Starting server in stdio mode..."
echo ""

# Start the server
python -m proxmox_mcp.server

echo ""
echo "👋 Server stopped."