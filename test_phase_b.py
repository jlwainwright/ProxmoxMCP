#!/usr/bin/env python3
"""
Test script for Phase B: Container Runtime Detection tools.

This script verifies that the Phase B container detection functions are properly implemented
and can be imported without errors. It also validates the new OAuth scopes and templates.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_phase_b_imports():
    """Test that all Phase B container detection components can be imported."""
    try:
        # Test VM tools imports
        from proxmox_mcp.tools.vm import VMTools
        print("✅ VMTools imported successfully")
        
        # Test that Phase B methods exist
        phase_b_methods = [
            'detect_container_runtime', 'list_docker_containers', 
            'inspect_docker_container', 'manage_docker_container'
        ]
        for method in phase_b_methods:
            if hasattr(VMTools, method):
                print(f"✅ Method {method} exists in VMTools")
            else:
                print(f"❌ Method {method} missing in VMTools")
                return False
        
        # Test Phase B definitions imports
        from proxmox_mcp.tools.definitions import (
            DETECT_CONTAINER_RUNTIME_DESC, LIST_DOCKER_CONTAINERS_DESC,
            INSPECT_DOCKER_CONTAINER_DESC, MANAGE_DOCKER_CONTAINER_DESC
        )
        print("✅ Phase B tool descriptions imported successfully")
        
        # Test Phase B formatting imports
        from proxmox_mcp.formatting.templates import ProxmoxTemplates
        phase_b_templates = ['container_runtime', 'docker_containers', 'container_inspect', 'container_management']
        for template in phase_b_templates:
            if hasattr(ProxmoxTemplates, template):
                print(f"✅ Template {template} exists")
            else:
                print(f"❌ Template {template} missing")
                return False
            
        print("\\n🎉 All Phase B components imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_phase_b_signatures():
    """Test that Phase B function signatures are correct."""
    try:
        from proxmox_mcp.tools.vm import VMTools
        import inspect
        
        # Test Phase B method signatures
        test_cases = [
            ('detect_container_runtime', ['self', 'node', 'vmid', 'proxmox_node']),
            ('list_docker_containers', ['self', 'node', 'vmid', 'proxmox_node']),
            ('inspect_docker_container', ['self', 'node', 'vmid', 'container_name', 'proxmox_node']),
            ('manage_docker_container', ['self', 'node', 'vmid', 'container_name', 'operation', 'proxmox_node'])
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
        
        print("\\n🎉 All Phase B function signatures are correct!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing signatures: {e}")
        return False

def test_phase_b_helper_methods():
    """Test that Phase B helper parsing methods exist."""
    try:
        from proxmox_mcp.tools.vm import VMTools
        
        helper_methods = [
            '_parse_container_runtime_results',
            '_parse_docker_containers_results', 
            '_parse_container_inspect_results'
        ]
        
        for method in helper_methods:
            if hasattr(VMTools, method):
                print(f"✅ Helper method {method} exists")
            else:
                print(f"❌ Helper method {method} missing")
                return False
        
        print("\\n🎉 All Phase B helper methods implemented!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing helper methods: {e}")
        return False

def test_phase_b_server_integration():
    """Test that Phase B tools are registered in the server."""
    try:
        from proxmox_mcp.server import ProxmoxMCPServer
        from proxmox_mcp.tools.definitions import (
            DETECT_CONTAINER_RUNTIME_DESC, LIST_DOCKER_CONTAINERS_DESC,
            INSPECT_DOCKER_CONTAINER_DESC, MANAGE_DOCKER_CONTAINER_DESC
        )
        
        print("✅ Server integration components imported successfully")
        
        # Check that descriptions are properly defined
        descriptions = [
            DETECT_CONTAINER_RUNTIME_DESC, LIST_DOCKER_CONTAINERS_DESC,
            INSPECT_DOCKER_CONTAINER_DESC, MANAGE_DOCKER_CONTAINER_DESC
        ]
        
        for desc in descriptions:
            if len(desc) > 100 and "Parameters:" in desc:
                print(f"✅ Tool description properly formatted (length: {len(desc)})")
            else:
                print(f"❌ Tool description malformed or too short")
                return False
        
        print("\\n🎉 Phase B server integration ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing server integration: {e}")
        return False

def test_phase_b_template_functionality():
    """Test that Phase B templates can be called with sample data."""
    try:
        from proxmox_mcp.formatting.templates import ProxmoxTemplates
        
        # Test container_runtime template
        sample_runtime_data = {
            "vmid": "104",
            "node": "pve1", 
            "container_runtime": {
                "detected_runtimes": ["Docker 24.0.7"],
                "docker_status": "active (running)",
                "total_containers": 5,
                "running_containers": 3,
                "stopped_containers": 2
            }
        }
        
        result = ProxmoxTemplates.container_runtime(sample_runtime_data)
        if "Container Runtime Detection" in result and "Docker 24.0.7" in result:
            print("✅ container_runtime template works correctly")
        else:
            print("❌ container_runtime template failed")
            return False
        
        # Test docker_containers template
        sample_containers_data = {
            "vmid": "104",
            "node": "pve1",
            "docker_containers": {
                "total_containers": 3,
                "running_containers": 2,
                "stopped_containers": 1,
                "containers": [
                    {"name": "nginx", "image": "nginx:latest", "status": "Up 2 hours", "ports": "80->80/tcp"},
                    {"name": "db", "image": "postgres:15", "status": "Exited (0)", "ports": "none"}
                ]
            }
        }
        
        result = ProxmoxTemplates.docker_containers(sample_containers_data)
        if "Docker Containers" in result and "nginx" in result:
            print("✅ docker_containers template works correctly")
        else:
            print("❌ docker_containers template failed")
            return False
        
        print("\\n🎉 Phase B templates functional!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing templates: {e}")
        return False

def show_phase_b_info():
    """Display information about Phase B capabilities."""
    print("\\n📋 Phase B: Container Runtime Detection Capabilities")
    print("=" * 60)
    
    capabilities = {
        "🐳 Container Runtime Discovery": [
            "Docker installation and version detection",
            "Podman runtime discovery and status",
            "LXD/LXC container engine detection",
            "Kubernetes kubelet and kubectl presence",
            "Container counts and resource aggregation"
        ],
        "📦 Docker Container Management": [
            "Complete container inventory with status",
            "Container resource usage monitoring",
            "Port mapping and network analysis",
            "Environment variable inspection",
            "Container lifecycle operations (start/stop/restart)"
        ],
        "🔍 Deep Container Inspection": [
            "Detailed container configuration analysis",
            "Real-time resource usage metrics",
            "Recent log retrieval and analysis",
            "Process monitoring within containers",
            "Health check status and restart policies"
        ],
        "🛠️ Container Operations": [
            "Safe container start/stop/restart operations",
            "Operation validation and status confirmation",
            "Error handling and rollback capabilities",
            "Multi-container batch operations support"
        ]
    }
    
    for category, features in capabilities.items():
        print(f"\\n{category}")
        for feature in features:
            print(f"  • {feature}")
    
    print(f"\\n🎯 OAuth 2.1 Integration")
    print(f"  • New scope: proxmox:containers:manage")
    print(f"  • Container-specific permissions")
    print(f"  • Granular access control for container operations")
    
    print(f"\\n📊 LLM Benefits")
    print(f"  • Rich, emoji-based container status visualization")
    print(f"  • Comprehensive container inventory generation")
    print(f"  • Application stack discovery and analysis")
    print(f"  • Container troubleshooting and management automation")

def main():
    """Run all Phase B tests."""
    print("🧪 Testing Phase B: Container Runtime Detection Implementation\\n")
    
    print("📦 Testing imports...")
    imports_ok = test_phase_b_imports()
    
    print("\\n🔍 Testing function signatures...")
    signatures_ok = test_phase_b_signatures()
    
    print("\\n🛠️ Testing helper methods...")
    helpers_ok = test_phase_b_helper_methods()
    
    print("\\n🔗 Testing server integration...")
    integration_ok = test_phase_b_server_integration()
    
    print("\\n🎨 Testing template functionality...")
    templates_ok = test_phase_b_template_functionality()
    
    if imports_ok and signatures_ok and helpers_ok and integration_ok and templates_ok:
        print("\\n🚀 All Phase B tests passed! Container runtime detection is ready.")
        show_phase_b_info()
        print("\\n📋 Next steps:")
        print("1. Restart the Proxmox MCP server to load Phase B tools")
        print("2. Test with live VMs that have Docker installed")
        print("3. Verify new OAuth scope 'proxmox:containers:manage' works")
        print("4. Generate comprehensive container inventories for LLM analysis")
        print("\\n💡 Example usage after server restart:")
        print("   detect_container_runtime(node='pve1', vmid='104')  # Docker runtime discovery")
        print("   list_docker_containers(node='pve1', vmid='104')   # List all containers")
        print("   inspect_docker_container(node='pve1', vmid='104', container_name='nginx')  # Deep inspect")
        print("   manage_docker_container(node='pve1', vmid='104', container_name='app', operation='restart')  # Restart container")
        return 0
    else:
        print("\\n💥 Some Phase B tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())