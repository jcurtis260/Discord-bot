"""
Red-DiscordBot Compatibility Layer

This module provides compatibility with Red-DiscordBot cogs by emulating
the Red Config API and Data Manager.
"""

import json
import asyncio
from typing import Any, Dict, Optional, List, Union
from pathlib import Path
import discord
from discord.ext import commands


class ConfigValue:
    """Represents a config value in the Red config system."""
    
    def __init__(self, identifier: str, data: Dict[str, Any], parent: 'Config'):
        self.identifier = identifier
        self._data = data
        self._parent = parent
    
    async def set(self, value: Any) -> None:
        """Set the config value."""
        keys = self.identifier.split('.')
        current = self._data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        await self._parent._save()
    
    async def get(self) -> Any:
        """Get the config value."""
        keys = self.identifier.split('.')
        current = self._data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    async def clear(self) -> None:
        """Clear the config value."""
        await self.set(None)


class ScopeConfig:
    """Represents a scoped config (guild, member, user, etc.)"""
    
    def __init__(self, scope_id: Optional[int], data: Dict[str, Any], parent: 'Config'):
        self.scope_id = scope_id
        self._data = data
        self._parent = parent
    
    def __call__(self, item_id: Optional[int] = None):
        """Allow calling to get nested scope."""
        if item_id is not None:
            key = str(item_id)
            if key not in self._data:
                self._data[key] = {}
            return ScopeConfig(item_id, self._data[key], self._parent)
        return self
    
    def __getattr__(self, name: str):
        """Get a config attribute."""
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return ConfigValue(name, self._data, self._parent)
    
    async def all(self) -> Dict[str, Any]:
        """Get all config data."""
        return self._data.copy()
    
    async def set(self, value: Dict[str, Any]) -> None:
        """Set all config data."""
        self._data.clear()
        self._data.update(value)
        await self._parent._save()
    
    async def clear(self) -> None:
        """Clear all config data."""
        self._data.clear()
        await self._parent._save()


class Config:
    """
    Emulates Red-DiscordBot's Config API.
    
    Stores configuration data in JSON files, organized by cog name.
    """
    
    GLOBAL = "global"
    GUILD = "guild"
    MEMBER = "member"
    USER = "user"
    ROLE = "role"
    CHANNEL = "channel"
    
    _instances: Dict[str, 'Config'] = {}
    
    def __init__(self, cog_name: str, cog_instance=None, force_registration: bool = False):
        self.cog_name = cog_name
        self.cog_instance = cog_instance
        self.force_registration = force_registration
        
        # Data directory
        self.data_path = Path(__file__).parent.parent / "red_cogs" / "data" / cog_name
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Config file
        self.config_file = self.data_path / "config.json"
        
        # Load existing data
        self._data: Dict[str, Any] = self._load()
        
        # Track if we need to save
        self._save_task: Optional[asyncio.Task] = None
        self._save_lock = asyncio.Lock()
        
        Config._instances[cog_name] = self
    
    def _load(self) -> Dict[str, Any]:
        """Load config from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    async def _save(self) -> None:
        """Save config to file (debounced)."""
        async with self._save_lock:
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self._data, f, indent=2)
            except Exception as e:
                print(f"Error saving config for {self.cog_name}: {e}")
    
    @classmethod
    def get_conf(cls, cog_instance, identifier: str, force_registration: bool = False):
        """Get or create a Config instance (Red API compatibility)."""
        cog_name = cog_instance.__class__.__name__
        if cog_name in cls._instances:
            return cls._instances[cog_name]
        return cls(cog_name, cog_instance, force_registration)
    
    def register_global(self, **defaults) -> None:
        """Register global defaults."""
        if self.GLOBAL not in self._data:
            self._data[self.GLOBAL] = {}
        for key, value in defaults.items():
            if key not in self._data[self.GLOBAL]:
                self._data[self.GLOBAL][key] = value
    
    def register_guild(self, **defaults) -> None:
        """Register guild defaults."""
        if self.GUILD not in self._data:
            self._data[self.GUILD] = {}
        self._guild_defaults = defaults
    
    def register_member(self, **defaults) -> None:
        """Register member defaults."""
        if self.MEMBER not in self._data:
            self._data[self.MEMBER] = {}
        self._member_defaults = defaults
    
    def register_user(self, **defaults) -> None:
        """Register user defaults."""
        if self.USER not in self._data:
            self._data[self.USER] = {}
        self._user_defaults = defaults
    
    def register_role(self, **defaults) -> None:
        """Register role defaults."""
        if self.ROLE not in self._data:
            self._data[self.ROLE] = {}
        self._role_defaults = defaults
    
    def register_channel(self, **defaults) -> None:
        """Register channel defaults."""
        if self.CHANNEL not in self._data:
            self._data[self.CHANNEL] = {}
        self._channel_defaults = defaults
    
    def guild(self, guild: Optional[Union[discord.Guild, int]] = None) -> ScopeConfig:
        """Get guild config."""
        if self.GUILD not in self._data:
            self._data[self.GUILD] = {}
        
        if guild is None:
            return ScopeConfig(None, self._data[self.GUILD], self)
        
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        key = str(guild_id)
        
        if key not in self._data[self.GUILD]:
            self._data[self.GUILD][key] = {}
        
        return ScopeConfig(guild_id, self._data[self.GUILD][key], self)
    
    def member(self, member: Union[discord.Member, int]) -> ScopeConfig:
        """Get member config."""
        if self.MEMBER not in self._data:
            self._data[self.MEMBER] = {}
        
        member_id = member.id if isinstance(member, discord.Member) else member
        key = str(member_id)
        
        if key not in self._data[self.MEMBER]:
            self._data[self.MEMBER][key] = {}
        
        return ScopeConfig(member_id, self._data[self.MEMBER][key], self)
    
    def user(self, user: Union[discord.User, int]) -> ScopeConfig:
        """Get user config."""
        if self.USER not in self._data:
            self._data[self.USER] = {}
        
        user_id = user.id if isinstance(user, discord.User) else user
        key = str(user_id)
        
        if key not in self._data[self.USER]:
            self._data[self.USER][key] = {}
        
        return ScopeConfig(user_id, self._data[self.USER][key], self)
    
    def role(self, role: Union[discord.Role, int]) -> ScopeConfig:
        """Get role config."""
        if self.ROLE not in self._data:
            self._data[self.ROLE] = {}
        
        role_id = role.id if isinstance(role, discord.Role) else role
        key = str(role_id)
        
        if key not in self._data[self.ROLE]:
            self._data[self.ROLE][key] = {}
        
        return ScopeConfig(role_id, self._data[self.ROLE][key], self)
    
    def channel(self, channel: Union[discord.TextChannel, int]) -> ScopeConfig:
        """Get channel config."""
        if self.CHANNEL not in self._data:
            self._data[self.CHANNEL] = {}
        
        channel_id = channel.id if isinstance(channel, discord.TextChannel) else channel
        key = str(channel_id)
        
        if key not in self._data[self.CHANNEL]:
            self._data[self.CHANNEL][key] = {}
        
        return ScopeConfig(channel_id, self._data[self.CHANNEL][key], self)
    
    async def clear_all(self) -> None:
        """Clear all config data."""
        self._data.clear()
        await self._save()


class RedCogManager:
    """
    Manages Red-DiscordBot cogs.
    
    Loads cogs from the red_cogs directory and provides compatibility
    with the Red cog ecosystem.
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.red_cogs_path = Path(__file__).parent.parent / "red_cogs"
        self.red_cogs_path.mkdir(exist_ok=True)
        
        # Track loaded Red cogs
        self.loaded_cogs: Dict[str, Any] = {}
    
    async def load_red_cog(self, cog_name: str) -> bool:
        """
        Load a Red cog from the red_cogs directory.
        
        Args:
            cog_name: Name of the cog to load (should be a directory in red_cogs/)
        
        Returns:
            True if successful, False otherwise
        """
        cog_path = self.red_cogs_path / cog_name
        
        if not cog_path.exists() or not cog_path.is_dir():
            return False
        
        # Check for __init__.py or main cog file
        init_file = cog_path / "__init__.py"
        cog_file = cog_path / f"{cog_name}.py"
        
        target_file = init_file if init_file.exists() else cog_file
        
        if not target_file.exists():
            return False
        
        try:
            # Load the cog using discord.py's extension system
            await self.bot.load_extension(f"red_cogs.{cog_name}")
            self.loaded_cogs[cog_name] = True
            return True
        except Exception as e:
            print(f"Error loading Red cog {cog_name}: {e}")
            return False
    
    async def unload_red_cog(self, cog_name: str) -> bool:
        """Unload a Red cog."""
        if cog_name not in self.loaded_cogs:
            return False
        
        try:
            await self.bot.unload_extension(f"red_cogs.{cog_name}")
            del self.loaded_cogs[cog_name]
            return True
        except Exception as e:
            print(f"Error unloading Red cog {cog_name}: {e}")
            return False
    
    async def reload_red_cog(self, cog_name: str) -> bool:
        """Reload a Red cog."""
        if cog_name not in self.loaded_cogs:
            return await self.load_red_cog(cog_name)
        
        try:
            await self.bot.reload_extension(f"red_cogs.{cog_name}")
            return True
        except Exception as e:
            print(f"Error reloading Red cog {cog_name}: {e}")
            return False
    
    def list_available_cogs(self) -> List[str]:
        """List all available Red cogs in the red_cogs directory."""
        cogs = []
        if not self.red_cogs_path.exists():
            return cogs
        
        for item in self.red_cogs_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # Check if it has a valid cog file
                init_file = item / "__init__.py"
                cog_file = item / f"{item.name}.py"
                if init_file.exists() or cog_file.exists():
                    cogs.append(item.name)
        
        return sorted(cogs)
    
    def is_loaded(self, cog_name: str) -> bool:
        """Check if a Red cog is loaded."""
        return cog_name in self.loaded_cogs
