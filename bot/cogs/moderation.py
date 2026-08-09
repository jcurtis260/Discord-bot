"""
Moderation cog for Discord bot.
Handles moderation commands and auto-moderation features.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)


class Moderation(commands.Cog):
    """Moderation commands and auto-moderation."""
    
    def __init__(self, bot):
        """Initialize moderation cog."""
        self.bot = bot
        self.spam_tracker = {}  # Track spam (user_id: [timestamps])
    
    async def log_action(self, guild_id: int, action: str, moderator_id: int,
                        target_user_id: Optional[int], reason: Optional[str]) -> None:
        """Log moderation action to database."""
        try:
            await self.bot.db.execute(
                """
                INSERT INTO mod_log (guild_id, action, moderator_id, target_user_id, reason)
                VALUES ($1, $2, $3, $4, $5)
                """,
                guild_id, action, moderator_id, target_user_id, reason
            )
        except Exception as e:
            logger.error(f"Failed to log moderation action: {e}")
    
    async def add_infraction(self, guild_id: int, user_id: int, moderator_id: int,
                           infraction_type: str, reason: str, duration: Optional[int] = None) -> int:
        """Add an infraction to the database."""
        expires_at = None
        if duration:
            expires_at = datetime.utcnow() + timedelta(seconds=duration)
        
        result = await self.bot.db.fetchrow(
            """
            INSERT INTO infractions (guild_id, user_id, moderator_id, type, reason, duration, expires_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            guild_id, user_id, moderator_id, infraction_type, reason, duration, expires_at
        )
        
        return result['id']
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(
        user="The user to warn",
        reason="Reason for the warning"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Warn a user."""
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot warn this user (role hierarchy).", ephemeral=True)
            return
        
        # Add infraction
        infraction_id = await self.add_infraction(
            interaction.guild.id, user.id, interaction.user.id, 'warn', reason
        )
        
        # Log action
        await self.log_action(interaction.guild.id, 'warn', interaction.user.id, user.id, reason)
        
        # Send DM to user
        try:
            embed = discord.Embed(
                title="⚠️ Warning",
                description=f"You have been warned in **{interaction.guild.name}**",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            await user.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass  # User has DMs disabled or delivery failed
        
        # Respond
        embed = discord.Embed(
            title="✅ User Warned",
            description=f"{user.mention} has been warned",
            color=discord.Color.green()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Infraction ID", value=f"#{infraction_id}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.describe(
        user="The user to mute",
        duration="Duration (e.g., 10m, 1h, 1d)",
        reason="Reason for the mute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, 
                   duration: str, reason: str):
        """Mute a user."""
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot mute this user (role hierarchy).", ephemeral=True)
            return
        
        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if duration_seconds is None:
            await interaction.response.send_message("❌ Invalid duration format. Use: 10m, 1h, 1d", ephemeral=True)
            return
        
        # Timeout user
        timeout_until = datetime.utcnow() + timedelta(seconds=duration_seconds)
        
        try:
            await user.timeout(timeout_until, reason=reason)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to timeout this user.", ephemeral=True)
            return
        
        # Add infraction
        infraction_id = await self.add_infraction(
            interaction.guild.id, user.id, interaction.user.id, 'mute', reason, duration_seconds
        )
        
        # Log action
        await self.log_action(interaction.guild.id, 'mute', interaction.user.id, user.id, reason)
        
        # Respond
        embed = discord.Embed(
            title="🔇 User Muted",
            description=f"{user.mention} has been muted for {duration}",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Infraction ID", value=f"#{infraction_id}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.describe(user="The user to unmute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        """Unmute a user."""
        try:
            await user.timeout(None)
            await interaction.response.send_message(f"✅ {user.mention} has been unmuted.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unmute this user.", ephemeral=True)
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        user="The user to kick",
        reason="Reason for the kick"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Kick a user."""
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot kick this user (role hierarchy).", ephemeral=True)
            return
        
        # Add infraction
        await self.add_infraction(
            interaction.guild.id, user.id, interaction.user.id, 'kick', reason
        )
        
        # Log action
        await self.log_action(interaction.guild.id, 'kick', interaction.user.id, user.id, reason)
        
        # Kick user
        try:
            await user.kick(reason=reason)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick this user.", ephemeral=True)
            return
        
        # Respond
        embed = discord.Embed(
            title="👢 User Kicked",
            description=f"{user.mention} has been kicked",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="The user to ban",
        duration="Duration (e.g., 7d, permanent)",
        reason="Reason for the ban"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, 
                  duration: str, reason: str):
        """Ban a user."""
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You cannot ban this user (role hierarchy).", ephemeral=True)
            return
        
        # Parse duration
        duration_seconds = None
        if duration.lower() != "permanent":
            duration_seconds = self.parse_duration(duration)
            if duration_seconds is None:
                await interaction.response.send_message("❌ Invalid duration format. Use: 7d, 30d, or 'permanent'", ephemeral=True)
                return
        
        # Add infraction
        await self.add_infraction(
            interaction.guild.id, user.id, interaction.user.id, 'ban', reason, duration_seconds
        )
        
        # Log action
        await self.log_action(interaction.guild.id, 'ban', interaction.user.id, user.id, reason)
        
        # Ban user
        try:
            await user.ban(reason=reason, delete_message_days=1)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban this user.", ephemeral=True)
            return
        
        # Respond
        duration_text = duration if duration.lower() == "permanent" else f"{duration} (temporary)"
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"{user.mention} has been banned",
            color=discord.Color.red()
        )
        embed.add_field(name="Duration", value=duration_text, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clear", description="Delete multiple messages")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        """Clear messages in a channel."""
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"✅ Deleted {len(deleted)} message(s).", ephemeral=True)
            
            # Log action
            await self.log_action(interaction.guild.id, 'clear', interaction.user.id, None, 
                                f"Cleared {len(deleted)} messages")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages.", ephemeral=True)
    
    @app_commands.command(name="infractions", description="View a user's infractions")
    @app_commands.describe(user="The user to check")
    async def infractions(self, interaction: discord.Interaction, user: discord.Member):
        """View user infractions."""
        infractions = await self.bot.db.fetch(
            """
            SELECT id, type, reason, created_at, active
            FROM infractions
            WHERE guild_id = $1 AND user_id = $2
            ORDER BY created_at DESC
            LIMIT 10
            """,
            interaction.guild.id, user.id
        )
        
        if not infractions:
            await interaction.response.send_message(f"{user.mention} has no infractions.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 Infractions for {user.display_name}",
            color=discord.Color.blue()
        )
        
        for infraction in infractions:
            status = "🟢 Active" if infraction['active'] else "⚫ Inactive"
            embed.add_field(
                name=f"#{infraction['id']} - {infraction['type'].upper()} {status}",
                value=f"{infraction['reason']}\n{infraction['created_at'].strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds."""
        match = re.match(r'^(\d+)([smhd])$', duration_str.lower())
        if not match:
            return None
        
        amount, unit = match.groups()
        amount = int(amount)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        return amount * multipliers.get(unit, 0)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(Moderation(bot))
