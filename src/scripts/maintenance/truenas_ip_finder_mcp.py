#!/usr/bin/env python3
"""
TrueNAS IP Finder using ProxmoxMCP Tools
Practical script to discover TrueNAS VM IP address using MCP server tools.

Usage:
    python truenas_ip_finder_mcp.py

This script demonstrates the exact MCP tool calls needed to discover the TrueNAS IP address.
"""

import json
import sys
from datetime import datetime

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_mcp_call(tool_name, parameters, description):
    """Print a formatted MCP tool call."""
    print(f"\n🔧 {description}")
    print(f"Tool: {tool_name}")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    print("-" * 40)

def main():
    """Main function to show TrueNAS discovery using ProxmoxMCP tools."""
    
    print_section("TrueNAS IP Discovery using ProxmoxMCP")
    print("Target VM: 800 (TrueNAS)")
    print("Node: pve1")
    print("MAC: BC:24:11:E6:DE:06")
    print("Goal: Find IP address for web interface access")
    
    # VM details
    truenas_node = "pve1"
    truenas_vmid = "800"
    
    print_section("Step 1: Check VM Status")
    print_mcp_call(
        "get_vm_status",
        {
            "node": truenas_node,
            "vmid": truenas_vmid
        },
        "Check if TrueNAS VM is running and get basic info"
    )
    
    print_section("Step 2: Get Network Configuration")
    print_mcp_call(
        "get_vm_network_config",
        {
            "node": truenas_node,
            "vmid": truenas_vmid
        },
        "Get network interfaces and IP addresses from inside VM"
    )
    
    print_section("Step 3: Execute Direct Network Commands")
    
    # Network commands to get IP info
    network_commands = [
        "ip addr show",
        "hostname -I",
        "ifconfig",
        "ip route show",
        "cat /etc/resolv.conf"
    ]
    
    for cmd in network_commands:
        print_mcp_call(
            "execute_vm_command",
            {
                "node": truenas_node,
                "vmid": truenas_vmid,
                "command": cmd
            },
            f"Execute '{cmd}' to get network info"
        )
    
    print_section("Step 4: Discover Web Services")
    print_mcp_call(
        "discover_web_services",
        {
            "node": truenas_node,
            "vmid": truenas_vmid
        },
        "Discover TrueNAS web interface and other web services"
    )
    
    print_section("Step 5: Discover API Endpoints")
    print_mcp_call(
        "discover_api_endpoints",
        {
            "node": truenas_node,
            "vmid": truenas_vmid
        },
        "Discover TrueNAS REST API endpoints"
    )
    
    print_section("Step 6: List VM Services")
    print_mcp_call(
        "list_vm_services",
        {
            "node": truenas_node,
            "vmid": truenas_vmid
        },
        "List all running services to identify TrueNAS components"
    )
    
    print_section("Alternative Methods if MCP Tools Fail")
    
    print("\n🔍 Proxmox Console Access:")
    print("1. Access Proxmox web interface")
    print("2. Navigate to pve1 → VM 800")
    print("3. Click 'Console' tab")
    print("4. Login to TrueNAS")
    print("5. Run: ifconfig or ip addr show")
    
    print("\n🔍 Network Scanning Methods:")
    print("1. Check DHCP server logs for MAC: BC:24:11:E6:DE:06")
    print("2. Scan common networks:")
    print("   - nmap -sn 192.168.1.0/24")
    print("   - nmap -sn 192.168.0.0/24")
    print("   - nmap -sn 10.0.0.0/24")
    print("3. Look for TrueNAS services on discovered IPs:")
    print("   - Port 80/443 (Web UI)")
    print("   - Port 22 (SSH)")
    print("   - Port 139/445 (SMB)")
    
    print("\n🔍 TrueNAS Specific Checks:")
    print("Once IP is found, test these URLs:")
    print("   - http://<IP>")
    print("   - https://<IP>")
    print("   - http://<IP>:8080")
    print("   - https://<IP>:8443")
    
    print_section("Expected Output Analysis")
    
    expected_outputs = {
        "get_vm_network_config": {
            "success": "Should show interface with IP address",
            "fields": ["interfaces", "gateway", "dns"],
            "example": "eth0: 192.168.1.100/24"
        },
        "execute_vm_command (ip addr show)": {
            "success": "Shows all network interfaces with IPs",
            "look_for": "inet 192.168.x.x/24"
        },
        "discover_web_services": {
            "success": "Should detect TrueNAS web interface",
            "look_for": ["nginx", "web server", "port 80/443"]
        },
        "discover_api_endpoints": {
            "success": "Should find TrueNAS REST API",
            "look_for": ["/api/v2.0", "swagger", "websocket"]
        }
    }
    
    for tool, expectations in expected_outputs.items():
        print(f"\n📋 {tool}:")
        for key, value in expectations.items():
            if isinstance(value, list):
                print(f"   {key}: {', '.join(value)}")
            else:
                print(f"   {key}: {value}")
    
    print_section("Ready to Execute")
    print("Copy the MCP tool calls above and execute them in your Claude Code session.")
    print("The tool calls are properly formatted and ready to use.")
    print("\nExample usage in Claude Code:")
    print("  Just paste each tool call exactly as shown above.")
    
    print(f"\n📝 Discovery session logged at: {datetime.now().isoformat()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())