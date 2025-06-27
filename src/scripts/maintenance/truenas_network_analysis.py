#!/usr/bin/env python3
"""
TrueNAS VM Network Analysis Script

This script analyzes the TrueNAS VM network configuration and attempts
to discover why IP discovery might have failed.
"""
import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/Users/jacques/DevFolder/ProxmoxMCP/src')

try:
    from proxmox_mcp.config.loader import load_config
    from proxmox_mcp.core.node_manager import NodeManager
    from proxmox_mcp.tools.vm import VMTools
except ImportError as e:
    print(f"Error importing ProxmoxMCP modules: {e}")
    sys.exit(1)

async def analyze_truenas_network():
    """Analyze TrueNAS VM network configuration."""
    try:
        # Load configuration
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/config.json"
        config = load_config(config_path)
        
        # Initialize node manager and tools
        node_manager = NodeManager(config)
        vm_tools = VMTools(node_manager)
        
        print("=== TrueNAS VM Network Analysis ===\n")
        
        # Try to get network configuration using guest agent
        print("1. Attempting to get network configuration via QEMU guest agent:")
        print("-" * 70)
        try:
            network_result = await vm_tools.get_vm_network_config("pve1", "800")
            if network_result:
                for content in network_result:
                    print(content.text)
            print()
        except Exception as e:
            print(f"Error getting network config via guest agent: {e}\n")
        
        # Try to detect OS to understand why guest agent might not work
        print("2. Attempting OS detection:")
        print("-" * 70)
        try:
            os_result = await vm_tools.detect_vm_os("pve1", "800")
            if os_result:
                for content in os_result:
                    print(content.text)
            print()
        except Exception as e:
            print(f"Error detecting OS: {e}\n")
        
        # Try to execute a simple command
        print("3. Testing QEMU guest agent connectivity:")
        print("-" * 70)
        try:
            cmd_result = await vm_tools.execute_command("pve1", "800", "echo 'Guest agent test'")
            if cmd_result:
                for content in cmd_result:
                    print(content.text)
            print()
        except Exception as e:
            print(f"Error executing command via guest agent: {e}\n")
        
        # Check direct API access for network information
        print("4. Direct API network information:")
        print("-" * 70)
        try:
            # Get the Proxmox API client
            proxmox = node_manager.get_api()
            
            # Try to get agent info
            try:
                agent_info = proxmox.nodes("pve1").qemu("800").agent.get()
                print("QEMU Guest Agent Status:")
                print(f"  Available: {agent_info}")
                print()
            except Exception as e:
                print(f"QEMU Guest Agent not available: {e}\n")
            
            # Get detailed network interface info from status
            vm_status = proxmox.nodes("pve1").qemu("800").status.current.get()
            if 'nics' in vm_status:
                print("Network Interface Statistics:")
                for nic, stats in vm_status['nics'].items():
                    print(f"  Interface: {nic}")
                    print(f"    Bytes in: {stats.get('netin', 0):,}")
                    print(f"    Bytes out: {stats.get('netout', 0):,}")
                print()
            
            # Check VM configuration for network setup
            vm_config = proxmox.nodes("pve1").qemu("800").config.get()
            print("Network Configuration from VM Config:")
            for key, value in vm_config.items():
                if key.startswith('net'):
                    print(f"  {key}: {value}")
            print()
            
        except Exception as e:
            print(f"Error accessing direct API: {e}\n")
        
        print("=== Network Analysis Complete ===")
        
    except Exception as e:
        print(f"Network analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_truenas_network())