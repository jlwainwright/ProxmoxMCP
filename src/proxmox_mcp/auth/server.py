"""
OAuth 2.1 Authorization Server implementation.

This module implements an OAuth 2.1 authorization server according to
the MCP specification, providing secure token-based authentication
for Proxmox MCP tools.
"""

import logging
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from fastapi import FastAPI, Request, Form, Query, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from ..config.models import AuthorizationConfig
from .models import (
    ClientInfo, AuthRequest, TokenRequest, TokenResponse,
    AuthorizationCode, ServerMetadata, ErrorResponse
)
from .middleware import AuthMiddleware
from .exceptions import (
    InvalidClientError, InvalidRequestError, UnsupportedGrantTypeError,
    InvalidTokenError
)

logger = logging.getLogger(__name__)

class AuthServer:
    """OAuth 2.1 Authorization Server for Proxmox MCP."""
    
    def __init__(self, auth_config: AuthorizationConfig, base_url: str = "http://localhost:8080"):
        """Initialize the authorization server.
        
        Args:
            auth_config: Authorization configuration
            base_url: Server base URL for endpoint generation
        """
        self.config = auth_config
        self.base_url = base_url.rstrip("/")
        self.middleware = AuthMiddleware(auth_config)
        
        # In-memory storage (should be replaced with persistent storage in production)
        self.clients: Dict[str, ClientInfo] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        
        # Register default client for testing
        self._register_default_client()
    
    def _register_default_client(self):
        """Register a default client for testing purposes."""
        default_client = ClientInfo(
            client_id="proxmox-mcp-client",
            client_secret=None,  # Public client
            client_name="Proxmox MCP Client", 
            redirect_uris=[
                "http://localhost:3000/callback",
                "https://localhost:3000/callback"
            ],
            grant_types=["authorization_code"],
            response_types=["code"],
            scope=self.config.scopes,
            is_confidential=False
        )
        self.clients[default_client.client_id] = default_client
        logger.info(f"Registered default client: {default_client.client_id}")
    
    def setup_routes(self, app: FastAPI):
        """Setup OAuth endpoints on FastAPI app.
        
        Args:
            app: FastAPI application instance
        """
        
        @app.get("/.well-known/oauth-authorization-server")
        async def authorization_server_metadata():
            """OAuth authorization server metadata endpoint."""
            metadata = ServerMetadata(
                issuer=self.config.issuer or self.base_url,
                authorization_endpoint=f"{self.base_url}/authorize",
                token_endpoint=f"{self.base_url}/token",
                registration_endpoint=f"{self.base_url}/register" if self.config.dynamic_client_registration else None,
                scopes_supported=self.config.scopes,
                response_types_supported=["code"],
                grant_types_supported=["authorization_code"],
                code_challenge_methods_supported=["S256"],
                token_endpoint_auth_methods_supported=["client_secret_post", "none"]
            )
            return metadata.model_dump()
        
        @app.get("/authorize")
        async def authorize(
            response_type: str = Query(...),
            client_id: str = Query(...),
            redirect_uri: str = Query(...),
            scope: Optional[str] = Query(None),
            state: Optional[str] = Query(None),
            code_challenge: Optional[str] = Query(None),
            code_challenge_method: Optional[str] = Query("S256"),
            audience: Optional[str] = Query(None)
        ):
            """OAuth authorization endpoint."""
            try:
                auth_request = AuthRequest(
                    response_type=response_type,
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    scope=scope,
                    state=state,
                    code_challenge=code_challenge,
                    code_challenge_method=code_challenge_method,
                    audience=audience
                )
                
                # Validate client
                client = self.clients.get(client_id)
                if not client:
                    raise InvalidClientError(f"Unknown client: {client_id}")
                
                # Validate redirect URI
                if redirect_uri not in client.redirect_uris:
                    raise InvalidRequestError("Invalid redirect_uri")
                
                # Validate response type
                if response_type not in client.response_types:
                    raise InvalidRequestError(f"Unsupported response_type: {response_type}")
                
                # Parse and validate scopes
                requested_scopes = scope.split() if scope else client.scope
                granted_scopes = [s for s in requested_scopes if s in self.config.scopes]
                
                # Generate authorization code
                code = secrets.token_urlsafe(32)
                auth_code = AuthorizationCode(
                    code=code,
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    scope=granted_scopes,
                    code_challenge=code_challenge,
                    code_challenge_method=code_challenge_method,
                    expires_at=datetime.utcnow() + timedelta(minutes=10)  # 10 minute expiry
                )
                
                self.authorization_codes[code] = auth_code
                
                # Redirect back to client with authorization code
                redirect_params = f"code={code}"
                if state:
                    redirect_params += f"&state={state}"
                
                separator = "&" if "?" in redirect_uri else "?"
                final_redirect = f"{redirect_uri}{separator}{redirect_params}"
                
                return RedirectResponse(url=final_redirect, status_code=302)
                
            except Exception as e:
                logger.error(f"Authorization error: {e}")
                error_params = f"error=invalid_request&error_description={str(e)}"
                if state:
                    error_params += f"&state={state}"
                separator = "&" if "?" in redirect_uri else "?"
                error_redirect = f"{redirect_uri}{separator}{error_params}"
                return RedirectResponse(url=error_redirect, status_code=302)
        
        @app.post("/token")
        async def token_endpoint(
            grant_type: str = Form(...),
            code: Optional[str] = Form(None),
            redirect_uri: Optional[str] = Form(None),
            client_id: str = Form(...),
            client_secret: Optional[str] = Form(None),
            code_verifier: Optional[str] = Form(None),
            scope: Optional[str] = Form(None),
            audience: Optional[str] = Form(None)
        ):
            """OAuth token endpoint."""
            try:
                token_request = TokenRequest(
                    grant_type=grant_type,
                    code=code,
                    redirect_uri=redirect_uri,
                    client_id=client_id,
                    client_secret=client_secret,
                    code_verifier=code_verifier,
                    scope=scope,
                    audience=audience
                )
                
                # Validate grant type
                if grant_type != "authorization_code":
                    raise UnsupportedGrantTypeError(grant_type)
                
                # Validate client
                client = self.clients.get(client_id)
                if not client:
                    raise InvalidClientError(f"Unknown client: {client_id}")
                
                # Validate client secret for confidential clients
                if client.is_confidential and client.client_secret != client_secret:
                    raise InvalidClientError("Invalid client credentials")
                
                # Validate authorization code
                if not code or code not in self.authorization_codes:
                    raise InvalidRequestError("Invalid authorization code")
                
                auth_code = self.authorization_codes[code]
                
                # Check code expiration
                if auth_code.is_expired:
                    del self.authorization_codes[code]
                    raise InvalidRequestError("Authorization code expired")
                
                # Validate code ownership
                if auth_code.client_id != client_id:
                    raise InvalidRequestError("Authorization code mismatch")
                
                # Validate redirect URI
                if auth_code.redirect_uri != redirect_uri:
                    raise InvalidRequestError("Redirect URI mismatch")
                
                # Validate PKCE if required
                if auth_code.code_challenge:
                    if not code_verifier:
                        raise InvalidRequestError("Code verifier required")
                    
                    # Verify PKCE challenge
                    if auth_code.code_challenge_method == "S256":
                        challenge = base64.urlsafe_b64encode(
                            hashlib.sha256(code_verifier.encode()).digest()
                        ).decode().rstrip("=")
                        if challenge != auth_code.code_challenge:
                            raise InvalidRequestError("Invalid code verifier")
                
                # Generate access token
                access_token = self.middleware.create_token(
                    client_id=client_id,
                    scopes=auth_code.scope,
                    expires_in=self.config.token_expiry
                )
                
                # Clean up authorization code (one-time use)
                del self.authorization_codes[code]
                
                # Return token response
                response = TokenResponse(
                    access_token=access_token,
                    token_type="Bearer",
                    expires_in=self.config.token_expiry,
                    scope=" ".join(auth_code.scope)
                )
                
                return JSONResponse(content=response.model_dump())
                
            except Exception as e:
                logger.error(f"Token error: {e}")
                error = ErrorResponse(
                    error="invalid_request",
                    error_description=str(e)
                )
                return JSONResponse(
                    content=error.model_dump(),
                    status_code=400
                )
        
        if self.config.dynamic_client_registration:
            @app.post("/register")
            async def register_client(request: Request):
                """Dynamic client registration endpoint."""
                try:
                    client_data = await request.json()
                    
                    # Generate client ID
                    client_id = f"client_{secrets.token_urlsafe(16)}"
                    
                    # Create client info
                    client = ClientInfo(
                        client_id=client_id,
                        client_name=client_data.get("client_name", "Unknown Client"),
                        redirect_uris=client_data.get("redirect_uris", []),
                        grant_types=client_data.get("grant_types", ["authorization_code"]),
                        response_types=client_data.get("response_types", ["code"]),
                        scope=client_data.get("scope", self.config.scopes),
                        client_uri=client_data.get("client_uri"),
                        is_confidential=client_data.get("token_endpoint_auth_method") != "none"
                    )
                    
                    # Generate client secret for confidential clients
                    if client.is_confidential:
                        client.client_secret = secrets.token_urlsafe(32)
                    
                    # Store client
                    self.clients[client_id] = client
                    
                    logger.info(f"Registered new client: {client_id}")
                    
                    # Return client information
                    response_data = client.model_dump()
                    if not client.is_confidential:
                        response_data.pop("client_secret", None)
                    
                    return JSONResponse(content=response_data, status_code=201)
                    
                except Exception as e:
                    logger.error(f"Client registration error: {e}")
                    error = ErrorResponse(
                        error="invalid_request",
                        error_description=str(e)
                    )
                    return JSONResponse(
                        content=error.model_dump(),
                        status_code=400
                    )