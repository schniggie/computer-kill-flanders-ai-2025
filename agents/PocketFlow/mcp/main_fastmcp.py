from pocketflow import Node, Flow, AsyncNode, AsyncFlow
from utils_fastmcp import call_llm, initialize_fastmcp_clients, get_all_fastmcp_tools, call_fastmcp_tool, get_fastmcp_client
import yaml
import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InitializeFastMCPNode(AsyncNode):
    """Initialize connections to all MCP servers using FastMCP."""
    
    async def prep_async(self, shared):
        """Prepare for FastMCP initialization"""
        print("🔌 Initializing FastMCP server connections...")
        return "mcp_servers.json"
    
    async def exec_async(self, config_path):
        """Connect to all MCP servers using FastMCP"""
        try:
            multi_client = await initialize_fastmcp_clients(config_path)
            return multi_client
        except Exception as e:
            logger.error(f"Failed to initialize FastMCP clients: {e}")
            raise
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store connection status and proceed"""
        multi_client = exec_res
        status = multi_client.get_connection_status()
        shared["fastmcp_client"] = multi_client
        shared["connection_status"] = status
        
        # Log connection results
        connected = [name for name, connected in status.items() if connected]
        failed = [name for name, connected in status.items() if not connected]
        
        if connected:
            print(f"✅ Connected to: {', '.join(connected)}")
        if failed:
            print(f"❌ Failed to connect to: {', '.join(failed)}")
        
        if not connected:
            print("⚠️  No MCP servers connected. The agent will have limited functionality.")
        
        return "get_tools"

class GetFastMCPToolsNode(AsyncNode):
    """Get available tools from all connected FastMCP servers."""
    
    async def prep_async(self, shared):
        """Check if we have any connected servers"""
        multi_client = shared.get("fastmcp_client")
        if not multi_client:
            raise RuntimeError("FastMCP client not initialized")
        
        connected_servers = multi_client.get_connected_servers()
        print(f"🔍 Getting tools from {len(connected_servers)} connected servers...")
        return multi_client
    
    async def exec_async(self, multi_client):
        """Retrieve tools from all connected FastMCP servers"""
        try:
            tools = await get_all_fastmcp_tools()
            return tools
        except Exception as e:
            logger.error(f"Failed to get tools: {e}")
            return []
    
    async def post_async(self, shared, prep_res, exec_res):
        """Store tools and format for decision making"""
        tools = exec_res
        shared["tools"] = tools
        
        if not tools:
            print("⚠️  No tools available from connected servers")
            return "no_tools"
        
        # Format tool information for LLM
        tool_info = []
        for i, tool in enumerate(tools, 1):
            properties = tool.inputSchema.get('properties', {})
            required = tool.inputSchema.get('required', [])
            
            params = []
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'unknown')
                req_status = "(Required)" if param_name in required else "(Optional)"
                params.append(f"    - {param_name} ({param_type}): {req_status}")
            
            server_info = f" [Server: {tool.server_name}]"
            tool_info.append(
                f"[{i}] {tool.name}{server_info}\n"
                f"  Description: {tool.description}\n"
                f"  Parameters:\n" + "\n".join(params)
            )
        
        shared["tool_info"] = "\n".join(tool_info)
        print(f"📋 Found {len(tools)} tools across all servers")
        return "decide"

class DecideFastMCPToolNode(AsyncNode):
    """Use LLM to analyze the question and decide which FastMCP tool to use."""
    
    async def prep_async(self, shared):
        """Prepare the prompt for LLM decision making"""
        tool_info = shared.get("tool_info", "No tools available")
        question = shared["question"]
        
        # Get server status for context
        connection_status = shared.get("connection_status", {})
        connected_servers = [name for name, status in connection_status.items() if status]
        
        prompt = f"""
### CONTEXT
You are an AI assistant that can use tools via Model Context Protocol (MCP) with FastMCP.
Connected MCP servers: {', '.join(connected_servers) if connected_servers else 'None'}

### AVAILABLE TOOLS
{tool_info}

### TASK
Answer this question: "{question}"

### INSTRUCTIONS
1. Analyze the question carefully
2. Extract any numbers, URLs, or specific parameters needed
3. Choose the most appropriate tool from the available options
4. Consider which server the tool comes from (shown in brackets)
5. If no suitable tool is available, explain what you would need

### RESPONSE FORMAT
Return your response in this YAML format:

```yaml
thinking: |
    <your step-by-step reasoning about what the question asks and which tool to use>
action: <"use_tool" or "no_suitable_tool">
tool_name: <name of the tool to use (if action is use_tool)>
server_name: <name of the server hosting the tool>
reason: <why you chose this tool or why no tool is suitable>
parameters:
    <parameter_name>: <parameter_value>
    <parameter_name>: <parameter_value>
```

IMPORTANT: 
- Extract numbers and parameters accurately from the question
- Use proper YAML indentation (2 spaces)
- Use the | character for multi-line text fields
- Only use tools that are actually available in the list above
"""
        return prompt
    
    async def exec_async(self, prompt):
        """Call LLM to process the question and decide action"""
        print("🤔 Analyzing question and selecting appropriate tool...")
        try:
            response = call_llm(prompt)
            return response
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    async def post_async(self, shared, prep_res, exec_res):
        """Parse LLM response and determine next action"""
        try:
            yaml_str = exec_res.split("```yaml")[1].split("```")[0].strip()
            decision = yaml.safe_load(yaml_str)
            
            action = decision.get("action", "").lower()
            
            if action == "use_tool":
                shared["tool_name"] = decision.get("tool_name")
                shared["server_name"] = decision.get("server_name")
                shared["parameters"] = decision.get("parameters", {})
                shared["thinking"] = decision.get("thinking", "")
                shared["reason"] = decision.get("reason", "")
                
                print(f"💡 Selected tool: {shared['tool_name']} from {shared['server_name']}")
                print(f"🔢 Parameters: {shared['parameters']}")
                
                return "execute"
            else:
                print(f"❌ No suitable tool found: {decision.get('reason', 'Unknown reason')}")
                shared["no_tool_reason"] = decision.get("reason", "No suitable tool available")
                return "no_tool"
                
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
            print("Raw response:", exec_res)
            logger.error(f"Failed to parse LLM response: {e}")
            return "error"

class ExecuteFastMCPToolNode(AsyncNode):
    """Execute the chosen tool on the appropriate FastMCP server."""
    
    async def prep_async(self, shared):
        """Prepare tool execution parameters"""
        tool_name = shared.get("tool_name")
        parameters = shared.get("parameters", {})
        server_name = shared.get("server_name")
        
        if not tool_name:
            raise ValueError("No tool specified for execution")
        
        return tool_name, parameters, server_name
    
    async def exec_async(self, inputs):
        """Execute the chosen tool using FastMCP"""
        tool_name, parameters, server_name = inputs
        print(f"🔧 Executing '{tool_name}' on {server_name} with parameters: {parameters}")
        
        try:
            result = await call_fastmcp_tool(tool_name, parameters)
            return result
        except Exception as e:
            logger.error(f"FastMCP tool execution failed: {e}")
            raise
    
    async def post_async(self, shared, prep_res, exec_res):
        """Present the final result"""
        print(f"\n✅ Result: {exec_res}")
        shared["result"] = exec_res
        return "success"

class NoToolNode(Node):
    """Handle cases where no suitable tool is available."""
    
    def exec(self, prep_res):
        """Provide fallback response when no tool is suitable"""
        return "I don't have a suitable tool to answer this question with the currently connected MCP servers."
    
    def post(self, shared, prep_res, exec_res):
        reason = shared.get("no_tool_reason", "No suitable tool found")
        print(f"\n❌ {exec_res}")
        print(f"💭 Reason: {reason}")
        
        # Suggest what might help
        connection_status = shared.get("connection_status", {})
        failed_servers = [name for name, status in connection_status.items() if not status]
        
        if failed_servers:
            print(f"💡 Tip: Some servers failed to connect: {', '.join(failed_servers)}")
            print("   Check if the required commands are installed and accessible.")
        
        return "done"

class EndNode(Node):
    """Final node to end the flow properly."""
    
    def exec(self, prep_res):
        """End the flow"""
        return "Completed"
    
    def post(self, shared, prep_res, exec_res):
        """Final completion"""
        return None

async def run_fastmcp_agent(question: str):
    """Run the FastMCP agent with the given question."""
    
    # Create nodes
    init_node = InitializeFastMCPNode()
    get_tools_node = GetFastMCPToolsNode()
    decide_node = DecideFastMCPToolNode()
    execute_node = ExecuteFastMCPToolNode()
    no_tool_node = NoToolNode()
    end_node = EndNode()
    
    # Connect the flow
    init_node - "get_tools" >> get_tools_node
    get_tools_node - "decide" >> decide_node
    get_tools_node - "no_tools" >> no_tool_node
    decide_node - "execute" >> execute_node
    decide_node - "no_tool" >> no_tool_node
    decide_node - "error" >> no_tool_node
    execute_node - "success" >> end_node
    no_tool_node - "done" >> end_node
    
    # Create and run the async flow
    flow = AsyncFlow(start=init_node)
    shared = {"question": question}
    
    try:
        await flow.run_async(shared)
        print("🎉 FastMCP Agent completed successfully!")
    except Exception as e:
        logger.error(f"Flow execution failed: {e}")
        print(f"❌ Error during execution: {e}")

def main():
    """Main entry point."""
    # Default question for testing
    default_question = "Can you help me search for information about AI safety research?"
    
    # Get question from command line if provided
    question = default_question
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("--"):
            question = sys.argv[1][2:]
        else:
            question = " ".join(sys.argv[1:])
    
    print("🚀 FastMCP Multi-Server Agent Starting")
    print(f"❓ Question: {question}")
    print("-" * 50)
    
    # Run the async agent
    try:
        asyncio.run(run_fastmcp_agent(question))
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()