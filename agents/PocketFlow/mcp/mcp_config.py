import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str
    type: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.type != "stdio":
            raise ValueError(f"Unsupported server type: {self.type}")
        
        if not self.command:
            raise ValueError("Command is required for stdio servers")

class MCPConfigManager:
    """Manager for parsing and handling MCP server configurations."""
    
    def __init__(self, config_path: str = "mcp_servers.json"):
        """Initialize with path to MCP servers configuration file."""
        self.config_path = config_path
        self.servers: Dict[str, MCPServerConfig] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load MCP server configuration from JSON file."""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Configuration file {self.config_path} not found")
                return
            
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            if "mcpServers" not in config_data:
                raise ValueError("Invalid configuration format: missing 'mcpServers' key")
            
            for server_name, server_config in config_data["mcpServers"].items():
                try:
                    self.servers[server_name] = MCPServerConfig(
                        name=server_name,
                        type=server_config.get("type", "stdio"),
                        command=server_config.get("command", ""),
                        args=server_config.get("args", []),
                        env=server_config.get("env")
                    )
                    logger.info(f"Loaded MCP server config: {server_name}")
                except Exception as e:
                    logger.error(f"Failed to load server config for {server_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load MCP configuration from {self.config_path}: {e}")
            raise
    
    def get_server_config(self, server_name: str) -> Optional[MCPServerConfig]:
        """Get configuration for a specific server."""
        return self.servers.get(server_name)
    
    def get_all_servers(self) -> Dict[str, MCPServerConfig]:
        """Get all server configurations."""
        return self.servers.copy()
    
    def get_server_names(self) -> List[str]:
        """Get list of all configured server names."""
        return list(self.servers.keys())
    
    def is_server_configured(self, server_name: str) -> bool:
        """Check if a server is configured."""
        return server_name in self.servers
    
    def validate_server_requirements(self) -> Dict[str, List[str]]:
        """
        Validate that required commands are available for each server.
        Returns a dict of server_name -> list of missing requirements.
        """
        missing_requirements = {}
        
        for server_name, config in self.servers.items():
            missing = []
            
            # Check if command exists in PATH
            import shutil
            if not shutil.which(config.command):
                missing.append(f"Command '{config.command}' not found in PATH")
            
            # Server-specific requirement checks
            if config.command == "npx":
                if not shutil.which("node"):
                    missing.append("Node.js not installed (required for npx)")
            elif config.command == "uvx":
                if not shutil.which("uv"):
                    missing.append("uv not installed (required for uvx)")
            elif config.command in ["podman", "docker"]:
                # Check for either podman or docker
                has_podman = shutil.which("podman")
                has_docker = shutil.which("docker")
                if config.command == "podman" and not has_podman:
                    if has_docker:
                        missing.append(f"Podman not found, but docker is available. Consider changing command to 'docker'")
                    else:
                        missing.append("Podman not installed")
                elif config.command == "docker" and not has_docker:
                    if has_podman:
                        missing.append(f"Docker not found, but podman is available. Consider changing command to 'podman'")
                    else:
                        missing.append("Docker not installed")
            
            if missing:
                missing_requirements[server_name] = missing
        
        return missing_requirements

def load_mcp_config(config_path: str = "mcp_servers.json") -> MCPConfigManager:
    """Convenience function to load MCP configuration."""
    return MCPConfigManager(config_path)

if __name__ == "__main__":
    # Test the configuration manager
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        config_manager = MCPConfigManager()
        
        print("=== MCP Server Configuration ===")
        servers = config_manager.get_all_servers()
        
        if not servers:
            print("No servers configured")
            sys.exit(1)
        
        for name, config in servers.items():
            print(f"\nServer: {name}")
            print(f"  Type: {config.type}")
            print(f"  Command: {config.command}")
            print(f"  Args: {config.args}")
            if config.env:
                print(f"  Environment: {config.env}")
        
        print("\n=== Requirement Check ===")
        missing = config_manager.validate_server_requirements()
        
        if not missing:
            print("✅ All server requirements are satisfied")
        else:
            print("❌ Missing requirements found:")
            for server, requirements in missing.items():
                print(f"  {server}:")
                for req in requirements:
                    print(f"    - {req}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)