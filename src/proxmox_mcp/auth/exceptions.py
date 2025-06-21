"""
Authentication and authorization exceptions.

This module defines custom exceptions for OAuth 2.1 and JWT token
handling, providing standardized error responses for authorization failures.
"""

class AuthError(Exception):
    """Base exception for authentication and authorization errors."""
    
    def __init__(self, message: str, error_code: str = "auth_error", status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

class InvalidTokenError(AuthError):
    """Raised when an access token is invalid, expired, or malformed."""
    
    def __init__(self, message: str = "Invalid or expired access token"):
        super().__init__(message, "invalid_token", 401)

class InsufficientScopeError(AuthError):
    """Raised when a token lacks required scopes for an operation."""
    
    def __init__(self, required_scope: str, message: str = None):
        if message is None:
            message = f"Insufficient scope. Required: {required_scope}"
        super().__init__(message, "insufficient_scope", 403)
        self.required_scope = required_scope

class InvalidClientError(AuthError):
    """Raised when client credentials are invalid or client is unknown."""
    
    def __init__(self, message: str = "Invalid client credentials"):
        super().__init__(message, "invalid_client", 401)

class UnsupportedGrantTypeError(AuthError):
    """Raised when an unsupported OAuth grant type is requested."""
    
    def __init__(self, grant_type: str):
        message = f"Unsupported grant type: {grant_type}"
        super().__init__(message, "unsupported_grant_type", 400)

class InvalidRequestError(AuthError):
    """Raised when an OAuth request is malformed or missing required parameters."""
    
    def __init__(self, message: str = "Invalid request parameters"):
        super().__init__(message, "invalid_request", 400)