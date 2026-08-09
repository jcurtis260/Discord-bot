"""
Red Cog Management Commands

Commands for managing Red-DiscordBot compatible cogs.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from modules.red_compat import RedCogManager


class RedManagement(commands.Cog):
    """Manage Red-DiscordBot compatible cogs."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.red_manager = RedCogManager(bot)
    
    async def cog_load(self):
        """Called when the cog is loaded."""
        # Auto-load enabled Red cogs from database
        if hasattr(self.bot, 'db') and self.bot.db:
            try:
                enabled_cogs = await self.bot.db.fetch(
                    "SELECT cog_name FROM red_cogs WHERE enabled = TRUE"
                )
                for record in enabled_cogs:
                    cog_name = record['cog_name']
                    success = await self.red_manager.load_red_cog(cog_name)
                    if success:
                        print(f"✓ Loaded Red cog: {cog_name}")
                    else:
                        print(f"✗ Failed to load Red cog: {cog_name}")
            except Exception as e:
                print(f"Error auto-loading Red cogs: {e}")
    
    async def _is_owner(self, interaction: discord.Interaction) -> bool:
        """Check if user is bot owner."""
        return interaction.user.id == self.bot.owner_id
    
    @app_commands.command(name="redcog-load", description="Load a Red-DiscordBot cog")
    @app_commands.describe(cog_name="Name of the cog to load")
    async def red_load(self, interaction: discord.Interaction, cog_name: str):
        """Load a Red cog."""
        if not await self._is_owner(interaction):
            await interaction.response.send_message("❌ Only the bot owner can manage Red cogs.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Check if already loaded
        if self.red_manager.is_loaded(cog_name):
            await interaction.followup.send(f"❌ Red cog `{cog_name}` is already loaded.")
            return
        
        # Try to load
        success = await self.red_manager.load_red_cog(cog_name)
        
        if success:
            # Save to database
            if hasattr(self.bot, 'db') and self.bot.db:
                await self.bot.db.execute(
                    """
                    INSERT INTO red_cogs (cog_name, enabled)
                    VALUES ($1, TRUE)
                    ON CONFLICT (cog_name) DO UPDATE SET enabled = TRUE
                    """,
                    cog_name
                )
            
            await interaction.followup.send(f"✅ Successfully loaded Red cog: `{cog_name}`")
        else:
            await interaction.followup.send(
                f"❌ Failed to load Red cog: `{cog_name}`\n"
                f"Make sure the cog exists in `red_cogs/{cog_name}/` and is compatible."
            )
    
    @app_commands.command(name="redcog-unload", description="Unload a Red-DiscordBot cog")
    @app_commands.describe(cog_name="Name of the cog to unload")
    async def red_unload(self, interaction: discord.Interaction, cog_name: str):
        """Unload a Red cog."""
        if not await self._is_owner(interaction):
            await interaction.response.send_message("❌ Only the bot owner can manage Red cogs.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        success = await self.red_manager.unload_red_cog(cog_name)
        
        if success:
            # Update database
            if hasattr(self.bot, 'db') and self.bot.db:
                await self.bot.db.execute(
                    "UPDATE red_cogs SET enabled = FALSE WHERE cog_name = $1",
                    cog_name
                )
            
            await interaction.followup.send(f"✅ Successfully unloaded Red cog: `{cog_name}`")
        else:
            await interaction.followup.send(f"❌ Red cog `{cog_name}` is not loaded.")
    
    @app_commands.command(name="redcog-reload", description="Reload a Red-DiscordBot cog")
    @app_commands.describe(cog_name="Name of the cog to reload")
    async def red_reload(self, interaction: discord.Interaction, cog_name: str):
        """Reload a Red cog."""
        if not await self._is_owner(interaction):
            await interaction.response.send_message("❌ Only the bot owner can manage Red cogs.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        success = await self.red_manager.reload_red_cog(cog_name)
        
        if success:
            await interaction.followup.send(f"✅ Successfully reloaded Red cog: `{cog_name}`")
        else:
            await interaction.followup.send(f"❌ Failed to reload Red cog: `{cog_name}`")
    
    @app_commands.command(name="redcog-list", description="List all available Red-DiscordBot cogs")
    async def red_list(self, interaction: discord.Interaction):
        """List all Red cogs."""
        available_cogs = self.red_manager.list_available_cogs()
        
        if not available_cogs:
            await interaction.response.send_message(
                "📦 No Red cogs found in the `red_cogs/` directory.\n\n"
                "To add Red cogs:\n"
                "1. Create a directory in `red_cogs/` with the cog name\n"
                "2. Add the cog files to that directory\n"
                "3. Use `/redcog-load <name>` to load it",
                ephemeral=True
            )
            return
        
        # Build status list
        embed = discord.Embed(
            title="📦 Red-DiscordBot Cogs",
            description="Available cogs from the Red ecosystem",
            color=discord.Color.blue()
        )
        
        loaded = []
        unloaded = []
        
        for cog in available_cogs:
            if self.red_manager.is_loaded(cog):
                loaded.append(cog)
            else:
                unloaded.append(cog)
        
        if loaded:
            embed.add_field(
                name="✅ Loaded",
                value="\n".join(f"• `{cog}`" for cog in loaded),
                inline=False
            )
        
        if unloaded:
            embed.add_field(
                name="📦 Available",
                value="\n".join(f"• `{cog}`" for cog in unloaded),
                inline=False
            )
        
        embed.set_footer(text=f"Total: {len(available_cogs)} cogs")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="redcog-info", description="Get information about a Red cog")
    @app_commands.describe(cog_name="Name of the cog")
    async def red_info(self, interaction: discord.Interaction, cog_name: str):
        """Get info about a Red cog."""
        available_cogs = self.red_manager.list_available_cogs()
        
        if cog_name not in available_cogs:
            await interaction.response.send_message(
                f"❌ Red cog `{cog_name}` not found.",
                ephemeral=True
            )
            return
        
        is_loaded = self.red_manager.is_loaded(cog_name)
        
        # Get cog info from database
        cog_info = None
        if hasattr(self.bot, 'db') and self.bot.db:
            cog_info = await self.bot.db.fetchrow(
                "SELECT * FROM red_cogs WHERE cog_name = $1",
                cog_name
            )
        
        embed = discord.Embed(
            title=f"📦 {cog_name}",
            description="Red-DiscordBot Compatible Cog",
            color=discord.Color.green() if is_loaded else discord.Color.greyple()
        )
        
        embed.add_field(
            name="Status",
            value="✅ Loaded" if is_loaded else "📦 Available",
            inline=True
        )
        
        if cog_info:
            if cog_info['loaded_at']:
                embed.add_field(
                    name="Loaded At",
                    value=f"<t:{int(cog_info['loaded_at'].timestamp())}:R>",
                    inline=True
                )
        
        embed.add_field(
            name="Location",
            value=f"`red_cogs/{cog_name}/`",
            inline=False
        )
        
        # Commands
        commands_text = "Use `/redcog-load` to load this cog" if not is_loaded else "Use `/redcog-unload` to unload"
        embed.add_field(
            name="Management",
            value=commands_text,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RedManagement(bot))
