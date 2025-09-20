# nodes.py

import json
import logging
from typing import Dict, Any, Optional
import yaml
from pocketflow import AsyncNode
from utils_fastmcp import FastMultiMCPClient, call_llm

logger = logging.getLogger(__name__)

class AsyncThinkNode(AsyncNode):
    """
    Universal TAO Think Node
    
    Analyzes the problem/query and available tools to decide the next action.
    Can work with any MCP servers and tools across any domain.
    """
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the context needed for thinking"""
        try:
            print("🔧 Preparing AsyncThinkNode...")
            query = shared.get("query", "")
            observations = shared.get("observations", [])
            thoughts = shared.get("thoughts", [])
            current_thought_number = shared.get("current_thought_number", 0)
            available_tools = shared.get("available_tools", {})
            
            # Update thought count
            shared["current_thought_number"] = current_thought_number + 1
            
            # Format previous observations
            observations_text = "\n".join([f"Observation {i+1}: {obs}" for i, obs in enumerate(observations)])
            if not observations_text:
                observations_text = "No observations yet."
            
            # Format available tools
            tools_text = self._format_available_tools(available_tools)
            
            prep_result = {
                "query": query,
                "observations_text": observations_text,
                "thoughts": thoughts,
                "current_thought_number": current_thought_number + 1,
                "tools_text": tools_text,
                "available_tools": available_tools
            }
            
            print(f"🔧 Prepared for thought {current_thought_number + 1}")
            return prep_result
        except Exception as e:
            logger.error(f"Error in AsyncThinkNode.prep_async: {e}")
            # Return minimal prep result
            return {
                "query": shared.get("query", ""),
                "observations_text": "No observations yet.",
                "thoughts": [],
                "current_thought_number": 1,
                "tools_text": "No tools available.",
                "available_tools": {}
            }
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the thinking process, decide the next action"""
        try:
            query = prep_res["query"]
            observations_text = prep_res["observations_text"]
            current_thought_number = prep_res["current_thought_number"]
            tools_text = prep_res["tools_text"]
            
            print(f"🧠 Starting thought {current_thought_number}...")
            
            # Build the prompt
            prompt = f"""
You are an AI assistant solving a problem using available tools. Based on the user's query and previous observations, think about what action to take next.

User query: {query}

Previous observations:
{observations_text}

Available tools:
{tools_text}

Please think about the next action and return your thinking process and decision in YAML format:
```yaml
thinking: |
    <detailed thinking process about what needs to be done>
action: <exact tool name from available tools, or 'answer' if ready to provide final answer>
action_input: <input parameters for the tool, or final answer text if action is 'answer'>
is_final: <set to true if this is the final answer, otherwise false>
```

Important guidelines:
- Use the exact tool name from the available tools list
- If no suitable tool is available, set action to "answer" and provide the best response you can
- Only set is_final to true when you have a complete answer to the user's query
- Think step by step about what information you need and which tool can provide it
"""
            
            # Call LLM to get thinking result
            response = call_llm(prompt)
            
            # Parse YAML response
            try:
                yaml_str = response.split("```yaml")[1].split("```")[0].strip()
                thought_data = yaml.safe_load(yaml_str)
            except (IndexError, yaml.YAMLError) as e:
                logger.error(f"Failed to parse YAML response: {e}")
                # Fallback to simple answer
                thought_data = {
                    "thinking": "Failed to parse LLM response, providing fallback answer",
                    "action": "answer",
                    "action_input": response,
                    "is_final": True
                }
            
            # Add thought number
            thought_data["thought_number"] = current_thought_number
            
            return thought_data
        except Exception as e:
            logger.error(f"Error in AsyncThinkNode.exec_async: {e}")
            # Return a safe fallback
            return {
                "thinking": f"Error occurred during thinking: {str(e)}",
                "action": "answer",
                "action_input": f"I encountered an error while processing your request: {str(e)}",
                "is_final": True,
                "thought_number": prep_res.get("current_thought_number", 1)
            }
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Save the thinking result and decide the next step in the flow"""
        try:
            # Save thinking result
            if "thoughts" not in shared:
                shared["thoughts"] = []
            shared["thoughts"].append(exec_res)
            
            # Save action information
            shared["current_action"] = exec_res["action"]
            shared["current_action_input"] = exec_res["action_input"]
            
            # If it's the final answer, end the flow
            if exec_res.get("is_final", False):
                shared["final_answer"] = exec_res["action_input"]
                print(f"🎯 Final Answer: {exec_res['action_input']}")
                return "end"
            
            # Otherwise continue with the action
            print(f"🤔 Thought {exec_res['thought_number']}: Decided to execute {exec_res['action']}")
            return "action"
        except Exception as e:
            logger.error(f"Error in AsyncThinkNode.post_async: {e}")
            # Return a safe fallback
            shared["final_answer"] = "Error occurred during thinking"
            return "end"
    
    def _format_available_tools(self, available_tools: Dict[str, Any]) -> str:
        """Format available tools for the prompt"""
        if not available_tools:
            return "No tools available."
        
        tools_list = []
        for server_name, tools in available_tools.items():
            if tools:
                tools_list.append(f"\nFrom {server_name} server:")
                for tool in tools:
                    name = tool.get("name", "unknown")
                    description = tool.get("description", "No description available")
                    tools_list.append(f"  - {name}: {description}")
        
        return "\n".join(tools_list) if tools_list else "No tools available."

class AsyncActionNode(AsyncNode):
    """
    Universal TAO Action Node
    
    Executes actions using available MCP tools.
    Handles any tool from any MCP server across any domain.
    """
    
    async def prep_async(self, shared: Dict[str, Any]) -> tuple:
        """Prepare to execute action"""
        action = shared["current_action"]
        action_input = shared["current_action_input"]
        mcp_client = shared.get("mcp_client")
        available_tools = shared.get("available_tools", {})
        return action, action_input, mcp_client, available_tools
    
    async def exec_async(self, inputs: tuple) -> str:
        """Execute action and return result"""
        action, action_input, mcp_client, available_tools = inputs
        
        print(f"🚀 Executing action: {action}, input: {action_input}")
        
        # If action is "answer", return the input directly
        if action == "answer":
            return action_input
        
        # Find the tool in available tools
        tool_info = self._find_tool(action, available_tools)
        if not tool_info:
            return f"Tool '{action}' not found in available tools"
        
        server_name, tool_schema = tool_info
        
        # Execute the tool via MCP client
        try:
            if not mcp_client:
                return "MCP client not available"
            
            result = await mcp_client.call_tool(action, self._prepare_tool_params(action_input, tool_schema))
            return str(result)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return f"Tool execution failed: {str(e)}"
    
    async def post_async(self, shared: Dict[str, Any], prep_res: tuple, exec_res: str) -> str:
        """Save action result"""
        # Save the current action result
        shared["current_action_result"] = exec_res
        print(f"✅ Action completed, result obtained")
        
        # Continue to observation node
        return "observe"
    
    def _find_tool(self, tool_name: str, available_tools: Dict[str, Any]) -> Optional[tuple]:
        """Find tool schema in available tools"""
        for server_name, tools in available_tools.items():
            for tool in tools:
                if tool.get("name") == tool_name:
                    return server_name, tool
        return None
    
    def _prepare_tool_params(self, action_input: Any, tool_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tool parameters based on input and schema"""
        # If action_input is already a dict, use it directly
        if isinstance(action_input, dict):
            return action_input
        
        # If action_input is a string, try to parse as JSON
        if isinstance(action_input, str):
            try:
                parsed = json.loads(action_input)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # If tool expects a single parameter, map the string to it
            input_schema = tool_schema.get("inputSchema", {})
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])
            
            # If there's only one required parameter, use the string for it
            if len(required) == 1:
                return {required[0]: action_input}
            
            # Otherwise, look for common parameter names
            common_params = ["query", "text", "input", "prompt", "message", "url"]
            for param in common_params:
                if param in properties:
                    return {param: action_input}
        
        # Fallback: return as-is or empty dict
        return action_input if isinstance(action_input, dict) else {}

class AsyncObserveNode(AsyncNode):
    """
    Universal TAO Observe Node
    
    Analyzes action results and generates observations.
    Works with results from any MCP tool across any domain.
    """
    
    async def prep_async(self, shared: Dict[str, Any]) -> tuple:
        """Prepare observation data"""
        action = shared["current_action"]
        action_input = shared["current_action_input"]
        action_result = shared["current_action_result"]
        return action, action_input, action_result
    
    async def exec_async(self, inputs: tuple) -> str:
        """Analyze action results, generate observation"""
        action, action_input, action_result = inputs
        
        # Build prompt
        prompt = f"""
You are an observer, needing to analyze action results and provide objective observations.

Action: {action}
Action input: {action_input}
Action result: {action_result}

Please provide a concise observation of this result. Focus on:
- What information was obtained
- Whether the action was successful
- Key insights or data points
- Any limitations or issues

Don't make decisions or suggest next steps, just describe what you observe.
"""
        
        # Call LLM to get observation result
        observation = call_llm(prompt)
        
        print(f"👁️ Observation: {observation[:50]}...")
        return observation
    
    async def post_async(self, shared: Dict[str, Any], prep_res: tuple, exec_res: str) -> str:
        """Save observation result and decide next flow step"""
        # Save observation result
        if "observations" not in shared:
            shared["observations"] = []
        shared["observations"].append(exec_res)
        
        # Continue thinking
        return "think"

class AsyncEndNode(AsyncNode):
    """
    Universal TAO End Node
    
    Properly terminates the flow.
    """
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare end node"""
        return {}
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> None:
        """Execute end operation"""
        print("🏁 TAO flow completed successfully!")
        return None
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: None):
        """End flow"""
        return None