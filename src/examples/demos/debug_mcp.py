#!/usr/bin/env python3
"""Debug MCP server stdout issues."""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Capture all stdout to see what's being printed
class DebugStdout:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.captured = []
    
    def write(self, text):
        self.captured.append(text)
        self.original_stdout.write(f"[STDOUT DEBUG]: {repr(text)}\n")
        self.original_stdout.flush()
    
    def flush(self):
        self.original_stdout.flush()

def main():
    print("=== Starting MCP Debug Test ===", file=sys.stderr)
    
    # Set up environment
    os.environ['PROXMOX_MCP_CONFIG'] = os.path.join(os.getcwd(), 'config-stdio.json')
    
    # Replace stdout with debug version
    debug_stdout = DebugStdout()
    sys.stdout = debug_stdout
    
    try:
        from proxmox_mcp.server import ProxmoxMCPServer
        
        print("Creating server...", file=sys.stderr)
        server = ProxmoxMCPServer()
        
        print("Server created successfully", file=sys.stderr)
        print("Testing MCP initialization...", file=sys.stderr)
        
        # Try to simulate what Claude Desktop does
        import asyncio
        
        async def test_mcp():
            try:
                # This would normally be run by FastMCP
                print("Testing async MCP operations...", file=sys.stderr)
                return True
            except Exception as e:
                print(f"MCP async error: {e}", file=sys.stderr)
                return False
        
        result = asyncio.run(test_mcp())
        print(f"MCP test result: {result}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error during debug test: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    finally:
        # Restore stdout
        sys.stdout = debug_stdout.original_stdout
        
        print("\n=== CAPTURED STDOUT CONTENT ===", file=sys.stderr)
        for i, content in enumerate(debug_stdout.captured):
            print(f"Capture {i}: {repr(content)}", file=sys.stderr)

if __name__ == "__main__":
    main()