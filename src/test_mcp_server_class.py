#!/usr/bin/env python3
"""
Test MCP Server class directly instead of FastMCP.
"""
import asyncio
from typing import Annotated
from pydantic import Field

def test_mcp_server():
    """Test using the base MCP Server class."""
    try:
        print("🔧 Testing MCP Server import...")
        from mcp.server import Server
        from mcp.types import Tool, TextContent, ListToolsResult
        print("✅ MCP Server import successful")
        
        print("🔧 Creating MCP Server instance...")
        server = Server("TestServer")
        print("✅ MCP Server instance created")
        
        print("🔧 Defining a tool...")
        def test_tool_handler(message: str = "hello") -> str:
            return f"Test response: {message}"
        
        # Create tool definition
        test_tool_def = Tool(
            name="test_tool",
            description="A simple test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Test message",
                        "default": "hello"
                    }
                }
            }
        )
        
        print("🔧 Registering tool with server...")
        
        @server.list_tools()
        async def list_tools():
            return ListToolsResult(tools=[test_tool_def])
        
        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "test_tool":
                return [TextContent(type="text", text=test_tool_handler(**arguments))]
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        print("✅ Tool registered with server")
        
        print("🔧 Testing tool enumeration...")
        
        async def check_tools():
            result = await server._list_tools_handler()
            tools = result.tools if hasattr(result, 'tools') else []
            print(f"📊 Found {len(tools)} tools")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            return len(tools)
        
        tool_count = asyncio.run(check_tools())
        
        if tool_count > 0:
            print("✅ MCP Server test successful!")
            return True
        else:
            print("❌ MCP Server test failed - no tools found")
            return False
            
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastmcp_alternative():
    """Test FastMCP with different syntax."""
    try:
        print("\n🔧 Testing FastMCP alternative syntax...")
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("TestServer")
        
        # Try different registration approach
        print("🔧 Trying tools property...")
        tools = mcp.tools if hasattr(mcp, 'tools') else None
        print(f"   Tools property: {tools}")
        
        print("🔧 Trying _tools attribute...")
        _tools = mcp._tools if hasattr(mcp, '_tools') else None
        print(f"   _tools attribute: {_tools}")
        
        print("🔧 Checking all attributes...")
        for attr in dir(mcp):
            if 'tool' in attr.lower():
                print(f"   Found attribute: {attr}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastMCP alternative test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔍 MCP Server Alternative Test")
    print("=" * 50)
    
    server_result = test_mcp_server()
    fastmcp_result = test_fastmcp_alternative()
    
    print(f"\n🎯 Test Results:")
    print(f"   MCP Server: {'✅ PASS' if server_result else '❌ FAIL'}")
    print(f"   FastMCP Alt: {'✅ PASS' if fastmcp_result else '❌ FAIL'}")

if __name__ == "__main__":
    main()