"""
AI-Powered Moderation

Uses AI to analyze messages for toxicity, spam, inappropriate content, etc.
Separate from rule-based auto-moderation.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
import asyncio
import logging

# Try to import AI libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    Anthropic = None

logger = logging.getLogger(__name__)


class AIMod(commands.Cog):
    """AI-powered content moderation."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Cache for whitelisted users per guild
        self.whitelisted_users = {}
    
    def _init_ai_clients(self):
        """Initialize AI clients based on config."""
        ai_provider = self.bot.config.get('ai.provider', 'openai')
        api_key = self.bot.config.get('ai.api_key')
        
        if not api_key:
            logger.warning("⚠️ AI Moderation: No API key configured")
            return
        
        if ai_provider == 'openai':
            if HAS_OPENAI:
                self.openai_client = openai.OpenAI(api_key=api_key)
            else:
                logger.error("⚠️ AI Moderation: OpenAI provider selected but 'openai' package not installed. Run: pip install openai")
        elif ai_provider == 'anthropic':
            if HAS_ANTHROPIC:
                self.anthropic_client = Anthropic(api_key=api_key)
            else:
                logger.error("⚠️ AI Moderation: Anthropic provider selected but 'anthropic' package not installed. Run: pip install anthropic")
    
    async def cog_load(self):
        """Load whitelisted users from database."""
        await self._load_whitelist()
    
    async def _load_whitelist(self):
        """Load all whitelisted users into cache."""
        if not self.bot.db:
            return
        
        try:
            whitelist = await self.bot.db.fetch(
                "SELECT guild_id, user_id FROM ai_mod_whitelist"
            )
            
            for record in whitelist:
                guild_id = record['guild_id']
                user_id = record['user_id']
                
                if guild_id not in self.whitelisted_users:
                    self.whitelisted_users[guild_id] = set()
                
                self.whitelisted_users[guild_id].add(user_id)
        except Exception as e:
            logger.error(f"Error loading AI mod whitelist: {e}")
    
    async def _get_ai_mod_config(self, guild_id: int) -> dict:
        """Get AI moderation configuration for a guild."""
        config = await self.bot.db.fetchrow(
            """
            SELECT ai_mod_enabled, ai_mod_threshold, ai_mod_action,
                   ai_mod_log_channel, ai_mod_check_toxicity,
                   ai_mod_check_spam, ai_mod_check_nsfw
            FROM guild_config
            WHERE guild_id = $1
            """,
            guild_id
        )
        
        if not config:
            return {
                'enabled': False,
                'threshold': 0.7,
                'action': 'warn',
                'log_channel': None,
                'check_toxicity': True,
                'check_spam': True,
                'check_nsfw': True
            }
        
        return {
            'enabled': config['ai_mod_enabled'] or False,
            'threshold': config['ai_mod_threshold'] or 0.7,
            'action': config['ai_mod_action'] or 'warn',
            'log_channel': config['ai_mod_log_channel'],
            'check_toxicity': config['ai_mod_check_toxicity'] if config['ai_mod_check_toxicity'] is not None else True,
            'check_spam': config['ai_mod_check_spam'] if config['ai_mod_check_spam'] is not None else True,
            'check_nsfw': config['ai_mod_check_nsfw'] if config['ai_mod_check_nsfw'] is not None else True
        }
    
    async def _analyze_message(self, message_content: str, checks: dict) -> dict:
        """
        Use AI to analyze a message for various issues.
        
        Returns:
            dict with 'flagged', 'reason', 'confidence', 'categories'
        """
        # Build analysis prompt
        check_list = []
        if checks['check_toxicity']:
            check_list.append("toxicity, hate speech, harassment, or bullying")
        if checks['check_spam']:
            check_list.append("spam or repetitive content")
        if checks['check_nsfw']:
            check_list.append("NSFW, sexual, or inappropriate content")
        
        checks_str = ", ".join(check_list)
        
        prompt = f"""Analyze this Discord message for: {checks_str}.

Message: "{message_content}"

Respond in JSON format:
{{
    "flagged": true/false,
    "confidence": 0.0-1.0,
    "reason": "brief explanation",
    "categories": ["category1", "category2"]
}}

Only flag messages that clearly violate Discord's community guidelines."""
        
        try:
            if self.openai_client:
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a content moderation assistant. Analyze messages objectively and only flag clear violations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                return result
            
            elif self.anthropic_client:
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-sonnet-20240229",
                    max_tokens=500,
                    temperature=0.3,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                import json
                result = json.loads(response.content[0].text)
                return result
            
            else:
                return {
                    'flagged': False,
                    'confidence': 0.0,
                    'reason': 'No AI client configured',
                    'categories': []
                }
        
        except Exception as e:
            logger.error(f"AI moderation analysis error: {e}")
            return {
                'flagged': False,
                'confidence': 0.0,
                'reason': f'Analysis error: {str(e)}',
                'categories': []
            }
    
    async def _take_action(self, message: discord.Message, analysis: dict, action: str, config: dict):
        """Take moderation action based on AI analysis."""
        # Delete the message
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        # Create reason
        reason = f"AI Moderation: {analysis['reason']} (confidence: {analysis['confidence']:.0%})"
        categories_str = ", ".join(analysis['categories'])
        
        # Warn user
        if action == 'warn':
            try:
                await message.channel.send(
                    f"⚠️ {message.author.mention}, your message was removed by AI moderation.\n"
                    f"**Reason:** {analysis['reason']}\n"
                    f"**Categories:** {categories_str}",
                    delete_after=15
                )
            except discord.Forbidden:
                pass
        
        # Timeout user
        elif action == 'timeout':
            try:
                from datetime import timedelta
                await message.author.timeout(
                    timedelta(minutes=10),
                    reason=reason
                )
                await message.channel.send(
                    f"🔇 {message.author.mention} has been timed out for 10 minutes.\n"
                    f"**Reason:** {analysis['reason']}",
                    delete_after=15
                )
            except discord.Forbidden:
                pass
        
        # Kick user
        elif action == 'kick':
            try:
                await message.author.kick(reason=reason)
                await message.channel.send(
                    f"👢 {message.author.mention} has been kicked.\n"
                    f"**Reason:** {analysis['reason']}"
                )
            except discord.Forbidden:
                pass
        
        # Log to database
        await self.bot.db.execute(
            """
            INSERT INTO infractions (guild_id, user_id, moderator_id, type, reason)
            VALUES ($1, $2, $3, $4, $5)
            """,
            message.guild.id,
            message.author.id,
            self.bot.user.id,
            f'ai_mod_{action}',
            reason
        )
        
        # Log to channel if configured
        if config['log_channel']:
            log_channel = message.guild.get_channel(config['log_channel'])
            if log_channel:
                embed = discord.Embed(
                    title="🤖 AI Moderation Action",
                    color=discord.Color.red(),
                    timestamp=message.created_at
                )
                
                embed.add_field(name="User", value=f"{message.author.mention} ({message.author})", inline=False)
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="Action", value=action.title(), inline=True)
                embed.add_field(name="Confidence", value=f"{analysis['confidence']:.0%}", inline=True)
                embed.add_field(name="Reason", value=analysis['reason'], inline=False)
                embed.add_field(name="Categories", value=categories_str or "None", inline=False)
                embed.add_field(name="Message Content", value=message.content[:1000], inline=False)
                
                try:
                    await log_channel.send(embed=embed)
                except discord.Forbidden:
                    pass
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check messages with AI moderation."""
        if message.author.bot or not message.guild:
            return
        
        # Skip if user has manage messages permission
        if message.author.guild_permissions.manage_messages:
            return
        
        # Check if user is whitelisted
        guild_whitelist = self.whitelisted_users.get(message.guild.id, set())
        if message.author.id in guild_whitelist:
            return
        
        # Get config
        config = await self._get_ai_mod_config(message.guild.id)
        
        if not config['enabled']:
            return
        
        # Skip empty messages or very short ones
        if not message.content or len(message.content.strip()) < 10:
            return
        
        # Analyze message
        analysis = await self._analyze_message(message.content, config)
        
        # Check if flagged and meets threshold
        if analysis['flagged'] and analysis['confidence'] >= config['threshold']:
            await self._take_action(message, analysis, config['action'], config)
    
    @app_commands.command(name="aimod-enable", description="Enable AI-powered moderation")
    @app_commands.default_permissions(administrator=True)
    async def aimod_enable(self, interaction: discord.Interaction):
        """Enable AI moderation."""
        # Ensure guild config exists
        await self.bot.db.ensure_guild(interaction.guild_id)
        
        await self.bot.db.execute(
            """
            INSERT INTO guild_config (guild_id, ai_mod_enabled)
            VALUES ($1, TRUE)
            ON CONFLICT (guild_id)
            DO UPDATE SET ai_mod_enabled = TRUE
            """,
            interaction.guild_id
        )
        
        await interaction.response.send_message(
            "✅ AI-powered moderation enabled.\n"
            "Messages will be analyzed for toxicity, spam, and inappropriate content.\n"
            "Use `/aimod-config` to customize settings."
        )
    
    @app_commands.command(name="aimod-disable", description="Disable AI-powered moderation")
    @app_commands.default_permissions(administrator=True)
    async def aimod_disable(self, interaction: discord.Interaction):
        """Disable AI moderation."""
        await self.bot.db.ensure_guild(interaction.guild_id)
        
        await self.bot.db.execute(
            """
            INSERT INTO guild_config (guild_id, ai_mod_enabled)
            VALUES ($1, FALSE)
            ON CONFLICT (guild_id)
            DO UPDATE SET ai_mod_enabled = FALSE
            """,
            interaction.guild_id
        )
        
        await interaction.response.send_message("✅ AI-powered moderation disabled.")
    
    @app_commands.command(name="aimod-config", description="View AI moderation configuration")
    async def aimod_config(self, interaction: discord.Interaction):
        """View AI moderation configuration."""
        config = await self._get_ai_mod_config(interaction.guild_id)
        
        status = "✅ Enabled" if config['enabled'] else "❌ Disabled"
        log_channel = f"<#{config['log_channel']}>" if config['log_channel'] else "Not set"
        
        checks = []
        if config['check_toxicity']:
            checks.append("Toxicity/Hate Speech")
        if config['check_spam']:
            checks.append("Spam")
        if config['check_nsfw']:
            checks.append("NSFW Content")
        
        embed = discord.Embed(
            title="🤖 AI Moderation Configuration",
            description=f"**Status:** {status}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Confidence Threshold",
            value=f"{config['threshold']:.0%}",
            inline=True
        )
        
        embed.add_field(
            name="Action",
            value=config['action'].title(),
            inline=True
        )
        
        embed.add_field(
            name="Log Channel",
            value=log_channel,
            inline=True
        )
        
        embed.add_field(
            name="Active Checks",
            value="\n".join(f"✅ {check}" for check in checks) if checks else "None",
            inline=False
        )
        
        # Count whitelisted users
        whitelist_count = len(self.whitelisted_users.get(interaction.guild_id, set()))
        embed.add_field(
            name="Whitelisted Users",
            value=f"{whitelist_count} users bypass AI moderation",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aimod-threshold", description="Set AI moderation confidence threshold")
    @app_commands.describe(threshold="Confidence threshold (0-100, higher = stricter)")
    @app_commands.default_permissions(administrator=True)
    async def aimod_threshold(self, interaction: discord.Interaction, threshold: int):
        """Set confidence threshold."""
        if not 0 <= threshold <= 100:
            await interaction.response.send_message(
                "❌ Threshold must be between 0 and 100.",
                ephemeral=True
            )
            return
        
        threshold_decimal = threshold / 100.0
        
        await self.bot.db.ensure_guild(interaction.guild_id)
        
        await self.bot.db.execute(
            """
            INSERT INTO guild_config (guild_id, ai_mod_threshold)
            VALUES ($2, $1)
            ON CONFLICT (guild_id)
            DO UPDATE SET ai_mod_threshold = $1
            """,
            threshold_decimal, interaction.guild_id
        )
        
        await interaction.response.send_message(
            f"✅ AI moderation threshold set to {threshold}%.\n"
            f"Only messages with {threshold}%+ confidence will be actioned."
        )
    
    @app_commands.command(name="aimod-action", description="Set AI moderation action")
    @app_commands.describe(action="Action to take on flagged messages")
    @app_commands.choices(action=[
        app_commands.Choice(name="Warn (Delete + Warning)", value="warn"),
        app_commands.Choice(name="Timeout (10 minutes)", value="timeout"),
        app_commands.Choice(name="Kick", value="kick"),
        app_commands.Choice(name="Log Only (No Action)", value="log")
    ])
    @app_commands.default_permissions(administrator=True)
    async def aimod_action(self, interaction: discord.Interaction, action: str):
        """Set the action for AI mod violations."""
        await self.bot.db.ensure_guild(interaction.guild_id)
        
        await self.bot.db.execute(
            """
            INSERT INTO guild_config (guild_id, ai_mod_action)
            VALUES ($2, $1)
            ON CONFLICT (guild_id)
            DO UPDATE SET ai_mod_action = $1
            """,
            action, interaction.guild_id
        )
        
        await interaction.response.send_message(
            f"✅ AI moderation action set to: **{action.title()}**"
        )
    
    @app_commands.command(name="aimod-logchannel", description="Set AI moderation log channel")
    @app_commands.describe(channel="Channel for AI moderation logs")
    @app_commands.default_permissions(administrator=True)
    async def aimod_logchannel(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ):
        """Set log channel."""
        channel_id = channel.id if channel else None
        
        await self.bot.db.ensure_guild(interaction.guild_id)
        
        await self.bot.db.execute(
            """
            INSERT INTO guild_config (guild_id, ai_mod_log_channel)
            VALUES ($2, $1)
            ON CONFLICT (guild_id)
            DO UPDATE SET ai_mod_log_channel = $1
            """,
            channel_id, interaction.guild_id
        )
        
        if channel:
            await interaction.response.send_message(
                f"✅ AI moderation logs will be sent to {channel.mention}"
            )
        else:
            await interaction.response.send_message(
                "✅ AI moderation logging disabled."
            )
    
    @app_commands.command(name="aimod-whitelist", description="Manage AI moderation whitelist")
    @app_commands.describe(
        action="Add or remove user from whitelist",
        user="User to whitelist/unwhitelist"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="List", value="list")
    ])
    @app_commands.default_permissions(administrator=True)
    async def aimod_whitelist(
        self,
        interaction: discord.Interaction,
        action: str,
        user: Optional[discord.Member] = None
    ):
        """Manage whitelist."""
        if action == "list":
            whitelist = self.whitelisted_users.get(interaction.guild_id, set())
            
            if not whitelist:
                await interaction.response.send_message(
                    "📝 No users are whitelisted from AI moderation.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🤖 AI Moderation Whitelist",
                description=f"**{len(whitelist)}** users bypass AI moderation",
                color=discord.Color.blue()
            )
            
            user_list = []
            for user_id in list(whitelist)[:20]:  # Limit to 20
                member = interaction.guild.get_member(user_id)
                if member:
                    user_list.append(f"• {member.mention} ({member})")
                else:
                    user_list.append(f"• User ID: {user_id}")
            
            embed.add_field(
                name="Whitelisted Users",
                value="\n".join(user_list) if user_list else "None",
                inline=False
            )
            
            if len(whitelist) > 20:
                embed.set_footer(text=f"Showing 20 of {len(whitelist)} users")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not user:
            await interaction.response.send_message(
                "❌ Please specify a user.",
                ephemeral=True
            )
            return
        
        if action == "add":
            # Add to database
            await self.bot.db.execute(
                """
                INSERT INTO ai_mod_whitelist (guild_id, user_id)
                VALUES ($1, $2)
                ON CONFLICT (guild_id, user_id) DO NOTHING
                """,
                interaction.guild_id, user.id
            )
            
            # Add to cache
            if interaction.guild_id not in self.whitelisted_users:
                self.whitelisted_users[interaction.guild_id] = set()
            self.whitelisted_users[interaction.guild_id].add(user.id)
            
            await interaction.response.send_message(
                f"✅ {user.mention} added to AI moderation whitelist.\n"
                f"Their messages will not be checked by AI moderation."
            )
        
        elif action == "remove":
            # Remove from database
            result = await self.bot.db.execute(
                """
                DELETE FROM ai_mod_whitelist
                WHERE guild_id = $1 AND user_id = $2
                """,
                interaction.guild_id, user.id
            )
            
            # Remove from cache
            if interaction.guild_id in self.whitelisted_users:
                self.whitelisted_users[interaction.guild_id].discard(user.id)
            
            if result == "DELETE 0":
                await interaction.response.send_message(
                    f"❌ {user.mention} is not whitelisted.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"✅ {user.mention} removed from AI moderation whitelist."
                )
    
    @app_commands.command(name="aimod-checks", description="Toggle specific AI moderation checks")
    @app_commands.describe(
        toxicity="Check for toxicity and hate speech",
        spam="Check for spam content",
        nsfw="Check for NSFW content"
    )
    @app_commands.default_permissions(administrator=True)
    async def aimod_checks(
        self,
        interaction: discord.Interaction,
        toxicity: Optional[bool] = None,
        spam: Optional[bool] = None,
        nsfw: Optional[bool] = None
    ):
        """Toggle specific checks."""
        await self.bot.db.ensure_guild(interaction.guild_id)
        
        updates = []
        if toxicity is not None:
            await self.bot.db.execute(
                """
                INSERT INTO guild_config (guild_id, ai_mod_check_toxicity)
                VALUES ($2, $1)
                ON CONFLICT (guild_id)
                DO UPDATE SET ai_mod_check_toxicity = $1
                """,
                toxicity, interaction.guild_id
            )
            updates.append(f"Toxicity: {'✅ Enabled' if toxicity else '❌ Disabled'}")
        
        if spam is not None:
            await self.bot.db.execute(
                """
                INSERT INTO guild_config (guild_id, ai_mod_check_spam)
                VALUES ($2, $1)
                ON CONFLICT (guild_id)
                DO UPDATE SET ai_mod_check_spam = $1
                """,
                spam, interaction.guild_id
            )
            updates.append(f"Spam: {'✅ Enabled' if spam else '❌ Disabled'}")
        
        if nsfw is not None:
            await self.bot.db.execute(
                """
                INSERT INTO guild_config (guild_id, ai_mod_check_nsfw)
                VALUES ($2, $1)
                ON CONFLICT (guild_id)
                DO UPDATE SET ai_mod_check_nsfw = $1
                """,
                nsfw, interaction.guild_id
            )
            updates.append(f"NSFW: {'✅ Enabled' if nsfw else '❌ Disabled'}")
        
        if updates:
            await interaction.response.send_message(
                "✅ AI moderation checks updated:\n" + "\n".join(f"• {u}" for u in updates)
            )
        else:
            await interaction.response.send_message(
                "❌ No changes specified. Use at least one parameter.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(AIMod(bot))
