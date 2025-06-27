"""
Configuration loading utilities for the Proxmox MCP server.

This module handles loading and validation of server configuration:
- JSON configuration file loading
- Environment variable handling
- Configuration validation using Pydantic models
- Security validation for production deployments
- Error handling for invalid configurations

The module ensures that all required configuration is present,
valid, and secure before the server starts operation.
"""
import json
import os
import logging
import re
from typing import Optional, Union, List
from .models import Config, MultiNodeConfig, NodeConfig

def load_config(config_path: Optional[str] = None) -> Config:
    """Load and validate configuration from JSON file.

    Supports both single-node and multi-node configurations:
    
    Single-node (legacy):
    {
        "proxmox": {"host": "...", ...},
        "auth": {"user": "...", ...},
        "logging": {...}
    }
    
    Multi-node (new):
    {
        "nodes": {
            "node_200": {"proxmox": {...}, "auth": {...}},
            "node_201": {"proxmox": {...}, "auth": {...}}
        },
        "default_node": "node_200",
        "logging": {...}
    }
    
    Args:
        config_path: Path to the JSON configuration file
                    If not provided, raises ValueError

    Returns:
        Config object containing validated configuration

    Raises:
        ValueError: If configuration is invalid or missing required fields
    """
    if not config_path:
        raise ValueError("PROXMOX_MCP_CONFIG environment variable must be set")

    try:
        with open(config_path) as f:
            config_data = json.load(f)
            
            # Security validation before functional validation
            security_warnings = _validate_security(config_data)
            if security_warnings:
                logger = logging.getLogger("proxmox-mcp.security")
                for warning in security_warnings:
                    logger.warning(f"SECURITY WARNING: {warning}")
            
            # Detect configuration type and validate
            if "nodes" in config_data:
                # Multi-node configuration
                _validate_multi_node_config(config_data)
            else:
                # Single-node configuration (legacy)
                _validate_single_node_config(config_data)
            
            return Config(**config_data)
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load config: {e}")

def _validate_single_node_config(config_data: dict) -> None:
    """Validate single-node configuration structure."""
    if not config_data.get('proxmox', {}).get('host'):
        raise ValueError("Single-node configuration: proxmox.host cannot be empty")
    
    if not config_data.get('auth', {}).get('user'):
        raise ValueError("Single-node configuration: auth.user cannot be empty")
    
    if not config_data.get('auth', {}).get('token_value'):
        raise ValueError("Single-node configuration: auth.token_value cannot be empty")

def _validate_multi_node_config(config_data: dict) -> None:
    """Validate multi-node configuration structure."""
    nodes = config_data.get('nodes', {})
    if not nodes:
        raise ValueError("Multi-node configuration: nodes cannot be empty")
    
    default_node = config_data.get('default_node')
    if not default_node:
        raise ValueError("Multi-node configuration: default_node must be specified")
    
    if default_node not in nodes:
        raise ValueError(f"Multi-node configuration: default_node '{default_node}' not found in nodes")
    
    # Validate each node configuration
    for node_id, node_config in nodes.items():
        if not node_config.get('proxmox', {}).get('host'):
            raise ValueError(f"Multi-node configuration: node '{node_id}' missing proxmox.host")
        
        if not node_config.get('auth', {}).get('user'):
            raise ValueError(f"Multi-node configuration: node '{node_id}' missing auth.user")
        
        if not node_config.get('auth', {}).get('token_value'):
            raise ValueError(f"Multi-node configuration: node '{node_id}' missing auth.token_value")

def load_multi_node_config(config_path: str) -> MultiNodeConfig:
    """Load multi-node configuration specifically.
    
    Helper function for loading the multi-node configuration from
    the proxmox-config/config.json file.
    
    Args:
        config_path: Path to multi-node configuration file
        
    Returns:
        MultiNodeConfig object
        
    Raises:
        ValueError: If configuration is not multi-node format
    """
    config = load_config(config_path)
    if not config.is_multi_node():
        raise ValueError("Configuration file is not in multi-node format")
    
    return config.get_multi_node_config()

def _validate_security(config_data: dict) -> List[str]:
    """Validate configuration for security best practices.
    
    Checks for common security issues and returns warnings.
    Does not prevent startup but logs security concerns.
    
    Args:
        config_data: Raw configuration dictionary
        
    Returns:
        List of security warning messages
    """
    warnings = []
    config_str = json.dumps(config_data)
    
    # Check for placeholder values
    placeholder_patterns = [
        r'CHANGE-THIS',
        r'your-token',
        r'example',
        r'placeholder',
        r'change-this-in-production'
    ]
    
    for pattern in placeholder_patterns:
        if re.search(pattern, config_str, re.IGNORECASE):
            warnings.append(f"Placeholder value detected: '{pattern}' - Replace with actual values")
    
    # Check SSL verification
    if _check_ssl_disabled(config_data):
        warnings.append("SSL verification disabled (verify_ssl: false) - Enable for production")
    
    # Check for root user usage
    if _check_root_user(config_data):
        warnings.append("Using root user account - Consider creating dedicated service account")
    
    # Check network binding
    unsafe_hosts = _check_unsafe_binding(config_data)
    if unsafe_hosts:
        warnings.append(f"Binding to all interfaces ({', '.join(unsafe_hosts)}) - Consider localhost or specific IP")
    
    # Check OAuth security if enabled
    oauth_warnings = _check_oauth_security(config_data)
    warnings.extend(oauth_warnings)
    
    return warnings

def _check_ssl_disabled(config_data: dict) -> bool:
    """Check if SSL verification is disabled."""
    # Single-node config
    if config_data.get('proxmox', {}).get('verify_ssl') is False:
        return True
    
    # Multi-node config
    nodes = config_data.get('nodes', {})
    for node_config in nodes.values():
        if node_config.get('proxmox', {}).get('verify_ssl') is False:
            return True
    
    return False

def _check_root_user(config_data: dict) -> bool:
    """Check if root user is being used."""
    # Single-node config
    user = config_data.get('auth', {}).get('user', '')
    if user.startswith('root@'):
        return True
    
    # Multi-node config  
    nodes = config_data.get('nodes', {})
    for node_config in nodes.values():
        user = node_config.get('auth', {}).get('user', '')
        if user.startswith('root@'):
            return True
    
    return False

def _check_unsafe_binding(config_data: dict) -> List[str]:
    """Check for unsafe network binding."""
    unsafe_hosts = []
    
    # Check transport configuration
    transport = config_data.get('transport', {})
    host = transport.get('host', '')
    if host == '0.0.0.0':
        unsafe_hosts.append(host)
    
    # Check per-node transport (if applicable)
    nodes = config_data.get('nodes', {})
    for node_config in nodes.values():
        transport = node_config.get('transport', {})
        host = transport.get('host', '')
        if host == '0.0.0.0':
            unsafe_hosts.append(host)
    
    return unsafe_hosts

def _check_oauth_security(config_data: dict) -> List[str]:
    """Check OAuth configuration for security issues."""
    warnings = []
    
    # Check global OAuth config
    auth_config = config_data.get('authorization', {})
    if auth_config.get('enabled'):
        warnings.extend(_validate_oauth_config(auth_config, 'global'))
    
    # Check per-node OAuth config
    nodes = config_data.get('nodes', {})
    for node_id, node_config in nodes.items():
        auth_config = node_config.get('authorization', {})
        if auth_config.get('enabled'):
            warnings.extend(_validate_oauth_config(auth_config, f'node {node_id}'))
    
    return warnings

def _validate_oauth_config(auth_config: dict, context: str) -> List[str]:
    """Validate OAuth configuration security."""
    warnings = []
    
    # Check JWT secret strength
    secret_key = auth_config.get('secret_key', '')
    if len(secret_key) < 32:
        warnings.append(f"JWT secret key too short in {context} ({len(secret_key)} chars) - Use 64+ characters")
    
    # Check token expiry
    token_expiry = auth_config.get('token_expiry', 3600)
    if token_expiry > 14400:  # 4 hours
        warnings.append(f"OAuth token expiry too long in {context} ({token_expiry}s) - Use 3600s or less")
    
    # Check for HTTP issuer
    issuer = auth_config.get('issuer', '')
    if issuer.startswith('http://'):
        warnings.append(f"OAuth issuer using HTTP in {context} - Use HTTPS for production")
    
    # Check dynamic client registration
    if auth_config.get('dynamic_client_registration', False):
        warnings.append(f"Dynamic client registration enabled in {context} - Disable for production")
    
    return warnings
