#!/usr/bin/env python3
"""
Debug script to identify initialization issues in ProxmoxMCP Server.
"""
import os
import sys
import traceback
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, '.')

def debug_initialization():
    """Debug server initialization step by step."""
    try:
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        print("🔧 Step 1: Loading configuration...")
        from proxmox_mcp.config.loader import load_config
        config = load_config(config_path)
        print(f"✅ Config loaded: {config.proxmox.host}:{config.proxmox.port}")
        
        print("\n🔧 Step 2: Setting up logging...")
        from proxmox_mcp.core.logging import setup_logging
        logger = setup_logging(config.logging)
        print("✅ Logging setup complete")
        
        print("\n🔧 Step 3: Initializing NodeManager...")
        # Try with mocked ProxmoxManager to avoid connection
        with patch('proxmox_mcp.core.node_manager.ProxmoxManager') as mock_manager:
            mock_manager_instance = Mock()
            mock_manager.return_value = mock_manager_instance
            
            from proxmox_mcp.core.node_manager import NodeManager
            node_manager = NodeManager(config)
            print("✅ NodeManager initialized successfully")
            
            print("\n🔧 Step 4: Initializing tool classes...")
            from proxmox_mcp.tools.node import NodeTools
            from proxmox_mcp.tools.vm import VMTools
            from proxmox_mcp.tools.storage import StorageTools
            from proxmox_mcp.tools.cluster import ClusterTools
            from proxmox_mcp.tools.monitoring import MonitoringTools
            from proxmox_mcp.tools.backup import BackupTools
            
            node_tools = NodeTools(node_manager)
            vm_tools = VMTools(node_manager)
            storage_tools = StorageTools(node_manager)
            cluster_tools = ClusterTools(node_manager)
            monitoring_tools = MonitoringTools(node_manager)
            backup_tools = BackupTools(node_manager)
            print("✅ All tool classes initialized")
            
            print("\n🔧 Step 5: Creating MCP server...")
            from mcp.server.fastmcp import FastMCP
            mcp = FastMCP("ProxmoxMCP")
            print("✅ FastMCP server created")
            
            print("\n🔧 Step 6: Manual tool registration test...")
            from proxmox_mcp.tools.definitions import GET_NODES_DESC
            from typing import Annotated
            from pydantic import Field
            
            @mcp.tool(description=GET_NODES_DESC)
            def test_get_nodes(
                proxmox_node: Annotated[str, Field(description="Proxmox instance to query")] = None
            ):
                return "test result"
            
            print("✅ Manual tool registration successful")
            
            print("\n🔧 Step 7: Testing tool enumeration...")
            import asyncio
            
            async def test_enum():
                tools_list = await mcp.list_tools()
                tools = tools_list.tools if hasattr(tools_list, 'tools') else []
                print(f"✅ Tools enumerated: {len(tools)} tools found")
                for tool in tools:
                    print(f"   - {tool.name}")
                return len(tools)
            
            tool_count = asyncio.run(test_enum())
            
            if tool_count > 0:
                print(f"\n🎉 Debug successful! Found {tool_count} tools")
                return True
            else:
                print("\n⚠️ No tools found - investigating tool registration")
                return False
        
    except Exception as e:
        print(f"\n❌ Initialization failed at step: {e}")
        traceback.print_exc()
        return False

def debug_full_server():
    """Try to debug the full server initialization."""
    try:
        print("\n" + "="*60)
        print("🔧 Full Server Initialization Debug")
        print("="*60)
        
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        # Mock the ProxmoxManager to avoid connection issues
        with patch('proxmox_mcp.core.node_manager.ProxmoxManager') as mock_manager:
            mock_manager_instance = Mock()
            mock_manager.return_value = mock_manager_instance
            
            from proxmox_mcp.server import ProxmoxMCPServer
            
            print("🚀 Creating ProxmoxMCPServer...")
            server = ProxmoxMCPServer(config_path)
            print("✅ Server created successfully")
            
            print("\n🔧 Testing MCP tool enumeration...")
            import asyncio
            
            async def test_server_tools():
                tools_list = await server.mcp.list_tools()
                tools = tools_list.tools if hasattr(tools_list, 'tools') else []
                print(f"📊 Server tools: {len(tools)}")
                for i, tool in enumerate(tools, 1):
                    print(f"   {i:2d}. {tool.name}")
                return len(tools)
            
            tool_count = asyncio.run(test_server_tools())
            
            if tool_count > 0:
                print(f"\n🎉 Full server debug successful! Found {tool_count} tools")
                return True
            else:
                print("\n⚠️ Server created but no tools registered")
                return False
        
    except Exception as e:
        print(f"\n❌ Full server initialization failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all debugging steps."""
    print("🔍 ProxmoxMCP Server Initialization Debug")
    print("=" * 50)
    
    step_result = debug_initialization()
    full_result = debug_full_server()
    
    print(f"\n🎯 Debug Results:")
    print(f"   Step-by-step: {'✅ PASS' if step_result else '❌ FAIL'}")
    print(f"   Full server: {'✅ PASS' if full_result else '❌ FAIL'}")

if __name__ == "__main__":
    main()