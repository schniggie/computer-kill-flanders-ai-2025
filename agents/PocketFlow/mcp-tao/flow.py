# flow.py

from pocketflow import AsyncFlow
from nodes import AsyncThinkNode, AsyncActionNode, AsyncObserveNode, AsyncEndNode

def create_universal_tao_flow():
    """
    Create a Universal Thought-Action-Observation loop flow with MCP integration
    
    This flow can work with any MCP servers and tools across any domain:
    - Web scraping and automation
    - File system operations
    - Database queries
    - API interactions
    - Research and analysis
    - Code generation and execution
    - And many more...
    
    How the flow works:
    1. AsyncThinkNode analyzes the problem and available tools to decide the next action
    2. AsyncActionNode executes the chosen action using MCP tools
    3. AsyncObserveNode observes and analyzes the action result
    4. Return to AsyncThinkNode to continue thinking, or end the flow
    
    Returns:
        AsyncFlow: Complete universal TAO loop flow
    """
    # Create async node instances
    think = AsyncThinkNode()
    action = AsyncActionNode()
    observe = AsyncObserveNode()
    end = AsyncEndNode()
    
    # Connect nodes
    # If ThinkNode returns "action", go to ActionNode
    think - "action" >> action
    
    # If ThinkNode returns "end", end the flow
    think - "end" >> end
    
    # After ActionNode completes, go to ObserveNode
    action - "observe" >> observe
    
    # After ObserveNode completes, return to ThinkNode
    observe - "think" >> think
    
    # Create and return async flow, starting from ThinkNode
    return AsyncFlow(start=think)