#!/usr/bin/env python3
"""
Main server implementation for Proxmox MCP.

This module implements the core MCP server for Proxmox integration, providing:
- Configuration loading and validation
- Logging setup
- Proxmox API connection management
- MCP tool registration and routing
- Signal handling for graceful shutdown

The server exposes a set of tools for managing Proxmox resources including:
- Node management
- VM operations
- Storage management
- Cluster status monitoring
"""
import logging
import os
import sys
import signal

from mcp.server import FastMCP

from .config.loader import load_config
from .core.logging import setup_logging
from .core.proxmox import ProxmoxManager
from .tools.node import NodeTools
from .tools.vm import VMTools
from .tools.storage import StorageTools
from .tools.cluster import ClusterTools
from .tools.definitions import (
    GET_NODES_DESC,
    GET_NODE_STATUS_DESC,
    GET_VMS_DESC,
    EXECUTE_VM_COMMAND_DESC,
    GET_CONTAINERS_DESC,
    GET_STORAGE_DESC,
    GET_CLUSTER_STATUS_DESC
)

class ProxmoxMCPServer:
    """Main server class for Proxmox MCP."""

    def __init__(self, config_path: str = None):
        """Initialize the server.

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config.logging)
        
        # Initialize core components
        self.proxmox_manager = ProxmoxManager(self.config.proxmox, self.config.auth)
        self.proxmox = self.proxmox_manager.get_api()
        
        # Initialize tools
        self.node_tools = NodeTools(self.proxmox)
        self.vm_tools = VMTools(self.proxmox)
        self.storage_tools = StorageTools(self.proxmox)
        self.cluster_tools = ClusterTools(self.proxmox)
        
        # Initialize MCP server
        self.mcp = FastMCP(
            name="ProxmoxMCP"
        )
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Register MCP tools with the server.
        
        Initializes and registers all available tools with the MCP server:
        - Node management tools (list nodes, get status)
        - VM operation tools (list VMs, execute commands)
        - Storage management tools (list storage)
        - Cluster tools (get cluster status)
        
        Each tool is registered with appropriate descriptions and parameter
        validation using Pydantic models.
        """
        
        # Node tools
        @self.mcp.tool(description=GET_NODES_DESC)
        def get_nodes():
            return self.node_tools.get_nodes()

        @self.mcp.tool(description=GET_NODE_STATUS_DESC)
        def get_node_status(node: str):
            return self.node_tools.get_node_status(node)

        # VM tools
        @self.mcp.tool(description=GET_VMS_DESC)
        def get_vms():
            return self.vm_tools.get_vms()

        @self.mcp.tool(description=EXECUTE_VM_COMMAND_DESC)
        async def execute_vm_command(node: str, vmid: str, command: str):
            return await self.vm_tools.execute_command(node, vmid, command)

        # Storage tools
        @self.mcp.tool(description=GET_STORAGE_DESC)
        def get_storage():
            return self.storage_tools.get_storage()

        # Cluster tools
        @self.mcp.tool(description=GET_CLUSTER_STATUS_DESC)
        def get_cluster_status():
            return self.cluster_tools.get_cluster_status()

    def start(self) -> None:
        """Start the MCP server.

        Initializes the server with:
        - Signal handlers for graceful shutdown (SIGINT, SIGTERM)
        - Async runtime for handling concurrent requests
        - Error handling and logging

        The server runs until terminated by a signal or fatal error.
        """
        def signal_handler(signum, frame):
            self.logger.info("Received signal to shutdown...")
            sys.exit(0)

        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            self.logger.info("Starting MCP server...")
            self.mcp.run()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            sys.exit(1)

def main():
    """Entry point for the Proxmox MCP server."""
    config_path = os.getenv("PROXMOX_MCP_CONFIG")
    if not config_path:
        print("PROXMOX_MCP_CONFIG environment variable must be set")
        sys.exit(1)

    try:
        server = ProxmoxMCPServer(config_path)
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
