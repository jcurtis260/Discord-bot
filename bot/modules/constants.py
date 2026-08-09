"""
Bot Color Constants

Consistent colors for Discord embeds throughout the bot.
"""

import discord


class BotColors:
    """Color constants for consistent Discord embed styling."""
    
    # Status colors
    SUCCESS = discord.Color.green()  # 0x2ecc71
    ERROR = discord.Color.red()  # 0xe74c3c
    WARNING = discord.Color.orange()  # 0xe67e22
    INFO = discord.Color.blue()  # 0x3498db
    
    # Feature colors
    MODERATION = discord.Color.red()
    LEVELING = discord.Color.purple()
    ECONOMY = discord.Color.gold()
    AI = discord.Color.teal()
    GAMES = discord.Color.magenta()
    UTILITY = discord.Color.blue()
    
    # Special colors
    GIVEAWAY = discord.Color.from_rgb(255, 215, 0)  # Gold
    PREMIUM = discord.Color.from_rgb(255, 105, 180)  # Hot pink
    
    @staticmethod
    def from_status(status: str) -> discord.Color:
        """
        Get color from status string.
        
        Args:
            status: Status string (success, error, warning, info)
        
        Returns:
            Discord color
        """
        status_map = {
            'success': BotColors.SUCCESS,
            'error': BotColors.ERROR,
            'warning': BotColors.WARNING,
            'info': BotColors.INFO,
        }
        return status_map.get(status.lower(), BotColors.INFO)


# Constants for command rate limiting
class RateLimits:
    """Rate limit constants for commands."""
    
    # Standard rate limits (cooldown in seconds)
    STANDARD = 5  # Most commands
    MODERATION = 3  # Mod commands
    ECONOMY = 10  # Economy commands
    AI = 30  # AI commands (expensive)
    GAMES = 60  # Games with rewards
    
    # Per-user limits
    DAILY_REWARD = 86400  # 24 hours
    WEEKLY_REWARD = 604800  # 7 days


# Constants for message lengths
class MessageLimits:
    """Message and content length limits."""
    
    MAX_MESSAGE_LENGTH = 2000  # Discord limit
    MAX_EMBED_DESCRIPTION = 4096  # Discord embed limit
    MAX_EMBED_FIELD_VALUE = 1024  # Discord embed field limit
    MAX_EMBED_FIELDS = 25  # Discord embed fields limit
    
    # Bot-specific limits
    MAX_CUSTOM_COMMAND_RESPONSE = 1000
    MAX_AI_RESPONSE = 500
    MAX_REMINDER_MESSAGE = 500
    MAX_WELCOME_MESSAGE = 1000


# Constants for pagination
class Pagination:
    """Pagination constants."""
    
    LEADERBOARD_PAGE_SIZE = 10
    COMMAND_LIST_PAGE_SIZE = 20
    INFRACTION_PAGE_SIZE = 10
    TRANSACTION_PAGE_SIZE = 15
    
    # Emoji for pagination buttons
    FIRST = "⏮️"
    PREVIOUS = "◀️"
    NEXT = "▶️"
    LAST = "⏭️"
    STOP = "⏹️"


# XP and Leveling constants
class LevelingConstants:
    """Constants for the leveling system."""
    
    XP_PER_MESSAGE = 15  # Base XP per message
    XP_MIN = 10  # Minimum XP
    XP_MAX = 25  # Maximum XP
    XP_COOLDOWN = 60  # Cooldown in seconds
    
    @staticmethod
    def xp_for_level(level: int) -> int:
        """Calculate total XP needed for a level."""
        return 5 * (level ** 2) + (50 * level) + 100
    
    @staticmethod
    def level_from_xp(xp: int) -> int:
        """Calculate level from XP."""
        level = 0
        while xp >= LevelingConstants.xp_for_level(level + 1):
            level += 1
        return level


# Economy constants
class EconomyConstants:
    """Constants for the economy system."""
    
    STARTING_BALANCE = 100
    DAILY_REWARD = 500
    WEEKLY_REWARD = 2000
    
    # Transaction limits
    MIN_TRANSFER = 1
    MAX_TRANSFER = 1000000
    
    # Betting limits
    MIN_BET = 10
    MAX_BET = 10000


# AI constants
class AIConstants:
    """Constants for AI systems."""
    
    MAX_CONTEXT_LENGTH = 20  # Messages to keep in context
    MAX_AI_RESPONSE_LENGTH = 500
    AI_RESPONSE_TIMEOUT = 30  # Seconds
    
    # AI Moderation
    DEFAULT_CONFIDENCE_THRESHOLD = 0.7
    MIN_MESSAGE_LENGTH_FOR_AI_MOD = 10
