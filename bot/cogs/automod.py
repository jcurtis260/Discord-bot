"""
Auto-Moderation System

Automatic moderation for spam, bad words, mass mentions, etc.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
import re


class AutoMod(commands.Cog):
    """Automatic moderation system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Track message spam
        self.message_tracker = defaultdict(list)  # user_id: [timestamps]
        self.mention_tracker = defaultdict(list)  # user_id: [timestamps]
        
        # Cache bad words per guild
        self.bad_words_cache = {}  # guild_id: [words]
    
    async def cog_load(self):
        """Load auto-mod settings."""
        await self._load_bad_words()
    
    async def _load_bad_words(self):
        """Load bad words from database."""
        if not self.bot.db:
            return
        
        guilds = await self.bot.db.fetch("SELECT guild_id, automod_bad_words FROM guild_config")
        
        for guild in guilds:
            if guild['automod_bad_words']:
                self.bad_words_cache[guild['guild_id']] = guild['automod_bad_words']
    
    async def _get_automod_config(self, guild_id: int) -> dict:
        """Get auto-mod configuration for a guild."""
        config = await self.bot.db.fetchrow(
            """
            SELECT automod_enabled, automod_spam_threshold, automod_mention_threshold,
                   automod_bad_words, automod_caps_threshold, automod_action
            FROM guild_config
            WHERE guild_id = $1
            """,
            guild_id
        )
        
        if not config:
            return {
                'enabled': False,
                'spam_threshold': 5,
                'mention_threshold': 5,
                'bad_words': [],
                'caps_threshold': 0.7,
                'action': 'warn'
            }
        
        return {
            'enabled': config['automod_enabled'] or False,
            'spam_threshold': config['automod_spam_threshold'] or 5,
            'mention_threshold': config['automod_mention_threshold'] or 5,
            'bad_words': config['automod_bad_words'] or [],
            'caps_threshold': config['automod_caps_threshold'] or 0.7,
            'action': config['automod_action'] or 'warn'
        }
    
    async def _take_action(self, message: discord.Message, reason: str, action: str):
        """Take moderation action."""
        # Delete the message
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        # Warn user
        if action == 'warn':
            try:
                await message.channel.send(
                    f"⚠️ {message.author.mention}, {reason}",
                    delete_after=10
                )
            except discord.Forbidden:
                pass
        
        # Timeout user
        elif action == 'timeout':
            try:
                await message.author.timeout(
                    timedelta(minutes=5),
                    reason=f"Auto-mod: {reason}"
                )
                await message.channel.send(
                    f"🔇 {message.author.mention} has been timed out for 5 minutes. Reason: {reason}",
                    delete_after=10
                )
            except discord.Forbidden:
                pass
        
        # Kick user
        elif action == 'kick':
            try:
                await message.author.kick(reason=f"Auto-mod: {reason}")
                await message.channel.send(
                    f"👢 {message.author.mention} has been kicked. Reason: {reason}"
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
            f'automod_{action}',
            reason
        )
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check messages for auto-mod violations."""
        if message.author.bot or not message.guild:
            return
        
        # Skip if user has manage messages permission
        if message.author.guild_permissions.manage_messages:
            return
        
        config = await self._get_automod_config(message.guild.id)
        
        if not config['enabled']:
            return
        
        # Check for spam (multiple messages in short time)
        now = datetime.utcnow()
        user_messages = self.message_tracker[message.author.id]
        
        # Clean old messages (older than 10 seconds)
        user_messages = [ts for ts in user_messages if (now - ts).total_seconds() < 10]
        user_messages.append(now)
        self.message_tracker[message.author.id] = user_messages
        
        if len(user_messages) >= config['spam_threshold']:
            await self._take_action(
                message,
                "spam detected (too many messages in a short time)",
                config['action']
            )
            self.message_tracker[message.author.id] = []
            return
        
        # Check for mass mentions
        mentions = len(message.mentions)
        if mentions >= config['mention_threshold']:
            await self._take_action(
                message,
                f"mass mention detected ({mentions} mentions)",
                config['action']
            )
            return
        
        # Check for bad words
        if config['bad_words']:
            content_lower = message.content.lower()
            for word in config['bad_words']:
                if word.lower() in content_lower:
                    await self._take_action(
                        message,
                        "message contained prohibited words",
                        config['action']
                    )
                    return
        
        # Check for excessive caps
        if len(message.content) > 10:
            caps_count = sum(1 for c in message.content if c.isupper())
            caps_ratio = caps_count / len(message.content)
            
            if caps_ratio >= config['caps_threshold']:
                await self._take_action(
                    message,
                    f"excessive caps ({int(caps_ratio * 100)}% uppercase)",
                    config['action']
                )
                return
    
    @app_commands.command(name="automod-enable", description="Enable auto-moderation")
    @app_commands.default_permissions(manage_guild=True)
    async def automod_enable(self, interaction: discord.Interaction):
        """Enable auto-moderation."""
        await self.bot.db.execute(
            "UPDATE guild_config SET automod_enabled = TRUE WHERE guild_id = $1",
            interaction.guild_id
        )
        
        await interaction.response.send_message("✅ Auto-moderation enabled.")
    
    @app_commands.command(name="automod-disable", description="Disable auto-moderation")
    @app_commands.default_permissions(manage_guild=True)
    async def automod_disable(self, interaction: discord.Interaction):
        """Disable auto-moderation."""
        await self.bot.db.execute(
            "UPDATE guild_config SET automod_enabled = FALSE WHERE guild_id = $1",
            interaction.guild_id
        )
        
        await interaction.response.send_message("✅ Auto-moderation disabled.")
    
    @app_commands.command(name="automod-config", description="View auto-mod configuration")
    async def automod_config(self, interaction: discord.Interaction):
        """View auto-mod configuration."""
        config = await self._get_automod_config(interaction.guild_id)
        
        status = "✅ Enabled" if config['enabled'] else "❌ Disabled"
        
        embed = discord.Embed(
            title="⚙️ Auto-Moderation Configuration",
            description=f"**Status:** {status}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Spam Threshold",
            value=f"{config['spam_threshold']} messages in 10 seconds",
            inline=True
        )
        
        embed.add_field(
            name="Mention Threshold",
            value=f"{config['mention_threshold']} mentions per message",
            inline=True
        )
        
        embed.add_field(
            name="Action",
            value=config['action'].title(),
            inline=True
        )
        
        embed.add_field(
            name="Caps Threshold",
            value=f"{int(config['caps_threshold'] * 100)}% uppercase",
            inline=True
        )
        
        embed.add_field(
            name="Bad Words",
            value=f"{len(config['bad_words'])} words filtered" if config['bad_words'] else "None",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="automod-action", description="Set auto-mod action")
    @app_commands.describe(action="Action to take (warn, timeout, kick)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Warn", value="warn"),
        app_commands.Choice(name="Timeout (5 min)", value="timeout"),
        app_commands.Choice(name="Kick", value="kick")
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def automod_action(self, interaction: discord.Interaction, action: str):
        """Set the action for auto-mod violations."""
        await self.bot.db.execute(
            "UPDATE guild_config SET automod_action = $1 WHERE guild_id = $2",
            action, interaction.guild_id
        )
        
        await interaction.response.send_message(
            f"✅ Auto-mod action set to: **{action.title()}**"
        )
    
    @app_commands.command(name="automod-badwords", description="Manage bad words filter")
    @app_commands.describe(
        action="Add or remove",
        words="Words to add/remove (comma separated)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="Clear", value="clear")
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def automod_badwords(
        self,
        interaction: discord.Interaction,
        action: str,
        words: Optional[str] = None
    ):
        """Manage the bad words filter."""
        current_words = self.bad_words_cache.get(interaction.guild_id, [])
        
        if action == "clear":
            await self.bot.db.execute(
                "UPDATE guild_config SET automod_bad_words = '{}' WHERE guild_id = $1",
                interaction.guild_id
            )
            self.bad_words_cache[interaction.guild_id] = []
            await interaction.response.send_message("✅ Bad words list cleared.")
            return
        
        if not words:
            await interaction.response.send_message(
                "❌ Please provide words to add/remove.",
                ephemeral=True
            )
            return
        
        word_list = [w.strip().lower() for w in words.split(',')]
        
        if action == "add":
            for word in word_list:
                if word not in current_words:
                    current_words.append(word)
            
            message = f"✅ Added {len(word_list)} word(s) to the filter."
        
        else:  # remove
            for word in word_list:
                if word in current_words:
                    current_words.remove(word)
            
            message = f"✅ Removed {len(word_list)} word(s) from the filter."
        
        # Update database
        await self.bot.db.execute(
            "UPDATE guild_config SET automod_bad_words = $1 WHERE guild_id = $2",
            current_words, interaction.guild_id
        )
        
        self.bad_words_cache[interaction.guild_id] = current_words
        
        await interaction.response.send_message(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
