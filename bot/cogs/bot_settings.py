"""
Bot Settings cog for Discord bot.
Allows admins to customize bot appearance and settings.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging
import aiohttp

logger = logging.getLogger(__name__)


class BotSettings(commands.Cog):
    """Bot appearance and settings management."""
    
    def __init__(self, bot):
        """Initialize bot settings cog."""
        self.bot = bot
    
    @app_commands.command(name="botavatar", description="Change the bot's avatar (Bot Owner)")
    @app_commands.describe(url="URL of the new avatar image")
    async def bot_avatar(self, interaction: discord.Interaction, url: str):
        """Change bot's avatar."""
        # Check if user is bot owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Only the bot owner can change the avatar.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("❌ Failed to download image.", ephemeral=True)
                        return
                    
                    image_data = await resp.read()
            
            # Update avatar
            await self.bot.user.edit(avatar=image_data)
            
            embed = discord.Embed(
                title="✅ Avatar Updated",
                description="Bot avatar has been changed successfully!",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Bot avatar changed by {interaction.user}")
            
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed to update avatar: {e}", ephemeral=True)
        except Exception as e:
            logger.error(f"Error changing avatar: {e}")
            await interaction.followup.send("❌ An error occurred while changing the avatar.", ephemeral=True)
    
    @app_commands.command(name="botname", description="Change the bot's username (Bot Owner)")
    @app_commands.describe(name="New username for the bot")
    async def bot_name(self, interaction: discord.Interaction, name: str):
        """Change bot's username."""
        # Check if user is bot owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Only the bot owner can change the bot name.",
                ephemeral=True
            )
            return
        
        if len(name) < 2 or len(name) > 32:
            await interaction.response.send_message(
                "❌ Name must be between 2 and 32 characters.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            old_name = self.bot.user.name
            await self.bot.user.edit(username=name)
            
            embed = discord.Embed(
                title="✅ Name Updated",
                description=f"Bot name changed from **{old_name}** to **{name}**",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Bot name changed from '{old_name}' to '{name}' by {interaction.user}")
            
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Failed to update name: {e}\n\n*Note: You can only change the bot name twice per hour.*",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error changing name: {e}")
            await interaction.followup.send("❌ An error occurred while changing the name.", ephemeral=True)
    
    @app_commands.command(name="botnickname", description="Change the bot's nickname in this server (Admin)")
    @app_commands.describe(nickname="New nickname (leave empty to reset)")
    @app_commands.checks.has_permissions(administrator=True)
    async def bot_nickname(self, interaction: discord.Interaction, nickname: Optional[str] = None):
        """Change bot's nickname in the current server."""
        try:
            old_nick = interaction.guild.me.nick
            await interaction.guild.me.edit(nick=nickname)
            
            if nickname:
                message = f"✅ Bot nickname changed to **{nickname}**"
            else:
                message = f"✅ Bot nickname reset to default (**{self.bot.user.name}**)"
            
            await interaction.response.send_message(message)
            logger.info(f"Bot nickname in {interaction.guild.name} changed from '{old_nick}' to '{nickname}' by {interaction.user}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to change my nickname.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error changing nickname: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while changing the nickname.",
                ephemeral=True
            )
    
    @app_commands.command(name="botstatus", description="Change the bot's status (Bot Owner)")
    @app_commands.describe(
        activity_type="Type of activity",
        activity_text="Activity text",
        status="Online status"
    )
    @app_commands.choices(activity_type=[
        app_commands.Choice(name="Playing", value="playing"),
        app_commands.Choice(name="Streaming", value="streaming"),
        app_commands.Choice(name="Listening to", value="listening"),
        app_commands.Choice(name="Watching", value="watching"),
        app_commands.Choice(name="Competing in", value="competing")
    ])
    @app_commands.choices(status=[
        app_commands.Choice(name="Online", value="online"),
        app_commands.Choice(name="Idle", value="idle"),
        app_commands.Choice(name="Do Not Disturb", value="dnd"),
        app_commands.Choice(name="Invisible", value="invisible")
    ])
    async def bot_status(self, interaction: discord.Interaction, 
                        activity_type: str, activity_text: str, status: str = "online"):
        """Change bot's status and activity."""
        # Check if user is bot owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Only the bot owner can change the bot status.",
                ephemeral=True
            )
            return
        
        try:
            # Map activity type
            activity_map = {
                'playing': discord.ActivityType.playing,
                'streaming': discord.ActivityType.streaming,
                'listening': discord.ActivityType.listening,
                'watching': discord.ActivityType.watching,
                'competing': discord.ActivityType.competing
            }
            
            # Map status
            status_map = {
                'online': discord.Status.online,
                'idle': discord.Status.idle,
                'dnd': discord.Status.dnd,
                'invisible': discord.Status.invisible
            }
            
            activity = discord.Activity(
                type=activity_map[activity_type],
                name=activity_text
            )
            
            await self.bot.change_presence(
                activity=activity,
                status=status_map[status]
            )
            
            # Update config in database (optional - for persistence)
            await self.bot.db.execute(
                """
                INSERT INTO bot_settings (setting_key, setting_value)
                VALUES ('status_activity_type', $1), ('status_activity_text', $2), ('status', $3)
                ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value
                """,
                activity_type, activity_text, status
            )
            
            embed = discord.Embed(
                title="✅ Status Updated",
                description=f"**Activity:** {activity_type.title()} {activity_text}\n**Status:** {status.title()}",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Bot status changed by {interaction.user}: {activity_type} {activity_text}, status: {status}")
            
        except Exception as e:
            logger.error(f"Error changing status: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while changing the status.",
                ephemeral=True
            )
    
    @app_commands.command(name="botconfig", description="View current bot configuration")
    async def bot_config(self, interaction: discord.Interaction):
        """Display current bot configuration."""
        guild_config = await self.bot.db.fetchrow(
            "SELECT * FROM guild_config WHERE guild_id = $1",
            interaction.guild.id
        )
        
        if not guild_config:
            await interaction.response.send_message(
                "❌ No configuration found for this server.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"⚙️ Bot Configuration - {interaction.guild.name}",
            color=discord.Color.blue()
        )
        
        # Bot Info
        embed.add_field(
            name="🤖 Bot Information",
            value=f"**Name:** {self.bot.user.name}\n"
                  f"**Nickname:** {interaction.guild.me.nick or 'None'}\n"
                  f"**ID:** {self.bot.user.id}",
            inline=False
        )
        
        # Features
        features_status = []
        features_status.append(f"📊 Leveling: {'✅' if guild_config['xp_enabled'] else '❌'}")
        features_status.append(f"💰 Economy: {'✅' if guild_config['economy_enabled'] else '❌'}")
        features_status.append(f"🤖 AI: {'✅' if guild_config['ai_enabled'] else '❌'}")
        features_status.append(f"🎉 Giveaways: {'✅' if guild_config['giveaways_enabled'] else '❌'}")
        features_status.append(f"🎮 Games: {'✅' if guild_config['games_enabled'] else '❌'}")
        
        embed.add_field(
            name="🎯 Features",
            value="\n".join(features_status),
            inline=True
        )
        
        # Settings
        settings = []
        settings.append(f"Prefix: `{guild_config['prefix']}`")
        settings.append(f"XP Rate: {guild_config['xp_rate']}")
        settings.append(f"Currency: {guild_config['currency_emoji']} {guild_config['currency_name']}")
        
        embed.add_field(
            name="⚙️ Settings",
            value="\n".join(settings),
            inline=True
        )
        
        # Channels
        channels = []
        if guild_config['welcome_channel']:
            channels.append(f"Welcome: <#{guild_config['welcome_channel']}>")
        if guild_config['log_channel']:
            channels.append(f"Logs: <#{guild_config['log_channel']}>")
        if guild_config['starboard_channel']:
            channels.append(f"Starboard: <#{guild_config['starboard_channel']}>")
        
        if channels:
            embed.add_field(
                name="📺 Channels",
                value="\n".join(channels),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="prefix", description="Change the bot's command prefix (Admin)")
    @app_commands.describe(new_prefix="New command prefix (1-10 characters)")
    @app_commands.checks.has_permissions(administrator=True)
    async def change_prefix(self, interaction: discord.Interaction, new_prefix: str):
        """Change the command prefix for this server."""
        if len(new_prefix) < 1 or len(new_prefix) > 10:
            await interaction.response.send_message(
                "❌ Prefix must be between 1 and 10 characters.",
                ephemeral=True
            )
            return
        
        try:
            await self.bot.db.execute(
                """
                INSERT INTO guild_config (guild_id, prefix)
                VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET prefix = $2
                """,
                interaction.guild.id, new_prefix
            )
            
            embed = discord.Embed(
                title="✅ Prefix Updated",
                description=f"Command prefix changed to `{new_prefix}`",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Prefix in {interaction.guild.name} changed to '{new_prefix}' by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error changing prefix: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while changing the prefix.",
                ephemeral=True
            )
    
    @app_commands.command(name="togglefeature", description="Enable/disable bot features (Admin)")
    @app_commands.describe(
        feature="Feature to toggle",
        enabled="Enable or disable"
    )
    @app_commands.choices(feature=[
        app_commands.Choice(name="Leveling/XP", value="xp_enabled"),
        app_commands.Choice(name="Economy", value="economy_enabled"),
        app_commands.Choice(name="AI Conversations", value="ai_enabled"),
        app_commands.Choice(name="Giveaways", value="giveaways_enabled"),
        app_commands.Choice(name="Games", value="games_enabled")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_feature(self, interaction: discord.Interaction, feature: str, enabled: bool):
        """Toggle bot features on/off."""
        try:
            await self.bot.db.execute(
                f"""
                INSERT INTO guild_config (guild_id, {feature})
                VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET {feature} = $2
                """,
                interaction.guild.id, enabled
            )
            
            feature_names = {
                'xp_enabled': 'Leveling/XP System',
                'economy_enabled': 'Economy System',
                'ai_enabled': 'AI Conversations',
                'giveaways_enabled': 'Giveaway System',
                'games_enabled': 'Games System'
            }
            
            status = "enabled" if enabled else "disabled"
            emoji = "✅" if enabled else "❌"
            
            embed = discord.Embed(
                title=f"{emoji} Feature {status.title()}",
                description=f"**{feature_names[feature]}** has been {status}.",
                color=discord.Color.green() if enabled else discord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{feature} {status} in {interaction.guild.name} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error toggling feature: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while toggling the feature.",
                ephemeral=True
            )


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(BotSettings(bot))
