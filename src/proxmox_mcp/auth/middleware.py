"""
Authentication middleware for HTTP transport.

This module provides middleware for validating JWT access tokens
in HTTP requests and enforcing scope-based authorization for MCP tools.
"""

import logging
from typing import Optional, List, Callable, Any
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from ..config.models import AuthorizationConfig
from .models import TokenInfo
from .exceptions import InvalidTokenError, InsufficientScopeError

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """JWT token validation middleware for FastAPI."""
    
    def __init__(self, auth_config: AuthorizationConfig):
        """Initialize the authentication middleware.
        
        Args:
            auth_config: Authorization configuration
        """
        self.auth_config = auth_config
        self.bearer_scheme = HTTPBearer(auto_error=False)
        
        # Generate secret key if not provided
        if not auth_config.secret_key:
            import secrets
            self.secret_key = secrets.token_urlsafe(32)
            logger.warning("No secret_key configured, using generated key (not suitable for production)")
        else:
            self.secret_key = auth_config.secret_key
    
    async def extract_token(self, request: Request) -> Optional[str]:
        """Extract bearer token from Authorization header.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Access token string or None if not present
        """
        credentials: HTTPAuthorizationCredentials = await self.bearer_scheme(request)
        if credentials and credentials.scheme.lower() == "bearer":
            return credentials.credentials
        return None
    
    def validate_token(self, token: str) -> TokenInfo:
        """Validate and decode a JWT access token.
        
        Args:
            token: JWT access token
            
        Returns:
            TokenInfo object with token claims
            
        Raises:
            InvalidTokenError: If token is invalid, expired, or malformed
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"],
                audience=self.auth_config.audience
            )
            
            # Extract required claims
            subject = payload.get("sub")
            audience = payload.get("aud")
            scopes = payload.get("scope", "").split() if payload.get("scope") else []
            expires_at = datetime.fromtimestamp(payload.get("exp", 0))
            client_id = payload.get("client_id", subject)
            issued_at = datetime.fromtimestamp(payload.get("iat", 0))
            
            if not subject or not audience:
                raise InvalidTokenError("Token missing required claims")
            
            token_info = TokenInfo(
                subject=subject,
                audience=audience,
                scopes=scopes,
                expires_at=expires_at,
                client_id=client_id,
                issued_at=issued_at
            )
            
            # Check expiration
            if token_info.is_expired:
                raise InvalidTokenError("Token has expired")
            
            return token_info
            
        except JWTError as e:
            logger.debug(f"JWT validation error: {e}")
            raise InvalidTokenError(f"Invalid token: {e}")
    
    def check_scope(self, token_info: TokenInfo, required_scope: str) -> None:
        """Check if token has required scope.
        
        Args:
            token_info: Validated token information
            required_scope: Required scope for operation
            
        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if not token_info.has_scope(required_scope):
            raise InsufficientScopeError(required_scope)
    
    def create_token(self, client_id: str, scopes: List[str], expires_in: int = None) -> str:
        """Create a new JWT access token.
        
        Args:
            client_id: Client identifier
            scopes: List of granted scopes
            expires_in: Token lifetime in seconds (defaults to config)
            
        Returns:
            Signed JWT access token
        """
        now = datetime.utcnow()
        expires_in = expires_in or self.auth_config.token_expiry
        
        payload = {
            "sub": client_id,
            "aud": self.auth_config.audience,
            "iss": self.auth_config.issuer,
            "client_id": client_id,
            "scope": " ".join(scopes),
            "iat": int(now.timestamp()),
            "exp": int((now.timestamp()) + expires_in)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

def require_scope(scope: str):
    """Decorator to require specific scope for MCP tool access.
    
    Args:
        scope: Required authorization scope
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # This will be integrated with FastMCP's tool registration
            # For now, return the original function
            return await func(*args, **kwargs)
        
        # Add scope metadata for later inspection
        wrapper._required_scope = scope
        return wrapper
    
    return decorator

# Common scope decorators for Proxmox tools
require_nodes_read = require_scope("proxmox:nodes:read")
require_vms_read = require_scope("proxmox:vms:read")
require_vms_execute = require_scope("proxmox:vms:execute")
require_storage_read = require_scope("proxmox:storage:read")
require_cluster_read = require_scope("proxmox:cluster:read")