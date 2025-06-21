"""
Configuration loading utilities for the Proxmox MCP server.

This module handles loading and validation of server configuration:
- JSON configuration file loading
- Environment variable handling
- Configuration validation using Pydantic models
- Error handling for invalid configurations

The module ensures that all required configuration is present
and valid before the server starts operation.
"""
import json
import os
from typing import Optional, Union
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
