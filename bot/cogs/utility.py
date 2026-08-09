"""
Utility cog for Discord bot.
Provides general utility and information commands.
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import logging
import platform
import psutil

logger = logging.getLogger(__name__)


class Utility(commands.Cog):
    """Utility and information commands."""
    
    def __init__(self, bot):
        """Initialize utility cog."""
        self.bot = bot
    
    @app_commands.command(name="help", description="Show bot help and commands")
    async def help(self, interaction: discord.Interaction):
        """Display help information."""
        embed = discord.Embed(
            title="🤖 Bot Help",
            description="AI-Powered Community Manager",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Leveling",
            value="`/rank` `/leaderboard` `/setxp` `/addxp` `/rolereward`",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Moderation",
            value="`/warn` `/mute` `/unmute` `/kick` `/ban` `/clear` `/infractions`",
            inline=False
        )
        
        embed.add_field(
            name="💰 Economy",
            value="`/balance` `/daily` `/pay` `/shop` `/buy`",
            inline=False
        )
        
        embed.add_field(
            name="🎉 Giveaways",
            value="`/giveaway` - Create giveaways\nReact with 🎉 to enter!",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Bot Settings",
            value="`/botconfig` `/prefix` `/togglefeature` `/botnickname`\n"
                  "`/botavatar` `/botname` `/botstatus` (owner only)",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Info",
            value="`/help` `/serverinfo` `/userinfo` `/botinfo` `/ping`",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Display bot latency."""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Display server information")
    async def serverinfo(self, interaction: discord.Interaction):
        """Show information about the server."""
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Member counts
        total_members = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = total_members - bots
        
        embed.add_field(name="👥 Members", value=f"{total_members:,} ({humans:,} humans, {bots:,} bots)", inline=False)
        embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=False)
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="💬 Channels", value=f"{len(guild.channels):,}", inline=True)
        embed.add_field(name="🎭 Roles", value=f"{len(guild.roles):,}", inline=True)
        embed.add_field(name="😀 Emojis", value=f"{len(guild.emojis):,}", inline=True)
        embed.add_field(name="🚀 Boosts", value=f"{guild.premium_subscription_count} (Level {guild.premium_tier})", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="userinfo", description="Display user information")
    @app_commands.describe(user="The user to get info about (defaults to yourself)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Show information about a user."""
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"👤 {user.display_name}",
            color=user.color or discord.Color.blue()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="Username", value=str(user), inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(user.created_at.timestamp())}:F>", inline=False)
        embed.add_field(name="Joined", value=f"<t:{int(user.joined_at.timestamp())}:F>", inline=False)
        
        roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
        if roles:
            embed.add_field(
                name=f"Roles ({len(roles)})",
                value=" ".join(roles[:10]) + ("..." if len(roles) > 10 else ""),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="botinfo", description="Display bot information")
    async def botinfo(self, interaction: discord.Interaction):
        """Show information about the bot."""
        embed = discord.Embed(
            title=f"🤖 {self.bot.user.name}",
            description="AI-Powered Community Manager",
            color=discord.Color.blue()
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Stats
        total_users = sum(g.member_count for g in self.bot.guilds)
        
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds):,}", inline=True)
        embed.add_field(name="Users", value=f"{total_users:,}", inline=True)
        embed.add_field(name="Commands", value=f"{len(self.bot.tree.get_commands()):,}", inline=True)
        
        # System info
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()
        
        embed.add_field(name="Memory Usage", value=f"{memory_usage:.2f} MB", inline=True)
        embed.add_field(name="CPU Usage", value=f"{cpu_usage:.1f}%", inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        
        # Bot stats
        embed.add_field(name="Commands Used", value=f"{self.bot.commands_used:,}", inline=True)
        embed.add_field(name="Messages Seen", value=f"{self.bot.messages_seen:,}", inline=True)
        
        embed.set_footer(text=f"discord.py {discord.__version__}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="avatar", description="Display a user's avatar")
    @app_commands.describe(user="The user to get avatar from (defaults to yourself)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display user's avatar."""
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ {user.display_name}'s Avatar",
            color=user.color or discord.Color.blue()
        )
        
        embed.set_image(url=user.display_avatar.url)
        embed.description = f"[Download]({user.display_avatar.url})"
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(Utility(bot))
