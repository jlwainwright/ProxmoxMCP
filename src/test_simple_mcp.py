#!/usr/bin/env python3
"""
Test basic FastMCP functionality to isolate the issue.
"""
import asyncio
from typing import Annotated
from pydantic import Field

def test_basic_fastmcp():
    """Test basic FastMCP functionality."""
    try:
        print("🔧 Testing basic FastMCP import...")
        from mcp.server.fastmcp import FastMCP
        print("✅ FastMCP import successful")
        
        print("🔧 Creating FastMCP instance...")
        mcp = FastMCP("TestServer")
        print("✅ FastMCP instance created")
        
        print("🔧 Registering a simple tool...")
        
        @mcp.tool(description="A simple test tool")
        def test_tool(message: Annotated[str, Field(description="Test message")] = "hello"):
            return f"Test response: {message}"
        
        print("✅ Tool registered")
        
        print("🔧 Testing tool enumeration...")
        
        async def check_tools():
            tools_list = await mcp.list_tools()
            tools = tools_list.tools if hasattr(tools_list, 'tools') else []
            print(f"📊 Found {len(tools)} tools")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            return len(tools)
        
        tool_count = asyncio.run(check_tools())
        
        if tool_count > 0:
            print("✅ Basic FastMCP test successful!")
            return True
        else:
            print("❌ Basic FastMCP test failed - no tools found")
            return False
            
    except Exception as e:
        print(f"❌ Basic FastMCP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_types():
    """Test MCP types and imports."""
    try:
        print("\n🔧 Testing MCP types import...")
        from mcp.types import TextContent as Content
        print("✅ MCP types import successful")
        
        print("🔧 Testing Content creation...")
        content = Content(type="text", text="test")
        print(f"✅ Content created: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP types test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all basic tests."""
    print("🔍 Basic FastMCP Functionality Test")
    print("=" * 50)
    
    types_result = test_mcp_types()
    basic_result = test_basic_fastmcp()
    
    print(f"\n🎯 Test Results:")
    print(f"   MCP Types: {'✅ PASS' if types_result else '❌ FAIL'}")
    print(f"   Basic FastMCP: {'✅ PASS' if basic_result else '❌ FAIL'}")

if __name__ == "__main__":
    main()