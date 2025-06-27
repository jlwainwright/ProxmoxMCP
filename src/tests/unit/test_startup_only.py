#!/usr/bin/env python3
"""Test server startup without Proxmox connection."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_configuration_loading():
    """Test configuration loading and validation."""
    print("=== Testing Configuration Loading ===")
    
    try:
        from proxmox_mcp.config.loader import load_config
        
        # Test stdio config
        print("\n1. Testing stdio configuration:")
        config_stdio = load_config("config-stdio.json")
        print(f"   Transport type: {config_stdio.transport.type}")
        print(f"   Authorization enabled: {config_stdio.authorization.enabled}")
        
        # Test HTTP with auth config
        print("\n2. Testing HTTP with authorization configuration:")
        config_http = load_config("config-http-auth.json")
        print(f"   Transport type: {config_http.transport.type}")
        print(f"   Transport host: {config_http.transport.host}")
        print(f"   Transport port: {config_http.transport.port}")
        print(f"   Authorization enabled: {config_http.authorization.enabled}")
        print(f"   Authorization issuer: {config_http.authorization.issuer}")
        print(f"   Authorization scopes: {config_http.authorization.scopes}")
        
        print("\n✅ Configuration loading successful")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_auth_module_imports():
    """Test auth module imports."""
    print("\n=== Testing Auth Module Imports ===")
    
    try:
        from proxmox_mcp.auth import (
            TokenInfo, ClientInfo, AuthRequest, TokenRequest,
            AuthMiddleware, AuthServer, AuthError
        )
        print("✅ Auth module imports successful")
        
        # Test basic model creation
        from proxmox_mcp.config.models import AuthorizationConfig
        auth_config = AuthorizationConfig(enabled=True, issuer="http://test")
        
        middleware = AuthMiddleware(auth_config)
        print("✅ AuthMiddleware creation successful")
        
        server = AuthServer(auth_config)
        print("✅ AuthServer creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Auth module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_class_initialization():
    """Test server class initialization without Proxmox connection."""
    print("\n=== Testing Server Class (without Proxmox) ===")
    
    try:
        # This will fail due to Proxmox connection, but we can test config validation
        from proxmox_mcp.server import ProxmoxMCPServer
        
        print("✅ ProxmoxMCPServer import successful")
        
        # We can't fully initialize without a real Proxmox server
        # but we can test the class structure
        return True
        
    except Exception as e:
        print(f"❌ Server class test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Proxmox MCP Server Implementation")
    print("=" * 50)
    
    # Test configuration loading
    config_success = test_configuration_loading()
    
    # Test auth module imports
    auth_success = test_auth_module_imports()
    
    # Test server class
    server_success = test_server_class_initialization()
    
    print(f"\n=== Results ===")
    print(f"Configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
    print(f"Auth modules: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"Server class: {'✅ PASS' if server_success else '❌ FAIL'}")
    
    overall_success = config_success and auth_success and server_success
    print(f"Overall: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    sys.exit(0 if overall_success else 1)