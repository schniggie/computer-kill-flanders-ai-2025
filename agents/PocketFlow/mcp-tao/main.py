# main.py

import asyncio
import sys
import os
import logging
from typing import Dict, Any

# Add the parent directory to the path to import from utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flow import create_universal_tao_flow
from utils_fastmcp import FastMultiMCPClient, call_llm
from mcp_config import MCPConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    Universal MCP-TAO Agent
    
    A powerful AI agent that combines:
    - Multi-MCP server support (any tools from any servers)
    - TAO pattern for intelligent multi-step workflows
    - FastMCP for reliable async handling
    
    Can work with any MCP servers across any domain:
    - Research and information gathering
    - Web automation and scraping
    - File system operations
    - Database interactions
    - API calls and integrations
    - Code generation and execution
    - And much more...
    """
    
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your query: ")
    
    if not query.strip():
        print("No query provided. Exiting.")
        return
    
    print(f"🚀 Starting Universal MCP-TAO Agent")
    print(f"📝 Query: {query}")
    print("=" * 50)
    
    # Initialize MCP client
    mcp_client = FastMultiMCPClient("mcp_servers.json")
    
    # LLM functionality is provided by call_llm function
    
    try:
        # Connect to all MCP servers
        print("🔌 Connecting to MCP servers...")
        await mcp_client.connect_all()
        
        # Get available tools
        print("🛠️ Gathering available tools...")
        all_tools = mcp_client.get_all_tools()
        
        # Transform to expected format: {server_name: [tool_objects]}
        available_tools = {}
        for tool in all_tools:
            if tool.server_name not in available_tools:
                available_tools[tool.server_name] = []
            available_tools[tool.server_name].append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
        
        if not any(tools for tools in available_tools.values()):
            print("⚠️ No tools available from any MCP server. Running in answer-only mode.")
        else:
            tool_count = sum(len(tools) for tools in available_tools.values())
            server_count = len([s for s, tools in available_tools.items() if tools])
            print(f"✅ Found {tool_count} tools from {server_count} servers")
        
        # Create shared data for the TAO flow
        shared = {
            "query": query,
            "thoughts": [],
            "observations": [],
            "current_thought_number": 0,
            "mcp_client": mcp_client,
            "available_tools": available_tools
        }
        
        # Create and run the universal TAO flow
        print("🧠 Starting TAO loop...")
        print("=" * 50)
        
        tao_flow = create_universal_tao_flow()
        await tao_flow.run_async(shared)
        
        # Print final result
        print("=" * 50)
        if "final_answer" in shared:
            print("🎯 Final Answer:")
            print(shared["final_answer"])
        else:
            print("⚠️ Flow did not produce a final answer")
        
        # Print summary
        thoughts_count = len(shared.get("thoughts", []))
        observations_count = len(shared.get("observations", []))
        print(f"\n📊 TAO Summary: {thoughts_count} thoughts, {observations_count} observations")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        print(f"❌ Error: {e}")
    
    print("✅ Universal MCP-TAO Agent completed")

if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the async main function
    asyncio.run(main())