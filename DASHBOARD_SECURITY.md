# Dashboard Security Setup Guide

This guide covers securing your bot's web dashboard with Discord OAuth2, API keys, and IP whitelisting.

## Table of Contents

1. [Overview](#overview)
2. [Security Features](#security-features)
3. [Discord OAuth2 Setup](#discord-oauth2-setup)
4. [Configuration](#configuration)
5. [API Key Authentication](#api-key-authentication)
6. [IP Whitelisting](#ip-whitelisting)
7. [Hosting Options](#hosting-options)
8. [Security Best Practices](#security-best-practices)

---

## Overview

The dashboard uses multiple layers of security:

- **Discord OAuth2**: Users log in with their Discord account
- **Owner-Only Access**: Only specified Discord user IDs can access
- **Session Management**: JWT tokens with configurable expiration
- **API Key Authentication**: Optional programmatic access
- **IP Whitelisting**: Optional IP-based access control
- **HTTPS Support**: For production deployments

---

## Security Features

### 🔒 Authentication Methods

1. **Discord OAuth2** (Primary)
   - Users log in with Discord
   - Only bot owner can access
   - Automatic session management

2. **API Key** (Optional)
   - For scripts and automation
   - Full owner-level access
   - Passed via `X-API-Key` header

3. **IP Whitelist** (Optional)
   - Restrict access by IP address
   - Additional security layer
   - Can be combined with OAuth2

---

## Discord OAuth2 Setup

### Step 1: Get Your Discord User ID

1. Enable Developer Mode in Discord:
   - User Settings → Advanced → Developer Mode (ON)

2. Right-click your username and select "Copy User ID"

3. Save this ID - you'll need it for `bot.owner_id`

### Step 2: Create OAuth2 Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)

2. Select your bot application (or create one if you haven't)

3. Go to **OAuth2** section in the left sidebar

4. Note your **Client ID** (at the top)

5. Click **"Reset Secret"** to generate a **Client Secret**
   - ⚠️ **Important**: Save this immediately, you can't see it again!

### Step 3: Add Redirect URI

1. In the **OAuth2** section, scroll to **"Redirects"**

2. Click **"Add Redirect"**

3. Add your callback URL:
   - **Local Development**: `http://localhost:3000/auth/callback`
   - **Production**: `https://yourdomain.com/auth/callback`

4. Click **"Save Changes"**

### Step 4: Configure Bot

Edit `config/bot_config.yaml`:

```yaml
bot:
  owner_id: "YOUR_DISCORD_USER_ID"  # From Step 1

dashboard:
  discord_client_id: "YOUR_CLIENT_ID"  # From Step 2
  discord_client_secret: "YOUR_CLIENT_SECRET"  # From Step 2
  discord_redirect_uri: "http://localhost:3000/auth/callback"  # From Step 3
  secret_key: "GENERATE_THIS"  # See next section
```

Or use environment variables in `.env`:

```bash
BOT_OWNER_ID=123456789012345678
DASHBOARD_DISCORD_CLIENT_ID=987654321098765432
DASHBOARD_DISCORD_CLIENT_SECRET=your_secret_here
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback
DASHBOARD_SECRET_KEY=your_generated_secret
```

---

## Configuration

### Generate Secure Keys

Generate a secure secret key for JWT signing:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it for `DASHBOARD_SECRET_KEY`.

### Required Settings

In `config/bot_config.yaml`:

```yaml
bot:
  owner_id: "YOUR_DISCORD_USER_ID"  # REQUIRED

dashboard:
  enabled: true
  port: 3000
  host: "0.0.0.0"
  
  # Security
  secret_key: "GENERATED_SECRET_KEY"  # REQUIRED
  session_timeout: 86400  # 24 hours
  
  # Discord OAuth2 (REQUIRED)
  discord_client_id: "YOUR_CLIENT_ID"
  discord_client_secret: "YOUR_CLIENT_SECRET"
  discord_redirect_uri: "http://localhost:3000/auth/callback"
```

### Additional Authorized Users (Optional)

To allow multiple users:

```yaml
dashboard:
  allowed_user_ids:
    - "123456789012345678"  # Your ID
    - "987654321098765432"  # Friend's ID
```

---

## API Key Authentication

For programmatic access (scripts, automation), you can use an API key.

### Generate API Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Configure

In `config/bot_config.yaml`:

```yaml
dashboard:
  api_key: "YOUR_GENERATED_API_KEY"
```

Or in `.env`:

```bash
DASHBOARD_API_KEY=your_generated_api_key
```

### Using API Key

Make requests with the `X-API-Key` header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:3000/api/bot/status
```

```python
import requests

headers = {"X-API-Key": "YOUR_API_KEY"}
response = requests.get("http://localhost:3000/api/bot/status", headers=headers)
print(response.json())
```

---

## IP Whitelisting

Restrict access to specific IP addresses (optional but recommended for production).

### Configure

In `config/bot_config.yaml`:

```yaml
dashboard:
  ip_whitelist:
    - "192.168.1.100"  # Your home IP
    - "10.0.0.5"       # VPN IP
    - "203.0.113.42"   # Office IP
```

### Find Your IP

```bash
curl ifconfig.me
```

### Notes

- If `ip_whitelist` is empty, all IPs are allowed
- Works with both OAuth2 and API key auth
- Useful for restricting to your home/office network

---

## Hosting Options

### ❌ Vercel (Not Recommended)

**Why Vercel doesn't work:**

- ❌ Discord bot needs 24/7 WebSocket connection
- ❌ Vercel serverless functions have 10-60 second timeout
- ❌ No built-in PostgreSQL or Redis
- ❌ No persistent storage for bot state

**Partial solution:**
- Host **frontend only** on Vercel
- Host bot + backend elsewhere

### ✅ Recommended Hosting

#### Option 1: VPS (Best Control)

**Providers:**
- DigitalOcean ($4-6/month)
- Linode ($5/month)
- Vultr ($5/month)
- Hetzner ($4/month)

**Pros:**
- Full control
- Can run Docker
- SSH access
- Best for learning

**Setup:**
```bash
# Clone repo
git clone https://github.com/yourusername/discord-bot.git
cd discord-bot

# Setup
./scripts/setup.sh

# Run with Docker
docker-compose up -d
```

#### Option 2: Railway (Easiest)

**Pros:**
- Easy deployment
- Free tier available ($5 credit/month)
- Built-in PostgreSQL and Redis
- GitHub integration

**Setup:**
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repo
3. Add PostgreSQL and Redis services
4. Set environment variables
5. Deploy

**Security on Railway:**
- Set `BOT_OWNER_ID` in environment variables
- Generate new `DASHBOARD_SECRET_KEY`
- Update `discord_redirect_uri` to your Railway domain

#### Option 3: Render (Good Balance)

**Pros:**
- Free tier available
- Easy deployment
- Built-in databases

**Setup:**
1. Go to [render.com](https://render.com)
2. Create new Web Service from Git
3. Add PostgreSQL and Redis instances
4. Configure environment variables
5. Deploy

### Frontend-Only on Vercel

If you want to host the React frontend on Vercel:

1. **Update CORS in backend:**

```yaml
dashboard:
  cors_origins:
    - "https://your-vercel-app.vercel.app"
```

2. **Update API URL in frontend:**

```typescript
// src/config.ts
export const API_URL = process.env.REACT_APP_API_URL || 'https://your-backend-url.com';
```

3. **Deploy to Vercel:**

```bash
cd dashboard/frontend
npm install -g vercel
vercel
```

---

## Security Best Practices

### ✅ Do's

1. **Always use HTTPS in production**
   ```yaml
   dashboard:
     https: true
     cert_path: "/path/to/cert.pem"
     key_path: "/path/to/key.pem"
   ```

2. **Use strong, unique secret keys**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Keep secrets in `.env`, not `bot_config.yaml`**
   ```bash
   # .env
   DASHBOARD_SECRET_KEY=xyz123...
   DASHBOARD_DISCORD_CLIENT_SECRET=abc456...
   ```

4. **Add `.env` to `.gitignore`**
   ```bash
   echo ".env" >> .gitignore
   ```

5. **Restrict owner_id strictly**
   ```yaml
   bot:
     owner_id: "YOUR_ID_ONLY"  # Don't share!
   ```

6. **Use IP whitelist in production**
   ```yaml
   dashboard:
     ip_whitelist:
       - "YOUR_IP_HERE"
   ```

7. **Enable CORS only for your domains**
   ```yaml
   dashboard:
     cors_origins:
       - "https://yourdomain.com"  # Not "*"
   ```

8. **Rotate API keys regularly**
   ```bash
   # Generate new key every 30-90 days
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

9. **Use environment-specific configs**
   ```yaml
   # config/bot_config.dev.yaml
   dashboard:
     discord_redirect_uri: "http://localhost:3000/auth/callback"
   
   # config/bot_config.prod.yaml
   dashboard:
     discord_redirect_uri: "https://yourdomain.com/auth/callback"
   ```

10. **Monitor access logs**
    ```bash
    tail -f logs/bot.log | grep "dashboard"
    ```

### ❌ Don'ts

1. **Never commit `.env` to Git**
2. **Never share your `DASHBOARD_SECRET_KEY`**
3. **Never use default secret key in production**
4. **Never expose dashboard on public IP without auth**
5. **Never use HTTP in production** (always HTTPS)
6. **Never add `*` to `allowed_user_ids`**
7. **Never disable authentication** (even for testing)
8. **Never log sensitive tokens**
9. **Never reuse keys across environments**
10. **Never store credentials in frontend code**

---

## Testing Authentication

### Test Discord OAuth2 Login

1. Start the bot and dashboard:
   ```bash
   docker-compose up
   ```

2. Open browser: `http://localhost:3000`

3. Click "Login with Discord"

4. Authorize the application

5. You should be redirected with a success message

### Test API Key

```bash
# Should succeed
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:3000/api/bot/status

# Should fail (401)
curl http://localhost:3000/api/bot/status

# Should fail (401)
curl -H "X-API-Key: wrong_key" http://localhost:3000/api/bot/status
```

### Test Owner Check

Try logging in with a different Discord account (not the owner):

- Should receive: `403 Forbidden - Access denied. Only the bot owner can access this dashboard.`

---

## Troubleshooting

### "Discord OAuth2 not configured"

**Problem:** Missing `discord_client_id` or `discord_client_secret`

**Solution:**
1. Get credentials from [Discord Developer Portal](https://discord.com/developers/applications)
2. Add to `config/bot_config.yaml` or `.env`
3. Restart dashboard

### "Access denied: Only bot owner can access"

**Problem:** Your Discord user ID doesn't match `bot.owner_id`

**Solution:**
1. Verify your Discord user ID:
   - Settings → Advanced → Developer Mode (ON)
   - Right-click username → Copy User ID
2. Update `bot.owner_id` in config
3. Restart dashboard

### "Invalid redirect URI"

**Problem:** Redirect URI in Discord app doesn't match config

**Solution:**
1. Go to Discord Developer Portal → Your App → OAuth2
2. Add exact URI from your config to "Redirects"
3. Make sure it matches exactly (including http/https)

### "401 Unauthorized" with API Key

**Problem:** API key doesn't match or is not configured

**Solution:**
1. Generate new key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Add to `dashboard.api_key` in config
3. Restart dashboard
4. Use exact key in `X-API-Key` header

### "403 Forbidden" from specific IP

**Problem:** IP is not in whitelist

**Solution:**
1. Check your public IP: `curl ifconfig.me`
2. Add to `dashboard.ip_whitelist` in config
3. Restart dashboard

---

## Advanced Setup

### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name bot.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bot.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/bot.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Using Docker with HTTPS

```yaml
# docker-compose.yml
services:
  dashboard:
    volumes:
      - ./ssl/cert.pem:/app/ssl/cert.pem:ro
      - ./ssl/key.pem:/app/ssl/key.pem:ro
    environment:
      - DASHBOARD_HTTPS=true
      - DASHBOARD_CERT_PATH=/app/ssl/cert.pem
      - DASHBOARD_KEY_PATH=/app/ssl/key.pem
```

---

## Summary

**Minimum Required Configuration:**

```yaml
bot:
  owner_id: "YOUR_DISCORD_USER_ID"

dashboard:
  secret_key: "GENERATED_SECRET_KEY"
  discord_client_id: "YOUR_CLIENT_ID"
  discord_client_secret: "YOUR_CLIENT_SECRET"
  discord_redirect_uri: "http://localhost:3000/auth/callback"
```

**Recommended Production Configuration:**

```yaml
bot:
  owner_id: "YOUR_DISCORD_USER_ID"

dashboard:
  https: true
  cert_path: "/path/to/cert.pem"
  key_path: "/path/to/key.pem"
  secret_key: "GENERATED_SECRET_KEY"
  discord_client_id: "YOUR_CLIENT_ID"
  discord_client_secret: "YOUR_CLIENT_SECRET"
  discord_redirect_uri: "https://yourdomain.com/auth/callback"
  api_key: "GENERATED_API_KEY"
  ip_whitelist:
    - "YOUR_IP"
  cors_origins:
    - "https://yourdomain.com"
```

---

## Support

If you encounter issues:

1. Check logs: `logs/bot.log`
2. Verify all environment variables are set
3. Test Discord OAuth2 redirect URI
4. Ensure bot owner_id is correct
5. Check firewall/network settings

For more help, open an issue on GitHub.
