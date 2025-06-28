#!/usr/bin/env python3
"""
Debug script to test the _setup_tools method specifically.
"""
import os
import sys
import traceback
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, '.')

def debug_setup_tools():
    """Debug the _setup_tools method specifically."""
    try:
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        # Mock the ProxmoxManager to avoid connection issues
        with patch('proxmox_mcp.core.node_manager.ProxmoxManager') as mock_manager:
            mock_manager_instance = Mock()
            mock_manager.return_value = mock_manager_instance
            
            from proxmox_mcp.server import ProxmoxMCPServer
            
            print("🔧 Creating server instance...")
            server = ProxmoxMCPServer(config_path)
            
            print("🔧 Checking if _setup_tools was called...")
            # Let's manually call _setup_tools and see what happens
            try:
                print("🔧 Manually calling _setup_tools...")
                server._setup_tools()
                print("✅ _setup_tools completed without error")
            except Exception as e:
                print(f"❌ _setup_tools failed: {e}")
                traceback.print_exc()
                return False
            
            print("\n🔧 Checking tools after manual setup...")
            import asyncio
            
            async def check_tools():
                tools_list = await server.mcp.list_tools()
                tools = tools_list.tools if hasattr(tools_list, 'tools') else []
                print(f"📊 Tools after manual setup: {len(tools)}")
                for i, tool in enumerate(tools, 1):
                    print(f"   {i:2d}. {tool.name}")
                return len(tools)
            
            tool_count = asyncio.run(check_tools())
            
            if tool_count > 0:
                print(f"\n🎉 Manual _setup_tools successful! Found {tool_count} tools")
                return True
            else:
                print("\n⚠️ Manual _setup_tools called but no tools found")
                
                # Let's try registering a single tool manually to see if that works
                print("\n🔧 Testing single tool registration...")
                from proxmox_mcp.tools.definitions import GET_NODES_DESC
                from typing import Annotated
                from pydantic import Field
                
                @server.mcp.tool(description=GET_NODES_DESC)
                def debug_get_nodes(
                    proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
                ):
                    return "debug result"
                
                # Check again
                tool_count_after = asyncio.run(check_tools())
                if tool_count_after > 0:
                    print(f"✅ Manual tool registration works! Found {tool_count_after} tools")
                    print("❌ Issue is in the _setup_tools method implementation")
                else:
                    print("❌ Even manual tool registration doesn't work")
                
                return False
        
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run the setup tools debug."""
    print("🔍 ProxmoxMCP _setup_tools Debug")
    print("=" * 50)
    
    result = debug_setup_tools()
    
    print(f"\n🎯 Debug Result: {'✅ PASS' if result else '❌ FAIL'}")

if __name__ == "__main__":
    main()