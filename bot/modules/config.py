"""
Configuration loader for Discord bot.
Handles loading and validation of configuration from YAML and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the bot."""
    
    def __init__(self, config_path: str = "../config/bot_config.yaml"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(__file__).parent / config_path
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from YAML file and environment variables."""
        # Load YAML config
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy bot_config.example.yaml to bot_config.yaml and configure it."
            )
        
        # Override with environment variables where available
        self._load_env_overrides()
    
    def _load_env_overrides(self) -> None:
        """Override configuration with environment variables."""
        # Discord
        if token := os.getenv('DISCORD_TOKEN'):
            self._config.setdefault('bot', {})['token'] = token
        
        # Database
        if db_url := os.getenv('DATABASE_URL'):
            # Parse DATABASE_URL
            self._config.setdefault('database', {})
            # Simple parsing (postgresql://user:pass@host:port/dbname)
            if db_url.startswith('postgresql://'):
                db_url = db_url.replace('postgresql://', '')
                if '@' in db_url:
                    creds, location = db_url.split('@')
                    if ':' in creds:
                        user, password = creds.split(':')
                        self._config['database']['user'] = user
                        self._config['database']['password'] = password
                    if '/' in location:
                        host_port, dbname = location.split('/')
                        if ':' in host_port:
                            host, port = host_port.split(':')
                            self._config['database']['host'] = host
                            self._config['database']['port'] = int(port)
                        self._config['database']['database'] = dbname
        
        # Redis
        if redis_url := os.getenv('REDIS_URL'):
            self._config.setdefault('redis', {})
            if redis_url.startswith('redis://'):
                redis_url = redis_url.replace('redis://', '')
                if ':' in redis_url:
                    host, port_db = redis_url.split(':')
                    self._config['redis']['host'] = host
                    if '/' in port_db:
                        port, db = port_db.split('/')
                        self._config['redis']['port'] = int(port)
                        self._config['redis']['db'] = int(db)
        
        # AI
        if openai_key := os.getenv('OPENAI_API_KEY'):
            self._config.setdefault('ai', {})['api_key'] = openai_key
        if anthropic_key := os.getenv('ANTHROPIC_API_KEY'):
            self._config.setdefault('ai', {})
            if self._config['ai'].get('provider') == 'anthropic':
                self._config['ai']['api_key'] = anthropic_key
        
        # Dashboard
        if secret := os.getenv('DASHBOARD_SECRET_KEY'):
            self._config.setdefault('dashboard', {})['secret_key'] = secret
        if port := os.getenv('DASHBOARD_PORT'):
            self._config.setdefault('dashboard', {})['port'] = int(port)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'bot.token', 'database.host')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """
        Validate required configuration values.
        
        Returns:
            True if configuration is valid
        
        Raises:
            ValueError: If required configuration is missing
        """
        required = [
            ('bot.token', 'Discord bot token'),
            ('database.host', 'Database host'),
            ('database.database', 'Database name'),
        ]
        
        for key, description in required:
            if not self.get(key):
                raise ValueError(f"Missing required configuration: {description} ({key})")
        
        return True
    
    @property
    def bot_token(self) -> str:
        """Get Discord bot token."""
        return self.get('bot.token', '')
    
    @property
    def command_prefix(self) -> str:
        """Get command prefix."""
        return self.get('bot.prefix', '/')
    
    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        db = self.get('database', {})
        return (
            f"postgresql://{db.get('user')}:{db.get('password')}@"
            f"{db.get('host')}:{db.get('port')}/{db.get('database')}"
        )
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        redis = self.get('redis', {})
        password = f":{redis.get('password')}@" if redis.get('password') else ""
        return f"redis://{password}{redis.get('host')}:{redis.get('port')}/{redis.get('db')}"


# Global config instance
config = Config()
