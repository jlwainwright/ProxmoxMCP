#!/usr/bin/env python3
"""Test the Proxmox MCP server with HTTP transport and authorization."""

import json
import subprocess
import sys
import os
import time
import requests
from urllib.parse import urlparse, parse_qs

def test_http_server():
    """Test the HTTP MCP server."""
    
    # Set up environment for HTTP mode
    env = os.environ.copy()
    env['PROXMOX_MCP_CONFIG'] = os.path.join(os.getcwd(), 'config-http-auth.json')
    
    print("=== Starting HTTP MCP Server ===")
    
    # Start the server process
    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'proxmox_mcp.server'],
            env=env,
            cwd='src',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        base_url = "http://localhost:8080"
        
        # Test 1: Check OAuth metadata
        print("\n=== Test 1: OAuth Authorization Server Metadata ===")
        try:
            response = requests.get(f"{base_url}/.well-known/oauth-authorization-server")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                metadata = response.json()
                print("Metadata:", json.dumps(metadata, indent=2))
            else:
                print("Response:", response.text)
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 2: Check MCP tools list
        print("\n=== Test 2: MCP Tools List ===")
        try:
            response = requests.get(f"{base_url}/mcp/tools")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                tools = response.json()
                print("Tools:", json.dumps(tools, indent=2))
            else:
                print("Response:", response.text)
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 3: Try unauthorized tool call
        print("\n=== Test 3: Unauthorized Tool Call ===")
        try:
            response = requests.post(
                f"{base_url}/mcp/tools/call",
                json={"tool": "get_nodes", "parameters": {}}
            )
            print(f"Status: {response.status_code}")
            print("Response:", response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 4: OAuth Authorization Flow (partial)
        print("\n=== Test 4: OAuth Authorization Request ===")
        try:
            auth_params = {
                "response_type": "code",
                "client_id": "proxmox-mcp-client",
                "redirect_uri": "http://localhost:3000/callback",
                "scope": "proxmox:nodes:read proxmox:vms:read",
                "code_challenge": "test-challenge",
                "code_challenge_method": "S256",
                "state": "test-state"
            }
            
            response = requests.get(f"{base_url}/authorize", params=auth_params, allow_redirects=False)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"Redirect to: {location}")
                
                # Parse authorization code from redirect
                parsed = urlparse(location)
                query_params = parse_qs(parsed.query)
                if 'code' in query_params:
                    auth_code = query_params['code'][0]
                    print(f"Authorization code: {auth_code}")
                    
                    # Test 5: Exchange code for token
                    print("\n=== Test 5: Token Exchange ===")
                    token_response = requests.post(
                        f"{base_url}/token",
                        data={
                            "grant_type": "authorization_code",
                            "code": auth_code,
                            "redirect_uri": "http://localhost:3000/callback",
                            "client_id": "proxmox-mcp-client",
                            "code_verifier": "test-verifier"  # This won't match, but tests the flow
                        }
                    )
                    print(f"Token Status: {token_response.status_code}")
                    print("Token Response:", token_response.json())
                    
            else:
                print("Response:", response.text)
                
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n=== Test Complete ===")
        return True
        
    except Exception as e:
        print(f"Server start error: {e}")
        return False
    
    finally:
        if 'process' in locals():
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def test_stdio_server():
    """Test the stdio MCP server."""
    
    # Set up environment for stdio mode
    env = os.environ.copy()
    env['PROXMOX_MCP_CONFIG'] = os.path.join(os.getcwd(), 'config-stdio.json')
    
    print("=== Testing Stdio MCP Server ===")
    
    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'proxmox_mcp.server'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd='src'
        )
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        request_line = json.dumps(init_request) + '\n'
        process.stdin.write(request_line)
        process.stdin.flush()
        
        # Read response
        stdout, stderr = process.communicate(timeout=10, input="")
        
        print("STDOUT:", stdout)
        if stderr:
            print("STDERR:", stderr)
        
        # Check if we got a valid response
        if stdout and "ProxmoxMCP" in stdout:
            print("✅ Stdio mode working correctly")
            return True
        else:
            print("❌ Stdio mode test failed")
            return False
            
    except Exception as e:
        print(f"Stdio test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Proxmox MCP Server with Authorization")
    print("=" * 50)
    
    # Test stdio mode first
    stdio_success = test_stdio_server()
    
    print("\n" + "=" * 50)
    
    # Test HTTP mode with authorization
    http_success = test_http_server()
    
    print(f"\n=== Results ===")
    print(f"Stdio mode: {'✅ PASS' if stdio_success else '❌ FAIL'}")
    print(f"HTTP mode: {'✅ PASS' if http_success else '❌ FAIL'}")
    
    sys.exit(0 if (stdio_success and http_success) else 1)