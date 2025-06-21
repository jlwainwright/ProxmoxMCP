#!/usr/bin/env python3
"""Test tools list from Proxmox MCP server."""

import json
import subprocess
import sys
import os

def test_tools_list():
    """Test the tools/list endpoint."""
    
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
        
        # Send initialize request first
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
        
        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        # Send both requests
        init_line = json.dumps(init_request) + '\n'
        tools_line = json.dumps(tools_request) + '\n'
        
        process.stdin.write(init_line)
        process.stdin.flush()
        
        process.stdin.write(tools_line)
        process.stdin.flush()
        
        # Read responses
        stdout, stderr = process.communicate(timeout=10, input="")
        
        print("=== RAW STDOUT ===")
        print(repr(stdout))
        print("\n=== STDERR ===")
        print(stderr)
        
        # Parse JSON responses
        lines = stdout.strip().split('\n')
        print(f"\n=== Found {len(lines)} response lines ===")
        
        for i, line in enumerate(lines):
            if line.strip():
                try:
                    response = json.loads(line)
                    print(f"\n=== Response {i+1} ===")
                    print(json.dumps(response, indent=2))
                except json.JSONDecodeError as e:
                    print(f"JSON decode error on line {i+1}: {e}")
                    print(f"Raw line: {repr(line)}")
        
        return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tools_list()
    sys.exit(0 if success else 1)