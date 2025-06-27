#!/usr/bin/env python3
"""
TrueNAS VM IP Discovery Script

This script attempts to discover the IP address of the TrueNAS VM
using alternative methods since QEMU guest agent is not configured.
"""
import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/Users/jacques/DevFolder/ProxmoxMCP/src')

try:
    from proxmox_mcp.config.loader import load_config
    from proxmox_mcp.core.node_manager import NodeManager
except ImportError as e:
    print(f"Error importing ProxmoxMCP modules: {e}")
    sys.exit(1)

def discover_truenas_ip():
    """Attempt to discover TrueNAS VM IP address using available methods."""
    try:
        # Load configuration
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/config.json"
        config = load_config(config_path)
        
        # Initialize node manager
        node_manager = NodeManager(config)
        proxmox = node_manager.get_api()
        
        print("=== TrueNAS VM IP Discovery ===\n")
        
        # Method 1: Try network-get-interfaces via QEMU guest agent
        print("1. Attempting network interface discovery via QEMU guest agent:")
        print("-" * 70)
        try:
            agent_result = proxmox.nodes("pve1").qemu("800").agent("network-get-interfaces").get()
            print("Network interfaces from guest agent:")
            print(json.dumps(agent_result, indent=2))
            print()
        except Exception as e:
            print(f"QEMU guest agent network interface discovery failed: {e}\n")
        
        # Method 2: Try get-osinfo via QEMU guest agent
        print("2. Attempting OS info discovery via QEMU guest agent:")
        print("-" * 70)
        try:
            osinfo_result = proxmox.nodes("pve1").qemu("800").agent("get-osinfo").get()
            print("OS information from guest agent:")
            print(json.dumps(osinfo_result, indent=2))
            print()
        except Exception as e:
            print(f"QEMU guest agent OS info discovery failed: {e}\n")
        
        # Method 3: Check network interfaces on the host for this VM
        print("3. Checking host network interfaces for VM 800:")
        print("-" * 70)
        try:
            # Get network information from the host node
            vm_config = proxmox.nodes("pve1").qemu("800").config.get()
            vm_status = proxmox.nodes("pve1").qemu("800").status.current.get()
            
            # Extract MAC address from config
            mac_address = None
            if 'net0' in vm_config:
                net_config = vm_config['net0']
                if 'virtio=' in net_config:
                    mac_address = net_config.split('virtio=')[1].split(',')[0]
            
            print(f"VM MAC Address: {mac_address}")
            print(f"VM Bridge: {'vmbr0' if 'bridge=vmbr0' in vm_config.get('net0', '') else 'unknown'}")
            print(f"VM Firewall: {'enabled' if 'firewall=1' in vm_config.get('net0', '') else 'disabled'}")
            
            # Network statistics
            if 'nics' in vm_status:
                for nic, stats in vm_status['nics'].items():
                    print(f"Interface {nic}:")
                    print(f"  - Traffic shows VM is active (in: {stats.get('netin', 0):,} bytes)")
                    print(f"  - Outbound traffic: {stats.get('netout', 0):,} bytes")
            print()
            
        except Exception as e:
            print(f"Error checking host network info: {e}\n")
        
        # Method 4: Suggest IP discovery methods
        print("4. Recommended IP Discovery Methods:")
        print("-" * 70)
        print("Since QEMU guest agent is not configured, you can discover the IP by:")
        print()
        print("A. Check your router/DHCP server logs for MAC address: BC:24:11:E6:DE:06")
        print("B. Use network scanning tools from another machine on the same network:")
        print("   - nmap -sn 192.168.0.0/24 (adjust subnet as needed)")
        print("   - arp -a | grep bc:24:11:e6:de:06")
        print("C. Check the TrueNAS console directly (if you have VM console access)")
        print("D. Access TrueNAS web UI if it's running on default ports:")
        print("   - Try http://[discovered-ip]:80 or https://[discovered-ip]:443")
        print("   - TrueNAS SCALE typically uses port 80/443 for web UI")
        print()
        print("E. Network scan for TrueNAS services:")
        print("   - TrueNAS typically runs SSH on port 22")
        print("   - Web interface on port 80/443")
        print("   - SMB/CIFS services on ports 139/445")
        print("   - NFS services on port 2049")
        print()
        
        # Method 5: Check if we can install guest agent
        print("5. QEMU Guest Agent Configuration:")
        print("-" * 70)
        print("To enable better VM introspection, consider installing QEMU guest agent:")
        print("- TrueNAS SCALE: Typically included, but may need enabling")
        print("- Access TrueNAS console and run: systemctl enable qemu-guest-agent")
        print("- Or through TrueNAS web UI: System > Advanced > Enable QEMU Guest Agent")
        print("- This will enable IP discovery, OS detection, and command execution")
        print()
        
        print("=== IP Discovery Analysis Complete ===")
        
    except Exception as e:
        print(f"IP discovery failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    discover_truenas_ip()