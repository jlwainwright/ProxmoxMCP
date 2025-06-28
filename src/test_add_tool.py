#!/usr/bin/env python3
"""
Test using add_tool method instead of decorator.
"""
import asyncio
from typing import Annotated
from pydantic import Field

def test_add_tool_method():
    """Test using the add_tool method."""
    try:
        print("🔧 Testing add_tool method...")
        from mcp.server.fastmcp import FastMCP
        from mcp.types import Tool
        
        mcp = FastMCP("TestServer")
        print("✅ FastMCP instance created")
        
        print("🔧 Creating tool definition...")
        
        def test_tool_func(message: str = "hello") -> str:
            return f"Test response: {message}"
        
        # Try using add_tool method
        print("🔧 Using add_tool method...")
        try:
            mcp.add_tool("test_tool", test_tool_func, description="A test tool")
            print("✅ Tool added with add_tool method")
        except Exception as e:
            print(f"❌ add_tool failed: {e}")
            
        print("🔧 Checking _tool_manager...")
        if hasattr(mcp, '_tool_manager'):
            tool_manager = mcp._tool_manager
            print(f"   Tool manager: {tool_manager}")
            if hasattr(tool_manager, 'tools'):
                tools = tool_manager.tools
                print(f"   Tools in manager: {len(tools) if tools else 0}")
                if tools:
                    for name, tool in tools.items():
                        print(f"      - {name}: {tool}")
        
        print("🔧 Testing tool enumeration...")
        
        async def check_tools():
            try:
                tools_list = await mcp.list_tools()
                tools = tools_list.tools if hasattr(tools_list, 'tools') else []
                print(f"📊 Found {len(tools)} tools via list_tools()")
                for tool in tools:
                    print(f"   - {tool.name}: {tool.description}")
                return len(tools)
            except Exception as e:
                print(f"❌ list_tools failed: {e}")
                return 0
        
        tool_count = asyncio.run(check_tools())
        
        if tool_count > 0:
            print("✅ add_tool method test successful!")
            return True
        else:
            print("❌ add_tool method test failed - no tools found")
            return False
            
    except Exception as e:
        print(f"❌ add_tool method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_decorator_issue():
    """Test if the decorator is working at all."""
    try:
        print("\n🔧 Testing decorator behavior...")
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("TestServer")
        
        print("🔧 Applying decorator...")
        
        @mcp.tool(description="Test decorator tool")
        def test_decorator_tool(message: Annotated[str, Field(description="Test message")] = "hello"):
            return f"Decorator response: {message}"
        
        print("✅ Decorator applied successfully")
        
        print("🔧 Checking if decorator actually registered anything...")
        
        # Check internal state
        if hasattr(mcp, '_tool_manager'):
            tool_manager = mcp._tool_manager
            print(f"   Tool manager: {tool_manager}")
            if hasattr(tool_manager, 'tools'):
                tools = tool_manager.tools
                print(f"   Tools in manager: {tools}")
                if tools:
                    print(f"   Number of tools: {len(tools)}")
                    for name, tool in tools.items():
                        print(f"      - {name}: {tool}")
                else:
                    print("   No tools in manager!")
            else:
                print("   Tool manager has no 'tools' attribute")
        else:
            print("   No _tool_manager found")
        
        return True
        
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔍 FastMCP add_tool Method Test")
    print("=" * 50)
    
    add_tool_result = test_add_tool_method()
    decorator_result = test_decorator_issue()
    
    print(f"\n🎯 Test Results:")
    print(f"   add_tool method: {'✅ PASS' if add_tool_result else '❌ FAIL'}")
    print(f"   Decorator test: {'✅ PASS' if decorator_result else '❌ FAIL'}")

if __name__ == "__main__":
    main()