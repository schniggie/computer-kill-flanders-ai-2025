import json
import shutil
import os
from typing import Dict, Any

def detect_container_runtime() -> str:
    """Detect available container runtime (docker or podman)."""
    if shutil.which("docker"):
        return "docker"
    elif shutil.which("podman"):
        return "podman"
    else:
        return "docker"  # Default fallback

def create_auto_config(output_file: str = "mcp_servers_auto.json") -> Dict[str, Any]:
    """Create an MCP configuration that auto-detects available tools."""
    
    container_cmd = detect_container_runtime()
    
    config = {
        "mcpServers": {
            "fetch": {
                "type": "stdio",
                "command": "uvx",
                "args": ["mcp-server-fetch"]
            },
            "playwright": {
                "type": "stdio",
                "command": container_cmd,
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "mcp/playwright"
                ]
            },
            "sequential-thinking": {
                "type": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-sequential-thinking"
                ]
            }
        }
    }
    
    # Write the configuration file
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Auto-generated configuration saved to {output_file}")
    print(f"🐳 Container runtime detected: {container_cmd}")
    
    # Show what tools are available
    print("\n🔍 Tool availability check:")
    tools = {
        "uvx": "fetch server",
        container_cmd: "playwright server", 
        "npx": "sequential-thinking server",
        "node": "npx dependency"
    }
    
    for tool, description in tools.items():
        available = "✅" if shutil.which(tool) else "❌"
        print(f"  {available} {tool} - {description}")
    
    return config

def suggest_installation_commands():
    """Suggest installation commands for missing tools."""
    print("\n💡 Installation suggestions for missing tools:")
    
    if not shutil.which("docker") and not shutil.which("podman"):
        print("  Container runtime:")
        print("    - Docker: https://docs.docker.com/get-docker/")
        print("    - Podman: https://podman.io/getting-started/installation")
    
    if not shutil.which("uvx"):
        print("  UV (for uvx):")
        print("    - curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("    - pip install uv")
    
    if not shutil.which("npx"):
        print("  Node.js (for npx):")
        print("    - https://nodejs.org/en/download/")
        print("    - brew install node  # macOS")
        print("    - apt install nodejs npm  # Ubuntu")

if __name__ == "__main__":
    print("🚀 Auto-detecting MCP server configuration...")
    
    try:
        config = create_auto_config()
        suggest_installation_commands()
        
        print("\n🎯 To use this configuration:")
        print("  python main_fastmcp.py  # Uses mcp_servers.json by default")
        print("  # OR")
        print("  # Rename mcp_servers_auto.json to mcp_servers.json")
        
    except Exception as e:
        print(f"❌ Error creating auto-config: {e}")