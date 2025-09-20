#!/usr/bin/env python3
"""
OSINT IRC Agent - Main Entry Point

An autonomous OSINT investigation agent that connects to IRC and conducts
intelligent investigations through natural conversation using the Agno framework.
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from irc_client import OSINTIRCBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/workspace/osint_agent.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Load environment variables and validate configuration."""
    
    # Load .env file if present
    load_dotenv()
    
    # Required environment variables
    required_vars = {
        'IRC_SERVER': os.getenv('IRC_SERVER', 'irc.libera.chat'),
        'IRC_CHANNELS': os.getenv('IRC_CHANNELS', '#osint-test'),
        'IRC_NICK': os.getenv('IRC_NICK', 'OSINT-Agent'),
        'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'openai'),
        'LLM_MODEL': os.getenv('LLM_MODEL', 'gpt-4'),
    }
    
    # Log configuration
    logger.info("=== OSINT IRC Agent Configuration ===")
    for key, value in required_vars.items():
        if 'KEY' in key or 'TOKEN' in key:
            logger.info(f"{key}: {'*' * min(len(value), 8) if value else 'Not set'}")
        else:
            logger.info(f"{key}: {value}")
    
    # Check for API keys based on provider
    provider = required_vars['LLM_PROVIDER'].lower()
    
    if provider == 'openai':
        if not os.getenv('OPENAI_API_KEY'):
            logger.warning("OPENAI_API_KEY not set - agent may not function properly")
    elif provider == 'anthropic':
        if not os.getenv('ANTHROPIC_API_KEY'):
            logger.warning("ANTHROPIC_API_KEY not set - agent may not function properly")
            
    # Ensure workspace directory exists
    workspace_dir = "/workspace"
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
        logger.info(f"Created workspace directory: {workspace_dir}")
    
    return required_vars

def main():
    """Main application entry point."""
    
    try:
        logger.info("Starting OSINT IRC Agent...")
        
        # Setup environment and configuration
        config = setup_environment()
        
        # Create and start the IRC bot
        bot = OSINTIRCBot()
        
        logger.info(f"Connecting to IRC server: {config['IRC_SERVER']}")
        logger.info(f"Joining channels: {config['IRC_CHANNELS']}")
        logger.info(f"Bot nickname: {config['IRC_NICK']}")
        
        # Run the bot
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("OSINT IRC Agent shutdown complete")

if __name__ == "__main__":
    """
    Usage Examples:
    
    # Basic usage with environment variables
    export IRC_SERVER="irc.libera.chat"
    export IRC_CHANNELS="#osint-test,#investigations"  
    export IRC_NICK="OSINT-Agent"
    export OPENAI_API_KEY="your_openai_api_key"
    python main.py
    
    # Using .env file
    echo "IRC_SERVER=irc.libera.chat" > .env
    echo "IRC_CHANNELS=#osint-test" >> .env
    echo "IRC_NICK=OSINT-Bot" >> .env
    echo "OPENAI_API_KEY=sk-..." >> .env
    python main.py
    
    Once connected, users can interact with the bot in several ways:
    
    1. Commands:
       !help - Show capabilities and usage
       !investigate <request> - Explicit investigation command
       
    2. Natural mentions:
       "OSINT-Agent: check out the username darkweb_trader"
       "OSINT-Agent, analyze suspicious-site.com for me"
       
    3. Private messages:
       Any private message to the bot is treated as an investigation request
    """
    
    main()