#!/usr/bin/env python3
"""
OSINT IRC Plugin - Separate module to avoid import issues
"""

import asyncio
import logging
import threading
import time
import irc3
from typing import Optional
from agent import OSINTAgent

logger = logging.getLogger(__name__)

@irc3.plugin
class OSINTPlugin:
    """OSINT plugin for IRC3 framework."""
    
    def __init__(self, bot):
        try:
            logger.info("🔧 OSINTPlugin __init__ called!")
            self.bot = bot
            self.osint_agent: Optional[OSINTAgent] = bot.config.get('osint_agent')
            logger.info(f"🔧 OSINTPlugin initialized - Agent available: {bool(self.osint_agent)}")
            
            if not self.osint_agent:
                logger.error("❌ OSINT agent not found in bot config!")
            else:
                logger.info("✅ OSINTPlugin successfully initialized with agent")
                
        except Exception as e:
            logger.error(f"💥 OSINTPlugin initialization failed: {e}", exc_info=True)
            raise
        
    @irc3.event(irc3.rfc.CONNECTED)
    def on_connected(self, **kwargs):
        """Called when bot connects to IRC server."""
        logger.info("🔗 Successfully connected to IRC server")
        
    @irc3.event(irc3.rfc.JOIN)
    def on_join(self, mask, channel, **kwargs):
        """Called when bot joins a channel."""
        if mask.nick == self.bot.nick:
            logger.info(f"✅ Joined channel: {channel}")
            # Send a greeting to confirm the bot is working
            self.bot.privmsg(channel, f"🤖 {self.bot.nick} is online and ready for OSINT investigations!")
            
    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask, target, data, **kwargs):
        """Handle all private messages and channel messages."""
        nick = mask.nick
        
        # Skip our own messages
        if nick == self.bot.nick:
            return
            
        logger.info(f"📥 Message from {nick} in {target}: '{data}'")
        
        # Clean up the message
        message = data.strip()
        
        try:
            # Handle !help command
            if message == '!help':
                self._handle_help_command(nick, target)
                return
                
            # Handle !investigate command  
            if message.startswith('!investigate '):
                investigation_query = message[13:].strip()  # Remove "!investigate "
                self._handle_investigate_command(nick, target, investigation_query)
                return
                
            # Handle direct mentions in channels
            if target.startswith('#') and self.bot.nick.lower() in message.lower():
                self._handle_mention(nick, target, message)
                return
                
            # Handle private messages (treat as investigations)
            if target == self.bot.nick:
                self._handle_private_investigation(nick, message)
                return
                
        except Exception as e:
            error_msg = f"❌ Error processing message: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.bot.privmsg(target, f"{nick}: {error_msg}")
    
    def _handle_help_command(self, nick: str, target: str):
        """Handle !help command."""
        logger.info(f"🔧 Processing !help command from {nick}")
        
        if not self.osint_agent:
            self.bot.privmsg(target, f"❌ {nick}: OSINT agent not initialized")
            return
            
        help_text = f"""✅ {nick}: OSINT Agent is active! Available commands:
• !help - Show this help message
• !investigate <query> - Start an OSINT investigation
• @{self.bot.nick} <query> - Mention me with your investigation request
• Private message me directly for confidential investigations

Example: !investigate username darkweb_trader"""

        self.bot.privmsg(target, help_text)
        logger.info("✅ Help response sent successfully")
        
    def _handle_investigate_command(self, nick: str, target: str, query: str):
        """Handle !investigate command."""
        logger.info(f"🔍 Processing !investigate command from {nick}: '{query}'")
        
        if not self.osint_agent:
            self.bot.privmsg(target, f"❌ {nick}: OSINT agent not initialized")
            return
            
        if not query:
            self.bot.privmsg(target, f"❌ {nick}: Please provide something to investigate. Example: !investigate username darkweb_trader")
            return
            
        # Acknowledge the request immediately
        self.bot.privmsg(target, f"🔍 {nick}: Starting OSINT investigation: '{query}'")
        
        # Start investigation in background thread
        investigation_thread = threading.Thread(
            target=self._run_investigation_thread,
            args=(nick, target, query),
            daemon=True
        )
        investigation_thread.start()
        
    def _handle_mention(self, nick: str, target: str, message: str):
        """Handle mentions of the bot in channels."""
        import re
        
        # Extract query after bot mention
        pattern = re.compile(f'{re.escape(self.bot.nick)}[:\s,]+(.+)', re.IGNORECASE)
        match = pattern.search(message)
        
        if match:
            query = match.group(1).strip()
            logger.info(f"🔍 Bot mentioned by {nick}: '{query}'")
            
            if query:
                self.bot.privmsg(target, f"🔍 {nick}: Investigating '{query}'")
                investigation_thread = threading.Thread(
                    target=self._run_investigation_thread,
                    args=(nick, target, query),
                    daemon=True
                )
                investigation_thread.start()
                
    def _handle_private_investigation(self, nick: str, message: str):
        """Handle private message investigations."""
        logger.info(f"🔒 Private investigation request from {nick}: '{message}'")
        
        if not self.osint_agent:
            self.bot.privmsg(nick, "❌ OSINT agent not initialized")
            return
            
        self.bot.privmsg(nick, f"🔍 Investigating privately: '{message}'")
        investigation_thread = threading.Thread(
            target=self._run_investigation_thread,
            args=(nick, nick, message),
            daemon=True
        )
        investigation_thread.start()
        
    def _run_investigation_thread(self, nick: str, target: str, query: str):
        """Thread wrapper for running async investigation."""
        try:
            # Run the async investigation in this thread
            result = asyncio.run(self._run_investigation(nick, target, query))
        except Exception as e:
            logger.error(f"❌ Investigation thread error: {e}", exc_info=True)
            self.bot.privmsg(target, f"❌ {nick}: Investigation failed due to system error")
        
    async def _run_investigation(self, nick: str, target: str, query: str):
        """Run OSINT investigation asynchronously."""
        try:
            logger.info(f"🚀 Starting investigation for {nick}: {query}")
            
            # Create unique user ID for the session
            user_id = f"{nick}!{target}"
            
            # Run the investigation
            result = await self.osint_agent.investigate(query, user_id)
            
            # Send result back synchronously (threading safe)
            self._send_investigation_result(target, nick, result)
            
            logger.info(f"✅ Investigation completed for {nick}")
            
        except Exception as e:
            error_msg = f"Investigation failed: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            self.bot.privmsg(target, f"❌ {nick}: {error_msg}")
            
    def _send_investigation_result(self, target: str, nick: str, result: str):
        """Send investigation result synchronously."""
        full_message = f"{nick}: {result}"
        
        # Split long messages to avoid IRC limits
        max_length = 400
        lines = full_message.split('\n')
        current_msg = ""
        
        for line in lines:
            if len(current_msg + line + '\n') > max_length:
                if current_msg:
                    self.bot.privmsg(target, current_msg.strip())
                    time.sleep(1.0)  # Rate limiting
                current_msg = line
            else:
                current_msg += line + '\n' if current_msg else line
                
        if current_msg:
            self.bot.privmsg(target, current_msg.strip())