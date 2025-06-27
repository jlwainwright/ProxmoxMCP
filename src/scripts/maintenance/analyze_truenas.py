#!/usr/bin/env python3
"""
TrueNAS VM Analysis Script

This script analyzes the TrueNAS VM (ID: 800) configuration using the Proxmox API
to gather comprehensive information about its current setup and configuration.
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
    from proxmox_mcp.tools.node import NodeTools
except ImportError as e:
    print(f"Error importing ProxmoxMCP modules: {e}")
    print("Please ensure you're running from the correct directory")
    sys.exit(1)

def analyze_truenas_vm():
    """Analyze TrueNAS VM (ID: 800) configuration and status."""
    try:
        # Load configuration
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/config.json"
        config = load_config(config_path)
        
        # Initialize node manager and tools
        node_manager = NodeManager(config)
        vm_tools = VMTools(node_manager)
        node_tools = NodeTools(node_manager)
        
        print("=== TrueNAS VM (ID: 800) Analysis ===\n")
        
        # 1. Get all VMs to see TrueNAS in context
        print("1. All VMs on pve1 node:")
        print("-" * 50)
        try:
            vms_result = vm_tools.get_vms()
            if vms_result:
                for content in vms_result:
                    print(content.text)
            print()
        except Exception as e:
            print(f"Error getting VMs list: {e}\n")
        
        # 2. Get detailed VM status for TrueNAS
        print("2. TrueNAS VM Status (ID: 800):")
        print("-" * 50)
        try:
            status_result = vm_tools.get_vm_status("pve1", "800")
            if status_result:
                for content in status_result:
                    print(content.text)
            print()
        except Exception as e:
            print(f"Error getting VM status: {e}\n")
        
        # 3. Get node status to understand the host
        print("3. Host Node (pve1) Status:")
        print("-" * 50)
        try:
            node_result = node_tools.get_node_status("pve1")
            if node_result:
                for content in node_result:
                    print(content.text)
            print()
        except Exception as e:
            print(f"Error getting node status: {e}\n")
        
        # 4. Try to get VM configuration directly from API if available
        print("4. Raw VM Configuration (if accessible):")
        print("-" * 50)
        try:
            # Get the Proxmox API client
            proxmox = node_manager.get_api()
            
            # Get VM configuration
            vm_config = proxmox.nodes("pve1").qemu("800").config.get()
            print("VM Configuration:")
            for key, value in vm_config.items():
                print(f"  {key}: {value}")
            print()
            
            # Get VM current status
            vm_status = proxmox.nodes("pve1").qemu("800").status.current.get()
            print("VM Current Status:")
            for key, value in vm_status.items():
                print(f"  {key}: {value}")
            print()
            
        except Exception as e:
            print(f"Error accessing VM configuration directly: {e}\n")
        
        print("=== Analysis Complete ===")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_truenas_vm()