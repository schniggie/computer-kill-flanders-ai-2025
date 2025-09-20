#!/usr/bin/env python3
"""
OSINT IRC Client - Clean Implementation
Fixed version with proper plugin architecture and command handling
"""

import logging
import os
import irc3
from agent import OSINTAgent
from osint_plugin import OSINTPlugin

logger = logging.getLogger(__name__)


class OSINTIRCBot:
    """Clean IRC bot implementation for OSINT operations."""
    
    def __init__(self):
        """Initialize the IRC bot with OSINT agent integration."""
        
        # Load IRC configuration from environment
        self.server = os.getenv('IRC_SERVER', 'irc.libera.chat')
        self.port = int(os.getenv('IRC_PORT', '6667'))
        self.nick = os.getenv('IRC_NICK', 'OSINT-Agent')
        self.channels = os.getenv('IRC_CHANNELS', '#osint-test').split(',')
        self.ssl = os.getenv('IRC_SSL', 'false').lower() == 'true'
        
        logger.info(f"🔧 Configuring IRC bot:")
        logger.info(f"  Server: {self.server}:{self.port}")
        logger.info(f"  Nick: {self.nick}")
        logger.info(f"  Channels: {self.channels}")
        logger.info(f"  SSL: {self.ssl}")
        
        # Initialize OSINT agent
        try:
            self.osint_agent = OSINTAgent(
                model_provider=os.getenv('LLM_PROVIDER', 'openai'),
                model_name=os.getenv('LLM_MODEL', 'gpt-4')
            )
            logger.info("✅ OSINT agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OSINT agent: {e}")
            raise
        
        # IRC bot configuration
        self.config = {
            'nick': self.nick,
            'username': self.nick,
            'realname': 'OSINT Investigation Agent',
            'host': self.server,
            'port': self.port,
            'ssl': self.ssl,
            'autojoins': self.channels,
            'includes': [  # Use 'includes' instead of 'plugins'
                'irc3.plugins.core',
                'irc3.plugins.ctcp',  
                'irc3.plugins.autojoins',
                'osint_plugin',  # Add our plugin by module name
            ],
            # Add connection debugging
            'debug': True,
            'verbose': True,
            # Connection timeout and retry settings
            'timeout': 60,
            'max_lag': 300,
            # CRITICAL: Pass the OSINT agent to plugins
            'osint_agent': self.osint_agent,
        }
        
    def run(self):
        """Start the IRC bot."""
        logger.info("🚀 Starting OSINT IRC bot...")
        
        try:
            # Create the IRC bot instance
            bot = irc3.IrcBot(**self.config)
            logger.info("✅ IRC bot instance created")
            
            # Plugin should be loaded via 'includes' config now
            logger.info("🔌 OSINT plugin should be loaded via includes config")
            
            # Start the bot (this blocks)
            logger.info("🔗 Connecting to IRC...")
            bot.run()
            
        except KeyboardInterrupt:
            logger.info("👋 Bot shutdown requested by user")
        except Exception as e:
            logger.error(f"💥 Bot error: {e}", exc_info=True)
            raise
        finally:
            logger.info("🛑 OSINT IRC bot stopped")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start bot
    bot = OSINTIRCBot()
    bot.run()