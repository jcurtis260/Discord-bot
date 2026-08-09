# Custom Port Configuration Guide

How to configure custom ports for your Discord bot dashboard.

## Table of Contents

1. [Why Custom Ports?](#why-custom-ports)
2. [Quick Setup](#quick-setup)
3. [Port Configuration](#port-configuration)
4. [Examples](#examples)
5. [Portainer Configuration](#portainer-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Why Custom Ports?

You might want to use custom ports instead of the defaults (3000 for frontend, 8080 for backend) for several reasons:

✅ **Avoid Conflicts** - Another service might already use port 3000 or 8080
✅ **Security** - Use non-standard ports to reduce automated scans
✅ **Multiple Instances** - Run multiple bot instances on the same server
✅ **Firewall Rules** - Your firewall might allow specific ports only
✅ **Personal Preference** - Use memorable or random port numbers

---

## Quick Setup

### Step 1: Choose Your Ports

Pick any ports between **1024-65535**. Avoid well-known ports (0-1023).

**Examples of good port choices:**
- 8192, 8193
- 5555, 6666
- 9876, 9877
- 7890, 7891
- Any random 4-5 digit number

### Step 2: Configure .env File

Edit your `.env` file:

```bash
# Frontend Port (what you access in browser)
DASHBOARD_FRONTEND_PORT=8192

# Backend API Port
DASHBOARD_BACKEND_PORT=8193

# Update redirect URI to match frontend port
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:8192/auth/callback

# Update API URL to match backend port
DASHBOARD_API_URL=http://localhost:8193
```

### Step 3: Update Discord OAuth Redirect

⚠️ **Important:** Update your Discord application's OAuth2 redirect URI:

1. Go to https://discord.com/developers/applications
2. Select your bot application
3. Go to **OAuth2** section
4. Update redirect URI to match your new frontend port:
   - **Local**: `http://localhost:8192/auth/callback`
   - **Production**: `https://yourdomain.com/auth/callback`

### Step 4: Deploy

**Docker Compose:**
```bash
docker-compose up -d
```

**Portainer:**
- Update environment variables in stack editor
- Click "Update the stack"

### Step 5: Access Dashboard

Open your browser to: `http://localhost:8192` (or your chosen frontend port)

---

## Port Configuration

### Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `DASHBOARD_FRONTEND_PORT` | External port for web UI | 3000 | 8192 |
| `DASHBOARD_BACKEND_PORT` | External port for API | 8080 | 8193 |
| `DASHBOARD_BACKEND_INTERNAL_PORT` | Internal container port | 8080 | 8080 (don't change) |
| `DASHBOARD_DISCORD_REDIRECT_URI` | OAuth2 callback URL | http://localhost:3000/auth/callback | http://localhost:8192/auth/callback |
| `DASHBOARD_API_URL` | Backend API URL for frontend | http://localhost:8080 | http://localhost:8193 |
| `DASHBOARD_HOST` | Bind address | 0.0.0.0 | 0.0.0.0 (don't change) |

### Port Mapping Explanation

Docker uses **port mapping** in the format: `HOST_PORT:CONTAINER_PORT`

- **HOST_PORT** (left side): Port on your machine (what you access)
- **CONTAINER_PORT** (right side): Port inside Docker container

**Example:**
```yaml
ports:
  - "8192:3000"  # Access via localhost:8192, maps to port 3000 inside container
```

---

## Examples

### Example 1: Random High Ports

**Use case:** Maximum security with random high-numbered ports

```bash
# .env
DASHBOARD_FRONTEND_PORT=54321
DASHBOARD_BACKEND_PORT=54322
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:54321/auth/callback
DASHBOARD_API_URL=http://localhost:54322
```

**Access:** `http://localhost:54321`

### Example 2: Sequential Ports

**Use case:** Easy to remember, sequential numbering

```bash
# .env
DASHBOARD_FRONTEND_PORT=8000
DASHBOARD_BACKEND_PORT=8001
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback
DASHBOARD_API_URL=http://localhost:8001
```

**Access:** `http://localhost:8000`

### Example 3: Memorable Ports

**Use case:** Easy to remember custom numbers

```bash
# .env
DASHBOARD_FRONTEND_PORT=7777
DASHBOARD_BACKEND_PORT=7778
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:7777/auth/callback
DASHBOARD_API_URL=http://localhost:7778
```

**Access:** `http://localhost:7777`

### Example 4: Multiple Bot Instances

**Use case:** Running multiple bot instances on same server

**Bot Instance 1:**
```bash
# bot1/.env
DASHBOARD_FRONTEND_PORT=3000
DASHBOARD_BACKEND_PORT=8080
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback
DASHBOARD_API_URL=http://localhost:8080
```

**Bot Instance 2:**
```bash
# bot2/.env
DASHBOARD_FRONTEND_PORT=3001
DASHBOARD_BACKEND_PORT=8081
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:3001/auth/callback
DASHBOARD_API_URL=http://localhost:8081
```

### Example 5: Production with Reverse Proxy

**Use case:** Behind Nginx/Caddy reverse proxy

```bash
# .env (backend uses internal port, nginx handles external)
DASHBOARD_FRONTEND_PORT=3000
DASHBOARD_BACKEND_PORT=8080
DASHBOARD_DISCORD_REDIRECT_URI=https://bot.yourdomain.com/auth/callback
DASHBOARD_API_URL=https://bot.yourdomain.com/api
```

**Nginx config:**
```nginx
server {
    listen 443 ssl;
    server_name bot.yourdomain.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8080;
    }
}
```

---

## Portainer Configuration

### Method 1: Environment Variables (Recommended)

When deploying via Portainer:

1. Go to **Stacks** → **Add stack** or **Edit stack**
2. Scroll to **Environment variables**
3. Click **"Advanced mode"**
4. Add your custom ports:

```env
DASHBOARD_FRONTEND_PORT=8192
DASHBOARD_BACKEND_PORT=8193
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:8192/auth/callback
DASHBOARD_API_URL=http://localhost:8193
```

5. Click **"Deploy the stack"** or **"Update the stack"**

### Method 2: Edit docker-compose.yml

1. Go to **Stacks** → Your stack → **Editor**
2. Find the dashboard services (uncomment if needed)
3. Verify port mappings use environment variables:

```yaml
dashboard-backend:
  ports:
    - "${DASHBOARD_BACKEND_PORT:-8080}:${DASHBOARD_BACKEND_INTERNAL_PORT:-8080}"

dashboard-frontend:
  ports:
    - "${DASHBOARD_FRONTEND_PORT:-3000}:3000"
```

4. Click **"Update the stack"**

### Verify Ports in Portainer

1. Go to **Containers**
2. Find `discord-bot-dashboard-frontend` and `discord-bot-dashboard-backend`
3. Check **Published Ports** column
4. Should show your custom ports (e.g., `8192:3000`, `8193:8080`)

---

## Troubleshooting

### Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Solution 1: Find what's using the port**

**Linux/Mac:**
```bash
# Check what's using port 3000
sudo lsof -i :3000

# Or
sudo netstat -tulpn | grep 3000
```

**Windows:**
```powershell
netstat -ano | findstr :3000
```

**Solution 2: Choose different port**

Update `.env` with a different port number.

**Solution 3: Stop conflicting service**

```bash
# Find process ID from above commands, then:
kill -9 <PID>
```

### Dashboard Not Accessible

**Issue:** Can't access `http://localhost:8192`

**Check 1: Verify container is running**
```bash
docker ps | grep dashboard
```

**Check 2: Check container logs**
```bash
docker logs discord-bot-dashboard-frontend
docker logs discord-bot-dashboard-backend
```

**Check 3: Verify port mapping**
```bash
docker port discord-bot-dashboard-frontend
```

Should show: `3000/tcp -> 0.0.0.0:8192`

**Check 4: Firewall**

If running on VPS, ensure firewall allows your custom port:

```bash
# UFW (Ubuntu)
sudo ufw allow 8192

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --add-port=8192/tcp --permanent
sudo firewall-cmd --reload
```

### Discord OAuth Redirect Mismatch

**Error:**
```
redirect_uri_mismatch
```

**Solution:**

1. Check your `.env` file:
```bash
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:8192/auth/callback
```

2. Go to Discord Developer Portal
3. OAuth2 → Redirects
4. Ensure **exact match**: `http://localhost:8192/auth/callback`
5. Port, protocol (http/https), and path must all match exactly

### Frontend Can't Reach Backend

**Issue:** Frontend loads but API calls fail

**Check 1: Verify DASHBOARD_API_URL**

In `.env`:
```bash
DASHBOARD_API_URL=http://localhost:8193
```

Must match your backend port.

**Check 2: CORS Configuration**

In `config/bot_config.yaml`:
```yaml
dashboard:
  cors_origins:
    - "http://localhost:8192"  # Add your custom frontend port
```

**Check 3: Test backend directly**

```bash
curl http://localhost:8193/health
```

Should return: `{"status": "healthy", ...}`

### Port Conflict with Multiple Instances

**Issue:** Running multiple bot instances

**Solution:** Each instance needs unique ports

**Instance 1:**
```bash
# bot1/.env
DASHBOARD_FRONTEND_PORT=3000
DASHBOARD_BACKEND_PORT=8080
```

**Instance 2:**
```bash
# bot2/.env
DASHBOARD_FRONTEND_PORT=3001
DASHBOARD_BACKEND_PORT=8081
```

Update `docker-compose.yml` to use different container names:
```yaml
services:
  dashboard-frontend:
    container_name: discord-bot-1-dashboard-frontend
```

---

## Port Ranges and Recommendations

### Avoid These Ports (Well-Known)

❌ **0-1023** - Privileged ports (require root)
- 22 (SSH), 80 (HTTP), 443 (HTTPS), etc.

### Safe Port Ranges

✅ **1024-49151** - Registered ports (safe to use)
✅ **49152-65535** - Dynamic/Private ports (most random)

### Recommended Ranges

🎯 **8000-9000** - Common for web apps, easy to remember
🎯 **30000-40000** - High ports, less likely to conflict
🎯 **50000-60000** - Random high ports, maximum security

### Reserved by Other Services (Avoid)

- 3000 - React/Node.js default
- 3306 - MySQL
- 5432 - PostgreSQL
- 6379 - Redis
- 8080 - Common proxy/app server
- 9000 - Portainer

---

## Security Considerations

### Don't Expose Ports Unnecessarily

Only expose ports you need to access:

```yaml
# Bad - exposes everything
services:
  postgres:
    ports:
      - "5432:5432"  # Don't expose database!

# Good - only expose dashboard
services:
  postgres:
    # No ports section - internal only
  
  dashboard-frontend:
    ports:
      - "${DASHBOARD_FRONTEND_PORT}:3000"  # Only this is accessible
```

### Use Firewall

Limit access to specific IPs:

```bash
# Only allow your IP
sudo ufw allow from YOUR_IP to any port 8192
sudo ufw deny 8192
```

### Change Ports Regularly

For maximum security, change ports periodically:

```bash
# Generate random port
python3 -c "import random; print(random.randint(10000, 60000))"
```

Update `.env` and redeploy.

---

## Quick Reference

### Default Ports

| Service | Default Port |
|---------|--------------|
| Dashboard Frontend | 3000 |
| Dashboard Backend | 8080 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| Portainer | 9443 |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Port configuration |
| `docker-compose.yml` | Port mappings |
| `config/bot_config.yaml` | CORS configuration |
| Discord Developer Portal | OAuth2 redirect URI |

### Common Commands

```bash
# Check port usage
sudo lsof -i :<port>

# Test port accessibility
curl http://localhost:<port>

# Generate random port
python3 -c "import random; print(random.randint(10000, 60000))"

# Restart after port change
docker-compose down && docker-compose up -d

# View container ports
docker ps
```

---

## Summary

**To use custom ports:**

1. Choose ports (e.g., 8192, 8193)
2. Update `.env`:
   ```bash
   DASHBOARD_FRONTEND_PORT=8192
   DASHBOARD_BACKEND_PORT=8193
   DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:8192/auth/callback
   DASHBOARD_API_URL=http://localhost:8193
   ```
3. Update Discord OAuth redirect URI
4. Deploy with Docker Compose or Portainer
5. Access at `http://localhost:8192`

**Need help?** Check troubleshooting section or open an issue on GitHub.
