"""
Node Manager for multi-node Proxmox MCP operations.

This module handles multiple ProxmoxManager instances and provides:
- Dynamic connection switching based on node selection
- Connection pooling and caching for performance
- Unified API access interface
- Health monitoring across all nodes
- Graceful error handling for node failures

The NodeManager serves as the central point for all multi-node
Proxmox API interactions, managing connections and routing requests
to the appropriate Proxmox instance.
"""
import logging
from typing import Dict, Optional, Union
from proxmoxer import ProxmoxAPI

from ..config.models import Config, MultiNodeConfig, NodeConfig
from .proxmox import ProxmoxManager


class NodeManager:
    """Manager class for multi-node Proxmox operations.
    
    This class handles:
    - Multiple ProxmoxManager instances (one per node)
    - Dynamic connection switching based on node selection
    - Connection health monitoring and caching
    - Unified API access interface
    - Graceful error handling for node failures
    
    The manager provides a single point of access to multiple Proxmox
    instances, ensuring proper initialization and error handling.
    """
    
    def __init__(self, config: Config):
        """Initialize the Node Manager.

        Args:
            config: Configuration object (single or multi-node)
        """
        self.logger = logging.getLogger("proxmox-mcp.node-manager")
        self.config = config
        self.managers: Dict[str, ProxmoxManager] = {}
        self.default_node: str
        
        # Initialize based on configuration type
        if config.is_multi_node():
            self._setup_multi_node()
        else:
            self._setup_single_node()
    
    def _setup_single_node(self) -> None:
        """Setup single-node configuration (legacy mode)."""
        self.logger.info("Initializing single-node configuration")
        node_config = self.config.get_single_node_config()
        
        # Create single manager with default node ID
        self.default_node = "default"
        self.managers[self.default_node] = ProxmoxManager(
            node_config.proxmox, 
            node_config.auth,
            self.default_node
        )
        
        self.logger.info(f"Single node initialized: {node_config.proxmox.host}")
    
    def _setup_multi_node(self) -> None:
        """Setup multi-node configuration."""
        self.logger.info("Initializing multi-node configuration")
        multi_config = self.config.get_multi_node_config()
        
        self.default_node = multi_config.default_node
        
        # Initialize managers for each node (lazy loading)
        for node_id, node_config in multi_config.nodes.items():
            self.logger.info(f"Registering node: {node_id} -> {node_config.proxmox.host}")
        
        self.logger.info(f"Multi-node initialized with {len(multi_config.nodes)} nodes, default: {self.default_node}")
    
    def _get_manager(self, node_id: str) -> ProxmoxManager:
        """Get or create ProxmoxManager for specified node.
        
        Implements lazy loading - managers are only created when first requested.
        
        Args:
            node_id: Node identifier to get manager for
            
        Returns:
            ProxmoxManager instance for the specified node
            
        Raises:
            ValueError: If node_id is not configured
        """
        # Return existing manager if available
        if node_id in self.managers:
            return self.managers[node_id]
        
        # For single-node mode, always use default
        if not self.config.is_multi_node():
            if node_id != "default" and node_id != self.default_node:
                self.logger.warning(f"Node '{node_id}' requested but only single node available, using default")
                node_id = self.default_node
            return self.managers[self.default_node]
        
        # Multi-node mode: create manager on demand
        multi_config = self.config.get_multi_node_config()
        if node_id not in multi_config.nodes:
            available_nodes = list(multi_config.nodes.keys())
            raise ValueError(f"Node '{node_id}' not configured. Available nodes: {available_nodes}")
        
        # Create new manager
        node_config = multi_config.nodes[node_id]
        self.logger.info(f"Creating connection to node: {node_id} -> {node_config.proxmox.host}")
        
        manager = ProxmoxManager(node_config.proxmox, node_config.auth, node_id)
        self.managers[node_id] = manager
        
        return manager
    
    def get_api(self, node_id: Optional[str] = None) -> ProxmoxAPI:
        """Get ProxmoxAPI instance for specified node.
        
        Provides access to the configured and tested ProxmoxAPI instance
        for making API calls to the specified node.
        
        Args:
            node_id: Node identifier. If None, uses default node
            
        Returns:
            ProxmoxAPI instance ready for making API calls
            
        Raises:
            ValueError: If node_id is not configured
            RuntimeError: If connection to node fails
        """
        if node_id is None:
            node_id = self.default_node
        
        try:
            manager = self._get_manager(node_id)
            return manager.get_api()
        except Exception as e:
            self.logger.error(f"Failed to get API for node '{node_id}': {e}")
            raise
    
    def get_available_nodes(self) -> Dict[str, str]:
        """Get list of available nodes with their host addresses.
        
        Returns:
            Dictionary mapping node_id to host address
        """
        if not self.config.is_multi_node():
            node_config = self.config.get_single_node_config()
            return {self.default_node: node_config.proxmox.host}
        
        multi_config = self.config.get_multi_node_config()
        return {
            node_id: node_config.proxmox.host 
            for node_id, node_config in multi_config.nodes.items()
        }
    
    def get_default_node(self) -> str:
        """Get the default node identifier.
        
        Returns:
            Default node identifier
        """
        return self.default_node
    
    def is_multi_node(self) -> bool:
        """Check if running in multi-node mode.
        
        Returns:
            True if multi-node configuration is active
        """
        return self.config.is_multi_node()
    
    def health_check(self, node_id: Optional[str] = None) -> Dict[str, bool]:
        """Perform health check on specified node(s).
        
        Args:
            node_id: Node to check. If None, checks all configured nodes
            
        Returns:
            Dictionary mapping node_id to health status (True = healthy)
        """
        results = {}
        
        nodes_to_check = [node_id] if node_id else list(self.get_available_nodes().keys())
        
        for check_node in nodes_to_check:
            try:
                api = self.get_api(check_node)
                # Simple health check - get version
                api.version.get()
                results[check_node] = True
                self.logger.debug(f"Node '{check_node}' health check: OK")
            except Exception as e:
                results[check_node] = False
                self.logger.warning(f"Node '{check_node}' health check failed: {e}")
        
        return results
    
    def close_connections(self) -> None:
        """Close all active connections.
        
        Useful for cleanup when shutting down the server.
        """
        self.logger.info("Closing all node connections")
        for node_id in list(self.managers.keys()):
            try:
                # ProxmoxAPI doesn't have explicit close method
                # but we can remove from our cache
                del self.managers[node_id]
                self.logger.debug(f"Closed connection to node: {node_id}")
            except Exception as e:
                self.logger.warning(f"Error closing connection to node '{node_id}': {e}")
        
        self.logger.info("All connections closed")