"""
Dashboard Backend API Server
FastAPI server for bot management dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import secrets
import logging

# Add bot directory to path
sys.path.append(str(Path(__file__).parent / '../../bot'))

from modules.database import Database
from modules.config import config
from auth import AuthManager, require_auth, require_owner
from settings import router as settings_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Discord Bot Dashboard API",
    description="Management API for Discord Bot",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('dashboard.cors_origins', ['http://localhost:3000']),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include settings router
from settings import router as settings_router
settings_router.owner_user = owner_user
settings_router.current_user = current_user
app.include_router(settings_router)

# Security schemes
security_bearer = HTTPBearer(auto_error=False)
security_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)

# Database and Auth
db: Optional[Database] = None
auth_manager: Optional[AuthManager] = None


# Dependency injection for auth_manager
def get_auth_manager():
    """Get auth manager instance."""
    if not auth_manager:
        raise HTTPException(status_code=500, detail="Auth manager not initialized")
    return auth_manager


# Wrapper functions for dependencies
async def current_user(
    request: Request,
    bearer_token: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    api_key: Optional[str] = Security(security_api_key),
    auth: AuthManager = Depends(get_auth_manager)
) -> Dict:
    """Get current authenticated user."""
    return await require_auth(request, bearer_token, api_key, auth)


async def owner_user(
    user: Dict = Depends(current_user),
    auth: AuthManager = Depends(get_auth_manager)
) -> Dict:
    """Require owner privileges."""
    return await require_owner(user, auth)


# ============================================================================
# MODELS
# ============================================================================

class User(BaseModel):
    """User model."""
    id: int
    username: str
    email: Optional[str]
    role: str


class ServerInfo(BaseModel):
    """Server information model."""
    guild_id: int
    name: str
    member_count: int
    features: dict


class BotStats(BaseModel):
    """Bot statistics model."""
    total_servers: int
    total_users: int
    total_commands: int
    uptime: str


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize connections on startup."""
    global db, auth_manager
    
    # Initialize database
    db = Database(config.database_url)
    await db.connect()
    logger.info("✅ Database connected")
    
    # Initialize auth manager
    auth_manager = AuthManager(config._config)
    logger.info("✅ Auth manager initialized")
    
    # Check security configuration
    if not config.get('dashboard.secret_key') or config.get('dashboard.secret_key') == 'CHANGE_THIS_SECRET_KEY_FOR_PRODUCTION':
        logger.warning("⚠️  WARNING: Using default secret key! Generate a secure one for production!")
    
    if not config.get('bot.owner_id'):
        logger.warning("⚠️  WARNING: No bot owner_id configured! Dashboard will be inaccessible!")
    
    if not config.get('dashboard.discord_client_id'):
        logger.warning("⚠️  Discord OAuth2 not configured. Dashboard login will not work!")
    
    logger.info("🔒 Security features:")
    logger.info(f"   - Owner ID: {config.get('bot.owner_id', 'NOT SET')}")
    logger.info(f"   - Discord OAuth: {'✅ Enabled' if config.get('dashboard.discord_client_id') else '❌ Disabled'}")
    logger.info(f"   - API Key Auth: {'✅ Enabled' if config.get('dashboard.api_key') else '❌ Disabled'}")
    logger.info(f"   - IP Whitelist: {'✅ Enabled' if config.get('dashboard.ip_whitelist') else '❌ Disabled'}")


@app.on_event("shutdown")
async def shutdown():
    """Close connections on shutdown."""
    if db:
        await db.close()
    logger.info("✅ Database disconnected")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.get("/api/auth/discord")
async def discord_login():
    """
    Redirect to Discord OAuth2 authorization.
    
    Returns:
        Discord OAuth2 URL and state
    """
    if not auth_manager.discord_client_id:
        raise HTTPException(
            status_code=503,
            detail="Discord OAuth2 not configured. Please set discord_client_id and discord_client_secret in config."
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Build Discord OAuth2 URL
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize?"
        f"client_id={auth_manager.discord_client_id}&"
        f"redirect_uri={auth_manager.discord_redirect_uri}&"
        f"response_type=code&"
        f"scope=identify&"
        f"state={state}"
    )
    
    return {
        "url": discord_auth_url,
        "state": state
    }


@app.get("/api/auth/callback")
async def discord_callback(code: str, state: str):
    """
    Handle Discord OAuth2 callback.
    
    Args:
        code: Authorization code from Discord
        state: CSRF state token
        
    Returns:
        JWT access token
    """
    try:
        # Exchange code for access token
        token_data = await auth_manager.exchange_code(code)
        discord_access_token = token_data['access_token']
        
        # Get user info
        user_info = await auth_manager.get_discord_user(discord_access_token)
        user_id = user_info['id']
        
        # Check if user is owner
        if not auth_manager.is_owner(user_id):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Only the bot owner can access this dashboard. Your ID: {user_id}"
            )
        
        # Create JWT token
        access_token = auth_manager.create_access_token({
            "sub": user_id,
            "username": user_info['username'],
            "discriminator": user_info.get('discriminator', '0'),
            "avatar": user_info.get('avatar'),
            "global_name": user_info.get('global_name')
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "username": user_info['username'],
                "discriminator": user_info.get('discriminator', '0'),
                "avatar": user_info.get('avatar'),
                "global_name": user_info.get('global_name')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )


@app.get("/api/auth/me")
async def get_current_user(user: Dict = Depends(current_user)):
    """
    Get current authenticated user.
    
    Returns:
        User information
    """
    return user


@app.post("/api/auth/logout")
async def logout(user: Dict = Depends(current_user)):
    """
    Logout endpoint.
    
    Note: With JWT, logout is handled client-side by deleting the token.
    This endpoint is provided for completeness.
    """
    return {"success": True, "message": "Logged out successfully"}


# ============================================================================
# BOT ENDPOINTS
# ============================================================================

@app.get("/api/bot/status")
async def get_bot_status(user: Dict = Depends(current_user)):
    """Get bot status and statistics."""
    # Query database for stats
    stats = await db.fetchrow("""
        SELECT 
            (SELECT COUNT(*) FROM guild_config) as total_servers,
            (SELECT COUNT(*) FROM users) as total_users
    """)
    
    return {
        "online": True,
        "latency": 45,
        "total_servers": stats['total_servers'] if stats else 0,
        "total_users": stats['total_users'] if stats else 0,
        "uptime": "Running"
    }


@app.get("/api/bot/config")
async def get_bot_config(user: Dict = Depends(owner_user)):
    """Get global bot configuration."""
    settings = await db.fetch("SELECT * FROM bot_settings")
    
    config_dict = {}
    for setting in settings:
        config_dict[setting['setting_key']] = setting['setting_value']
    
    return config_dict


# ============================================================================
# SERVER ENDPOINTS
# ============================================================================

@app.get("/api/servers")
async def list_servers(user: Dict = Depends(current_user)):
    """List all servers the bot is in."""
    servers = await db.fetch("""
        SELECT guild_id, prefix, xp_enabled, economy_enabled, ai_enabled
        FROM guild_config
        ORDER BY guild_id
    """)
    
    return [dict(server) for server in servers]


@app.get("/api/servers/{guild_id}")
async def get_server(guild_id: int, user: Dict = Depends(current_user)):
    """Get detailed server information."""
    server = await db.fetchrow(
        "SELECT * FROM guild_config WHERE guild_id = $1",
        guild_id
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Get member count
    member_count = await db.fetchval(
        "SELECT COUNT(*) FROM guild_members WHERE guild_id = $1",
        guild_id
    )
    
    return {
        **dict(server),
        "member_count": member_count
    }


@app.put("/api/servers/{guild_id}/config")
async def update_server_config(guild_id: int, config: dict, user: Dict = Depends(owner_user)):
    """Update server configuration."""
    # TODO: Validate config and update database
    return {"success": True, "message": "Configuration updated"}


# ============================================================================
# MODERATION ENDPOINTS
# ============================================================================

@app.get("/api/servers/{guild_id}/infractions")
async def get_infractions(guild_id: int, limit: int = 50, user: Dict = Depends(current_user)):
    """Get recent infractions for a server."""
    infractions = await db.fetch("""
        SELECT * FROM infractions
        WHERE guild_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """, guild_id, limit)
    
    return [dict(inf) for inf in infractions]


# ============================================================================
# LEVELING ENDPOINTS
# ============================================================================

@app.get("/api/servers/{guild_id}/leaderboard")
async def get_leaderboard(guild_id: int, limit: int = 10, user: Dict = Depends(current_user)):
    """Get XP leaderboard for a server."""
    leaderboard = await db.fetch("""
        SELECT user_id, xp, level, message_count
        FROM guild_members
        WHERE guild_id = $1
        ORDER BY xp DESC
        LIMIT $2
    """, guild_id, limit)
    
    return [dict(entry) for entry in leaderboard]


@app.get("/api/servers/{guild_id}/role-rewards")
async def get_role_rewards(guild_id: int, user: Dict = Depends(current_user)):
    """Get role rewards configuration."""
    rewards = await db.fetch("""
        SELECT * FROM role_rewards
        WHERE guild_id = $1
        ORDER BY required_level ASC
    """, guild_id)
    
    return [dict(reward) for reward in rewards]


# ============================================================================
# ECONOMY ENDPOINTS
# ============================================================================

@app.get("/api/servers/{guild_id}/economy/shop")
async def get_shop_items(guild_id: int, user: Dict = Depends(current_user)):
    """Get shop items for a server."""
    items = await db.fetch("""
        SELECT * FROM shop_items
        WHERE guild_id = $1 AND purchasable = TRUE
        ORDER BY price ASC
    """, guild_id)
    
    return [dict(item) for item in items]


@app.post("/api/servers/{guild_id}/economy/shop")
async def create_shop_item(guild_id: int, item: dict, user: Dict = Depends(owner_user)):
    """Create a new shop item."""
    # TODO: Validate and create item
    return {"success": True, "message": "Item created"}


# ============================================================================
# GIVEAWAY ENDPOINTS
# ============================================================================

@app.get("/api/servers/{guild_id}/giveaways")
async def get_giveaways(guild_id: int, status: str = "active", user: Dict = Depends(current_user)):
    """Get giveaways for a server."""
    giveaways = await db.fetch("""
        SELECT g.*, COUNT(e.user_id) as entry_count
        FROM giveaways g
        LEFT JOIN giveaway_entries e ON g.id = e.giveaway_id
        WHERE g.guild_id = $1 AND g.status = $2
        GROUP BY g.id
        ORDER BY g.created_at DESC
    """, guild_id, status)
    
    return [dict(giveaway) for giveaway in giveaways]


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/servers/{guild_id}/analytics")
async def get_analytics(guild_id: int, user: Dict = Depends(current_user)):
    """Get analytics data for a server."""
    # Get various stats
    stats = await db.fetchrow("""
        SELECT 
            COUNT(DISTINCT user_id) as total_members,
            SUM(message_count) as total_messages,
            AVG(level) as avg_level
        FROM guild_members
        WHERE guild_id = $1
    """, guild_id)
    
    # Get command usage
    command_usage = await db.fetch("""
        SELECT action, COUNT(*) as count
        FROM mod_log
        WHERE guild_id = $1
        GROUP BY action
        ORDER BY count DESC
        LIMIT 10
    """, guild_id)
    
    return {
        "stats": dict(stats) if stats else {},
        "command_usage": [dict(cmd) for cmd in command_usage]
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Discord Bot Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = config.get('dashboard.port', 8080)
    host = config.get('dashboard.host', '0.0.0.0')
    
    print(f"🚀 Starting Dashboard API on {host}:{port}")
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
