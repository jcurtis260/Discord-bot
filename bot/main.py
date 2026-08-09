"""
Main Discord Bot
AI-Powered Community Manager with MEE6-like features
"""

import discord
from discord.ext import commands
import logging
import sys
from pathlib import Path
import asyncio
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from modules.config import config
from modules.database import Database, RedisCache

# Configure logging
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Main Discord bot class."""
    
    def __init__(self):
        """Initialize the bot."""
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True
        intents.voice_states = True
        intents.presences = True
        
        # Initialize bot
        super().__init__(
            command_prefix=config.command_prefix,
            intents=intents,
            help_command=None,  # We'll create a custom help command
            case_insensitive=True,
            strip_after_prefix=True
        )
        
        # Database and cache
        self.db: Optional[Database] = None
        self.cache: Optional[RedisCache] = None
        
        # Bot configuration
        self.config = config
        
        # Statistics
        self.commands_used = 0
        self.messages_seen = 0
    
    async def setup_hook(self) -> None:
        """Set up the bot before it starts."""
        logger.info("Setting up bot...")
        
        # Get bot owner ID
        app_info = await self.application_info()
        self.owner_id = app_info.owner.id
        logger.info(f"Bot owner: {app_info.owner} (ID: {self.owner_id})")
        
        # Connect to database
        try:
            self.db = Database(config.database_url)
            await self.db.connect()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
        
        # Connect to Redis
        try:
            self.cache = RedisCache(config.redis_url)
            await self.cache.connect()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Redis is optional, so we don't raise
        
        # Load extensions (cogs)
        await self.load_cogs()
        
        # Sync commands (for slash commands)
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def load_cogs(self) -> None:
        """Load all cog extensions."""
        cogs_dir = Path(__file__).parent / 'cogs'
        
        if not cogs_dir.exists():
            logger.warning(f"Cogs directory not found: {cogs_dir}")
            return
        
        # Load all Python files in cogs directory
        for file in cogs_dir.glob('*.py'):
            if file.stem.startswith('_'):
                continue
            
            try:
                await self.load_extension(f'cogs.{file.stem}')
                logger.info(f"Loaded cog: {file.stem}")
            except Exception as e:
                logger.error(f"Failed to load cog {file.stem}: {e}")
    
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        logger.info(f"Discord.py version: {discord.__version__}")
        logger.info("Bot is ready!")
        
        # Set bot status
        activity_type = config.get('bot.activity_type', 'watching').lower()
        activity_text = config.get('bot.activity', 'your server')
        
        activity_map = {
            'playing': discord.ActivityType.playing,
            'streaming': discord.ActivityType.streaming,
            'listening': discord.ActivityType.listening,
            'watching': discord.ActivityType.watching,
            'competing': discord.ActivityType.competing
        }
        
        activity_type_enum = activity_map.get(activity_type, discord.ActivityType.watching)
        activity = discord.Activity(type=activity_type_enum, name=activity_text)
        
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_command(self, ctx: commands.Context) -> None:
        """Called when a command is invoked."""
        self.commands_used += 1
        logger.info(f"Command used: {ctx.command} by {ctx.author} in {ctx.guild}")
    
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ This command is on cooldown. Try again in {error.retry_after:.1f}s")
            return
        
        # Log unexpected errors
        logger.error(f"Command error in {ctx.command}: {error}", exc_info=error)
        await ctx.send("❌ An error occurred while executing this command.")
    
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Called when the bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Initialize guild in database
        if self.db:
            try:
                await self.db.execute(
                    """
                    INSERT INTO guild_config (guild_id)
                    VALUES ($1)
                    ON CONFLICT (guild_id) DO NOTHING
                    """,
                    guild.id
                )
            except Exception as e:
                logger.error(f"Failed to initialize guild in database: {e}")
    
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Called when the bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
    
    async def on_message(self, message: discord.Message) -> None:
        """Called when a message is received."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        self.messages_seen += 1
        
        # Process commands
        await self.process_commands(message)
    
    async def close(self) -> None:
        """Clean up before shutting down."""
        logger.info("Shutting down bot...")
        
        # Close database connections
        if self.db:
            await self.db.close()
        
        if self.cache:
            await self.cache.close()
        
        await super().close()
        logger.info("Bot shut down complete")


async def main():
    """Main entry point."""
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create and start bot
    bot = DiscordBot()
    
    try:
        async with bot:
            await bot.start(config.bot_token)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await bot.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
