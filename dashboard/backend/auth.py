"""
Authentication and Authorization for Dashboard
Implements Discord OAuth2, session management, and owner-only access
"""

from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict
import httpx
import secrets
import logging

logger = logging.getLogger(__name__)

# Security schemes
security_bearer = HTTPBearer()
security_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


class AuthManager:
    """Manages authentication and authorization."""
    
    def __init__(self, config: Dict):
        """
        Initialize auth manager.
        
        Args:
            config: Configuration dictionary with auth settings
        """
        self.secret_key = config.get('dashboard.secret_key', secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire = config.get('dashboard.session_timeout', 86400)
        
        # Discord OAuth2 settings
        self.discord_client_id = config.get('dashboard.discord_client_id')
        self.discord_client_secret = config.get('dashboard.discord_client_secret')
        self.discord_redirect_uri = config.get('dashboard.discord_redirect_uri', 'http://localhost:3000/auth/callback')
        
        # Owner settings
        self.owner_id = str(config.get('bot.owner_id', ''))
        self.allowed_user_ids = [str(uid) for uid in config.get('dashboard.allowed_user_ids', [])]
        if self.owner_id and self.owner_id not in self.allowed_user_ids:
            self.allowed_user_ids.append(self.owner_id)
        
        # API Key for programmatic access
        self.api_key = config.get('dashboard.api_key')
        
        # IP Whitelist (optional)
        self.ip_whitelist = config.get('dashboard.ip_whitelist', [])
        
        # Prevent unauthorized access if not configured
        if not self.owner_id and not self.allowed_user_ids:
            logger.warning("⚠️  No owner_id or allowed_user_ids configured! Dashboard will be inaccessible.")
        
        if self.discord_client_id and self.discord_client_secret:
            logger.info("✅ Discord OAuth2 enabled")
        else:
            logger.warning("⚠️  Discord OAuth2 not configured. Only API key auth available.")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in token
            expires_delta: Optional expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=self.access_token_expire)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def verify_api_key(self, api_key: str) -> bool:
        """
        Verify API key.
        
        Args:
            api_key: API key to verify
            
        Returns:
            True if valid, False otherwise
        """
        if not self.api_key:
            return False
        
        return secrets.compare_digest(api_key, self.api_key)
    
    def check_ip_whitelist(self, client_ip: str) -> bool:
        """
        Check if IP is whitelisted.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if allowed, False otherwise
        """
        # If no whitelist configured, allow all
        if not self.ip_whitelist:
            return True
        
        return client_ip in self.ip_whitelist
    
    def is_owner(self, user_id: str) -> bool:
        """
        Check if user is the bot owner or in allowed list.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            True if owner or allowed, False otherwise
        """
        return user_id in self.allowed_user_ids
    
    async def get_discord_user(self, access_token: str) -> Dict:
        """
        Get Discord user info from OAuth2 access token.
        
        Args:
            access_token: Discord OAuth2 access token
            
        Returns:
            User info dictionary
            
        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail="Failed to fetch Discord user info"
                )
            
            return response.json()
    
    async def exchange_code(self, code: str) -> Dict:
        """
        Exchange OAuth2 code for access token.
        
        Args:
            code: OAuth2 authorization code
            
        Returns:
            Token response dictionary
            
        Raises:
            HTTPException: If exchange fails
        """
        data = {
            'client_id': self.discord_client_id,
            'client_secret': self.discord_client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.discord_redirect_uri
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://discord.com/api/v10/oauth2/token',
                data=data,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Discord OAuth2 token exchange failed: {response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to exchange authorization code"
                )
            
            return response.json()


# Dependency functions
async def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer),
    auth_manager: AuthManager = None
) -> Dict:
    """
    Verify bearer token from Authorization header.
    
    Args:
        credentials: HTTP credentials
        auth_manager: AuthManager instance
        
    Returns:
        Decoded token payload
    """
    if not auth_manager:
        raise HTTPException(status_code=500, detail="Auth manager not initialized")
    
    return auth_manager.verify_token(credentials.credentials)


async def verify_api_key_header(
    api_key: Optional[str] = Security(security_api_key),
    auth_manager: AuthManager = None
) -> bool:
    """
    Verify API key from X-API-Key header.
    
    Args:
        api_key: API key string
        auth_manager: AuthManager instance
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If API key invalid
    """
    if not auth_manager:
        raise HTTPException(status_code=500, detail="Auth manager not initialized")
    
    if not api_key or not auth_manager.verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return True


async def require_auth(
    request: Request,
    bearer_token: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    api_key: Optional[str] = Security(security_api_key),
    auth_manager: AuthManager = None
) -> Dict:
    """
    Require authentication via bearer token or API key.
    
    Args:
        request: FastAPI request
        bearer_token: Optional bearer token
        api_key: Optional API key
        auth_manager: AuthManager instance
        
    Returns:
        User info dictionary
        
    Raises:
        HTTPException: If not authenticated
    """
    if not auth_manager:
        raise HTTPException(status_code=500, detail="Auth manager not initialized")
    
    # Check IP whitelist first
    client_ip = request.client.host
    if not auth_manager.check_ip_whitelist(client_ip):
        logger.warning(f"⚠️  Blocked request from non-whitelisted IP: {client_ip}")
        raise HTTPException(
            status_code=403,
            detail="Access denied: IP not whitelisted"
        )
    
    # Try API key first
    if api_key and auth_manager.verify_api_key(api_key):
        return {
            "type": "api_key",
            "user_id": "api",
            "username": "API Access",
            "is_owner": True
        }
    
    # Try bearer token
    if bearer_token:
        try:
            payload = auth_manager.verify_token(bearer_token.credentials)
            user_id = payload.get("sub")
            
            # Verify user is owner
            if not auth_manager.is_owner(user_id):
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: Only bot owner can access dashboard"
                )
            
            return {
                "type": "discord_oauth",
                "user_id": user_id,
                "username": payload.get("username"),
                "discriminator": payload.get("discriminator"),
                "avatar": payload.get("avatar"),
                "is_owner": True
            }
        except HTTPException:
            pass
    
    # No valid authentication provided
    raise HTTPException(
        status_code=401,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def require_owner(
    user: Dict = Depends(require_auth),
    auth_manager: AuthManager = None
) -> Dict:
    """
    Require user to be bot owner.
    
    Args:
        user: User info from require_auth
        auth_manager: AuthManager instance
        
    Returns:
        User info dictionary
        
    Raises:
        HTTPException: If not owner
    """
    if not auth_manager:
        raise HTTPException(status_code=500, detail="Auth manager not initialized")
    
    # API key access is always owner-level
    if user.get("type") == "api_key":
        return user
    
    # Check if Discord user is owner
    user_id = user.get("user_id")
    if not auth_manager.is_owner(user_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Owner privileges required"
        )
    
    return user
