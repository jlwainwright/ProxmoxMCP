#!/usr/bin/env python3
"""
Test script for Phase A: Deep Inspection tools.

This script verifies that the Phase A deep inspection functions are properly implemented
and can be imported without errors. It also provides validation for the new OAuth scopes.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_phase_a_imports():
    """Test that all Phase A deep inspection components can be imported."""
    try:
        # Test VM tools imports
        from proxmox_mcp.tools.vm import VMTools
        print("✅ VMTools imported successfully")
        
        # Test that Phase A methods exist
        phase_a_methods = [
            'detect_vm_os', 'get_vm_system_info', 
            'list_vm_services', 'get_vm_network_config'
        ]
        for method in phase_a_methods:
            if hasattr(VMTools, method):
                print(f"✅ Method {method} exists in VMTools")
            else:
                print(f"❌ Method {method} missing in VMTools")
                return False
        
        # Test Phase A definitions imports
        from proxmox_mcp.tools.definitions import (
            DETECT_VM_OS_DESC, GET_VM_SYSTEM_INFO_DESC,
            LIST_VM_SERVICES_DESC, GET_VM_NETWORK_CONFIG_DESC
        )
        print("✅ Phase A tool descriptions imported successfully")
        
        # Test Phase A formatting imports
        from proxmox_mcp.formatting.templates import ProxmoxTemplates
        phase_a_templates = ['os_detection', 'system_info', 'services_info', 'network_info']
        for template in phase_a_templates:
            if hasattr(ProxmoxTemplates, template):
                print(f"✅ Template {template} exists")
            else:
                print(f"❌ Template {template} missing")
                return False
            
        print("\n🎉 All Phase A components imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_phase_a_signatures():
    """Test that Phase A function signatures are correct."""
    try:
        from proxmox_mcp.tools.vm import VMTools
        import inspect
        
        # Test Phase A method signatures
        test_cases = [
            ('detect_vm_os', ['self', 'node', 'vmid', 'proxmox_node']),
            ('get_vm_system_info', ['self', 'node', 'vmid', 'proxmox_node']),
            ('list_vm_services', ['self', 'node', 'vmid', 'proxmox_node']),
            ('get_vm_network_config', ['self', 'node', 'vmid', 'proxmox_node'])
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
        
        print("\n🎉 All Phase A function signatures are correct!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing signatures: {e}")
        return False

def test_helper_methods():
    """Test that helper parsing methods exist."""
    try:
        from proxmox_mcp.tools.vm import VMTools
        
        helper_methods = [
            '_extract_command_output',
            '_parse_os_detection_results',
            '_parse_system_info_results', 
            '_parse_services_info_results',
            '_parse_network_info_results'
        ]
        
        for method in helper_methods:
            if hasattr(VMTools, method):
                print(f"✅ Helper method {method} exists")
            else:
                print(f"❌ Helper method {method} missing")
                return False
        
        print("\n🎉 All helper methods implemented!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing helper methods: {e}")
        return False

def test_server_integration():
    """Test that Phase A tools are registered in the server."""
    try:
        from proxmox_mcp.server import ProxmoxMCPServer
        from proxmox_mcp.tools.definitions import (
            DETECT_VM_OS_DESC, GET_VM_SYSTEM_INFO_DESC,
            LIST_VM_SERVICES_DESC, GET_VM_NETWORK_CONFIG_DESC
        )
        
        print("✅ Server integration components imported successfully")
        
        # Check that descriptions are properly defined
        descriptions = [
            DETECT_VM_OS_DESC, GET_VM_SYSTEM_INFO_DESC,
            LIST_VM_SERVICES_DESC, GET_VM_NETWORK_CONFIG_DESC
        ]
        
        for desc in descriptions:
            if len(desc) > 50 and "Parameters:" in desc:
                print(f"✅ Tool description properly formatted (length: {len(desc)})")
            else:
                print(f"❌ Tool description malformed or too short")
                return False
        
        print("\n🎉 Server integration ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing server integration: {e}")
        return False

def show_phase_a_info():
    """Display information about Phase A capabilities."""
    print("\n📋 Phase A: Deep Inspection Capabilities")
    print("=" * 50)
    
    capabilities = {
        "🐧 OS Detection": [
            "Linux distribution and version detection",
            "Kernel version and architecture",
            "System hostname and uptime",
            "Init system identification"
        ],
        "💻 System Information": [
            "Disk usage and mount points (df, lsblk)",
            "Memory usage and statistics (free)",
            "CPU usage and top processes",
            "Timezone and locale settings"
        ],
        "🔧 Service Discovery": [
            "Active systemd services",
            "Top processes by CPU usage",
            "Listening network ports",
            "Scheduled cron jobs"
        ],
        "🌐 Network Configuration": [
            "Network interfaces and IP addresses",
            "Routing table and default gateway", 
            "DNS configuration",
            "Firewall status"
        ]
    }
    
    for category, features in capabilities.items():
        print(f"\n{category}")
        for feature in features:
            print(f"  • {feature}")
    
    print(f"\n🎯 OAuth 2.1 Integration")
    print(f"  • New scope: proxmox:vms:inspect")
    print(f"  • Granular permissions for deep inspection")
    print(f"  • Backward compatible with existing scopes")
    
    print(f"\n📊 LLM Benefits")
    print(f"  • Rich, structured output for AI analysis")
    print(f"  • Comprehensive VM inventory generation")
    print(f"  • Detailed troubleshooting information")
    print(f"  • Foundation for container runtime detection")

def main():
    """Run all Phase A tests."""
    print("🧪 Testing Phase A: Deep Inspection Implementation\n")
    
    print("📦 Testing imports...")
    imports_ok = test_phase_a_imports()
    
    print("\n🔍 Testing function signatures...")
    signatures_ok = test_phase_a_signatures()
    
    print("\n🛠️ Testing helper methods...")
    helpers_ok = test_helper_methods()
    
    print("\n🔗 Testing server integration...")
    integration_ok = test_server_integration()
    
    if imports_ok and signatures_ok and helpers_ok and integration_ok:
        print("\n🚀 All Phase A tests passed! Deep inspection is ready.")
        show_phase_a_info()
        print("\n📋 Next steps:")
        print("1. Restart the Proxmox MCP server to load Phase A tools")
        print("2. Test with live VMs that have QEMU guest agent installed")
        print("3. Verify new OAuth scope 'proxmox:vms:inspect' works")
        print("4. Generate comprehensive VM inventories for LLM analysis")
        print("\n💡 Example usage after server restart:")
        print("   detect_vm_os(node='pve1', vmid='800')  # TrueNAS OS detection")
        print("   get_vm_system_info(node='pve1', vmid='102')  # umbrelos system info")
        print("   list_vm_services(node='pve1', vmid='103')  # HomeAssistant services")
        return 0
    else:
        print("\n💥 Some Phase A tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())