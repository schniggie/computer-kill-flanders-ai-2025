from openai import OpenAI
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_config import MCPConfigManager, MCPServerConfig

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """Represents a tool from an MCP server."""
    name: str
    description: str
    server_name: str
    inputSchema: Dict[str, Any]
    
    @property
    def qualified_name(self) -> str:
        """Get fully qualified tool name including server."""
        return f"{self.server_name}.{self.name}"

class MCPServerClient:
    """Client for a single MCP server."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.stdio_context = None
        self.is_connected = False
        self.tools: List[MCPTool] = []
    
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            server_params = StdioServerParameters(
                command=self.config.command,
                args=self.config.args,
                env=self.config.env or {}
            )
            
            logger.info(f"Connecting to {self.config.name} via {self.config.command}")
            
            # Start the server process using proper context management
            self.stdio_context = stdio_client(server_params)
            read, write = await self.stdio_context.__aenter__()
            
            self.session = ClientSession(read, write)
            await self.session.__aenter__()
            
            # Initialize the session
            await self.session.initialize()
            self.is_connected = True
            
            # Load available tools
            await self.load_tools()
            
            logger.info(f"✅ Connected to {self.config.name} ({len(self.tools)} tools)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to {self.config.name}: {e}")
            self.is_connected = False
            await self._cleanup_failed_connection()
            return False
    
    async def _cleanup_failed_connection(self):
        """Clean up resources after a failed connection."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None
        except Exception as e:
            logger.debug(f"Error during failed connection cleanup for {self.config.name}: {e}")
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None
            self.is_connected = False
            logger.info(f"Disconnected from {self.config.name}")
        except Exception as e:
            logger.error(f"Error disconnecting from {self.config.name}: {e}")
    
    async def load_tools(self):
        """Load available tools from the server."""
        if not self.session or not self.is_connected:
            return
        
        try:
            tools_response = await self.session.list_tools()
            self.tools = [
                MCPTool(
                    name=tool.name,
                    description=tool.description,
                    server_name=self.config.name,
                    inputSchema=tool.inputSchema
                )
                for tool in tools_response.tools
            ]
            logger.debug(f"Loaded {len(self.tools)} tools from {self.config.name}")
        except Exception as e:
            logger.error(f"Failed to load tools from {self.config.name}: {e}")
            self.tools = []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on this server."""
        if not self.session or not self.is_connected:
            raise RuntimeError(f"Not connected to {self.config.name}")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result.content[0].text if result.content else None
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} on {self.config.name}: {e}")
            raise

class MultiMCPClient:
    """Client that manages multiple MCP servers."""
    
    def __init__(self, config_path: str = "mcp_servers.json"):
        self.config_manager = MCPConfigManager(config_path)
        self.clients: Dict[str, MCPServerClient] = {}
        self.all_tools: List[MCPTool] = []
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all configured servers. Returns connection status for each."""
        connection_results = {}
        
        for server_name, config in self.config_manager.get_all_servers().items():
            client = MCPServerClient(config)
            self.clients[server_name] = client
            
            # Try to connect with timeout and error handling
            try:
                # Add a timeout to prevent hanging on problematic servers
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
    
    async def disconnect_all(self):
        """Disconnect from all servers."""
        disconnect_tasks = []
        for client in self.clients.values():
            if client.is_connected:
                disconnect_tasks.append(client.disconnect())
        
        if disconnect_tasks:
            # Wait for all disconnections to complete
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        self.clients.clear()
        self.all_tools.clear()
    
    def get_all_tools(self) -> List[MCPTool]:
        """Get all tools from all connected servers."""
        return self.all_tools.copy()
    
    def get_server_tools(self, server_name: str) -> List[MCPTool]:
        """Get tools from a specific server."""
        client = self.clients.get(server_name)
        return client.tools.copy() if client and client.is_connected else []
    
    def find_tool(self, tool_name: str) -> Optional[Tuple[MCPTool, str]]:
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

# Global multi-MCP client instance
_multi_client: Optional[MultiMCPClient] = None

def call_llm(prompt: str) -> str:
    """Call LLM with the given prompt."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

async def initialize_mcp_clients(config_path: str = "mcp_servers.json") -> MultiMCPClient:
    """Initialize and connect to all MCP servers."""
    global _multi_client
    _multi_client = MultiMCPClient(config_path)
    await _multi_client.connect_all()
    return _multi_client

async def get_all_tools() -> List[MCPTool]:
    """Get all available tools from all connected MCP servers."""
    if not _multi_client:
        raise RuntimeError("MCP clients not initialized. Call initialize_mcp_clients() first.")
    return _multi_client.get_all_tools()

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Call an MCP tool by name."""
    if not _multi_client:
        raise RuntimeError("MCP clients not initialized. Call initialize_mcp_clients() first.")
    return await _multi_client.call_tool(tool_name, arguments)

async def cleanup_mcp_clients():
    """Cleanup and disconnect all MCP clients."""
    global _multi_client
    if _multi_client:
        await _multi_client.disconnect_all()
        _multi_client = None

def get_mcp_client() -> Optional[MultiMCPClient]:
    """Get the global MCP client instance."""
    return _multi_client

# Compatibility functions for the existing interface
def get_tools(server_path=None) -> List[Any]:
    """
    Compatibility function for the original interface.
    Returns tools in the format expected by the original code.
    """
    if not _multi_client:
        # Return empty list if no clients initialized
        return []
    
    tools = _multi_client.get_all_tools()
    
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
    Compatibility function for the original interface.
    This function bridges the sync/async gap by running the async version.
    """
    if not _multi_client:
        return f"Error: MCP clients not initialized"
    
    try:
        # Run the async call_mcp_tool in the event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, we need to handle this differently
            # For now, we'll return an error message
            return f"Error: Cannot run async operation in existing event loop"
        else:
            return loop.run_until_complete(call_mcp_tool(tool_name, arguments))
    except Exception as e:
        return f"Error calling tool {tool_name}: {e}"

if __name__ == "__main__":
    # Test the multi-MCP client
    async def test_client():
        logging.basicConfig(level=logging.INFO)
        
        try:
            # Initialize clients
            client = await initialize_mcp_clients()
            
            # Show connection status
            status = client.get_connection_status()
            print("=== Connection Status ===")
            for server, connected in status.items():
                print(f"{server}: {'✅ Connected' if connected else '❌ Disconnected'}")
            
            # Show available tools
            tools = await get_all_tools()
            print(f"\n=== Available Tools ({len(tools)} total) ===")
            for tool in tools:
                print(f"{tool.qualified_name}: {tool.description}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await cleanup_mcp_clients()
    
    asyncio.run(test_client())
