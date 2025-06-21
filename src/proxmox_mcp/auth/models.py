"""
OAuth 2.1 data models for authentication and authorization.

This module defines Pydantic models for OAuth flows, token handling,
and client management according to the MCP authorization specification.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class TokenInfo(BaseModel):
    """Information extracted from a validated access token."""
    
    subject: str = Field(description="Token subject (typically client_id)")
    audience: str = Field(description="Token audience (server identifier)")
    scopes: List[str] = Field(description="Granted scopes for this token")
    expires_at: datetime = Field(description="Token expiration timestamp")
    client_id: str = Field(description="Client identifier")
    issued_at: datetime = Field(description="Token issued timestamp")
    
    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.utcnow() > self.expires_at
    
    def has_scope(self, required_scope: str) -> bool:
        """Check if token has a specific scope."""
        return required_scope in self.scopes

class ClientInfo(BaseModel):
    """OAuth client registration information."""
    
    client_id: str = Field(description="Unique client identifier")
    client_secret: Optional[str] = Field(description="Client secret (confidential clients)")
    client_name: str = Field(description="Human-readable client name")
    redirect_uris: List[str] = Field(description="Allowed redirect URIs")
    grant_types: List[str] = Field(description="Allowed grant types", default=["authorization_code"])
    response_types: List[str] = Field(description="Allowed response types", default=["code"])
    scope: List[str] = Field(description="Allowed scopes for this client")
    client_uri: Optional[str] = Field(description="Client website URI", default=None)
    is_confidential: bool = Field(description="Whether client can keep secrets", default=False)
    created_at: datetime = Field(description="Client registration timestamp", default_factory=datetime.utcnow)

class AuthRequest(BaseModel):
    """OAuth authorization request parameters."""
    
    response_type: str = Field(description="OAuth response type (typically 'code')")
    client_id: str = Field(description="Client identifier")
    redirect_uri: str = Field(description="Authorization callback URI")
    scope: Optional[str] = Field(description="Requested scopes (space-separated)", default=None)
    state: Optional[str] = Field(description="Client state parameter", default=None)
    code_challenge: Optional[str] = Field(description="PKCE code challenge", default=None)
    code_challenge_method: Optional[str] = Field(description="PKCE challenge method", default="S256")
    audience: Optional[str] = Field(description="Target audience", default=None)

class TokenRequest(BaseModel):
    """OAuth token request parameters."""
    
    grant_type: str = Field(description="OAuth grant type")
    code: Optional[str] = Field(description="Authorization code (for authorization_code grant)", default=None)
    redirect_uri: Optional[str] = Field(description="Callback URI (must match auth request)", default=None)
    client_id: str = Field(description="Client identifier")
    client_secret: Optional[str] = Field(description="Client secret (confidential clients)", default=None)
    code_verifier: Optional[str] = Field(description="PKCE code verifier", default=None)
    scope: Optional[str] = Field(description="Requested scopes", default=None)
    audience: Optional[str] = Field(description="Target audience", default=None)

class TokenResponse(BaseModel):
    """OAuth token response."""
    
    access_token: str = Field(description="Access token")
    token_type: str = Field(description="Token type (Bearer)", default="Bearer")
    expires_in: int = Field(description="Token lifetime in seconds")
    scope: Optional[str] = Field(description="Granted scopes", default=None)
    refresh_token: Optional[str] = Field(description="Refresh token", default=None)

class AuthorizationCode(BaseModel):
    """Temporary authorization code for OAuth flow."""
    
    code: str = Field(description="Authorization code")
    client_id: str = Field(description="Client identifier")
    redirect_uri: str = Field(description="Callback URI")
    scope: List[str] = Field(description="Granted scopes")
    code_challenge: Optional[str] = Field(description="PKCE code challenge", default=None)
    code_challenge_method: Optional[str] = Field(description="PKCE challenge method", default=None)
    expires_at: datetime = Field(description="Code expiration timestamp")
    created_at: datetime = Field(description="Code creation timestamp", default_factory=datetime.utcnow)
    
    @property
    def is_expired(self) -> bool:
        """Check if the authorization code is expired."""
        return datetime.utcnow() > self.expires_at

class ServerMetadata(BaseModel):
    """OAuth authorization server metadata."""
    
    issuer: str = Field(description="Authorization server identifier")
    authorization_endpoint: str = Field(description="Authorization endpoint URL")
    token_endpoint: str = Field(description="Token endpoint URL") 
    registration_endpoint: Optional[str] = Field(description="Dynamic registration endpoint", default=None)
    scopes_supported: List[str] = Field(description="Supported scopes")
    response_types_supported: List[str] = Field(description="Supported response types", default=["code"])
    grant_types_supported: List[str] = Field(description="Supported grant types", default=["authorization_code"])
    code_challenge_methods_supported: List[str] = Field(description="PKCE methods", default=["S256"])
    token_endpoint_auth_methods_supported: List[str] = Field(description="Token auth methods", default=["client_secret_post", "none"])
    
class ErrorResponse(BaseModel):
    """OAuth error response."""
    
    error: str = Field(description="Error code")
    error_description: Optional[str] = Field(description="Human-readable error description", default=None)
    error_uri: Optional[str] = Field(description="Error documentation URI", default=None)
    state: Optional[str] = Field(description="Client state parameter", default=None)