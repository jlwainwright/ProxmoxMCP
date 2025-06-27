"""
Base classes and utilities for Proxmox MCP tools.

This module provides the foundation for all Proxmox MCP tools, including:
- Base tool class with common functionality
- Response formatting utilities
- Error handling mechanisms
- Logging setup

All tool implementations inherit from the ProxmoxTool base class to ensure
consistent behavior and error handling across the MCP server.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from mcp.types import TextContent as Content
from proxmoxer import ProxmoxAPI
from ..formatting import ProxmoxTemplates
from ..core.node_manager import NodeManager

class ProxmoxTool:
    """Base class for Proxmox MCP tools.
    
    This class provides common functionality used by all Proxmox tool implementations:
    - Multi-node Proxmox API access via NodeManager
    - Standardized logging
    - Response formatting
    - Error handling
    - Dynamic node selection
    
    All tool classes should inherit from this base class to ensure consistent
    behavior and error handling across the MCP server.
    """

    def __init__(self, node_manager: NodeManager):
        """Initialize the tool.

        Args:
            node_manager: NodeManager instance for multi-node API access
        """
        self.node_manager = node_manager
        self.logger = logging.getLogger(f"proxmox-mcp.{self.__class__.__name__.lower()}")
    
    def _get_api(self, node_id: Optional[str] = None) -> ProxmoxAPI:
        """Get ProxmoxAPI instance for specified node.
        
        Provides dynamic node selection for tool operations.
        If node_id is None, uses the default node.
        
        Args:
            node_id: Node identifier to get API for
            
        Returns:
            ProxmoxAPI instance for the specified node
            
        Raises:
            ValueError: If node_id is not configured
            RuntimeError: If connection to node fails
        """
        try:
            return self.node_manager.get_api(node_id)
        except Exception as e:
            self.logger.error(f"Failed to get API for node '{node_id}': {e}")
            raise

    def _format_response(self, data: Any, resource_type: Optional[str] = None) -> List[Content]:
        """Format response data into MCP content using templates.

        This method handles formatting of various Proxmox resource types into
        consistent MCP content responses. It uses specialized templates for
        different resource types (nodes, VMs, storage, etc.) and falls back
        to JSON formatting for unknown types.

        Args:
            data: Raw data from Proxmox API to format
            resource_type: Type of resource for template selection. Valid types:
                         'nodes', 'node_status', 'vms', 'storage', 'containers', 'cluster'

        Returns:
            List of Content objects formatted according to resource type
        """
        if resource_type == "nodes":
            formatted = ProxmoxTemplates.node_list(data)
        elif resource_type == "node_status":
            # For node_status, data should be a tuple of (node_name, status_dict)
            if isinstance(data, tuple) and len(data) == 2:
                formatted = ProxmoxTemplates.node_status(data[0], data[1])
            else:
                formatted = ProxmoxTemplates.node_status("unknown", data)
        elif resource_type == "vms":
            formatted = ProxmoxTemplates.vm_list(data)
        elif resource_type == "storage":
            formatted = ProxmoxTemplates.storage_list(data)
        elif resource_type == "containers":
            formatted = ProxmoxTemplates.container_list(data)
        elif resource_type == "cluster":
            formatted = ProxmoxTemplates.cluster_status(data)
        elif resource_type == "vm_status":
            formatted = ProxmoxTemplates.vm_status(data)
        else:
            # Fallback to JSON formatting for unknown types
            import json
            formatted = json.dumps(data, indent=2)

        return [Content(type="text", text=formatted)]

    def _handle_error(self, operation: str, error: Exception) -> None:
        """Handle and log errors from Proxmox operations.

        Provides standardized error handling across all tools by:
        - Logging errors with appropriate context
        - Categorizing errors into specific exception types
        - Converting Proxmox-specific errors into standard Python exceptions

        Args:
            operation: Description of the operation that failed (e.g., "get node status")
            error: The exception that occurred during the operation

        Raises:
            ValueError: For invalid input, missing resources, or permission issues
            RuntimeError: For unexpected errors or API failures
        """
        error_msg = str(error)
        self.logger.error(f"Failed to {operation}: {error_msg}")

        if "not found" in error_msg.lower():
            raise ValueError(f"Resource not found: {error_msg}")
        if "permission denied" in error_msg.lower():
            raise ValueError(f"Permission denied: {error_msg}")
        if "invalid" in error_msg.lower():
            raise ValueError(f"Invalid input: {error_msg}")
        
        raise RuntimeError(f"Failed to {operation}: {error_msg}")
