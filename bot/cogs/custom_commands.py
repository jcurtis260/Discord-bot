"""
Custom Commands

Allows server admins to create custom commands with custom responses.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import random


class CustomCommands(commands.Cog):
    """Create and manage custom commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="cc-add", description="Add a custom command")
    @app_commands.describe(
        name="Command name (without prefix)",
        response="Response when the command is used"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def cc_add(
        self,
        interaction: discord.Interaction,
        name: str,
        response: str
    ):
        """Add a custom command."""
        # Validate name
        name = name.lower().strip()
        if not name or ' ' in name:
            await interaction.response.send_message(
                "❌ Command name must not contain spaces.",
                ephemeral=True
            )
            return
        
        # Check if command already exists
        existing = await self.bot.db.fetchrow(
            "SELECT id FROM custom_commands WHERE guild_id = $1 AND command_name = $2",
            interaction.guild_id, name
        )
        
        if existing:
            await interaction.response.send_message(
                f"❌ Custom command `{name}` already exists. Use `/cc-edit` to modify it.",
                ephemeral=True
            )
            return
        
        # Add command
        await self.bot.db.execute(
            """
            INSERT INTO custom_commands (guild_id, command_name, response, created_by)
            VALUES ($1, $2, $3, $4)
            """,
            interaction.guild_id, name, response, interaction.user.id
        )
        
        await interaction.response.send_message(
            f"✅ Custom command `{name}` created!\n"
            f"Use it with: `/{name}` or `{self.bot.command_prefix}{name}`"
        )
    
    @app_commands.command(name="cc-edit", description="Edit a custom command")
    @app_commands.describe(
        name="Command name to edit",
        response="New response"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def cc_edit(
        self,
        interaction: discord.Interaction,
        name: str,
        response: str
    ):
        """Edit a custom command."""
        name = name.lower().strip()
        
        result = await self.bot.db.execute(
            """
            UPDATE custom_commands 
            SET response = $1, updated_at = NOW()
            WHERE guild_id = $2 AND command_name = $3
            """,
            response, interaction.guild_id, name
        )
        
        if result == "UPDATE 0":
            await interaction.response.send_message(
                f"❌ Custom command `{name}` not found.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            f"✅ Custom command `{name}` updated!"
        )
    
    @app_commands.command(name="cc-delete", description="Delete a custom command")
    @app_commands.describe(name="Command name to delete")
    @app_commands.default_permissions(manage_guild=True)
    async def cc_delete(self, interaction: discord.Interaction, name: str):
        """Delete a custom command."""
        name = name.lower().strip()
        
        result = await self.bot.db.execute(
            "DELETE FROM custom_commands WHERE guild_id = $1 AND command_name = $2",
            interaction.guild_id, name
        )
        
        if result == "DELETE 0":
            await interaction.response.send_message(
                f"❌ Custom command `{name}` not found.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            f"✅ Custom command `{name}` deleted."
        )
    
    @app_commands.command(name="cc-list", description="List all custom commands")
    async def cc_list(self, interaction: discord.Interaction):
        """List all custom commands for this server."""
        commands_data = await self.bot.db.fetch(
            """
            SELECT command_name, usage_count 
            FROM custom_commands 
            WHERE guild_id = $1 
            ORDER BY command_name
            """,
            interaction.guild_id
        )
        
        if not commands_data:
            await interaction.response.send_message(
                "📝 No custom commands yet. Create one with `/cc-add`",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📝 Custom Commands",
            description=f"Total: {len(commands_data)} commands",
            color=discord.Color.blue()
        )
        
        # Group into chunks
        command_list = []
        for cmd in commands_data:
            uses = f" ({cmd['usage_count']} uses)" if cmd['usage_count'] > 0 else ""
            command_list.append(f"`{cmd['command_name']}`{uses}")
        
        # Split into fields if too many
        chunk_size = 20
        for i in range(0, len(command_list), chunk_size):
            chunk = command_list[i:i+chunk_size]
            embed.add_field(
                name=f"Commands {i+1}-{min(i+chunk_size, len(command_list))}",
                value="\n".join(chunk),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="cc-info", description="Get info about a custom command")
    @app_commands.describe(name="Command name")
    async def cc_info(self, interaction: discord.Interaction, name: str):
        """Get information about a custom command."""
        name = name.lower().strip()
        
        cmd = await self.bot.db.fetchrow(
            """
            SELECT * FROM custom_commands 
            WHERE guild_id = $1 AND command_name = $2
            """,
            interaction.guild_id, name
        )
        
        if not cmd:
            await interaction.response.send_message(
                f"❌ Custom command `{name}` not found.",
                ephemeral=True
            )
            return
        
        creator = await self.bot.fetch_user(cmd['created_by'])
        
        embed = discord.Embed(
            title=f"📝 Custom Command: {name}",
            description=f"**Response:**\n{cmd['response']}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Creator", value=creator.mention if creator else "Unknown", inline=True)
        embed.add_field(name="Uses", value=str(cmd['usage_count']), inline=True)
        embed.add_field(
            name="Created",
            value=f"<t:{int(cmd['created_at'].timestamp())}:R>",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen for custom command triggers."""
        if message.author.bot or not message.guild:
            return
        
        # Check if message starts with prefix
        prefix = self.bot.command_prefix
        if not message.content.startswith(prefix):
            return
        
        # Extract command name
        command_name = message.content[len(prefix):].split()[0].lower()
        
        # Look up custom command
        cmd = await self.bot.db.fetchrow(
            """
            SELECT response FROM custom_commands 
            WHERE guild_id = $1 AND command_name = $2
            """,
            message.guild.id, command_name
        )
        
        if cmd:
            # Increment use count
            await self.bot.db.execute(
                """
                UPDATE custom_commands 
                SET usage_count = usage_count + 1 
                WHERE guild_id = $1 AND command_name = $2
                """,
                message.guild.id, command_name
            )
            
            # Send response
            await message.channel.send(cmd['response'])


async def setup(bot: commands.Bot):
    await bot.add_cog(CustomCommands(bot))
