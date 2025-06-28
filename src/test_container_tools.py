#!/usr/bin/env python3
"""
Test script to verify container tools are working correctly.
"""
import sys
import os
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, '.')

def test_container_tools():
    """Test that container tools can be imported and instantiated."""
    try:
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        print("🔧 Testing container tools import...")
        from proxmox_mcp.tools.containers import ContainerTools
        from proxmox_mcp.tools.definitions import (
            GET_CONTAINERS_DESC, START_CONTAINER_DESC,
            STOP_CONTAINER_DESC, GET_CONTAINER_STATUS_DESC
        )
        print("✅ Container tools imported successfully")
        
        print("🔧 Testing container tools instantiation...")
        with patch('proxmox_mcp.core.node_manager.ProxmoxManager') as mock_proxmox_manager:
            from proxmox_mcp.core.node_manager import NodeManager
            from proxmox_mcp.config.loader import load_config
            
            # Setup mock
            mock_manager_instance = Mock()
            mock_api = Mock()
            mock_manager_instance.get_api.return_value = mock_api
            mock_proxmox_manager.return_value = mock_manager_instance
            
            config = load_config(config_path)
            node_manager = NodeManager(config)
            
            # Create container tools
            container_tools = ContainerTools(node_manager)
            print("✅ ContainerTools instantiated successfully")
            
            print("🔧 Testing method availability...")
            methods = ['get_containers', 'start_container', 'stop_container', 'get_container_status']
            for method in methods:
                if hasattr(container_tools, method):
                    print(f"✅ Method {method} exists")
                else:
                    print(f"❌ Method {method} missing")
                    return False
            
            print("🔧 Testing method call (get_containers)...")
            # Mock cluster resources call for containers
            mock_api.cluster.resources.get.return_value = [
                {
                    'type': 'lxc',
                    'vmid': '200',
                    'name': 'web-server',
                    'node': 'pve1',
                    'status': 'running',
                    'template': 'ubuntu-22.04',
                    'cpu': 0.15,
                    'maxcpu': 2,
                    'mem': 536870912,  # 512MB in bytes
                    'maxmem': 2147483648,  # 2GB in bytes
                    'disk': 1073741824,  # 1GB in bytes
                    'maxdisk': 21474836480,  # 20GB in bytes
                    'uptime': 86400  # 1 day
                }
            ]
            
            result = container_tools.get_containers()
            
            # Verify result
            if result and len(result) > 0 and "LXC Containers" in result[0].text:
                print("✅ get_containers returns correct format")
            else:
                print(f"❌ get_containers returned unexpected result: {result}")
                return False
            
            print("🔧 Testing method call (start_container)...")
            # Mock container status and start calls
            mock_api.nodes('pve1').lxc('200').status.current.get.return_value = {'status': 'stopped'}
            mock_api.nodes('pve1').lxc('200').status.start.post.return_value = "UPID:pve1:12345"
            
            result = container_tools.start_container("pve1", "200")
            
            # Verify result
            if result and len(result) > 0 and "Container Start Operation" in result[0].text:
                print("✅ start_container returns correct format")
            else:
                print(f"❌ start_container returned unexpected result: {result}")
                return False
                
            print("\\n🎉 All container tools tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_with_containers():
    """Test that the server can be created with container tools."""
    try:
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        print("\\n🔧 Testing server with container tools...")
        
        with patch('proxmox_mcp.core.node_manager.ProxmoxManager') as mock_proxmox_manager:
            mock_manager_instance = Mock()
            mock_api = Mock()
            mock_manager_instance.get_api.return_value = mock_api
            mock_proxmox_manager.return_value = mock_manager_instance
            
            from proxmox_mcp.server import ProxmoxMCPServer
            
            server = ProxmoxMCPServer(config_path)
            print("✅ Server created with container tools")
            
            # Verify container tools are initialized
            if hasattr(server, 'container_tools'):
                print("✅ Server has container_tools attribute")
            else:
                print("❌ Server missing container_tools attribute")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Container Tools Implementation")
    print("=" * 50)
    
    tools_test = test_container_tools()
    server_test = test_server_with_containers()
    
    print(f"\\n🎯 Test Results:")
    print(f"   Container Tools: {'✅ PASS' if tools_test else '❌ FAIL'}")
    print(f"   Server Integration: {'✅ PASS' if server_test else '❌ FAIL'}")
    
    if tools_test and server_test:
        print("\\n🚀 Container tools implementation is complete and working!")
        return True
    else:
        print("\\n💥 Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)