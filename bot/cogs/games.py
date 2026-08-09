"""
Games cog for Discord bot.
Includes trivia, gambling games, and fun games.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List
import logging
import random
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Games(commands.Cog):
    """Fun games and gambling."""
    
    def __init__(self, bot):
        """Initialize games cog."""
        self.bot = bot
        self.active_games = {}  # Track active games per channel
    
    async def get_currency_emoji(self, guild_id: int) -> str:
        """Get server's currency emoji."""
        config = await self.bot.db.fetchrow(
            "SELECT currency_emoji FROM guild_config WHERE guild_id = $1",
            guild_id
        )
        return config['currency_emoji'] if config else "💰"
    
    async def get_balance(self, guild_id: int, user_id: int) -> int:
        """Get user's balance."""
        data = await self.bot.db.fetchrow(
            "SELECT balance FROM guild_members WHERE guild_id = $1 AND user_id = $2",
            guild_id, user_id
        )
        return data['balance'] if data else 0
    
    async def update_balance(self, guild_id: int, user_id: int, amount: int, description: str):
        """Update user's balance."""
        await self.bot.db.execute(
            """
            UPDATE guild_members
            SET balance = balance + $1
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
            guild_id, user_id, amount, 'game', description
        )
    
    # ============================================================================
    # TRIVIA GAME
    # ============================================================================
    
    @app_commands.command(name="trivia", description="Start a trivia game")
    @app_commands.describe(category="Trivia category (optional)")
    async def trivia(self, interaction: discord.Interaction, category: Optional[str] = None):
        """Start a trivia game."""
        if interaction.channel.id in self.active_games:
            await interaction.response.send_message(
                "❌ A game is already active in this channel!",
                ephemeral=True
            )
            return
        
        # Get random question
        query = """
            SELECT id, question, correct_answer, incorrect_answers, difficulty
            FROM trivia_questions
            WHERE guild_id IS NULL OR guild_id = $1
        """
        params = [interaction.guild.id]
        
        if category:
            query += " AND category = $2"
            params.append(category)
        
        query += " ORDER BY RANDOM() LIMIT 1"
        
        question = await self.bot.db.fetchrow(query, *params)
        
        if not question:
            await interaction.response.send_message(
                "❌ No trivia questions available. Ask an admin to add some!",
                ephemeral=True
            )
            return
        
        # Mark channel as having active game
        self.active_games[interaction.channel.id] = 'trivia'
        
        # Prepare answers
        answers = [question['correct_answer']] + list(question['incorrect_answers'])
        random.shuffle(answers)
        correct_index = answers.index(question['correct_answer'])
        
        # Create embed
        embed = discord.Embed(
            title="🎯 Trivia Time!",
            description=question['question'],
            color=discord.Color.blue()
        )
        
        # Add answers
        answer_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
        for i, answer in enumerate(answers):
            embed.add_field(
                name=f"{answer_emojis[i]} Option {i+1}",
                value=answer,
                inline=False
            )
        
        embed.set_footer(text=f"Difficulty: {question['difficulty'].title()} • React with your answer!")
        
        message = await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Trivia started!", ephemeral=True)
        
        # Add reactions
        for i in range(len(answers)):
            await message.add_reaction(answer_emojis[i])
        
        # Wait for answers (30 seconds)
        def check(reaction, user):
            return (
                user != self.bot.user and
                str(reaction.emoji) in answer_emojis[:len(answers)] and
                reaction.message.id == message.id
            )
        
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass  # Task was cancelled, continue with results
        
        # Fetch final reactions
        message = await interaction.channel.fetch_message(message.id)
        
        # Count correct answers
        correct_emoji = answer_emojis[correct_index]
        winners = []
        
        for reaction in message.reactions:
            if str(reaction.emoji) == correct_emoji:
                users = [user async for user in reaction.users() if not user.bot]
                winners.extend(users)
        
        # Announce results
        result_embed = discord.Embed(
            title="✅ Trivia Results",
            description=f"**Correct Answer:** {question['correct_answer']}",
            color=discord.Color.green()
        )
        
        if winners:
            winner_mentions = [user.mention for user in winners[:10]]
            result_embed.add_field(
                name=f"🏆 Winners ({len(winners)})",
                value="\n".join(winner_mentions) + ("..." if len(winners) > 10 else ""),
                inline=False
            )
            
            # Award currency
            emoji = await self.get_currency_emoji(interaction.guild.id)
            reward = 10
            
            for winner in winners:
                try:
                    await self.update_balance(
                        interaction.guild.id,
                        winner.id,
                        reward,
                        "Won trivia question"
                    )
                except Exception as e:
                    logger.error(f"Failed to update balance for {winner.id}: {e}")
            
            result_embed.add_field(
                name="💰 Reward",
                value=f"Each winner earned {emoji} {reward}!",
                inline=False
            )
        else:
            result_embed.add_field(
                name="😢 No Winners",
                value="Nobody got the correct answer!",
                inline=False
            )
        
        await interaction.channel.send(embed=result_embed)
        
        # Remove active game
        if interaction.channel.id in self.active_games:
            del self.active_games[interaction.channel.id]
    
    # ============================================================================
    # GAMBLING GAMES
    # ============================================================================
    
    @app_commands.command(name="coinflip", description="Flip a coin and bet on it")
    @app_commands.describe(
        bet="Amount to bet",
        choice="Heads or Tails"
    )
    @app_commands.choices(choice=[
        app_commands.Choice(name="Heads", value="heads"),
        app_commands.Choice(name="Tails", value="tails")
    ])
    async def coinflip(self, interaction: discord.Interaction, bet: int, choice: str):
        """Coinflip gambling game."""
        if bet < 10:
            await interaction.response.send_message("❌ Minimum bet is 10.", ephemeral=True)
            return
        
        # Check balance
        balance = await self.get_balance(interaction.guild.id, interaction.user.id)
        if balance < bet:
            emoji = await self.get_currency_emoji(interaction.guild.id)
            await interaction.response.send_message(
                f"❌ Insufficient funds. You have {emoji} {balance}.",
                ephemeral=True
            )
            return
        
        # Flip coin
        result = random.choice(['heads', 'tails'])
        won = result == choice
        
        embed = discord.Embed(
            title="🪙 Coinflip",
            color=discord.Color.gold() if won else discord.Color.red()
        )
        
        emoji = await self.get_currency_emoji(interaction.guild.id)
        
        embed.add_field(name="Your Choice", value=choice.title(), inline=True)
        embed.add_field(name="Result", value=result.title(), inline=True)
        embed.add_field(name="Bet", value=f"{emoji} {bet}", inline=True)
        
        if won:
            winnings = bet * 2
            await self.update_balance(
                interaction.guild.id,
                interaction.user.id,
                bet,  # Add bet amount (they keep their bet + win bet)
                "Won coinflip"
            )
            
            embed.description = f"🎉 **You won!** +{emoji} {bet}"
            new_balance = balance + bet
        else:
            await self.update_balance(
                interaction.guild.id,
                interaction.user.id,
                -bet,
                "Lost coinflip"
            )
            
            embed.description = f"😢 **You lost!** -{emoji} {bet}"
            new_balance = balance - bet
        
        embed.add_field(
            name="New Balance",
            value=f"{emoji} {new_balance}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="slots", description="Play slot machine")
    @app_commands.describe(bet="Amount to bet")
    async def slots(self, interaction: discord.Interaction, bet: int):
        """Slot machine game."""
        if bet < 10:
            await interaction.response.send_message("❌ Minimum bet is 10.", ephemeral=True)
            return
        
        balance = await self.get_balance(interaction.guild.id, interaction.user.id)
        if balance < bet:
            emoji = await self.get_currency_emoji(interaction.guild.id)
            await interaction.response.send_message(
                f"❌ Insufficient funds. You have {emoji} {balance}.",
                ephemeral=True
            )
            return
        
        # Slot symbols
        symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']
        weights = [30, 25, 20, 15, 6, 3, 1]  # Rarity weights
        
        # Spin
        reels = random.choices(symbols, weights=weights, k=3)
        
        # Calculate winnings
        multiplier = 0
        if reels[0] == reels[1] == reels[2]:
            # Three of a kind
            symbol_values = {
                '🍒': 2,
                '🍋': 3,
                '🍊': 4,
                '🍇': 5,
                '🔔': 10,
                '💎': 20,
                '7️⃣': 50
            }
            multiplier = symbol_values.get(reels[0], 2)
        elif reels[0] == reels[1] or reels[1] == reels[2]:
            # Two of a kind
            multiplier = 0.5
        
        won = multiplier > 0
        winnings = int(bet * multiplier)
        
        # Create embed
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description=f"**[ {' | '.join(reels)} ]**",
            color=discord.Color.gold() if won else discord.Color.red()
        )
        
        emoji = await self.get_currency_emoji(interaction.guild.id)
        
        if won:
            net_gain = winnings - bet
            await self.update_balance(
                interaction.guild.id,
                interaction.user.id,
                net_gain,
                "Won slots"
            )
            
            embed.add_field(
                name="🎉 Winner!",
                value=f"**{multiplier}x** multiplier\n+{emoji} {net_gain}",
                inline=False
            )
            new_balance = balance + net_gain
        else:
            await self.update_balance(
                interaction.guild.id,
                interaction.user.id,
                -bet,
                "Lost slots"
            )
            
            embed.add_field(
                name="😢 Lost",
                value=f"-{emoji} {bet}",
                inline=False
            )
            new_balance = balance - bet
        
        embed.add_field(name="New Balance", value=f"{emoji} {new_balance}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================================================
    # FUN GAMES
    # ============================================================================
    
    @app_commands.command(name="rps", description="Play Rock Paper Scissors")
    @app_commands.describe(choice="Your choice")
    @app_commands.choices(choice=[
        app_commands.Choice(name="🪨 Rock", value="rock"),
        app_commands.Choice(name="📄 Paper", value="paper"),
        app_commands.Choice(name="✂️ Scissors", value="scissors")
    ])
    async def rps(self, interaction: discord.Interaction, choice: str):
        """Rock Paper Scissors game."""
        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)
        
        emojis = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
        
        # Determine winner
        if choice == bot_choice:
            result = "It's a tie!"
            color = discord.Color.yellow()
        elif (
            (choice == 'rock' and bot_choice == 'scissors') or
            (choice == 'paper' and bot_choice == 'rock') or
            (choice == 'scissors' and bot_choice == 'paper')
        ):
            result = "🎉 You won!"
            color = discord.Color.green()
        else:
            result = "😢 You lost!"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="Rock Paper Scissors",
            description=result,
            color=color
        )
        
        embed.add_field(
            name="Your Choice",
            value=f"{emojis[choice]} {choice.title()}",
            inline=True
        )
        embed.add_field(
            name="Bot's Choice",
            value=f"{emojis[bot_choice]} {bot_choice.title()}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roll", description="Roll dice")
    @app_commands.describe(sides="Number of sides on the dice (default: 6)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a dice."""
        if sides < 2 or sides > 100:
            await interaction.response.send_message(
                "❌ Dice must have between 2 and 100 sides.",
                ephemeral=True
            )
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"**Result: {result}**",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"d{sides}")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(Games(bot))
