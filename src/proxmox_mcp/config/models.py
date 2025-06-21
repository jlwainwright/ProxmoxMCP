"""
Configuration models for the Proxmox MCP server.

This module defines Pydantic models for configuration validation:
- Proxmox connection settings
- Authentication credentials
- Logging configuration
- Transport configuration (stdio/HTTP)
- Authorization/OAuth configuration
- Tool-specific parameter models

The models provide:
- Type validation
- Default values
- Field descriptions
- Required vs optional field handling
"""
from typing import Optional, Annotated, List, Dict, Union
from pydantic import BaseModel, Field

class NodeStatus(BaseModel):
    """Model for node status query parameters.
    
    Validates and documents the required parameters for
    querying a specific node's status in the cluster.
    """
    node: Annotated[str, Field(description="Name/ID of node to query (e.g. 'pve1', 'proxmox-node2')")]

class VMCommand(BaseModel):
    """Model for VM command execution parameters.
    
    Validates and documents the required parameters for
    executing commands within a VM via QEMU guest agent.
    """
    node: Annotated[str, Field(description="Host node name (e.g. 'pve1', 'proxmox-node2')")]
    vmid: Annotated[str, Field(description="VM ID number (e.g. '100', '101')")]
    command: Annotated[str, Field(description="Shell command to run (e.g. 'uname -a', 'systemctl status nginx')")]

class ProxmoxConfig(BaseModel):
    """Model for Proxmox connection configuration.
    
    Defines the required and optional parameters for
    establishing a connection to the Proxmox API server.
    Provides sensible defaults for optional parameters.
    """
    host: str  # Required: Proxmox host address
    port: int = 8006  # Optional: API port (default: 8006)
    verify_ssl: bool = True  # Optional: SSL verification (default: True)
    service: str = "PVE"  # Optional: Service type (default: PVE)

class AuthConfig(BaseModel):
    """Model for Proxmox authentication configuration.
    
    Defines the required parameters for API authentication
    using token-based authentication. All fields are required
    to ensure secure API access.
    """
    user: str  # Required: Username (e.g., 'root@pam')
    token_name: str  # Required: API token name
    token_value: str  # Required: API token secret

class LoggingConfig(BaseModel):
    """Model for logging configuration.
    
    Defines logging parameters with sensible defaults.
    Supports both file and console logging with
    customizable format and log levels.
    """
    level: str = "INFO"  # Optional: Log level (default: INFO)
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Optional: Log format
    file: Optional[str] = None  # Optional: Log file path (default: None for console logging)

class TransportConfig(BaseModel):
    """Model for transport configuration.
    
    Defines the transport method for the MCP server.
    - stdio: Standard input/output (default, lightweight)
    - http: HTTP server (required for OAuth authorization)
    """
    type: str = "stdio"  # Transport type: "stdio" or "http"
    host: str = "127.0.0.1"  # HTTP server host (only used for http transport)
    port: int = 8080  # HTTP server port (only used for http transport)

class AuthorizationConfig(BaseModel):
    """Model for OAuth 2.1 authorization configuration.
    
    Defines settings for optional OAuth-based authorization.
    When enabled, requires HTTP transport and provides secure
    token-based access control for MCP tools.
    """
    enabled: bool = False  # Enable/disable authorization
    issuer: Optional[str] = None  # OAuth issuer URL (required when enabled)
    audience: str = "proxmox-mcp-server"  # Token audience validation
    scopes: List[str] = [  # Available authorization scopes
        "proxmox:nodes:read",
        "proxmox:vms:read", 
        "proxmox:vms:execute",
        "proxmox:storage:read",
        "proxmox:cluster:read"
    ]
    token_expiry: int = 3600  # Access token expiry in seconds (1 hour)
    dynamic_client_registration: bool = True  # Allow dynamic client registration
    secret_key: Optional[str] = None  # JWT signing secret (generated if not provided)

class NodeConfig(BaseModel):
    """Configuration for a single Proxmox node.
    
    Combines Proxmox connection and authentication settings
    for a single node instance.
    """
    proxmox: ProxmoxConfig  # Required: Proxmox connection settings
    auth: AuthConfig  # Required: Authentication credentials
    logging: Optional[LoggingConfig] = None  # Optional: Node-specific logging
    transport: Optional[TransportConfig] = None  # Optional: Node-specific transport
    authorization: Optional[AuthorizationConfig] = None  # Optional: Node-specific auth

class MultiNodeConfig(BaseModel):
    """Configuration for multiple Proxmox nodes.
    
    Manages configurations for multiple Proxmox instances
    with a default node selection.
    """
    nodes: Dict[str, NodeConfig]  # Required: Node configurations by ID
    default_node: str  # Required: Default node ID to use
    logging: LoggingConfig  # Required: Global logging configuration
    transport: TransportConfig = TransportConfig()  # Optional: Global transport settings
    authorization: AuthorizationConfig = AuthorizationConfig()  # Optional: Global OAuth settings

class Config(BaseModel):
    """Root configuration model.
    
    Supports both single-node and multi-node configurations.
    Automatically detects configuration type based on structure.
    """
    # Single-node configuration (legacy)
    proxmox: Optional[ProxmoxConfig] = None
    auth: Optional[AuthConfig] = None
    
    # Multi-node configuration (new)
    nodes: Optional[Dict[str, NodeConfig]] = None
    default_node: Optional[str] = None
    
    # Common configuration
    logging: LoggingConfig  # Required: Logging configuration
    transport: TransportConfig = TransportConfig()  # Optional: Transport settings
    authorization: AuthorizationConfig = AuthorizationConfig()  # Optional: OAuth settings
    
    def is_multi_node(self) -> bool:
        """Check if this is a multi-node configuration."""
        return self.nodes is not None and len(self.nodes) > 0
    
    def get_single_node_config(self) -> NodeConfig:
        """Get single-node configuration (legacy mode)."""
        if self.is_multi_node():
            raise ValueError("Cannot get single-node config from multi-node configuration")
        
        if not self.proxmox or not self.auth:
            raise ValueError("Single-node configuration missing required fields")
            
        return NodeConfig(
            proxmox=self.proxmox,
            auth=self.auth,
            logging=self.logging,
            transport=self.transport,
            authorization=self.authorization
        )
    
    def get_multi_node_config(self) -> MultiNodeConfig:
        """Get multi-node configuration."""
        if not self.is_multi_node():
            raise ValueError("Cannot get multi-node config from single-node configuration")
            
        if not self.nodes or not self.default_node:
            raise ValueError("Multi-node configuration missing required fields")
            
        return MultiNodeConfig(
            nodes=self.nodes,
            default_node=self.default_node,
            logging=self.logging,
            transport=self.transport,
            authorization=self.authorization
        )
