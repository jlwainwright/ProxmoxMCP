#!/usr/bin/env python3
"""
Test script for VM control operations.

This script verifies that the new VM control functions are properly implemented
and can be imported without errors.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all new VM control components can be imported."""
    try:
        # Test VM tools imports
        from proxmox_mcp.tools.vm import VMTools
        print("✅ VMTools imported successfully")
        
        # Test that new methods exist
        vm_methods = ['start_vm', 'stop_vm', 'restart_vm', 'suspend_vm', 'get_vm_status']
        for method in vm_methods:
            if hasattr(VMTools, method):
                print(f"✅ Method {method} exists in VMTools")
            else:
                print(f"❌ Method {method} missing in VMTools")
                return False
        
        # Test definitions imports
        from proxmox_mcp.tools.definitions import (
            START_VM_DESC, STOP_VM_DESC, RESTART_VM_DESC, 
            SUSPEND_VM_DESC, GET_VM_STATUS_DESC
        )
        print("✅ VM control descriptions imported successfully")
        
        # Test formatting imports
        from proxmox_mcp.formatting.formatters import ProxmoxFormatters
        if hasattr(ProxmoxFormatters, 'format_vm_operation_result'):
            print("✅ VM operation formatter exists")
        else:
            print("❌ VM operation formatter missing")
            return False
            
        from proxmox_mcp.formatting.templates import ProxmoxTemplates
        if hasattr(ProxmoxTemplates, 'vm_status'):
            print("✅ VM status template exists")
        else:
            print("❌ VM status template missing")
            return False
            
        # Test theme updates
        from proxmox_mcp.formatting.theme import ProxmoxTheme
        if 'vm_control' in ProxmoxTheme.ACTIONS:
            print("✅ VM control theme action exists")
        else:
            print("❌ VM control theme action missing")
            return False
            
        print("\n🎉 All VM control components imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_function_signatures():
    """Test that function signatures are correct."""
    try:
        from proxmox_mcp.tools.vm import VMTools
        import inspect
        
        # Test method signatures
        test_cases = [
            ('start_vm', ['self', 'node', 'vmid', 'proxmox_node']),
            ('stop_vm', ['self', 'node', 'vmid', 'proxmox_node']),
            ('restart_vm', ['self', 'node', 'vmid', 'proxmox_node']),
            ('suspend_vm', ['self', 'node', 'vmid', 'proxmox_node']),
            ('get_vm_status', ['self', 'node', 'vmid', 'proxmox_node'])
        ]
        
        for method_name, expected_params in test_cases:
            method = getattr(VMTools, method_name)
            sig = inspect.signature(method)
            actual_params = list(sig.parameters.keys())
            
            if actual_params == expected_params:
                print(f"✅ {method_name} signature correct: {actual_params}")
            else:
                print(f"❌ {method_name} signature mismatch. Expected: {expected_params}, Got: {actual_params}")
                return False
        
        print("\n🎉 All function signatures are correct!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing signatures: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing VM Control Implementation\n")
    
    print("📦 Testing imports...")
    imports_ok = test_imports()
    
    print("\n🔍 Testing function signatures...")
    signatures_ok = test_function_signatures()
    
    if imports_ok and signatures_ok:
        print("\n🚀 All tests passed! VM control implementation is ready.")
        print("\nNext steps:")
        print("1. Restart the Proxmox MCP server to load the new tools")
        print("2. Test VM control operations with live VMs")
        print("3. Verify OAuth scopes work correctly (proxmox:vms:control)")
        return 0
    else:
        print("\n💥 Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())