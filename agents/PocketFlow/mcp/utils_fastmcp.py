from openai import OpenAI
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
from fastmcp.client import Client
from fastmcp.mcp_config import MCPConfig

logger = logging.getLogger(__name__)

@dataclass 
class FastMCPTool:
    """Represents a tool from a FastMCP server."""
    name: str
    description: str
    server_name: str
    inputSchema: Dict[str, Any]
    
    @property
    def qualified_name(self) -> str:
        """Get fully qualified tool name including server."""
        return f"{self.server_name}.{self.name}"

class FastMCPServerClient:
    """Client for a single MCP server using FastMCP."""
    
    def __init__(self, server_name: str, server_config: dict):
        self.server_name = server_name
        self.server_config = server_config
        self.client: Optional[Client] = None
        self.is_connected = False
        self.tools: List[FastMCPTool] = []
    
    async def connect(self) -> bool:
        """Connect to the MCP server using FastMCP."""
        try:
            logger.info(f"Connecting to {self.server_name} via {self.server_config.get('command')}")
            
            # Create MCPConfig for this specific server
            # FastMCP expects the config in a specific format
            mcp_config_dict = {
                "mcpServers": {
                    self.server_name: self.server_config
                }
            }
            
            config = MCPConfig(**mcp_config_dict)
            self.client = Client(config)
            
            # Test connection by listing tools
            async with self.client:
                await self.load_tools()
                self.is_connected = True
            
            logger.info(f"✅ Connected to {self.server_name} ({len(self.tools)} tools)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to {self.server_name}: {e}")
            self.is_connected = False
            return False
    
    async def load_tools(self):
        """Load available tools from the server."""
        if not self.client:
            return
        
        try:
            async with self.client:
                mcp_tools = await self.client.list_tools()
                self.tools = [
                    FastMCPTool(
                        name=tool.name,
                        description=tool.description,
                        server_name=self.server_name,
                        inputSchema=tool.inputSchema
                    )
                    for tool in mcp_tools
                ]
                logger.debug(f"Loaded {len(self.tools)} tools from {self.server_name}")
        except Exception as e:
            logger.error(f"Failed to load tools from {self.server_name}: {e}")
            self.tools = []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on this server."""
        if not self.client:
            raise RuntimeError(f"Not connected to {self.server_name}")
        
        try:
            async with self.client:
                result = await self.client.call_tool(tool_name, arguments)
                # FastMCP's call_tool returns structured content
                if hasattr(result, 'content') and result.content:
                    # If it's a list of content blocks, join them
                    if isinstance(result.content, list):
                        return '\n'.join(str(block) for block in result.content)
                    return str(result.content)
                return str(result)
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} on {self.server_name}: {e}")
            raise

class FastMultiMCPClient:
    """Client that manages multiple MCP servers using FastMCP."""
    
    def __init__(self, config_path: str = "mcp_servers.json"):
        self.config_path = config_path
        self.clients: Dict[str, FastMCPServerClient] = {}
        self.all_tools: List[FastMCPTool] = []
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            self.config_data = {"mcpServers": {}}
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all configured servers."""
        connection_results = {}
        servers = self.config_data.get("mcpServers", {})
        
        for server_name, server_config in servers.items():
            client = FastMCPServerClient(server_name, server_config)
            self.clients[server_name] = client
            
            # Try to connect with timeout
            try:
                connection_results[server_name] = await asyncio.wait_for(
                    client.connect(), timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout connecting to {server_name}")
                connection_results[server_name] = False
            except Exception as e:
                logger.error(f"Unexpected error connecting to {server_name}: {e}")
                connection_results[server_name] = False
        
        # Aggregate all tools from successfully connected servers
        self.all_tools = []
        for client in self.clients.values():
            if client.is_connected:
                self.all_tools.extend(client.tools)
        
        connected_count = sum(connection_results.values())
        total_count = len(connection_results)
        logger.info(f"Connected to {connected_count}/{total_count} servers")
        
        return connection_results
    
    def get_all_tools(self) -> List[FastMCPTool]:
        """Get all tools from all connected servers."""
        return self.all_tools.copy()
    
    def find_tool(self, tool_name: str) -> Optional[Tuple[FastMCPTool, str]]:
        """Find a tool by name. Returns (tool, server_name) or None."""
        for tool in self.all_tools:
            if tool.name == tool_name:
                return tool, tool.server_name
        return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool by name. Automatically routes to the correct server."""
        tool_info = self.find_tool(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool, server_name = tool_info
        client = self.clients.get(server_name)
        
        if not client or not client.is_connected:
            raise RuntimeError(f"Server '{server_name}' not connected")
        
        return await client.call_tool(tool_name, arguments)
    
    def get_connected_servers(self) -> List[str]:
        """Get list of successfully connected server names."""
        return [name for name, client in self.clients.items() if client.is_connected]
    
    def get_connection_status(self) -> Dict[str, bool]:
        """Get connection status for all servers."""
        return {name: client.is_connected for name, client in self.clients.items()}

# Global FastMCP client instance
_fast_multi_client: Optional[FastMultiMCPClient] = None

def call_llm(prompt: str) -> str:
    """Call LLM with the given prompt."""
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"),
        base_url=os.environ.get("OPENAI_BASE_URL")
    )
    r = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

async def initialize_fastmcp_clients(config_path: str = "mcp_servers.json") -> FastMultiMCPClient:
    """Initialize and connect to all MCP servers using FastMCP."""
    global _fast_multi_client
    _fast_multi_client = FastMultiMCPClient(config_path)
    await _fast_multi_client.connect_all()
    return _fast_multi_client

async def get_all_fastmcp_tools() -> List[FastMCPTool]:
    """Get all available tools from all connected FastMCP servers."""
    if not _fast_multi_client:
        raise RuntimeError("FastMCP clients not initialized. Call initialize_fastmcp_clients() first.")
    return _fast_multi_client.get_all_tools()

async def call_fastmcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Call a FastMCP tool by name."""
    if not _fast_multi_client:
        raise RuntimeError("FastMCP clients not initialized. Call initialize_fastmcp_clients() first.")
    return await _fast_multi_client.call_tool(tool_name, arguments)

def get_fastmcp_client() -> Optional[FastMultiMCPClient]:
    """Get the global FastMCP client instance."""
    return _fast_multi_client

# Compatibility functions for the existing interface
def get_tools(server_path=None) -> List[Any]:
    """
    Compatibility function for the original interface using FastMCP.
    Returns tools in the format expected by the original code.
    """
    if not _fast_multi_client:
        return []
    
    tools = _fast_multi_client.get_all_tools()
    
    # Convert to the format expected by the original code
    class DictObject(dict):
        def __init__(self, data):
            super().__init__(data)
            for key, value in data.items():
                if isinstance(value, dict):
                    self[key] = DictObject(value)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    self[key] = [DictObject(item) for item in value]
        
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError:
                raise AttributeError(f"'DictObject' object has no attribute '{key}'")
    
    return [
        DictObject({
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        })
        for tool in tools
    ]

def call_tool(server_path=None, tool_name=None, arguments=None):
    """
    Compatibility function for the original interface using FastMCP.
    """
    if not _fast_multi_client:
        return f"Error: FastMCP clients not initialized"
    
    try:
        # For FastMCP, we need to run the async call
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, create a task
            # This is a common pattern for async compatibility
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, call_fastmcp_tool(tool_name, arguments))
                return future.result()
        else:
            return loop.run_until_complete(call_fastmcp_tool(tool_name, arguments))
    except Exception as e:
        return f"Error calling tool {tool_name}: {e}"

if __name__ == "__main__":
    # Test the FastMCP client
    async def test_fastmcp_client():
        logging.basicConfig(level=logging.INFO)
        
        try:
            # Initialize clients
            client = await initialize_fastmcp_clients()
            
            # Show connection status
            status = client.get_connection_status()
            print("=== FastMCP Connection Status ===")
            for server, connected in status.items():
                print(f"{server}: {'✅ Connected' if connected else '❌ Disconnected'}")
            
            # Show available tools
            tools = await get_all_fastmcp_tools()
            print(f"\n=== Available FastMCP Tools ({len(tools)} total) ===")
            for tool in tools:
                print(f"{tool.qualified_name}: {tool.description}")
            
            # Test a tool call if tools are available
            if tools:
                # Find a simple tool to test
                for tool in tools:
                    if 'fetch' in tool.name.lower():
                        print(f"\n=== Testing {tool.name} ===")
                        try:
                            result = await call_fastmcp_tool(tool.name, {"url": "https://example.com"})
                            print(f"Result: {result[:200]}...")
                        except Exception as e:
                            print(f"Test failed: {e}")
                        break
            
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test_fastmcp_client())