"""
Economy cog for Discord bot.
Handles virtual currency, shop, and transactions.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Economy(commands.Cog):
    """Economy system with currency and shop."""
    
    def __init__(self, bot):
        """Initialize economy cog."""
        self.bot = bot
    
    async def get_balance(self, guild_id: int, user_id: int) -> int:
        """Get user's balance."""
        data = await self.bot.db.fetchrow(
            "SELECT balance FROM guild_members WHERE guild_id = $1 AND user_id = $2",
            guild_id, user_id
        )
        
        if data is None:
            # Initialize user
            await self.bot.db.execute(
                """
                INSERT INTO guild_members (guild_id, user_id, balance)
                VALUES ($1, $2, 0)
                ON CONFLICT (guild_id, user_id) DO NOTHING
                """,
                guild_id, user_id
            )
            return 0
        
        return data['balance']
    
    async def add_balance(self, guild_id: int, user_id: int, amount: int, 
                         transaction_type: str, description: str) -> int:
        """Add to user's balance and log transaction."""
        # Update balance
        await self.bot.db.execute(
            """
            UPDATE guild_members
            SET balance = balance + $1, total_earned = total_earned + $1
            WHERE guild_id = $2 AND user_id = $3
            """,
            amount, guild_id, user_id
        )
        
        # Log transaction
        await self.bot.db.execute(
            """
            INSERT INTO economy_transactions (guild_id, user_id, amount, transaction_type, description)
            VALUES ($1, $2, $3, $4, $5)
            """,
            guild_id, user_id, amount, transaction_type, description
        )
        
        return await self.get_balance(guild_id, user_id)
    
    async def remove_balance(self, guild_id: int, user_id: int, amount: int,
                           transaction_type: str, description: str) -> int:
        """Remove from user's balance and log transaction."""
        # Update balance
        await self.bot.db.execute(
            """
            UPDATE guild_members
            SET balance = balance - $1, total_spent = total_spent + $1
            WHERE guild_id = $2 AND user_id = $3
            """,
            amount, guild_id, user_id
        )
        
        # Log transaction
        await self.bot.db.execute(
            """
            INSERT INTO economy_transactions (guild_id, user_id, amount, transaction_type, description)
            VALUES ($1, $2, $3, $4, $5)
            """,
            guild_id, user_id, -amount, transaction_type, description
        )
        
        return await self.get_balance(guild_id, user_id)
    
    async def get_currency_emoji(self, guild_id: int) -> str:
        """Get server's currency emoji."""
        config = await self.bot.db.fetchrow(
            "SELECT currency_emoji FROM guild_config WHERE guild_id = $1",
            guild_id
        )
        return config['currency_emoji'] if config else "💰"
    
    @app_commands.command(name="balance", description="Check your or another user's balance")
    @app_commands.describe(user="The user to check (defaults to yourself)")
    async def balance(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Check balance."""
        user = user or interaction.user
        
        balance = await self.get_balance(interaction.guild.id, user.id)
        emoji = await self.get_currency_emoji(interaction.guild.id)
        
        # Get stats
        stats = await self.bot.db.fetchrow(
            "SELECT total_earned, total_spent FROM guild_members WHERE guild_id = $1 AND user_id = $2",
            interaction.guild.id, user.id
        )
        
        embed = discord.Embed(
            title=f"{emoji} Balance - {user.display_name}",
            color=discord.Color.green()
        )
        embed.add_field(name="Current Balance", value=f"{emoji} {balance:,}", inline=False)
        
        if stats:
            embed.add_field(name="Total Earned", value=f"{emoji} {stats['total_earned']:,}", inline=True)
            embed.add_field(name="Total Spent", value=f"{emoji} {stats['total_spent']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily reward."""
        # Check last claim
        data = await self.bot.db.fetchrow(
            """
            SELECT last_daily, daily_streak FROM guild_members
            WHERE guild_id = $1 AND user_id = $2
            """,
            interaction.guild.id, interaction.user.id
        )
        
        if data and data['last_daily']:
            time_since_last = datetime.utcnow() - data['last_daily']
            if time_since_last < timedelta(hours=20):
                # Too soon
                wait_time = timedelta(hours=24) - time_since_last
                hours = int(wait_time.total_seconds() // 3600)
                minutes = int((wait_time.total_seconds() % 3600) // 60)
                await interaction.response.send_message(
                    f"⏰ You've already claimed your daily reward! Come back in {hours}h {minutes}m",
                    ephemeral=True
                )
                return
        
        # Get reward amount
        config = await self.bot.db.fetchrow(
            "SELECT daily_reward FROM guild_config WHERE guild_id = $1",
            interaction.guild.id
        )
        base_reward = config['daily_reward'] if config else 50
        
        # Calculate streak
        streak = data['daily_streak'] if data else 0
        if data and data['last_daily'] and (datetime.utcnow() - data['last_daily']) < timedelta(hours=48):
            streak += 1
        else:
            streak = 1
        
        # Streak bonus (10 extra per day, max 100)
        streak_bonus = min(streak * 10, 100)
        total_reward = base_reward + streak_bonus
        
        # Update database
        await self.bot.db.execute(
            """
            UPDATE guild_members
            SET last_daily = $1, daily_streak = $2
            WHERE guild_id = $3 AND user_id = $4
            """,
            datetime.utcnow(), streak, interaction.guild.id, interaction.user.id
        )
        
        # Add balance
        new_balance = await self.add_balance(
            interaction.guild.id, interaction.user.id, total_reward,
            'daily', 'Daily reward'
        )
        
        emoji = await self.get_currency_emoji(interaction.guild.id)
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received {emoji} **{total_reward:,}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Base Reward", value=f"{emoji} {base_reward:,}", inline=True)
        embed.add_field(name="Streak Bonus", value=f"{emoji} {streak_bonus:,}", inline=True)
        embed.add_field(name="Current Streak", value=f"🔥 {streak} day(s)", inline=False)
        embed.add_field(name="New Balance", value=f"{emoji} {new_balance:,}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pay", description="Pay another user")
    @app_commands.describe(
        user="The user to pay",
        amount="Amount to pay"
    )
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Transfer money to another user."""
        if user.bot:
            await interaction.response.send_message("❌ You cannot pay bots.", ephemeral=True)
            return
        
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot pay yourself.", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.", ephemeral=True)
            return
        
        # Check sender balance
        sender_balance = await self.get_balance(interaction.guild.id, interaction.user.id)
        if sender_balance < amount:
            await interaction.response.send_message(
                f"❌ Insufficient funds. You have {sender_balance:,}",
                ephemeral=True
            )
            return
        
        # Transfer
        await self.remove_balance(
            interaction.guild.id, interaction.user.id, amount,
            'transfer', f'Paid {user.name}'
        )
        await self.add_balance(
            interaction.guild.id, user.id, amount,
            'transfer', f'Received from {interaction.user.name}'
        )
        
        emoji = await self.get_currency_emoji(interaction.guild.id)
        
        await interaction.response.send_message(
            f"✅ Paid {emoji} **{amount:,}** to {user.mention}"
        )
    
    @app_commands.command(name="shop", description="View the server shop")
    async def shop(self, interaction: discord.Interaction):
        """Display shop items."""
        items = await self.bot.db.fetch(
            """
            SELECT id, name, description, price, stock
            FROM shop_items
            WHERE guild_id = $1 AND purchasable = TRUE
            ORDER BY price ASC
            """,
            interaction.guild.id
        )
        
        if not items:
            await interaction.response.send_message(
                "🏪 The shop is empty. Ask an admin to add items!",
                ephemeral=True
            )
            return
        
        emoji = await self.get_currency_emoji(interaction.guild.id)
        
        embed = discord.Embed(
            title=f"🏪 {interaction.guild.name} Shop",
            color=discord.Color.blue()
        )
        
        for item in items:
            stock_text = f"Stock: {item['stock']}" if item['stock'] else "Stock: ∞"
            embed.add_field(
                name=f"{item['name']} - {emoji} {item['price']:,}",
                value=f"{item['description']}\n{stock_text}\nID: {item['id']}",
                inline=False
            )
        
        embed.set_footer(text="Use /buy <item_id> to purchase an item")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item_id="The item ID to purchase")
    async def buy(self, interaction: discord.Interaction, item_id: int):
        """Purchase an item."""
        # Get item
        item = await self.bot.db.fetchrow(
            """
            SELECT * FROM shop_items
            WHERE guild_id = $1 AND id = $2 AND purchasable = TRUE
            """,
            interaction.guild.id, item_id
        )
        
        if not item:
            await interaction.response.send_message("❌ Item not found.", ephemeral=True)
            return
        
        # Check stock
        if item['stock'] is not None and item['stock'] <= 0:
            await interaction.response.send_message("❌ Item is out of stock.", ephemeral=True)
            return
        
        # Check balance
        balance = await self.get_balance(interaction.guild.id, interaction.user.id)
        if balance < item['price']:
            emoji = await self.get_currency_emoji(interaction.guild.id)
            await interaction.response.send_message(
                f"❌ Insufficient funds. You need {emoji} {item['price']:,} but have {emoji} {balance:,}",
                ephemeral=True
            )
            return
        
        # Purchase
        await self.remove_balance(
            interaction.guild.id, interaction.user.id, item['price'],
            'spend', f"Purchased {item['name']}"
        )
        
        # Add to inventory
        await self.bot.db.execute(
            """
            INSERT INTO user_inventory (guild_id, user_id, item_id, quantity)
            VALUES ($1, $2, $3, 1)
            ON CONFLICT (guild_id, user_id, item_id) DO UPDATE
            SET quantity = user_inventory.quantity + 1
            """,
            interaction.guild.id, interaction.user.id, item_id
        )
        
        # Update stock
        if item['stock'] is not None:
            await self.bot.db.execute(
                "UPDATE shop_items SET stock = stock - 1 WHERE id = $1",
                item_id
            )
        
        emoji = await self.get_currency_emoji(interaction.guild.id)
        
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You bought **{item['name']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Price", value=f"{emoji} {item['price']:,}", inline=True)
        embed.add_field(name="New Balance", value=f"{emoji} {balance - item['price']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(Economy(bot))
