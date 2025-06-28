#!/usr/bin/env python3
"""
Test script to enumerate all available MCP tools in ProxmoxMCP.
"""
import os
import sys
import asyncio
import json

# Add current directory to path
sys.path.insert(0, '.')

async def test_mcp_tools():
    """Test and enumerate all registered MCP tools."""
    try:
        config_path = "/Users/jacques/DevFolder/ProxmoxMCP/src/config/config.json"
        os.environ["PROXMOX_MCP_CONFIG"] = config_path
        
        from proxmox_mcp.server import ProxmoxMCPServer
        
        print("🚀 Initializing ProxmoxMCP Server...")
        server = ProxmoxMCPServer(config_path)
        
        # Access the MCP server instance
        mcp = server.mcp
        
        # Get list of registered tools
        tools_list = await mcp.list_tools()
        tools = tools_list if isinstance(tools_list, list) else []
        
        print(f"\n📊 MCP Server Statistics:")
        print(f"   Tools registered: {len(tools)}")
        
        # Group tools by category
        tool_categories = {
            "Node Management": [],
            "VM Operations": [],
            "VM Deep Inspection": [],
            "Container Management": [],
            "Application Discovery": [],
            "Storage Management": [],
            "Cluster Management": [],
            "Monitoring Tools": [],
            "Backup & Recovery": [],
            "Other": []
        }
        
        print(f"\n🛠️  Registered MCP Tools:")
        print("=" * 60)
        
        for i, tool in enumerate(tools, 1):
            tool_name = tool.name
            # Categorize tools
            if "node" in tool_name.lower():
                category = "Node Management"
            elif any(x in tool_name.lower() for x in ["start_vm", "stop_vm", "restart_vm", "suspend_vm", "get_vm_status"]):
                category = "VM Operations"
            elif any(x in tool_name.lower() for x in ["detect_vm_os", "get_vm_system_info", "list_vm_services", "get_vm_network_config"]):
                category = "VM Deep Inspection"
            elif any(x in tool_name.lower() for x in ["docker", "container"]):
                category = "Container Management"
            elif any(x in tool_name.lower() for x in ["discover", "analyze_application"]):
                category = "Application Discovery"
            elif "storage" in tool_name.lower():
                category = "Storage Management"
            elif "cluster" in tool_name.lower():
                category = "Cluster Management"
            elif any(x in tool_name.lower() for x in ["grafana", "prometheus", "alerting", "log_aggregation"]):
                category = "Monitoring Tools"
            elif any(x in tool_name.lower() for x in ["backup", "recovery", "disaster"]):
                category = "Backup & Recovery"
            else:
                category = "Other"
                
            tool_categories[category].append(tool_name)
            
            # Get description
            description = getattr(tool, 'description', 'No description available')
            
            print(f"{i:2d}. {tool_name}")
            print(f"    📝 {description[:80]}{'...' if len(description) > 80 else ''}")
        
        print(f"\n📋 Tools by Category:")
        print("=" * 60)
        
        total_tools = 0
        for category, tools in tool_categories.items():
            if tools:
                print(f"\n🔧 {category} ({len(tools)} tools):")
                for tool in sorted(tools):
                    print(f"   • {tool}")
                total_tools += len(tools)
        
        print(f"\n🎯 Summary:")
        print(f"   Total tools: {total_tools}")
        print(f"   Categories with tools: {len([c for c, t in tool_categories.items() if t])}")
        
        # Show implementation phases
        print(f"\n📈 Implementation Phases Detected:")
        phase_counts = {
            "Core Tools": len(tool_categories["Node Management"]) + len(tool_categories["VM Operations"]) + len(tool_categories["Storage Management"]) + len(tool_categories["Cluster Management"]),
            "Phase A - Deep Inspection": len(tool_categories["VM Deep Inspection"]),
            "Phase B - Container Management": len(tool_categories["Container Management"]),
            "Phase C - Application Discovery": len(tool_categories["Application Discovery"]),
            "Phase 1 - Enhanced Monitoring": len(tool_categories["Monitoring Tools"]),
            "Phase 2 - Backup & Recovery": len(tool_categories["Backup & Recovery"])
        }
        
        for phase, count in phase_counts.items():
            if count > 0:
                print(f"   ✅ {phase}: {count} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool enumeration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the tool enumeration."""
    print("🔍 ProxmoxMCP Tool Enumeration")
    print("=" * 50)
    
    # Run the async test
    result = asyncio.run(test_mcp_tools())
    
    if result:
        print(f"\n🎉 All tools successfully enumerated!")
    else:
        print(f"\n⚠️  Tool enumeration failed.")

if __name__ == "__main__":
    main()