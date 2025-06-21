"""
Authentication and authorization module for Proxmox MCP.

This module provides OAuth 2.1-based authorization for the Proxmox MCP server,
implementing secure token-based access control according to the MCP specification.

Key components:
- OAuth 2.1 authorization server
- JWT token validation middleware
- Scope-based permission system
- Dynamic client registration
- HTTP transport integration
"""

from .models import TokenInfo, ClientInfo, AuthRequest, TokenRequest
from .middleware import AuthMiddleware
from .server import AuthServer
from .exceptions import AuthError, InvalidTokenError, InsufficientScopeError

__all__ = [
    "TokenInfo",
    "ClientInfo", 
    "AuthRequest",
    "TokenRequest",
    "AuthMiddleware",
    "AuthServer",
    "AuthError",
    "InvalidTokenError",
    "InsufficientScopeError",
]