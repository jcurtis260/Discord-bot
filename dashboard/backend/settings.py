"""
Settings Management API Endpoints
Comprehensive admin panel for all bot configuration
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import yaml
from pathlib import Path

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Forward declarations - will be set from server.py
owner_user = None
current_user = None
get_db = None


# ============================================================================
# PYDANTIC MODELS FOR SETTINGS
# ============================================================================

class BotGlobalSettings(BaseModel):
    """Global bot settings."""
    status: str = Field(..., description="Bot status: online, idle, dnd, invisible")
    activity: str = Field(..., description="Activity text")
    activity_type: str = Field(..., description="Activity type: playing, watching, listening, streaming")
    

class AISettings(BaseModel):
    """AI configuration settings."""
    enabled: bool
    provider: str = Field(..., description="AI provider: openai, anthropic, local, chatgpt_web")
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=0.8, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=500, ge=1, le=4000)
    default_personality: Optional[str] = None
    conversation_memory: Optional[int] = Field(default=10, ge=1, le=50)
    random_engage_rate: Optional[float] = Field(default=0.05, ge=0.0, le=1.0)


class ModerationSettings(BaseModel):
    """Moderation configuration settings."""
    auto_mod_enabled: bool
    spam_threshold: Optional[int] = Field(default=5, ge=1, le=20)
    mention_threshold: Optional[int] = Field(default=5, ge=1, le=20)
    caps_threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    automod_action: Optional[str] = Field(default="warn", description="Action: warn, timeout, kick")


class AIModerationSettings(BaseModel):
    """AI-powered moderation settings."""
    enabled: bool
    threshold: float = Field(..., ge=0.0, le=1.0, description="Confidence threshold")
    action: str = Field(..., description="Action: warn, timeout, kick, log")
    check_toxicity: bool = True
    check_spam: bool = True
    check_nsfw: bool = True
    log_channel: Optional[int] = None


class LevelingSettings(BaseModel):
    """Leveling system settings."""
    enabled: bool
    xp_rate: int = Field(..., ge=1, le=100, description="XP per message")
    xp_cooldown: int = Field(..., ge=0, le=300, description="Cooldown in seconds")
    announce_level_up: bool = True
    level_up_channel: Optional[int] = None


class EconomySettings(BaseModel):
    """Economy system settings."""
    enabled: bool
    currency_name: str = Field(..., min_length=1, max_length=20)
    currency_emoji: str = Field(..., min_length=1, max_length=10)
    starting_balance: int = Field(..., ge=0, le=100000)
    daily_reward: int = Field(..., ge=0, le=10000)
    daily_streak_bonus: int = Field(..., ge=0, le=1000)
    message_earn_rate: int = Field(..., ge=0, le=100)
    message_earn_cooldown: int = Field(..., ge=0, le=300)


class GuildFeatureToggles(BaseModel):
    """Feature toggles for a guild."""
    welcome_messages: bool = True
    farewell_messages: bool = True
    reaction_roles: bool = True
    custom_commands: bool = True
    reminders: bool = True
    giveaways: bool = True
    games: bool = True


class GuildSettings(BaseModel):
    """Complete guild settings."""
    prefix: Optional[str] = Field(default="/", min_length=1, max_length=5)
    xp_enabled: Optional[bool] = True
    economy_enabled: Optional[bool] = True
    ai_enabled: Optional[bool] = True
    features: Optional[GuildFeatureToggles] = None


class DashboardSettings(BaseModel):
    """Dashboard configuration."""
    session_timeout: int = Field(..., ge=3600, le=604800, description="Session timeout in seconds")
    cors_origins: List[str]
    ip_whitelist: Optional[List[str]] = []
    allowed_user_ids: Optional[List[str]] = []


# ============================================================================
# SETTINGS ENDPOINTS
# ============================================================================

@router.get("/bot/global")
async def get_bot_global_settings(user: Dict = Depends(owner_user)):
    """Get global bot settings."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return {
            "status": config_data.get('bot', {}).get('status', 'online'),
            "activity": config_data.get('bot', {}).get('activity', 'Watching your server'),
            "activity_type": config_data.get('bot', {}).get('activity_type', 'watching'),
            "owner_id": config_data.get('bot', {}).get('owner_id', '')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {str(e)}")


@router.put("/bot/global")
async def update_bot_global_settings(
    settings: BotGlobalSettings,
    user: Dict = Depends(owner_user)
):
    """Update global bot settings."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Update bot settings
        if 'bot' not in config_data:
            config_data['bot'] = {}
        
        config_data['bot']['status'] = settings.status
        config_data['bot']['activity'] = settings.activity
        config_data['bot']['activity_type'] = settings.activity_type
        
        # Write back to file
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return {"success": True, "message": "Bot settings updated. Restart bot to apply changes."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@router.get("/ai")
async def get_ai_settings(user: Dict = Depends(owner_user)):
    """Get AI configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        ai_config = config_data.get('ai', {})
        return {
            "enabled": ai_config.get('enabled', True),
            "provider": ai_config.get('provider', 'openai'),
            "model": ai_config.get('model', 'gpt-4'),
            "temperature": ai_config.get('temperature', 0.8),
            "max_tokens": ai_config.get('max_tokens', 500),
            "default_personality": ai_config.get('default_personality', 'friendly'),
            "conversation_memory": ai_config.get('conversation_memory', 10),
            "random_engage_rate": ai_config.get('random_engage_rate', 0.05)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load AI config: {str(e)}")


@router.put("/ai")
async def update_ai_settings(
    settings: AISettings,
    user: Dict = Depends(owner_user)
):
    """Update AI configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Update AI settings
        if 'ai' not in config_data:
            config_data['ai'] = {}
        
        config_data['ai']['enabled'] = settings.enabled
        config_data['ai']['provider'] = settings.provider
        if settings.model:
            config_data['ai']['model'] = settings.model
        if settings.temperature is not None:
            config_data['ai']['temperature'] = settings.temperature
        if settings.max_tokens is not None:
            config_data['ai']['max_tokens'] = settings.max_tokens
        if settings.default_personality:
            config_data['ai']['default_personality'] = settings.default_personality
        if settings.conversation_memory is not None:
            config_data['ai']['conversation_memory'] = settings.conversation_memory
        if settings.random_engage_rate is not None:
            config_data['ai']['random_engage_rate'] = settings.random_engage_rate
        
        # Write back
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return {"success": True, "message": "AI settings updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update AI config: {str(e)}")


@router.get("/moderation")
async def get_moderation_settings(user: Dict = Depends(owner_user)):
    """Get moderation configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        mod_config = config_data.get('moderation', {})
        return {
            "auto_mod_enabled": mod_config.get('auto_mod_enabled', True),
            "spam_threshold": mod_config.get('spam_threshold', 5),
            "mention_threshold": mod_config.get('max_mentions', 5),
            "caps_threshold": mod_config.get('caps_threshold', 0.7),
            "automod_action": mod_config.get('action', 'warn')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load moderation config: {str(e)}")


@router.put("/moderation")
async def update_moderation_settings(
    settings: ModerationSettings,
    user: Dict = Depends(owner_user)
):
    """Update moderation configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if 'moderation' not in config_data:
            config_data['moderation'] = {}
        
        config_data['moderation']['auto_mod_enabled'] = settings.auto_mod_enabled
        config_data['moderation']['spam_threshold'] = settings.spam_threshold
        config_data['moderation']['max_mentions'] = settings.mention_threshold
        config_data['moderation']['caps_threshold'] = settings.caps_threshold
        config_data['moderation']['action'] = settings.automod_action
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return {"success": True, "message": "Moderation settings updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update moderation config: {str(e)}")


@router.get("/leveling")
async def get_leveling_settings(user: Dict = Depends(owner_user)):
    """Get leveling system configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        leveling_config = config_data.get('leveling', {})
        return {
            "enabled": leveling_config.get('enabled', True),
            "xp_rate": leveling_config.get('xp_per_message', 15),
            "xp_cooldown": leveling_config.get('xp_cooldown', 60),
            "announce_level_up": leveling_config.get('announce_level_up', True),
            "level_up_channel": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load leveling config: {str(e)}")


@router.put("/leveling")
async def update_leveling_settings(
    settings: LevelingSettings,
    user: Dict = Depends(owner_user)
):
    """Update leveling system configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if 'leveling' not in config_data:
            config_data['leveling'] = {}
        
        config_data['leveling']['enabled'] = settings.enabled
        config_data['leveling']['xp_per_message'] = settings.xp_rate
        config_data['leveling']['xp_cooldown'] = settings.xp_cooldown
        config_data['leveling']['announce_level_up'] = settings.announce_level_up
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return {"success": True, "message": "Leveling settings updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update leveling config: {str(e)}")


@router.get("/economy")
async def get_economy_settings(user: Dict = Depends(owner_user)):
    """Get economy system configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        economy_config = config_data.get('economy', {})
        return {
            "enabled": economy_config.get('enabled', True),
            "currency_name": economy_config.get('currency_name', 'Credits'),
            "currency_emoji": economy_config.get('currency_emoji', '💰'),
            "starting_balance": economy_config.get('starting_balance', 100),
            "daily_reward": economy_config.get('daily_reward', 50),
            "daily_streak_bonus": economy_config.get('daily_streak_bonus', 10),
            "message_earn_rate": economy_config.get('message_earn_rate', 5),
            "message_earn_cooldown": economy_config.get('message_earn_cooldown', 60)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load economy config: {str(e)}")


@router.put("/economy")
async def update_economy_settings(
    settings: EconomySettings,
    user: Dict = Depends(owner_user)
):
    """Update economy system configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if 'economy' not in config_data:
            config_data['economy'] = {}
        
        config_data['economy']['enabled'] = settings.enabled
        config_data['economy']['currency_name'] = settings.currency_name
        config_data['economy']['currency_emoji'] = settings.currency_emoji
        config_data['economy']['starting_balance'] = settings.starting_balance
        config_data['economy']['daily_reward'] = settings.daily_reward
        config_data['economy']['daily_streak_bonus'] = settings.daily_streak_bonus
        config_data['economy']['message_earn_rate'] = settings.message_earn_rate
        config_data['economy']['message_earn_cooldown'] = settings.message_earn_cooldown
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return {"success": True, "message": "Economy settings updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update economy config: {str(e)}")


@router.get("/features")
async def get_feature_toggles(user: Dict = Depends(owner_user)):
    """Get feature toggle configuration."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        features = config_data.get('features', {})
        return {
            "welcome_messages": features.get('welcome_messages', True),
            "farewell_messages": features.get('farewell_messages', True),
            "reaction_roles": features.get('reaction_roles', True),
            "custom_commands": features.get('custom_commands', True),
            "reminders": features.get('reminders', True),
            "giveaways": config_data.get('giveaways', {}).get('enabled', True),
            "games": config_data.get('games', {}).get('enabled', True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load features config: {str(e)}")


@router.put("/features")
async def update_feature_toggles(
    settings: GuildFeatureToggles,
    user: Dict = Depends(owner_user)
):
    """Update feature toggles."""
    config_path = Path(__file__).parent / '../../config/bot_config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if 'features' not in config_data:
            config_data['features'] = {}
        
        config_data['features']['welcome_messages'] = settings.welcome_messages
        config_data['features']['farewell_messages'] = settings.farewell_messages
        config_data['features']['reaction_roles'] = settings.reaction_roles
        config_data['features']['custom_commands'] = settings.custom_commands
        config_data['features']['reminders'] = settings.reminders
        
        if 'giveaways' not in config_data:
            config_data['giveaways'] = {}
        config_data['giveaways']['enabled'] = settings.giveaways
        
        if 'games' not in config_data:
            config_data['games'] = {}
        config_data['games']['enabled'] = settings.games
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return {"success": True, "message": "Feature toggles updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update features config: {str(e)}")


@router.get("/guild/{guild_id}")
async def get_guild_settings(
    guild_id: int,
    user: Dict = Depends(current_user),
    db: Database = Depends(get_db)
):
    """Get settings for a specific guild."""
    settings = await db.fetchrow(
        "SELECT * FROM guild_config WHERE guild_id = $1",
        guild_id
    )
    
    if not settings:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    return dict(settings)


@router.put("/guild/{guild_id}")
async def update_guild_settings(
    guild_id: int,
    settings: GuildSettings,
    user: Dict = Depends(owner_user),
    db: Database = Depends(get_db)
):
    """Update settings for a specific guild."""
    await db.ensure_guild(guild_id)
    
    # Build update query dynamically
    updates = []
    values = []
    param_count = 1
    
    if settings.prefix is not None:
        updates.append(f"prefix = ${param_count}")
        values.append(settings.prefix)
        param_count += 1
    
    if settings.xp_enabled is not None:
        updates.append(f"xp_enabled = ${param_count}")
        values.append(settings.xp_enabled)
        param_count += 1
    
    if settings.economy_enabled is not None:
        updates.append(f"economy_enabled = ${param_count}")
        values.append(settings.economy_enabled)
        param_count += 1
    
    if settings.ai_enabled is not None:
        updates.append(f"ai_enabled = ${param_count}")
        values.append(settings.ai_enabled)
        param_count += 1
    
    if updates:
        query = f"""
            UPDATE guild_config
            SET {', '.join(updates)}
            WHERE guild_id = ${param_count}
        """
        values.append(guild_id)
        
        await db.execute(query, *values)
    
    return {"success": True, "message": "Guild settings updated successfully"}


# Dependency to get database
async def get_db():
    """Get database instance."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db
