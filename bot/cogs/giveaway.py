"""
Giveaway cog for Discord bot.
Handles giveaway creation and management.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timedelta
import random
import logging
import re

logger = logging.getLogger(__name__)


class Giveaway(commands.Cog):
    """Giveaway system."""
    
    def __init__(self, bot):
        """Initialize giveaway cog."""
        self.bot = bot
        self.check_giveaways.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.check_giveaways.cancel()
    
    @commands.loop(seconds=30)
    async def check_giveaways(self):
        """Check for ended giveaways."""
        ended = await self.bot.db.fetch(
            """
            SELECT * FROM giveaways
            WHERE status = 'active' AND ends_at <= $1
            """,
            datetime.utcnow()
        )
        
        for giveaway in ended:
            await self.end_giveaway(giveaway['id'])
    
    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        """Wait for bot to be ready."""
        await self.bot.wait_until_ready()
    
    async def end_giveaway(self, giveaway_id: int):
        """End a giveaway and pick winners."""
        # Get giveaway
        giveaway = await self.bot.db.fetchrow(
            "SELECT * FROM giveaways WHERE id = $1",
            giveaway_id
        )
        
        if not giveaway or giveaway['status'] != 'active':
            return
        
        # Get all entries
        entries = await self.bot.db.fetch(
            "SELECT user_id, entries FROM giveaway_entries WHERE giveaway_id = $1",
            giveaway_id
        )
        
        if not entries:
            # No entries, cancel giveaway
            await self.bot.db.execute(
                "UPDATE giveaways SET status = 'cancelled' WHERE id = $1",
                giveaway_id
            )
            
            # Notify
            try:
                guild = self.bot.get_guild(giveaway['guild_id'])
                channel = guild.get_channel(giveaway['channel_id'])
                if channel:
                    await channel.send(f"🎉 Giveaway for **{giveaway['prize']}** ended with no entries!")
            except:
                pass
            return
        
        # Pick winners
        user_pool = []
        for entry in entries:
            user_pool.extend([entry['user_id']] * entry['entries'])
        
        winner_count = min(giveaway['winner_count'], len(set(user_pool)))
        winners = random.sample(list(set(user_pool)), winner_count)
        
        # Save winners
        for winner_id in winners:
            await self.bot.db.execute(
                """
                INSERT INTO giveaway_winners (giveaway_id, user_id)
                VALUES ($1, $2)
                """,
                giveaway_id, winner_id
            )
        
        # Update status
        await self.bot.db.execute(
            "UPDATE giveaways SET status = 'ended' WHERE id = $1",
            giveaway_id
        )
        
        # Announce winners
        try:
            guild = self.bot.get_guild(giveaway['guild_id'])
            channel = guild.get_channel(giveaway['channel_id'])
            
            if channel:
                winner_mentions = [f"<@{winner_id}>" for winner_id in winners]
                embed = discord.Embed(
                    title="🎉 Giveaway Ended!",
                    description=f"**Prize:** {giveaway['prize']}",
                    color=discord.Color.gold()
                )
                embed.add_field(
                    name="Winners",
                    value="\n".join(winner_mentions),
                    inline=False
                )
                
                await channel.send(embed=embed)
                
                # DM winners
                for winner_id in winners:
                    try:
                        user = await self.bot.fetch_user(winner_id)
                        await user.send(
                            f"🎉 Congratulations! You won **{giveaway['prize']}** in {guild.name}!"
                        )
                    except:
                        pass
        except Exception as e:
            logger.error(f"Failed to announce giveaway winners: {e}")
    
    @app_commands.command(name="giveaway", description="Create a giveaway")
    @app_commands.describe(
        duration="Duration (e.g., 1h, 1d)",
        winners="Number of winners",
        prize="Prize description"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_create(self, interaction: discord.Interaction, 
                             duration: str, winners: int, prize: str):
        """Create a new giveaway."""
        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if duration_seconds is None:
            await interaction.response.send_message(
                "❌ Invalid duration format. Use: 1h, 1d, 1w",
                ephemeral=True
            )
            return
        
        if winners < 1 or winners > 20:
            await interaction.response.send_message(
                "❌ Winner count must be between 1 and 20.",
                ephemeral=True
            )
            return
        
        ends_at = datetime.utcnow() + timedelta(seconds=duration_seconds)
        
        # Create giveaway
        giveaway_id = await self.bot.db.fetchval(
            """
            INSERT INTO giveaways (guild_id, channel_id, prize, winner_count, duration, ends_at, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            interaction.guild.id, interaction.channel.id, prize, winners,
            duration_seconds, ends_at, interaction.user.id
        )
        
        # Create embed
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**{prize}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Winners", value=str(winners), inline=True)
        embed.add_field(name="Ends", value=f"<t:{int(ends_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Host", value=interaction.user.mention, inline=True)
        embed.set_footer(text=f"React with 🎉 to enter • ID: {giveaway_id}")
        
        message = await interaction.channel.send(embed=embed)
        await message.add_reaction("🎉")
        
        # Update message ID
        await self.bot.db.execute(
            "UPDATE giveaways SET message_id = $1 WHERE id = $2",
            message.id, giveaway_id
        )
        
        await interaction.response.send_message(f"✅ Giveaway created! ID: {giveaway_id}", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle giveaway entries."""
        if payload.user_id == self.bot.user.id:
            return
        
        if str(payload.emoji) != "🎉":
            return
        
        # Check if message is a giveaway
        giveaway = await self.bot.db.fetchrow(
            """
            SELECT * FROM giveaways
            WHERE message_id = $1 AND status = 'active'
            """,
            payload.message_id
        )
        
        if not giveaway:
            return
        
        # Add entry
        try:
            await self.bot.db.execute(
                """
                INSERT INTO giveaway_entries (giveaway_id, user_id, entries)
                VALUES ($1, $2, 1)
                ON CONFLICT (giveaway_id, user_id) DO NOTHING
                """,
                giveaway['id'], payload.user_id
            )
        except Exception as e:
            logger.error(f"Failed to add giveaway entry: {e}")
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds."""
        match = re.match(r'^(\d+)([smhdw])$', duration_str.lower())
        if not match:
            return None
        
        amount, unit = match.groups()
        amount = int(amount)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }
        
        return amount * multipliers.get(unit, 0)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(Giveaway(bot))
