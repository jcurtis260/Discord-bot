"""
Leveling cog for Discord bot.
Handles XP, levels, and role rewards.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timedelta
import logging
import math
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class Leveling(commands.Cog):
    """Leveling and XP system."""
    
    def __init__(self, bot):
        """Initialize leveling cog."""
        self.bot = bot
    
    def calculate_level(self, xp: int) -> int:
        """Calculate level from XP."""
        # Level formula: level = floor(0.1 * sqrt(xp))
        return math.floor(0.1 * math.sqrt(xp))
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calculate XP required for a specific level."""
        # Inverse of level formula: xp = (level / 0.1)^2
        return math.ceil((level / 0.1) ** 2)
    
    async def get_user_data(self, guild_id: int, user_id: int) -> dict:
        """Get user leveling data."""
        data = await self.bot.db.fetchrow(
            """
            SELECT xp, level, message_count, last_xp_gain
            FROM guild_members
            WHERE guild_id = $1 AND user_id = $2
            """,
            guild_id, user_id
        )
        
        if data is None:
            # Initialize user
            await self.bot.db.execute(
                """
                INSERT INTO guild_members (guild_id, user_id, xp, level, message_count)
                VALUES ($1, $2, 0, 0, 0)
                ON CONFLICT (guild_id, user_id) DO NOTHING
                """,
                guild_id, user_id
            )
            return {'xp': 0, 'level': 0, 'message_count': 0, 'last_xp_gain': None}
        
        return dict(data)
    
    async def add_xp(self, guild_id: int, user_id: int, amount: int) -> tuple[int, bool]:
        """
        Add XP to a user.
        
        Returns:
            Tuple of (new_level, leveled_up)
        """
        # Get current data
        data = await self.get_user_data(guild_id, user_id)
        
        # Calculate new XP and level
        new_xp = data['xp'] + amount
        old_level = data['level']
        new_level = self.calculate_level(new_xp)
        leveled_up = new_level > old_level
        
        # Update database
        await self.bot.db.execute(
            """
            UPDATE guild_members
            SET xp = $1, level = $2, message_count = message_count + 1, last_xp_gain = $3
            WHERE guild_id = $4 AND user_id = $5
            """,
            new_xp, new_level, datetime.utcnow(), guild_id, user_id
        )
        
        return new_level, leveled_up
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle XP gain from messages."""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Check if leveling is enabled
        config = await self.bot.db.fetchrow(
            "SELECT xp_enabled, xp_rate, xp_cooldown FROM guild_config WHERE guild_id = $1",
            message.guild.id
        )
        
        if not config or not config['xp_enabled']:
            return
        
        # Check cooldown (with Redis null safety)
        if self.bot.cache:
            cache_key = f"xp_cooldown:{message.guild.id}:{message.author.id}"
            if await self.bot.cache.exists(cache_key):
                return  # User is on cooldown
        else:
            # Fallback: check database for cooldown if Redis unavailable
            user_data = await self.get_user_data(message.guild.id, message.author.id)
            if user_data.get('last_xp_gain'):
                cooldown = timedelta(seconds=config['xp_cooldown'])
                time_since_last = datetime.utcnow() - user_data['last_xp_gain']
                if time_since_last < cooldown:
                    return  # User is on cooldown
        
        # Add XP
        xp_amount = config['xp_rate']
        new_level, leveled_up = await self.add_xp(message.guild.id, message.author.id, xp_amount)
        
        # Set cooldown (with Redis null safety)
        if self.bot.cache:
            cache_key = f"xp_cooldown:{message.guild.id}:{message.author.id}"
            await self.bot.cache.set(cache_key, "1", ttl=config['xp_cooldown'])
        
        # Handle level up
        if leveled_up:
            await self.handle_level_up(message, new_level)
    
    async def handle_level_up(self, message: discord.Message, new_level: int):
        """Handle level up events."""
        # Check if announcements are enabled
        config = await self.bot.db.fetchrow(
            "SELECT announce_level_up FROM guild_config WHERE guild_id = $1",
            message.guild.id
        )
        
        if config and config['announce_level_up']:
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} just reached **Level {new_level}**!",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed, delete_after=10)
        
        # Check for role rewards
        rewards = await self.bot.db.fetch(
            """
            SELECT role_id FROM role_rewards
            WHERE guild_id = $1 AND required_level = $2
            """,
            message.guild.id, new_level
        )
        
        for reward in rewards:
            role = message.guild.get_role(reward['role_id'])
            if role and role not in message.author.roles:
                try:
                    await message.author.add_roles(role, reason=f"Level {new_level} reward")
                    await message.channel.send(
                        f"🎁 {message.author.mention} earned the {role.mention} role!",
                        delete_after=10
                    )
                except discord.Forbidden:
                    logger.warning(f"Failed to assign role reward in guild {message.guild.id}")
    
    @app_commands.command(name="rank", description="View your or another user's rank")
    @app_commands.describe(user="The user to check (defaults to yourself)")
    async def rank(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Display user's rank card."""
        user = user or interaction.user
        
        # Get user data
        data = await self.get_user_data(interaction.guild.id, user.id)
        
        # Calculate progress to next level
        current_level_xp = self.calculate_xp_for_level(data['level'])
        next_level_xp = self.calculate_xp_for_level(data['level'] + 1)
        xp_for_next_level = next_level_xp - current_level_xp
        xp_progress = data['xp'] - current_level_xp
        progress_percent = (xp_progress / xp_for_next_level) * 100 if xp_for_next_level > 0 else 100
        
        # Get user rank
        rank = await self.bot.db.fetchval(
            """
            SELECT COUNT(*) + 1
            FROM guild_members
            WHERE guild_id = $1 AND xp > (
                SELECT xp FROM guild_members WHERE guild_id = $1 AND user_id = $2
            )
            """,
            interaction.guild.id, user.id
        )
        
        # Create embed
        embed = discord.Embed(
            title=f"📊 Rank Card - {user.display_name}",
            color=user.color or discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Rank", value=f"#{rank}", inline=True)
        embed.add_field(name="Level", value=str(data['level']), inline=True)
        embed.add_field(name="XP", value=f"{data['xp']:,}", inline=True)
        embed.add_field(
            name="Progress",
            value=f"{xp_progress:,} / {xp_for_next_level:,} XP ({progress_percent:.1f}%)",
            inline=False
        )
        embed.add_field(name="Messages Sent", value=f"{data['message_count']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="View the server leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """Display server leaderboard."""
        # Get top 10 users
        top_users = await self.bot.db.fetch(
            """
            SELECT user_id, xp, level, message_count
            FROM guild_members
            WHERE guild_id = $1
            ORDER BY xp DESC
            LIMIT 10
            """,
            interaction.guild.id
        )
        
        if not top_users:
            await interaction.response.send_message("No users found in the leaderboard.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🏆 {interaction.guild.name} Leaderboard",
            description="Top 10 members by XP",
            color=discord.Color.gold()
        )
        
        for i, user_data in enumerate(top_users, 1):
            user = interaction.guild.get_member(user_data['user_id'])
            if user:
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                embed.add_field(
                    name=f"{medal} {user.display_name}",
                    value=f"Level {user_data['level']} • {user_data['xp']:,} XP",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setxp", description="Set a user's XP (Admin)")
    @app_commands.describe(
        user="The user to modify",
        amount="Amount of XP to set"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setxp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Set user's XP (admin only)."""
        if amount < 0:
            await interaction.response.send_message("❌ XP amount must be positive.", ephemeral=True)
            return
        
        new_level = self.calculate_level(amount)
        
        await self.bot.db.execute(
            """
            UPDATE guild_members
            SET xp = $1, level = $2
            WHERE guild_id = $3 AND user_id = $4
            """,
            amount, new_level, interaction.guild.id, user.id
        )
        
        await interaction.response.send_message(
            f"✅ Set {user.mention}'s XP to {amount:,} (Level {new_level})"
        )
    
    @app_commands.command(name="addxp", description="Add XP to a user (Admin)")
    @app_commands.describe(
        user="The user to modify",
        amount="Amount of XP to add"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Add XP to user (admin only)."""
        if amount <= 0:
            await interaction.response.send_message("❌ XP amount must be positive.", ephemeral=True)
            return
        
        new_level, leveled_up = await self.add_xp(interaction.guild.id, user.id, amount)
        
        message = f"✅ Added {amount:,} XP to {user.mention} (Now Level {new_level})"
        if leveled_up:
            message += " 🎉"
        
        await interaction.response.send_message(message)
    
    @app_commands.command(name="rolereward", description="Add a role reward for reaching a level (Admin)")
    @app_commands.describe(
        level="The level required",
        role="The role to grant"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def rolereward(self, interaction: discord.Interaction, level: int, role: discord.Role):
        """Add a role reward."""
        if level < 1:
            await interaction.response.send_message("❌ Level must be at least 1.", ephemeral=True)
            return
        
        try:
            await self.bot.db.execute(
                """
                INSERT INTO role_rewards (guild_id, role_id, required_level)
                VALUES ($1, $2, $3)
                ON CONFLICT (guild_id, role_id) DO UPDATE SET required_level = $3
                """,
                interaction.guild.id, role.id, level
            )
            
            await interaction.response.send_message(
                f"✅ Added role reward: {role.mention} at Level {level}"
            )
        except Exception as e:
            logger.error(f"Failed to add role reward: {e}")
            await interaction.response.send_message("❌ Failed to add role reward.", ephemeral=True)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(Leveling(bot))
