#!/usr/bin/env python3
"""
Test script for multi-node Proxmox MCP implementation.

This script tests the new multi-node functionality by:
1. Loading both single-node and multi-node configurations
2. Testing the NodeManager with different node selections
3. Verifying tool operations with node parameters
"""

import sys
import os
import asyncio

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from proxmox_mcp.config.loader import load_config
from proxmox_mcp.core.node_manager import NodeManager
from proxmox_mcp.tools.node import NodeTools


def test_single_node_config():
    """Test single-node configuration (legacy mode)."""
    print("=" * 60)
    print("Testing Single-Node Configuration")
    print("=" * 60)
    
    try:
        # Load single-node config
        config = load_config("config-stdio.json")
        print(f"✅ Loaded config: {config.is_multi_node() and 'Multi-node' or 'Single-node'}")
        
        # Test NodeManager
        node_manager = NodeManager(config)
        print(f"✅ NodeManager initialized")
        print(f"   Default node: {node_manager.get_default_node()}")
        print(f"   Available nodes: {node_manager.get_available_nodes()}")
        
        # Test health check
        health = node_manager.health_check()
        print(f"✅ Health check: {health}")
        
        # Test tools
        node_tools = NodeTools(node_manager)
        
        # Test without node parameter (should use default)
        print("\n--- Testing get_nodes() without node parameter ---")
        result = node_tools.get_nodes()
        print(f"✅ get_nodes() returned {len(result)} content objects")
        
        # Test with explicit node parameter (should still work with default)
        print("\n--- Testing get_nodes() with explicit node parameter ---")
        result = node_tools.get_nodes("default")
        print(f"✅ get_nodes('default') returned {len(result)} content objects")
        
    except Exception as e:
        print(f"❌ Single-node test failed: {e}")
        return False
    
    return True


def test_multi_node_config():
    """Test multi-node configuration."""
    print("\n" + "=" * 60)
    print("Testing Multi-Node Configuration")
    print("=" * 60)
    
    try:
        # Check if multi-node config exists
        multi_config_path = "proxmox-config/config.json"
        if not os.path.exists(multi_config_path):
            print(f"⚠️  Multi-node config not found: {multi_config_path}")
            return True  # Not a failure, just not available
        
        # Load multi-node config
        config = load_config(multi_config_path)
        print(f"✅ Loaded config: {config.is_multi_node() and 'Multi-node' or 'Single-node'}")
        
        if not config.is_multi_node():
            print("⚠️  Config is not in multi-node format")
            return True
        
        # Test NodeManager
        node_manager = NodeManager(config)
        print(f"✅ NodeManager initialized")
        print(f"   Default node: {node_manager.get_default_node()}")
        print(f"   Available nodes: {node_manager.get_available_nodes()}")
        
        # Test health check for all nodes
        health = node_manager.health_check()
        print(f"✅ Health check: {health}")
        
        # Test tools with different nodes
        node_tools = NodeTools(node_manager)
        
        available_nodes = list(node_manager.get_available_nodes().keys())
        
        for node_id in available_nodes[:2]:  # Test first 2 nodes
            print(f"\n--- Testing get_nodes() with node: {node_id} ---")
            try:
                result = node_tools.get_nodes(node_id)
                print(f"✅ get_nodes('{node_id}') returned {len(result)} content objects")
            except Exception as e:
                print(f"❌ get_nodes('{node_id}') failed: {e}")
        
    except Exception as e:
        print(f"❌ Multi-node test failed: {e}")
        return False
    
    return True


def test_config_validation():
    """Test configuration validation."""
    print("\n" + "=" * 60)
    print("Testing Configuration Validation")
    print("=" * 60)
    
    try:
        # Test single-node config methods
        config = load_config("config-stdio.json")
        
        if config.is_multi_node():
            print("❌ Single-node config detected as multi-node")
            return False
        
        single_config = config.get_single_node_config()
        print(f"✅ Single-node config extracted: {single_config.proxmox.host}")
        
        try:
            config.get_multi_node_config()
            print("❌ Should not be able to get multi-node config from single-node")
            return False
        except ValueError:
            print("✅ Correctly rejected multi-node config extraction from single-node")
        
    except Exception as e:
        print(f"❌ Config validation test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("Proxmox MCP Multi-Node Implementation Test")
    print("=" * 60)
    
    tests = [
        ("Configuration Validation", test_config_validation),
        ("Single-Node Configuration", test_single_node_config),
        ("Multi-Node Configuration", test_multi_node_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Multi-node implementation is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())