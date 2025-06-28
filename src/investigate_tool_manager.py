#!/usr/bin/env python3
"""
Investigate the ToolManager class to understand how tools are stored and accessed.
"""
import asyncio
from typing import Annotated
from pydantic import Field

def investigate_tool_manager():
    """Investigate the ToolManager class in detail."""
    try:
        print("🔧 Investigating ToolManager...")
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("TestServer")
        tool_manager = mcp._tool_manager
        
        print(f"🔧 ToolManager type: {type(tool_manager)}")
        print("🔧 ToolManager attributes:")
        for attr in dir(tool_manager):
            if not attr.startswith('__'):
                try:
                    value = getattr(tool_manager, attr)
                    print(f"   {attr}: {type(value)} = {value}")
                except Exception as e:
                    print(f"   {attr}: Error accessing - {e}")
        
        print("\n🔧 Registering a tool to see what changes...")
        
        @mcp.tool(description="Test tool for investigation")
        def investigate_tool(message: Annotated[str, Field(description="Test message")] = "hello"):
            return f"Investigation response: {message}"
        
        print("✅ Tool registered")
        
        print("🔧 ToolManager attributes after registration:")
        for attr in dir(tool_manager):
            if not attr.startswith('__'):
                try:
                    value = getattr(tool_manager, attr)
                    print(f"   {attr}: {type(value)} = {value}")
                except Exception as e:
                    print(f"   {attr}: Error accessing - {e}")
        
        print("\n🔧 Testing list_tools() call...")
        
        async def test_list_tools():
            try:
                result = await mcp.list_tools()
                print(f"   list_tools() result type: {type(result)}")
                print(f"   list_tools() result: {result}")
                if hasattr(result, 'tools'):
                    print(f"   tools attribute: {result.tools}")
                    return len(result.tools)
                return 0
            except Exception as e:
                print(f"   list_tools() failed: {e}")
                import traceback
                traceback.print_exc()
                return 0
        
        tool_count = asyncio.run(test_list_tools())
        print(f"🔧 Tool count from list_tools(): {tool_count}")
        
        # Try calling the tool manager's list_tools directly
        print("\n🔧 Testing tool manager's list_tools directly...")
        try:
            if hasattr(tool_manager, 'list_tools'):
                direct_result = asyncio.run(tool_manager.list_tools())
                print(f"   Direct list_tools() result: {direct_result}")
                print(f"   Direct result type: {type(direct_result)}")
        except Exception as e:
            print(f"   Direct list_tools() failed: {e}")
        
        return tool_count > 0
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_mcp_version_details():
    """Check detailed MCP version information."""
    try:
        print("\n🔧 Checking MCP version details...")
        import mcp
        print(f"   MCP version: {mcp.__version__ if hasattr(mcp, '__version__') else 'Unknown'}")
        
        print("🔧 FastMCP module info...")
        from mcp.server.fastmcp import FastMCP
        print(f"   FastMCP: {FastMCP}")
        
        # Check if there are any recent API changes
        print("🔧 Available FastMCP methods:")
        for attr in dir(FastMCP):
            if not attr.startswith('_'):
                print(f"   {attr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Version check failed: {e}")
        return False

def main():
    """Run the investigation."""
    print("🔍 ToolManager Investigation")
    print("=" * 50)
    
    version_result = check_mcp_version_details()
    investigation_result = investigate_tool_manager()
    
    print(f"\n🎯 Investigation Results:")
    print(f"   Version check: {'✅ PASS' if version_result else '❌ FAIL'}")
    print(f"   Tool manager: {'✅ WORKING' if investigation_result else '❌ NOT WORKING'}")

if __name__ == "__main__":
    main()