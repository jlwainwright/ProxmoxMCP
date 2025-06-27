#!/usr/bin/env python3
"""Test tool calls to identify stdout issues."""

import sys
import os
import json
import subprocess

def test_tool_call():
    """Test calling an MCP tool to see what goes to stdout."""
    
    # Set up environment
    env = os.environ.copy()
    env['PROXMOX_MCP_CONFIG'] = os.path.join(os.getcwd(), 'config-stdio.json')
    
    print("=== Testing MCP tool call ===", file=sys.stderr)
    
    try:
        # Start the server process
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
                    "name": "claude-ai",
                    "version": "0.1.0"
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
        
        # Send tool call request (this might be where the error occurs)
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_nodes",
                "arguments": {}
            }
        }
        
        # Send requests one by one
        requests = [init_request, tools_request, tool_call_request]
        
        for i, req in enumerate(requests):
            print(f"Sending request {i+1}: {req['method']}", file=sys.stderr)
            request_line = json.dumps(req) + '\n'
            process.stdin.write(request_line)
            process.stdin.flush()
            
            # Small delay to let server process
            import time
            time.sleep(0.5)
        
        # Get output with timeout
        try:
            stdout, stderr = process.communicate(timeout=10, input="")
            
            print("=== STDOUT ===", file=sys.stderr)
            print(repr(stdout), file=sys.stderr)
            print("\n=== STDERR ===", file=sys.stderr)  
            print(repr(stderr), file=sys.stderr)
            print(f"\n=== Return Code: {process.returncode} ===", file=sys.stderr)
            
            # Try to parse each line as JSON
            if stdout:
                lines = stdout.strip().split('\n')
                print(f"\n=== Parsing {len(lines)} response lines ===", file=sys.stderr)
                
                for i, line in enumerate(lines):
                    if line.strip():
                        try:
                            response = json.loads(line)
                            print(f"Response {i+1}: {response.get('method', 'result')}", file=sys.stderr)
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error on line {i+1}: {e}", file=sys.stderr)
                            print(f"Problematic line: {repr(line)}", file=sys.stderr)
                            # This is likely our culprit!
                            break
                            
        except subprocess.TimeoutExpired:
            print("Process timed out", file=sys.stderr)
            process.kill()
            
    except Exception as e:
        print(f"Test error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    test_tool_call()