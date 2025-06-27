#!/usr/bin/env python3
"""
Demo script for Proxmox MCP functionality.
This script demonstrates how to use the Proxmox MCP tools once you have a valid connection.
"""

import sys
import logging
from proxmox_mcp.config.loader import load_config
from proxmox_mcp.core.proxmox import ProxmoxManager
from proxmox_mcp.tools.node import NodeTools
from proxmox_mcp.tools.vm import VMTools
from proxmox_mcp.tools.storage import StorageTools
from proxmox_mcp.tools.cluster import ClusterTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("proxmox-mcp-demo")

def main():
    """Main function to demonstrate Proxmox MCP functionality."""
    
    # Load configuration
    config_path = "config.json"
    try:
        config = load_config(config_path)
        logger.info(f"Loaded configuration from {config_path}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Initialize Proxmox connection
    try:
        logger.info(f"Connecting to Proxmox at {config.proxmox.host}...")
        proxmox_manager = ProxmoxManager(config.proxmox, config.auth)
        proxmox = proxmox_manager.get_api()
        logger.info("Successfully connected to Proxmox API")
    except Exception as e:
        logger.error(f"Failed to connect to Proxmox: {e}")
        sys.exit(1)
    
    # Initialize tools
    node_tools = NodeTools(proxmox)
    vm_tools = VMTools(proxmox)
    storage_tools = StorageTools(proxmox)
    cluster_tools = ClusterTools(proxmox)
    
    # Demonstrate functionality
    try:
        # Get nodes
        logger.info("Getting nodes...")
        nodes = node_tools.get_nodes()
        print("\n=== Nodes ===")
        for content in nodes:
            print(content.text)
        
        # Get VMs
        logger.info("Getting VMs...")
        vms = vm_tools.get_vms()
        print("\n=== VMs ===")
        for content in vms:
            print(content.text)
        
        # Get storage
        logger.info("Getting storage...")
        storage = storage_tools.get_storage()
        print("\n=== Storage ===")
        for content in storage:
            print(content.text)
        
        # Get cluster status
        logger.info("Getting cluster status...")
        cluster = cluster_tools.get_cluster_status()
        print("\n=== Cluster Status ===")
        for content in cluster:
            print(content.text)
            
    except Exception as e:
        logger.error(f"Error during demonstration: {e}")
        sys.exit(1)
    
    logger.info("Demo completed successfully")

if __name__ == "__main__":
    main()