"""
ChatGPT Web Authentication Provider

Uses ChatGPT web interface with session token authentication.
No API key needed - uses your ChatGPT account.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Try to import ChatGPT libraries
try:
    from revChatGPT.V1 import Chatbot
    REVCHATGPT_AVAILABLE = True
except ImportError:
    REVCHATGPT_AVAILABLE = False
    logger.warning("revChatGPT not available. Install with: pip install revChatGPT")

try:
    import poe
    POE_AVAILABLE = True
except ImportError:
    POE_AVAILABLE = False
    logger.warning("poe-api not available. Install with: pip install poe-api")


class ChatGPTWebProvider:
    """
    ChatGPT Web Interface Provider
    
    Uses session token authentication to access ChatGPT without API key.
    Supports both revChatGPT and Poe.com methods.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize ChatGPT web provider.
        
        Args:
            config: Configuration dict with session tokens
        """
        self.config = config
        self.method = config.get('web_method', 'revchatgpt')  # revchatgpt or poe
        self.chatbot = None
        self.poe_client = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the selected method."""
        if self.method == 'revchatgpt':
            self._init_revchatgpt()
        elif self.method == 'poe':
            self._init_poe()
        else:
            logger.error(f"Unknown web method: {self.method}")
    
    def _init_revchatgpt(self):
        """Initialize revChatGPT."""
        if not REVCHATGPT_AVAILABLE:
            logger.error("revChatGPT not installed")
            return
        
        # Get session token from config
        session_token = self.config.get('chatgpt_session_token')
        access_token = self.config.get('chatgpt_access_token')
        
        if not session_token and not access_token:
            logger.error("No ChatGPT session/access token provided")
            return
        
        try:
            config = {
                "session_token": session_token,
            }
            
            # If access_token is provided, use it instead
            if access_token:
                config = {
                    "access_token": access_token,
                }
            
            self.chatbot = Chatbot(config=config)
            logger.info("✅ ChatGPT web (revChatGPT) initialized")
        
        except Exception as e:
            logger.error(f"Failed to initialize revChatGPT: {e}")
    
    def _init_poe(self):
        """Initialize Poe.com client."""
        if not POE_AVAILABLE:
            logger.error("poe-api not installed")
            return
        
        # Get Poe token from config
        poe_token = self.config.get('poe_token')
        
        if not poe_token:
            logger.error("No Poe token provided")
            return
        
        try:
            self.poe_client = poe.Client(poe_token)
            logger.info("✅ Poe.com client initialized")
        
        except Exception as e:
            logger.error(f"Failed to initialize Poe client: {e}")
    
    async def generate_response(
        self,
        messages: List[Dict],
        personality: str = 'friendly',
        **kwargs
    ) -> str:
        """
        Generate response using ChatGPT web interface.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            personality: Personality type (not used in web mode)
            **kwargs: Additional arguments
        
        Returns:
            Generated response text
        """
        if self.method == 'revchatgpt':
            return await self._generate_revchatgpt(messages)
        elif self.method == 'poe':
            return await self._generate_poe(messages)
        else:
            return "ChatGPT web provider not initialized."
    
    async def _generate_revchatgpt(self, messages: List[Dict]) -> str:
        """Generate response using revChatGPT."""
        if not self.chatbot:
            return "❌ ChatGPT web is not configured. Please set session token."
        
        try:
            # Format conversation for ChatGPT
            # Use only the last user message for simplicity
            last_user_message = None
            for msg in reversed(messages):
                if msg['role'] == 'user':
                    last_user_message = msg['content']
                    break
            
            if not last_user_message:
                return "No message to respond to."
            
            # Send message to ChatGPT
            response_text = ""
            
            # Run in thread pool to avoid blocking
            def chat():
                nonlocal response_text
                for data in self.chatbot.ask(last_user_message):
                    response_text = data["message"]
            
            await asyncio.to_thread(chat)
            
            return response_text if response_text else "Failed to get response from ChatGPT."
        
        except Exception as e:
            logger.error(f"revChatGPT error: {e}")
            
            # Check for common errors
            if "expired" in str(e).lower() or "unauthorized" in str(e).lower():
                return "❌ ChatGPT session expired. Please refresh your session token."
            
            return f"❌ ChatGPT error: {str(e)}"
    
    async def _generate_poe(self, messages: List[Dict]) -> str:
        """Generate response using Poe.com."""
        if not self.poe_client:
            return "❌ Poe is not configured. Please set Poe token."
        
        try:
            # Get bot name from config (default to GPT-4)
            bot_name = self.config.get('poe_bot', 'GPT-4')
            
            # Format conversation for Poe
            last_user_message = None
            for msg in reversed(messages):
                if msg['role'] == 'user':
                    last_user_message = msg['content']
                    break
            
            if not last_user_message:
                return "No message to respond to."
            
            # Send message to Poe
            response_text = ""
            
            def poe_chat():
                nonlocal response_text
                for chunk in self.poe_client.send_message(bot_name, last_user_message):
                    response_text = chunk["text"]
            
            await asyncio.to_thread(poe_chat)
            
            return response_text if response_text else "Failed to get response from Poe."
        
        except Exception as e:
            logger.error(f"Poe error: {e}")
            
            if "expired" in str(e).lower() or "unauthorized" in str(e).lower():
                return "❌ Poe session expired. Please refresh your Poe token."
            
            return f"❌ Poe error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if provider is available and configured."""
        if self.method == 'revchatgpt':
            return REVCHATGPT_AVAILABLE and self.chatbot is not None
        elif self.method == 'poe':
            return POE_AVAILABLE and self.poe_client is not None
        return False


class ChatGPTWebManager:
    """
    Manages ChatGPT web authentication and session tokens.
    """
    
    @staticmethod
    def get_setup_instructions(method: str = 'revchatgpt') -> str:
        """Get setup instructions for the specified method."""
        
        if method == 'revchatgpt':
            return """
# ChatGPT Web Setup (revChatGPT)

## Method 1: Session Token (Easiest)

1. **Login to ChatGPT:**
   - Go to https://chat.openai.com/
   - Login to your account

2. **Get Session Token:**
   - Open browser DevTools (F12)
   - Go to Application tab (Chrome) or Storage tab (Firefox)
   - Find Cookies → https://chat.openai.com
   - Copy the value of `__Secure-next-auth.session-token`

3. **Add to Config:**
   ```yaml
   ai:
     provider: "chatgpt_web"
     web_method: "revchatgpt"
     chatgpt_session_token: "YOUR_SESSION_TOKEN_HERE"
   ```

## Method 2: Access Token (More Reliable)

1. **Login to ChatGPT:**
   - Go to https://chat.openai.com/
   - Login to your account

2. **Get Access Token:**
   - Go to https://chat.openai.com/api/auth/session
   - Copy the `accessToken` value

3. **Add to Config:**
   ```yaml
   ai:
     provider: "chatgpt_web"
     web_method: "revchatgpt"
     chatgpt_access_token: "YOUR_ACCESS_TOKEN_HERE"
   ```

## Notes:
- Session tokens expire after ~1-2 weeks
- Access tokens expire after ~1-2 months
- You'll need to refresh tokens when they expire
- Free ChatGPT accounts have rate limits
- ChatGPT Plus accounts have higher limits
"""
        
        elif method == 'poe':
            return """
# Poe.com Setup

Poe gives you access to multiple AI models including:
- ChatGPT (GPT-3.5, GPT-4)
- Claude (Instant, 2, 3)
- And many more!

## Setup Steps:

1. **Create Poe Account:**
   - Go to https://poe.com/
   - Sign up or login

2. **Get Poe Token:**
   - Open browser DevTools (F12)
   - Go to Application → Cookies → https://poe.com
   - Copy the value of `p-b` cookie

3. **Add to Config:**
   ```yaml
   ai:
     provider: "chatgpt_web"
     web_method: "poe"
     poe_token: "YOUR_POE_TOKEN_HERE"
     poe_bot: "GPT-4"  # Options: ChatGPT, GPT-4, Claude-instant, Claude-2, etc.
   ```

## Available Bots:
- `ChatGPT` - GPT-3.5-turbo (free)
- `GPT-4` - GPT-4 (requires subscription)
- `Claude-instant` - Fast Claude (free)
- `Claude-2` - Claude 2 (requires subscription)
- `Claude-3-Opus` - Most capable Claude
- And many community bots!

## Notes:
- Free Poe accounts have daily limits
- Poe subscription unlocks GPT-4 and Claude-2
- Tokens expire after a few weeks
"""
        
        return "Unknown method"
