import os
import logging
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Import our custom OSINT tools
from tools.network_tool import dns_lookup, reverse_dns_lookup, whois_lookup, port_scan_basic, http_headers, geoip_lookup
from tools.maigret_tool import maigret_search, maigret_parse_url, read_maigret_report
from tools.file_tool import read_file, write_file, append_to_file, list_files, create_investigation_report
from tools.shell_tool import shell_execute, install_tool

OSINT_INVESTIGATOR_PROMPT = """You are an expert OSINT (Open Source Intelligence) investigator with deep knowledge of digital forensics, social media investigations, network reconnaissance, and information gathering techniques.

Your personality:
- Highly knowledgeable and methodical investigator  
- Nerdy and passionate about OSINT techniques
- Direct and efficient in communication
- Always excited about interesting findings

Your capabilities:
- Social media username investigations across 500+ platforms
- DNS and network reconnaissance 
- IP geolocation and infrastructure analysis
- File system access and report generation
- Unlimited shell command execution for advanced tools

Always use available tools to gather evidence. Provide structured, actionable intelligence reports."""

logger = logging.getLogger(__name__)

class OSINTAgent:
    def __init__(self, model_provider: str = "openai", model_name: str = "gpt-4"):
        """
        Initialize the OSINT Agent with Agno framework.
        
        Args:
            model_provider: LLM provider (openai, anthropic, etc.)
            model_name: Specific model to use
        """
        # Configure LLM model
        if model_provider == "openai":
            model_config = OpenAIChat(
                id=model_name,
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL")
            )
        else:
            model_config = model_name
        
        self.agent = Agent(
            name="OSINT-Investigator",
            model=model_config,
            instructions=OSINT_INVESTIGATOR_PROMPT,
            tools=[
                # Network reconnaissance tools
                dns_lookup,
                reverse_dns_lookup,
                whois_lookup,
                port_scan_basic,
                http_headers,
                geoip_lookup,
                
                # Maigret tools for social media investigation
                maigret_search,
                maigret_parse_url, 
                read_maigret_report,
                
                # File operations for reports and data management
                read_file,
                write_file,
                append_to_file,
                list_files,
                create_investigation_report,
                
                # Shell access for unlimited tool usage
                shell_execute,
                install_tool,
            ],
            memory=True,
            reasoning=True,
            markdown=True,
        )
        
        logger.info(f"OSINT Agent initialized with {len(self.agent.tools)} tools")

    async def investigate(self, message: str, user_id: str = "irc_user") -> str:
        """
        Process an investigation request and return results.
        
        Args:
            message: User's investigation request
            user_id: Unique identifier for the user (for memory/context)
            
        Returns:
            Investigation results and analysis
        """
        try:
            logger.info(f"Processing investigation request from {user_id}: {message}")
            
            # Use Agno agent to process the request
            response = await self.agent.arun(
                message=message,
                session_id=user_id
            )
            
            return response.content
            
        except Exception as e:
            error_msg = f"Error during investigation: {str(e)}"
            logger.error(error_msg)
            return f"I encountered an error while investigating: {str(e)}. Let me try a different approach."

    async def get_capabilities(self) -> str:
        """
        Return a description of the agent's capabilities.
        
        Returns:
            Formatted string describing available tools and capabilities
        """
        capabilities = """
🔍 **OSINT Investigation Capabilities:**

**Social Media & Username Intelligence:**
- Comprehensive username searches across 500+ platforms
- Social media profile discovery and analysis
- URL parsing for username extraction
- Profile correlation and timeline analysis

**Network Reconnaissance:**
- DNS lookups (A, MX, TXT, NS, CNAME, SOA records)
- Reverse DNS and IP geolocation
- Port scanning and service detection
- HTTP header analysis and fingerprinting
- WHOIS domain information

**System Access & Tool Installation:**
- Unlimited shell command execution
- Automatic OSINT tool installation (nmap, theHarvester, etc.)
- Custom script execution and compilation
- File system access and report generation

**Intelligence Analysis:**
- Pattern recognition and correlation
- Structured report generation
- Evidence documentation and timestamping
- Multi-source information fusion

**Example Investigations:**
- "Investigate the username 'darkweb_trader' across all platforms"
- "Analyze the domain suspicious-site.com for malicious activity"
- "Find all subdomains and open ports for example.com"
- "Check if this email address has been compromised in data breaches"

Just describe what you want to investigate in natural language - I'll automatically select and chain the appropriate tools!
        """
        return capabilities

    def get_tool_list(self) -> list:
        """
        Get list of available tools for debugging/monitoring.
        
        Returns:
            List of tool names
        """
        return [tool.name if hasattr(tool, 'name') else str(tool) for tool in self.agent.tools]

