"""
Welcome & Goodbye Messages

Sends customizable messages when members join or leave the server.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import random


class Welcome(commands.Cog):
    """Welcome and goodbye message system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def _format_message(self, template: str, member: discord.Member) -> str:
        """Format a message template with member/guild info."""
        return template.format(
            user=member.mention,
            username=member.name,
            server=member.guild.name,
            member_count=member.guild.member_count
        )
    
    @app_commands.command(name="welcome-set", description="Set the welcome message")
    @app_commands.describe(
        channel="Channel to send welcome messages",
        message="Welcome message (use {user} for mention, {username}, {server}, {member_count})"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def welcome_set(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str
    ):
        """Set welcome message and channel."""
        await self.bot.db.execute(
            """
            UPDATE guild_config 
            SET welcome_channel = $1, welcome_message = $2 
            WHERE guild_id = $3
            """,
            channel.id, message, interaction.guild_id
        )
        
        # Test message
        test_msg = self._format_message(message, interaction.user)
        
        embed = discord.Embed(
            title="✅ Welcome Message Set",
            description=f"Channel: {channel.mention}\n\n**Preview:**\n{test_msg}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="welcome-disable", description="Disable welcome messages")
    @app_commands.default_permissions(manage_guild=True)
    async def welcome_disable(self, interaction: discord.Interaction):
        """Disable welcome messages."""
        await self.bot.db.execute(
            """
            UPDATE guild_config 
            SET welcome_channel = NULL, welcome_message = NULL 
            WHERE guild_id = $1
            """,
            interaction.guild_id
        )
        
        await interaction.response.send_message("✅ Welcome messages disabled.")
    
    @app_commands.command(name="goodbye-set", description="Set the goodbye message")
    @app_commands.describe(
        channel="Channel to send goodbye messages",
        message="Goodbye message (use {username}, {server}, {member_count})"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def goodbye_set(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str
    ):
        """Set goodbye message and channel."""
        await self.bot.db.execute(
            """
            UPDATE guild_config 
            SET goodbye_channel = $1, goodbye_message = $2 
            WHERE guild_id = $3
            """,
            channel.id, message, interaction.guild_id
        )
        
        # Test message
        test_msg = self._format_message(message, interaction.user)
        
        embed = discord.Embed(
            title="✅ Goodbye Message Set",
            description=f"Channel: {channel.mention}\n\n**Preview:**\n{test_msg}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="goodbye-disable", description="Disable goodbye messages")
    @app_commands.default_permissions(manage_guild=True)
    async def goodbye_disable(self, interaction: discord.Interaction):
        """Disable goodbye messages."""
        await self.bot.db.execute(
            """
            UPDATE guild_config 
            SET goodbye_channel = NULL, goodbye_message = NULL 
            WHERE guild_id = $1
            """,
            interaction.guild_id
        )
        
        await interaction.response.send_message("✅ Goodbye messages disabled.")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Send welcome message when a member joins."""
        if member.bot:
            return
        
        # Get guild config
        config = await self.bot.db.fetchrow(
            """
            SELECT welcome_channel, welcome_message 
            FROM guild_config 
            WHERE guild_id = $1
            """,
            member.guild.id
        )
        
        if not config or not config['welcome_channel'] or not config['welcome_message']:
            return
        
        channel = member.guild.get_channel(config['welcome_channel'])
        if not channel:
            return
        
        # Format and send message
        message = self._format_message(config['welcome_message'], member)
        
        try:
            await channel.send(message)
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Send goodbye message when a member leaves."""
        if member.bot:
            return
        
        # Get guild config
        config = await self.bot.db.fetchrow(
            """
            SELECT goodbye_channel, goodbye_message 
            FROM guild_config 
            WHERE guild_id = $1
            """,
            member.guild.id
        )
        
        if not config or not config['goodbye_channel'] or not config['goodbye_message']:
            return
        
        channel = member.guild.get_channel(config['goodbye_channel'])
        if not channel:
            return
        
        # Format and send message
        message = self._format_message(config['goodbye_message'], member)
        
        try:
            await channel.send(message)
        except discord.Forbidden:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
