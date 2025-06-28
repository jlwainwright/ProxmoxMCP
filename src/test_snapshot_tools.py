#!/usr/bin/env python3
"""
Test script to verify snapshot tools are working correctly.
"""
import sys
import os
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, '.')

def test_snapshot_tools():
    """Test that snapshot tools can be imported and instantiated."""
    try:
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        print("🔧 Testing snapshot tools import...")
        from proxmox_mcp.tools.snapshots import SnapshotTools
        from proxmox_mcp.tools.definitions import (
            CREATE_VM_SNAPSHOT_DESC, LIST_VM_SNAPSHOTS_DESC,
            DELETE_VM_SNAPSHOT_DESC, ROLLBACK_VM_SNAPSHOT_DESC
        )
        print("✅ Snapshot tools imported successfully")
        
        print("🔧 Testing snapshot tools instantiation...")
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
            
            # Create snapshot tools
            snapshot_tools = SnapshotTools(node_manager)
            print("✅ SnapshotTools instantiated successfully")
            
            print("🔧 Testing method availability...")
            methods = ['create_vm_snapshot', 'list_vm_snapshots', 'delete_vm_snapshot', 'rollback_vm_snapshot']
            for method in methods:
                if hasattr(snapshot_tools, method):
                    print(f"✅ Method {method} exists")
                else:
                    print(f"❌ Method {method} missing")
                    return False
            
            print("🔧 Testing method call (create_vm_snapshot)...")
            # Mock successful snapshot creation
            mock_api.nodes('pve1').qemu('100').snapshot.post.return_value = "UPID:pve1:12345"
            
            result = snapshot_tools.create_vm_snapshot("pve1", "100", "test-snapshot", "Test description")
            
            # Verify result
            if result and len(result) > 0 and "Snapshot Creation" in result[0].text:
                print("✅ create_vm_snapshot returns correct format")
            else:
                print(f"❌ create_vm_snapshot returned unexpected result: {result}")
                return False
            
            print("🔧 Testing method call (list_vm_snapshots)...")
            # Mock snapshot list
            mock_api.nodes('pve1').qemu('100').snapshot.get.return_value = [
                {
                    'name': 'test-snapshot',
                    'description': 'Test description',
                    'snaptime': 1640995200,  # 2022-01-01 00:00:00
                    'parent': 'current'
                }
            ]
            
            result = snapshot_tools.list_vm_snapshots("pve1", "100")
            
            # Verify result
            if result and len(result) > 0 and "VM Snapshots" in result[0].text:
                print("✅ list_vm_snapshots returns correct format")
            else:
                print(f"❌ list_vm_snapshots returned unexpected result: {result}")
                return False
                
            print("\n🎉 All snapshot tools tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_with_snapshots():
    """Test that the server can be created with snapshot tools."""
    try:
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        print("\n🔧 Testing server with snapshot tools...")
        
        with patch('proxmox_mcp.core.node_manager.ProxmoxManager') as mock_proxmox_manager:
            mock_manager_instance = Mock()
            mock_api = Mock()
            mock_manager_instance.get_api.return_value = mock_api
            mock_proxmox_manager.return_value = mock_manager_instance
            
            from proxmox_mcp.server import ProxmoxMCPServer
            
            server = ProxmoxMCPServer(config_path)
            print("✅ Server created with snapshot tools")
            
            # Verify snapshot tools are initialized
            if hasattr(server, 'snapshot_tools'):
                print("✅ Server has snapshot_tools attribute")
            else:
                print("❌ Server missing snapshot_tools attribute")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Snapshot Tools Implementation")
    print("=" * 50)
    
    tools_test = test_snapshot_tools()
    server_test = test_server_with_snapshots()
    
    print(f"\n🎯 Test Results:")
    print(f"   Snapshot Tools: {'✅ PASS' if tools_test else '❌ FAIL'}")
    print(f"   Server Integration: {'✅ PASS' if server_test else '❌ FAIL'}")
    
    if tools_test and server_test:
        print("\n🚀 Snapshot tools implementation is complete and working!")
        return True
    else:
        print("\n💥 Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)