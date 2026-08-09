"""
Reminder System

Set reminders for yourself or others.
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional
from datetime import datetime, timedelta
import parsedatetime
import asyncio


class Reminders(commands.Cog):
    """Reminder system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cal = parsedatetime.Calendar()
    
    async def cog_load(self):
        """Start the reminder checker."""
        self.check_reminders.start()
    
    async def cog_unload(self):
        """Stop the reminder checker."""
        self.check_reminders.cancel()
    
    def _parse_time(self, time_string: str) -> Optional[datetime]:
        """Parse a time string into a datetime."""
        time_struct, parse_status = self.cal.parse(time_string)
        
        if parse_status == 0:
            return None
        
        return datetime(*time_struct[:6])
    
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        """Check for reminders that need to be sent."""
        if not self.bot.db:
            return
        
        try:
            # Get due reminders
            reminders = await self.bot.db.fetch(
                """
                SELECT * FROM reminders 
                WHERE remind_at <= NOW() AND completed = FALSE
                """
            )
            
            for reminder in reminders:
                # Mark as completed
                await self.bot.db.execute(
                    "UPDATE reminders SET completed = TRUE WHERE id = $1",
                    reminder['id']
                )
                
                # Get user
                user = await self.bot.fetch_user(reminder['user_id'])
                if not user:
                    continue
                
                # Create embed
                embed = discord.Embed(
                    title="⏰ Reminder",
                    description=reminder['message'],
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                
                embed.set_footer(text=f"Set {(datetime.utcnow() - reminder['created_at']).days} day(s) ago")
                
                # Try to send in channel if available
                if reminder['channel_id']:
                    try:
                        channel = self.bot.get_channel(reminder['channel_id'])
                        if channel:
                            await channel.send(
                                content=user.mention,
                                embed=embed
                            )
                            continue
                    except discord.Forbidden:
                        pass
                
                # Fall back to DM
                try:
                    await user.send(embed=embed)
                except discord.Forbidden:
                    pass
        
        except Exception as e:
            print(f"Error checking reminders: {e}")
    
    @check_reminders.before_loop
    async def before_check_reminders(self):
        """Wait until bot is ready."""
        await self.bot.wait_until_ready()
    
    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(
        time="When to remind (e.g., '30 minutes', 'tomorrow at 3pm', '2 hours')",
        message="What to remind you about"
    )
    async def remind(
        self,
        interaction: discord.Interaction,
        time: str,
        message: str
    ):
        """Set a reminder."""
        # Parse time
        remind_at = self._parse_time(time)
        
        if not remind_at:
            await interaction.response.send_message(
                "❌ I couldn't understand that time. Try something like:\n"
                "• `30 minutes`\n"
                "• `2 hours`\n"
                "• `tomorrow at 3pm`\n"
                "• `next friday at 5pm`",
                ephemeral=True
            )
            return
        
        # Make sure it's in the future
        if remind_at <= datetime.utcnow():
            await interaction.response.send_message(
                "❌ That time is in the past!",
                ephemeral=True
            )
            return
        
        # Save to database
        await self.bot.db.execute(
            """
            INSERT INTO reminders (user_id, guild_id, channel_id, message, remind_at)
            VALUES ($1, $2, $3, $4, $5)
            """,
            interaction.user.id,
            interaction.guild_id if interaction.guild else None,
            interaction.channel_id,
            message,
            remind_at
        )
        
        # Calculate time until
        delta = remind_at - datetime.utcnow()
        
        # Format time string
        if delta.days > 0:
            time_str = f"{delta.days} day(s)"
        elif delta.seconds >= 3600:
            time_str = f"{delta.seconds // 3600} hour(s)"
        else:
            time_str = f"{delta.seconds // 60} minute(s)"
        
        embed = discord.Embed(
            title="✅ Reminder Set",
            description=f"I'll remind you about:\n**{message}**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="When",
            value=f"<t:{int(remind_at.timestamp())}:R> (in {time_str})",
            inline=False
        )
        
        embed.set_footer(text="I'll DM you or ping you in this channel")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="reminders", description="View your active reminders")
    async def reminders_list(self, interaction: discord.Interaction):
        """List active reminders."""
        reminders = await self.bot.db.fetch(
            """
            SELECT * FROM reminders 
            WHERE user_id = $1 AND completed = FALSE 
            ORDER BY remind_at ASC
            LIMIT 10
            """,
            interaction.user.id
        )
        
        if not reminders:
            await interaction.response.send_message(
                "📝 You don't have any active reminders.\nUse `/remind` to set one!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📝 Your Active Reminders",
            color=discord.Color.blue()
        )
        
        for i, reminder in enumerate(reminders, 1):
            time_str = f"<t:{int(reminder['remind_at'].timestamp())}:R>"
            
            embed.add_field(
                name=f"{i}. {reminder['message'][:50]}",
                value=f"**When:** {time_str}\n**ID:** `{reminder['id']}`",
                inline=False
            )
        
        if len(reminders) == 10:
            embed.set_footer(text="Showing first 10 reminders")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="reminder-delete", description="Delete a reminder")
    @app_commands.describe(reminder_id="ID of the reminder to delete")
    async def reminder_delete(self, interaction: discord.Interaction, reminder_id: int):
        """Delete a reminder."""
        result = await self.bot.db.execute(
            """
            DELETE FROM reminders 
            WHERE id = $1 AND user_id = $2
            """,
            reminder_id, interaction.user.id
        )
        
        if result == "DELETE 0":
            await interaction.response.send_message(
                "❌ Reminder not found or you don't own it.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            "✅ Reminder deleted.",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
