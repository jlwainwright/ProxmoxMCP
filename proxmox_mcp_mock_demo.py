#!/usr/bin/env python3
"""
Mock demo script for Proxmox MCP functionality.
This script demonstrates the output format of Proxmox MCP tools using mock data.
"""

import sys
import logging
from unittest.mock import Mock
from mcp.types import TextContent as Content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("proxmox-mcp-mock-demo")

class MockProxmoxTools:
    """Mock implementation of Proxmox MCP tools."""
    
    def get_nodes(self):
        """Mock implementation of get_nodes."""
        return [
            Content(type="text", text="""
🖥️ Proxmox Nodes
═══════════════

Node: pve1
  • Status: 🟢 ONLINE
  • CPU: 12.5% (8 cores)
  • Memory: 8.2 GB / 32.0 GB (25.6%)
  • Uptime: 45d 7h 22m

Node: pve2
  • Status: 🟢 ONLINE
  • CPU: 5.3% (8 cores)
  • Memory: 6.1 GB / 32.0 GB (19.1%)
  • Uptime: 45d 6h 15m
""")
        ]
    
    def get_vms(self):
        """Mock implementation of get_vms."""
        return [
            Content(type="text", text="""
🖥️ Virtual Machines
══════════════════

VM: 100 (web-server)
  • Status: 🟢 RUNNING
  • Node: pve1
  • CPU: 2 cores
  • Memory: 1.2 GB / 4.0 GB

VM: 101 (db-server)
  • Status: 🟢 RUNNING
  • Node: pve1
  • CPU: 4 cores
  • Memory: 3.5 GB / 8.0 GB

VM: 102 (backup-server)
  • Status: 🔴 STOPPED
  • Node: pve2
  • CPU: 2 cores
  • Memory: 0.0 GB / 4.0 GB
""")
        ]
    
    def get_storage(self):
        """Mock implementation of get_storage."""
        return [
            Content(type="text", text="""
💾 Storage Resources
══════════════════

Storage: local-lvm
  • Type: LVM-Thin
  • Status: 🟢 AVAILABLE
  • Used: 256.2 GB / 500.0 GB (51.2%)
  • Node: pve1

Storage: ceph-pool
  • Type: RBD
  • Status: 🟢 AVAILABLE
  • Used: 1.2 TB / 4.0 TB (30.0%)
  • Shared: Yes
""")
        ]
    
    def get_cluster_status(self):
        """Mock implementation of get_cluster_status."""
        return [
            Content(type="text", text="""
🔄 Cluster Status
═══════════════

Cluster: pve-cluster
  • Status: 🟢 HEALTHY
  • Nodes: 2 online, 0 offline
  • Quorum: Yes
  • Services: 
    - corosync: 🟢 RUNNING
    - pve-cluster: 🟢 RUNNING
    - ceph: 🟢 RUNNING
""")
        ]
    
    async def execute_command(self, node, vmid, command):
        """Mock implementation of execute_command."""
        return [
            Content(type="text", text=f"""
🖥️ Console Command Result
  • Status: SUCCESS
  • Command: {command}

Output:
Linux web-server 5.15.0-generic #1 SMP PREEMPT_DYNAMIC Thu Jun 15 05:53:08 UTC 2023 x86_64 GNU/Linux
""")
        ]

def main():
    """Main function to demonstrate Proxmox MCP functionality with mock data."""
    
    logger.info("Starting mock demonstration of Proxmox MCP")
    
    # Create mock tools
    mock_tools = MockProxmoxTools()
    
    # Demonstrate functionality with mock data
    try:
        # Get nodes
        logger.info("Getting nodes (mock data)...")
        nodes = mock_tools.get_nodes()
        print("\n=== Nodes ===")
        for content in nodes:
            print(content.text)
        
        # Get VMs
        logger.info("Getting VMs (mock data)...")
        vms = mock_tools.get_vms()
        print("\n=== VMs ===")
        for content in vms:
            print(content.text)
        
        # Get storage
        logger.info("Getting storage (mock data)...")
        storage = mock_tools.get_storage()
        print("\n=== Storage ===")
        for content in storage:
            print(content.text)
        
        # Get cluster status
        logger.info("Getting cluster status (mock data)...")
        cluster = mock_tools.get_cluster_status()
        print("\n=== Cluster Status ===")
        for content in cluster:
            print(content.text)
            
    except Exception as e:
        logger.error(f"Error during demonstration: {e}")
        sys.exit(1)
    
    logger.info("Mock demo completed successfully")

if __name__ == "__main__":
    main()