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
from typing import Optional, Annotated, List
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

class Config(BaseModel):
    """Root configuration model.
    
    Combines all configuration models into a single validated
    configuration object. Core sections are required, while
    transport and authorization are optional with defaults.
    """
    proxmox: ProxmoxConfig  # Required: Proxmox connection settings
    auth: AuthConfig  # Required: Authentication credentials
    logging: LoggingConfig  # Required: Logging configuration
    transport: TransportConfig = TransportConfig()  # Optional: Transport settings
    authorization: AuthorizationConfig = AuthorizationConfig()  # Optional: OAuth settings
