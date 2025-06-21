#!/usr/bin/env python3
"""Simple test for the Proxmox MCP server."""

import json
import subprocess
import sys
import os

def test_mcp_server():
    """Test the MCP server with a simple request."""
    
    # Set up environment
    env = os.environ.copy()
    env['PROXMOX_MCP_CONFIG'] = os.path.join(os.getcwd(), 'config.json')
    
    # Start the server process
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
        
        # Send the request
        request_line = json.dumps(init_request) + '\n'
        process.stdin.write(request_line)
        process.stdin.flush()
        
        # Read response (with timeout)
        try:
            stdout, stderr = process.communicate(timeout=10)
            
            print("=== STDOUT ===")
            print(stdout)
            print("\n=== STDERR ===")
            print(stderr)
            print(f"\n=== Return Code: {process.returncode} ===")
            
            if stdout:
                try:
                    response = json.loads(stdout.strip())
                    print(f"\n=== Parsed Response ===")
                    print(json.dumps(response, indent=2))
                    return True
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    return False
            
        except subprocess.TimeoutExpired:
            print("Server did not respond within timeout")
            process.kill()
            return False
            
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)