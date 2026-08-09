"""
Dashboard Backend API Server
FastAPI server for bot management dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add bot directory to path
sys.path.append(str(Path(__file__).parent / '../../bot'))

from modules.database import Database
from modules.config import config

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

# Database connection
db: Optional[Database] = None

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
    global db
    db = Database(config.database_url)
    await db.connect()
    print("✅ Database connected")


@app.on_event("shutdown")
async def shutdown():
    """Close connections on shutdown."""
    if db:
        await db.close()
    print("✅ Database disconnected")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint.
    
    Returns JWT token for authenticated requests.
    """
    # TODO: Implement proper authentication
    # This is a placeholder
    return {
        "access_token": "placeholder_token",
        "token_type": "bearer"
    }


@app.get("/api/auth/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user."""
    # TODO: Implement proper user retrieval
    return {
        "id": 1,
        "username": "admin",
        "role": "admin"
    }


# ============================================================================
# BOT ENDPOINTS
# ============================================================================

@app.get("/api/bot/status")
async def get_bot_status():
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
async def get_bot_config():
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
async def list_servers():
    """List all servers the bot is in."""
    servers = await db.fetch("""
        SELECT guild_id, prefix, xp_enabled, economy_enabled, ai_enabled
        FROM guild_config
        ORDER BY guild_id
    """)
    
    return [dict(server) for server in servers]


@app.get("/api/servers/{guild_id}")
async def get_server(guild_id: int):
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
async def update_server_config(guild_id: int, config: dict):
    """Update server configuration."""
    # TODO: Validate config and update database
    return {"success": True, "message": "Configuration updated"}


# ============================================================================
# MODERATION ENDPOINTS
# ============================================================================

@app.get("/api/servers/{guild_id}/infractions")
async def get_infractions(guild_id: int, limit: int = 50):
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
async def get_leaderboard(guild_id: int, limit: int = 10):
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
async def get_role_rewards(guild_id: int):
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
async def get_shop_items(guild_id: int):
    """Get shop items for a server."""
    items = await db.fetch("""
        SELECT * FROM shop_items
        WHERE guild_id = $1 AND purchasable = TRUE
        ORDER BY price ASC
    """, guild_id)
    
    return [dict(item) for item in items]


@app.post("/api/servers/{guild_id}/economy/shop")
async def create_shop_item(guild_id: int, item: dict):
    """Create a new shop item."""
    # TODO: Validate and create item
    return {"success": True, "message": "Item created"}


# ============================================================================
# GIVEAWAY ENDPOINTS
# ============================================================================

@app.get("/api/servers/{guild_id}/giveaways")
async def get_giveaways(guild_id: int, status: str = "active"):
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
async def get_analytics(guild_id: int):
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
