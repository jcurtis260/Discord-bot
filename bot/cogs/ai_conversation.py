"""
AI Conversation cog for Discord bot.
Handles AI-powered conversations with personality.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict
import logging
import json
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import AI providers
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic not available")

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    LOCAL_MODEL_AVAILABLE = True
except ImportError:
    LOCAL_MODEL_AVAILABLE = False
    logger.warning("Transformers not available for local models")

try:
    from modules.chatgpt_web import ChatGPTWebProvider
    CHATGPT_WEB_AVAILABLE = True
except ImportError:
    CHATGPT_WEB_AVAILABLE = False
    logger.warning("ChatGPT web provider not available")


class AIConversation(commands.Cog):
    """AI-powered conversation system."""
    
    def __init__(self, bot):
        """Initialize AI conversation cog."""
        self.bot = bot
        self.context_cache = {}  # In-memory cache for conversation context
        
        # Initialize AI providers
        self.openai_client = None
        self.anthropic_client = None
        self.local_model = None
        self.local_tokenizer = None
        self.chatgpt_web = None
        self._init_ai_providers()
        
        self.personalities = {
            'friendly': {
                'system_prompt': "You are a friendly and helpful Discord bot assistant. Be conversational, use appropriate emojis occasionally, and help users with their questions. Keep responses concise (under 300 characters when possible).",
                'temperature': 0.8
            },
            'professional': {
                'system_prompt': "You are a professional Discord bot assistant. Provide clear, concise, and helpful responses. Maintain a formal but friendly tone. Keep responses brief and informative.",
                'temperature': 0.5
            },
            'humorous': {
                'system_prompt': "You are a fun and humorous Discord bot assistant. Make jokes, use puns, and keep the conversation light and entertaining. Use emojis and be playful, but still helpful.",
                'temperature': 0.9
            },
            'casual': {
                'system_prompt': "You are a casual and laid-back Discord bot. Chat like a friend, use slang when appropriate, and keep things chill. Be helpful but don't be too formal about it.",
                'temperature': 0.8
            }
        }
        
        # Initialize AI client (consolidated method)
        self.ai_client = None
        self.ai_provider = self.bot.config.get('ai.provider', 'openai')
        self._init_combined_ai()
    
    def _init_ai_client(self):
        """Initialize AI client based on configuration."""
        # Check for ChatGPT web first
        if self.ai_provider == 'chatgpt_web' and CHATGPT_WEB_AVAILABLE:
            web_config = {
                'web_method': self.bot.config.get('ai.web_method', 'revchatgpt'),
                'chatgpt_session_token': self.bot.config.get('ai.chatgpt_session_token'),
                'chatgpt_access_token': self.bot.config.get('ai.chatgpt_access_token'),
                'poe_token': self.bot.config.get('ai.poe_token'),
                'poe_bot': self.bot.config.get('ai.poe_bot', 'GPT-4'),
            }
            try:
                self.chatgpt_web = ChatGPTWebProvider(web_config)
                if self.chatgpt_web.is_available():
                    logger.info("✅ ChatGPT web provider initialized")
                else:
                    logger.warning("ChatGPT web provider not fully configured")
            except Exception as e:
                logger.error(f"Failed to initialize ChatGPT web: {e}")
        
        # Standard API providers
        elif self.ai_provider == 'openai' and OPENAI_AVAILABLE:
            api_key = self.bot.config.get('ai.api_key')
            if api_key:
                self.ai_client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")
        elif self.ai_provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            api_key = self.bot.config.get('ai.api_key')
            if api_key:
                self.ai_client = anthropic.AsyncAnthropic(api_key=api_key)
                logger.info("Anthropic client initialized")
        else:
            logger.warning(f"AI provider {self.ai_provider} not available or no API key configured")
    
    async def get_ai_config(self, guild_id: int) -> Dict:
        """Get AI configuration for a guild."""
        config = await self.bot.db.fetchrow(
            """
            SELECT ai_enabled, ai_personality, ai_engagement_rate
            FROM guild_config
            WHERE guild_id = $1
            """,
            guild_id
        )
        
        if not config:
            return {'ai_enabled': False, 'ai_personality': 'friendly', 'ai_engagement_rate': 0.1}
        
        return dict(config)
    
    async def is_ai_enabled_in_channel(self, guild_id: int, channel_id: int) -> bool:
        """Check if AI is enabled in a specific channel."""
        # Check guild-wide setting
        guild_config = await self.get_ai_config(guild_id)
        if not guild_config['ai_enabled']:
            return False
        
        # Check channel-specific setting
        channel_config = await self.bot.db.fetchrow(
            """
            SELECT enabled FROM ai_channels
            WHERE guild_id = $1 AND channel_id = $2
            """,
            guild_id, channel_id
        )
        
        if channel_config is not None:
            return channel_config['enabled']
        
        # Default to enabled if no channel-specific config
        return True
    
    async def get_conversation_context(self, guild_id: int, channel_id: int) -> List[Dict]:
        """Get recent conversation context from database."""
        context = await self.bot.db.fetchrow(
            """
            SELECT message_history FROM ai_context
            WHERE guild_id = $1 AND channel_id = $2
            """,
            guild_id, channel_id
        )
        
        if context and context['message_history']:
            return context['message_history']
        
        return []
    
    async def save_conversation_context(self, guild_id: int, channel_id: int, messages: List[Dict]):
        """Save conversation context to database."""
        # Keep only last 20 messages
        messages = messages[-20:]
        
        await self.bot.db.execute(
            """
            INSERT INTO ai_context (guild_id, channel_id, message_history, last_updated)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id, channel_id) 
            DO UPDATE SET message_history = $3, last_updated = $4
            """,
            guild_id, channel_id, json.dumps(messages), datetime.utcnow()
        )
    
    async def generate_ai_response(self, messages: List[Dict], personality: str = 'friendly') -> str:
        """Generate AI response using configured provider."""
        personality_config = self.personalities.get(personality, self.personalities['friendly'])
        
        # ChatGPT Web Provider
        if self.ai_provider == 'chatgpt_web' and self.chatgpt_web:
            try:
                return await self.chatgpt_web.generate_response(messages, personality)
            except Exception as e:
                logger.error(f"ChatGPT web error: {e}")
                return f"❌ ChatGPT web error: {str(e)}"
        
        # Local Model Provider
        elif self.ai_provider == 'local' and self.local_model:
            return await self._generate_local_response(messages, personality)
        
        # Standard API providers (OpenAI, Anthropic)
        elif not self.ai_client:
            return "❌ AI is not configured. Please set up an API key or configure web authentication."
        
        # Add system prompt
        full_messages = [
            {"role": "system", "content": personality_config['system_prompt']}
        ] + messages
        
        try:
            if self.ai_provider == 'openai':
                response = await self.ai_client.chat.completions.create(
                    model=self.bot.config.get('ai.model', 'gpt-4'),
                    messages=full_messages,
                    max_tokens=self.bot.config.get('ai.max_tokens', 500),
                    temperature=personality_config['temperature']
                )
                return response.choices[0].message.content
            
            elif self.ai_provider == 'anthropic':
                # Anthropic format is slightly different
                system_prompt = personality_config['system_prompt']
                user_messages = [m for m in messages if m['role'] != 'system']
                
                response = await self.ai_client.messages.create(
                    model=self.bot.config.get('ai.model', 'claude-3-sonnet-20240229'),
                    max_tokens=self.bot.config.get('ai.max_tokens', 500),
                    temperature=personality_config['temperature'],
                    system=system_prompt,
                    messages=user_messages
                )
                return response.content[0].text
        
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return "❌ Sorry, I encountered an error generating a response."
    
    async def _generate_local_response(self, messages: List[Dict], personality: str = 'friendly') -> str:
        """Generate response using local model."""
        if not self.local_model or not self.local_tokenizer:
            return "Local AI model not available. Please configure an API key."
        
        try:
            # Format conversation for local model
            personality_config = self.personalities.get(personality, self.personalities['friendly'])
            prompt = f"{personality_config['system_prompt']}\n\n"
            
            for msg in messages[-5:]:  # Use last 5 messages
                role = msg['role']
                content = msg['content']
                if role == 'user':
                    prompt += f"User: {content}\n"
                elif role == 'assistant':
                    prompt += f"Assistant: {content}\n"
            
            prompt += "Assistant:"
            
            # Generate response
            inputs = self.local_tokenizer(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            
            with torch.no_grad():
                outputs = self.local_model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=personality_config['temperature'],
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.local_tokenizer.eos_token_id
                )
            
            response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the assistant's response
            response = response.split("Assistant:")[-1].strip()
            
            # Limit length
            if len(response) > 500:
                response = response[:500] + "..."
            
            return response
        
        except Exception as e:
            logger.error(f"Local model generation error: {e}")
            return "I'm having trouble generating a response right now."
    
    def should_respond_randomly(self, engagement_rate: float) -> bool:
        """Determine if bot should randomly join conversation."""
        return random.random() < engagement_rate
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle incoming messages for AI responses."""
        # Ignore bot messages and DMs
        if message.author.bot or not message.guild:
            return
        
        # Check if AI is enabled
        if not await self.is_ai_enabled_in_channel(message.guild.id, message.channel.id):
            return
        
        bot_mentioned = self.bot.user.mentioned_in(message)
        is_reply_to_bot = False
        
        # Check if replying to bot
        if message.reference:
            try:
                referenced = await message.channel.fetch_message(message.reference.message_id)
                is_reply_to_bot = referenced.author.id == self.bot.user.id
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass  # Message not found or no access
        
        # Get AI config
        ai_config = await self.get_ai_config(message.guild.id)
        
        # Determine if we should respond
        should_respond = (
            bot_mentioned or 
            is_reply_to_bot or 
            self.should_respond_randomly(ai_config['ai_engagement_rate'])
        )
        
        if not should_respond:
            return
        
        # Show typing indicator
        async with message.channel.typing():
            # Get conversation context
            context = await self.get_conversation_context(message.guild.id, message.channel.id)
            
            # Add current message to context
            context.append({
                "role": "user",
                "content": f"{message.author.display_name}: {message.content}"
            })
            
            # Generate response
            response = await self.generate_ai_response(
                context,
                ai_config['ai_personality']
            )
            
            # Add bot response to context
            context.append({
                "role": "assistant",
                "content": response
            })
            
            # Save context
            await self.save_conversation_context(message.guild.id, message.channel.id, context)
            
            # Send response
            if len(response) > 2000:
                response = response[:1997] + "..."
            
            await message.reply(response, mention_author=False)
    
    @app_commands.command(name="ai", description="Configure AI settings (Admin)")
    @app_commands.describe(
        action="Action to perform",
        value="Value for the action"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Enable in channel", value="enable"),
        app_commands.Choice(name="Disable in channel", value="disable"),
        app_commands.Choice(name="Set personality", value="personality"),
        app_commands.Choice(name="Set engagement rate", value="engagement"),
        app_commands.Choice(name="Clear context", value="clear")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def ai_config(self, interaction: discord.Interaction, action: str, value: Optional[str] = None):
        """Configure AI settings."""
        if action == "enable":
            await self.bot.db.execute(
                """
                INSERT INTO ai_channels (guild_id, channel_id, enabled)
                VALUES ($1, $2, TRUE)
                ON CONFLICT (guild_id, channel_id) DO UPDATE SET enabled = TRUE
                """,
                interaction.guild.id, interaction.channel.id
            )
            
            # Also enable guild-wide
            await self.bot.db.execute(
                """
                INSERT INTO guild_config (guild_id, ai_enabled)
                VALUES ($1, TRUE)
                ON CONFLICT (guild_id) DO UPDATE SET ai_enabled = TRUE
                """,
                interaction.guild.id
            )
            
            await interaction.response.send_message(
                "✅ AI enabled in this channel! Mention me or reply to my messages to chat.",
                ephemeral=True
            )
        
        elif action == "disable":
            await self.bot.db.execute(
                """
                INSERT INTO ai_channels (guild_id, channel_id, enabled)
                VALUES ($1, $2, FALSE)
                ON CONFLICT (guild_id, channel_id) DO UPDATE SET enabled = FALSE
                """,
                interaction.guild.id, interaction.channel.id
            )
            
            await interaction.response.send_message(
                "✅ AI disabled in this channel.",
                ephemeral=True
            )
        
        elif action == "personality":
            if value not in self.personalities:
                valid = ", ".join(self.personalities.keys())
                await interaction.response.send_message(
                    f"❌ Invalid personality. Valid options: {valid}",
                    ephemeral=True
                )
                return
            
            await self.bot.db.execute(
                """
                INSERT INTO guild_config (guild_id, ai_personality)
                VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET ai_personality = $2
                """,
                interaction.guild.id, value
            )
            
            await interaction.response.send_message(
                f"✅ AI personality set to **{value}**",
                ephemeral=True
            )
        
        elif action == "engagement":
            try:
                rate = float(value)
                if rate < 0 or rate > 1:
                    raise ValueError()
            except (ValueError, TypeError):
                await interaction.response.send_message(
                    "❌ Engagement rate must be a number between 0 and 1 (e.g., 0.1 for 10%)",
                    ephemeral=True
                )
                return
            
            await self.bot.db.execute(
                """
                INSERT INTO guild_config (guild_id, ai_engagement_rate)
                VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET ai_engagement_rate = $2
                """,
                interaction.guild.id, rate
            )
            
            await interaction.response.send_message(
                f"✅ AI engagement rate set to {rate*100:.0f}%",
                ephemeral=True
            )
        
        elif action == "clear":
            await self.bot.db.execute(
                """
                DELETE FROM ai_context
                WHERE guild_id = $1 AND channel_id = $2
                """,
                interaction.guild.id, interaction.channel.id
            )
            
            await interaction.response.send_message(
                "✅ Conversation context cleared for this channel.",
                ephemeral=True
            )
    
    @app_commands.command(name="chat", description="Chat with the AI bot")
    @app_commands.describe(message="Your message to the AI")
    async def chat(self, interaction: discord.Interaction, message: str):
        """Direct chat command with AI."""
        await interaction.response.defer()
        
        # Check if AI is enabled
        if not await self.is_ai_enabled_in_channel(interaction.guild.id, interaction.channel.id):
            await interaction.followup.send(
                "❌ AI is not enabled in this channel. Use `/ai action:enable` to enable it.",
                ephemeral=True
            )
            return
        
        # Get context and generate response
        ai_config = await self.get_ai_config(interaction.guild.id)
        context = await self.get_conversation_context(interaction.guild.id, interaction.channel.id)
        
        context.append({
            "role": "user",
            "content": f"{interaction.user.display_name}: {message}"
        })
        
        response = await self.generate_ai_response(context, ai_config['ai_personality'])
        
        context.append({
            "role": "assistant",
            "content": response
        })
        
        await self.save_conversation_context(interaction.guild.id, interaction.channel.id, context)
        
        if len(response) > 2000:
            response = response[:1997] + "..."
        
        await interaction.followup.send(response)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(AIConversation(bot))
