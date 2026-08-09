"""
Reaction Roles

Allows users to get roles by reacting to messages.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
import json


class ReactionRoles(commands.Cog):
    """Reaction role system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Cache reaction role mappings
        self.reaction_roles = {}
    
    async def cog_load(self):
        """Load reaction roles from database."""
        await self._load_reaction_roles()
    
    async def _load_reaction_roles(self):
        """Load all reaction roles into cache."""
        if not self.bot.db:
            return
        
        roles = await self.bot.db.fetch("SELECT * FROM reaction_roles")
        
        for role in roles:
            key = (role['guild_id'], role['message_id'], role['emoji'])
            self.reaction_roles[key] = role['role_id']
    
    @app_commands.command(name="reactionrole-add", description="Add a reaction role to a message")
    @app_commands.describe(
        message_id="ID of the message",
        emoji="Emoji to react with",
        role="Role to give"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def rr_add(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: discord.Role
    ):
        """Add a reaction role."""
        try:
            message_id_int = int(message_id)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid message ID.",
                ephemeral=True
            )
            return
        
        # Validate role position
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message(
                "❌ I cannot assign this role as it's higher than or equal to my highest role.",
                ephemeral=True
            )
            return
        
        if role.managed:
            await interaction.response.send_message(
                "❌ This role is managed by an integration and cannot be assigned.",
                ephemeral=True
            )
            return
        
        # Try to fetch the message
        message = None
        for channel in interaction.guild.text_channels:
            try:
                message = await channel.fetch_message(message_id_int)
                break
            except (discord.NotFound, discord.Forbidden):
                continue
        
        if not message:
            await interaction.response.send_message(
                "❌ Could not find that message. Make sure I have access to the channel.",
                ephemeral=True
            )
            return
        
        # Add to database
        await self.bot.db.execute(
            """
            INSERT INTO reaction_roles (guild_id, message_id, channel_id, emoji, role_id)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id, message_id, emoji) 
            DO UPDATE SET role_id = EXCLUDED.role_id, channel_id = EXCLUDED.channel_id
            """,
            interaction.guild_id, message_id_int, message.channel.id, emoji, role.id
        )
        
        # Update cache
        key = (interaction.guild_id, message_id_int, emoji)
        self.reaction_roles[key] = role.id
        
        # Add reaction to message
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            pass
        
        embed = discord.Embed(
            title="✅ Reaction Role Added",
            description=f"React with {emoji} on [this message]({message.jump_url}) to get {role.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reactionrole-remove", description="Remove a reaction role")
    @app_commands.describe(
        message_id="ID of the message",
        emoji="Emoji to remove"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def rr_remove(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str
    ):
        """Remove a reaction role."""
        try:
            message_id_int = int(message_id)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid message ID.",
                ephemeral=True
            )
            return
        
        result = await self.bot.db.execute(
            """
            DELETE FROM reaction_roles 
            WHERE guild_id = $1 AND message_id = $2 AND emoji = $3
            """,
            interaction.guild_id, message_id_int, emoji
        )
        
        if result == "DELETE 0":
            await interaction.response.send_message(
                "❌ No reaction role found with that message ID and emoji.",
                ephemeral=True
            )
            return
        
        # Update cache
        key = (interaction.guild_id, message_id_int, emoji)
        self.reaction_roles.pop(key, None)
        
        await interaction.response.send_message("✅ Reaction role removed.")
    
    @app_commands.command(name="reactionrole-list", description="List all reaction roles")
    async def rr_list(self, interaction: discord.Interaction):
        """List all reaction roles for this server."""
        roles = await self.bot.db.fetch(
            """
            SELECT * FROM reaction_roles 
            WHERE guild_id = $1 
            ORDER BY created_at DESC
            """,
            interaction.guild_id
        )
        
        if not roles:
            await interaction.response.send_message(
                "📝 No reaction roles set up yet. Use `/reactionrole-add` to create one.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📝 Reaction Roles",
            description=f"Total: {len(roles)} reaction roles",
            color=discord.Color.blue()
        )
        
        for rr in roles[:10]:  # Limit to 10
            role = interaction.guild.get_role(rr['role_id'])
            channel = interaction.guild.get_channel(rr['channel_id'])
            
            role_name = role.mention if role else f"Unknown Role ({rr['role_id']})"
            channel_name = channel.mention if channel else "Unknown Channel"
            
            embed.add_field(
                name=f"{rr['emoji']} → {role_name}",
                value=f"Message: {rr['message_id']} in {channel_name}",
                inline=False
            )
        
        if len(roles) > 10:
            embed.set_footer(text=f"Showing 10 of {len(roles)} reaction roles")
        
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle reaction role assignment."""
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is a reaction role
        key = (payload.guild_id, payload.message_id, str(payload.emoji))
        role_id = self.reaction_roles.get(key)
        
        if not role_id:
            return
        
        # Get guild and member
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        role = guild.get_role(role_id)
        if not role:
            return
        
        # Add role
        try:
            await member.add_roles(role, reason="Reaction role")
        except discord.Forbidden:
            pass
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle reaction role removal."""
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is a reaction role
        key = (payload.guild_id, payload.message_id, str(payload.emoji))
        role_id = self.reaction_roles.get(key)
        
        if not role_id:
            return
        
        # Get guild and member
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        role = guild.get_role(role_id)
        if not role:
            return
        
        # Remove role
        try:
            await member.remove_roles(role, reason="Reaction role removed")
        except discord.Forbidden:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))
