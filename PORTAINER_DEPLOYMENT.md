# Portainer Deployment Guide

Complete guide to deploying and managing your Discord bot using Portainer's web interface.

## Table of Contents

1. [What is Portainer?](#what-is-portainer)
2. [Installation](#installation)
3. [Initial Setup](#initial-setup)
4. [Deploying the Bot Stack](#deploying-the-bot-stack)
5. [Managing Your Stack](#managing-your-stack)
6. [Monitoring and Logs](#monitoring-and-logs)
7. [Updating the Bot](#updating-the-bot)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)

---

## What is Portainer?

**Portainer** is a lightweight web-based management UI for Docker. It makes managing containers, images, networks, and volumes easy through a graphical interface instead of command-line tools.

### Why Use Portainer for Your Discord Bot?

✅ **Easy Management** - Visual interface for all Docker operations
✅ **Stack Deployment** - Deploy entire `docker-compose.yml` stacks with one click
✅ **Live Monitoring** - Real-time container stats, logs, and resource usage
✅ **No Command Line** - Everything through a web browser
✅ **Remote Access** - Manage your bot from anywhere (with proper security)
✅ **Backup & Restore** - Easy stack backup and redeployment

---

## Installation

### Option 1: Quick Install (Recommended)

Run this single command to install Portainer:

```bash
docker volume create portainer_data

docker run -d -p 9000:9000 -p 9443:9443 \
  --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

**What this does:**
- Creates a persistent volume for Portainer data
- Runs Portainer on ports 9000 (HTTP) and 9443 (HTTPS)
- Auto-restarts if it crashes or server reboots
- Gives Portainer access to manage Docker

### Option 2: Docker Compose Install

Create `portainer-compose.yml`:

```yaml
version: '3.8'

services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: always
    ports:
      - "9000:9000"
      - "9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data

volumes:
  portainer_data:
```

Deploy:

```bash
docker-compose -f portainer-compose.yml up -d
```

### Verify Installation

Open your browser and navigate to:
- **HTTP**: `http://localhost:9000`
- **HTTPS**: `https://localhost:9443`

You should see the Portainer setup page.

---

## Initial Setup

### 1. Create Admin Account

On first access, Portainer will ask you to create an admin account:

1. **Username**: Choose an admin username (e.g., `admin`)
2. **Password**: Use a **strong password** (minimum 12 characters)
3. Click **"Create user"**

⚠️ **Important**: This is the only time you can set the admin password. If you don't create it within 5 minutes, Portainer will lock down for security.

### 2. Connect to Docker

After creating your account:

1. Select **"Get Started"** or **"Docker"**
2. Choose **"Manage the local Docker environment"**
3. Click **"Connect"**

Portainer will connect to your local Docker daemon.

### 3. Verify Connection

You should now see the Portainer dashboard with:
- **Containers**: Currently running containers
- **Images**: Available Docker images
- **Volumes**: Persistent storage volumes
- **Networks**: Docker networks

---

## Deploying the Bot Stack

### Step 1: Prepare Your Configuration

Before deploying, ensure you have configured:

1. **Environment Variables** (`.env` file):

```bash
# Create .env from template
cp .env.example .env

# Edit with your values
nano .env  # or use any text editor
```

**Required values:**
```env
DISCORD_TOKEN=your_bot_token_here
BOT_OWNER_ID=your_discord_user_id

DATABASE_URL=postgresql://bot_user:password@postgres:5432/discord_bot
REDIS_URL=redis://redis:6379/0

DASHBOARD_SECRET_KEY=generate_with_python_secrets
DASHBOARD_DISCORD_CLIENT_ID=your_client_id
DASHBOARD_DISCORD_CLIENT_SECRET=your_client_secret

OPENAI_API_KEY=your_openai_key  # Optional
```

2. **Bot Configuration** (`config/bot_config.yaml`):

```bash
# Create from template
cp config/bot_config.example.yaml config/bot_config.yaml

# Edit with your settings
nano config/bot_config.yaml
```

### Step 2: Upload Files to Portainer

#### Method A: Git Repository (Recommended)

1. In Portainer, go to **Stacks** → **Add stack**
2. Name your stack: `discord-bot`
3. Select **"Git Repository"**
4. Enter repository URL: `https://github.com/jcurtis260/Discord-bot.git`
5. Reference: `cursor/discord-bot-plan-ea5f`
6. Compose path: `docker-compose.yml`
7. Click **"Deploy the stack"**

#### Method B: Upload via Web Editor

1. In Portainer, go to **Stacks** → **Add stack**
2. Name your stack: `discord-bot`
3. Select **"Web editor"**
4. Copy and paste your entire `docker-compose.yml` content
5. Click **"Deploy the stack"**

#### Method C: Upload from Local File

1. In Portainer, go to **Stacks** → **Add stack**
2. Name your stack: `discord-bot`
3. Select **"Upload"**
4. Upload your `docker-compose.yml` file
5. Click **"Deploy the stack"**

### Step 3: Configure Environment Variables

After selecting your deployment method:

1. Scroll to **"Environment variables"** section
2. Click **"Advanced mode"**
3. Paste your `.env` file contents:

```env
DISCORD_TOKEN=your_token
BOT_OWNER_ID=123456789
DATABASE_URL=postgresql://bot_user:securepass123@postgres:5432/discord_bot
REDIS_URL=redis://redis:6379/0
DASHBOARD_SECRET_KEY=your_secret_key
DASHBOARD_DISCORD_CLIENT_ID=your_client_id
DASHBOARD_DISCORD_CLIENT_SECRET=your_client_secret
```

Or use **"Simple mode"** to add variables one by one.

### Step 4: Deploy the Stack

1. Review your configuration
2. Click **"Deploy the stack"** at the bottom
3. Wait for deployment (1-3 minutes)

Portainer will:
- Pull all required Docker images
- Create networks
- Create volumes
- Start all services (PostgreSQL, Redis, bot, dashboard)

### Step 5: Verify Deployment

1. Go to **Stacks** → **discord-bot**
2. You should see all services running:
   - ✅ `postgres` - Database
   - ✅ `redis` - Cache
   - ✅ `bot` - Discord bot
   - ✅ `dashboard-backend` - API server
   - ✅ `dashboard-frontend` - Web UI

3. Check the **"Status"** column - all should be **"running"**

---

## Managing Your Stack

### Viewing Container Details

1. Go to **Containers** in the left sidebar
2. Click on any container name (e.g., `discord-bot_bot_1`)
3. View:
   - **Logs** - Real-time container logs
   - **Inspect** - Detailed container configuration
   - **Stats** - CPU, memory, network usage
   - **Console** - Access container shell

### Starting/Stopping Services

#### Stop Individual Container:
1. Go to **Containers**
2. Select the container checkbox
3. Click **"Stop"** at the top

#### Start Container:
1. Go to **Containers**
2. Select the stopped container
3. Click **"Start"**

#### Restart Container:
1. Select container
2. Click **"Restart"**

#### Stop Entire Stack:
1. Go to **Stacks** → **discord-bot**
2. Click **"Stop this stack"**

#### Start Stack:
1. Go to **Stacks** → **discord-bot**
2. Click **"Start this stack"**

### Removing the Stack

⚠️ **Warning**: This will delete all containers but keep volumes (data is preserved)

1. Go to **Stacks** → **discord-bot**
2. Click **"Delete this stack"**
3. Confirm deletion

To delete volumes too:
1. Go to **Volumes**
2. Select `discord_bot_postgres_data` and `discord_bot_redis_data`
3. Click **"Remove"**

---

## Monitoring and Logs

### Real-Time Logs

#### View Bot Logs:
1. Go to **Containers**
2. Click on `discord-bot_bot_1`
3. Click **"Logs"** tab
4. Toggle **"Auto-refresh logs"** for live updates
5. Adjust **"Lines"** dropdown to show more/fewer lines

#### View Dashboard Logs:
1. Click on `discord-bot_dashboard-backend_1`
2. Click **"Logs"** tab

#### Search Logs:
- Use the **"Search"** box to filter logs
- Example: Search for "ERROR" to find errors

### Container Statistics

1. Go to **Containers**
2. Click on any container
3. Click **"Stats"** tab

View:
- **CPU Usage** - Real-time CPU percentage
- **Memory Usage** - RAM consumption
- **Network I/O** - Bytes sent/received
- **Block I/O** - Disk read/write

### Stack Overview

1. Go to **Stacks** → **discord-bot**
2. See all services at a glance:
   - Status (running/stopped/error)
   - Image version
   - Created date
   - Quick actions (logs, inspect, stats)

---

## Updating the Bot

### Method 1: Redeploy from Git (Easiest)

If you deployed from Git repository:

1. Go to **Stacks** → **discord-bot**
2. Click **"Editor"** tab
3. Click **"Pull and redeploy"** (⟳ icon)
4. Select **"Pull latest image version"**
5. Click **"Update the stack"**

This will:
- Pull latest code from GitHub
- Pull new Docker images
- Restart services with new code

### Method 2: Manual Update

#### Update via Web Editor:

1. Go to **Stacks** → **discord-bot**
2. Click **"Editor"** tab
3. Modify the `docker-compose.yml` content
4. Click **"Update the stack"**
5. Select **"Pull and redeploy"**

#### Update Individual Service:

1. Go to **Images**
2. Select the image (e.g., `discord-bot_bot`)
3. Click **"Pull image"** to get latest version
4. Go to **Containers**
5. **Stop** the container
6. **Remove** the container
7. Go to **Stacks** → **discord-bot**
8. Click **"Deploy the stack"** (recreates removed container)

### Method 3: Force Rebuild

If you made code changes:

1. Go to **Stacks** → **discord-bot**
2. Click **"Editor"** tab
3. At bottom, enable **"Build"** option
4. Click **"Update the stack"**

This forces Docker to rebuild images from scratch.

---

## Troubleshooting

### Container Won't Start

**Check Logs:**
1. Go to **Containers**
2. Click on the failing container
3. Click **"Logs"**
4. Look for error messages

**Common Issues:**

#### Database Connection Failed
```
Error: could not connect to server
```

**Solution:**
1. Check if `postgres` container is running
2. Verify `DATABASE_URL` environment variable
3. Restart the bot container

#### Port Already in Use
```
Error: bind: address already in use
```

**Solution:**
1. Go to **Containers** or **Stacks**
2. Check if another service is using the same port
3. Either stop the conflicting service or change port in `docker-compose.yml`

#### Out of Memory
```
killed: OOM command not found
```

**Solution:**
1. Go to **Host** → **Dashboard**
2. Check available memory
3. Stop unnecessary containers
4. Add memory limits to `docker-compose.yml`:

```yaml
services:
  bot:
    mem_limit: 512m
    mem_reservation: 256m
```

### Stack Deployment Failed

1. Go to **Stacks** → **discord-bot** → **Logs** tab
2. Read deployment logs for errors
3. Common issues:
   - Invalid YAML syntax
   - Missing environment variables
   - Network conflicts
   - Volume permission issues

### View Container Console

Access container shell to debug:

1. Go to **Containers**
2. Click on container
3. Click **"Console"** tab
4. Select **"/bin/bash"** or **"/bin/sh"**
5. Click **"Connect"**

Now you can run commands inside the container:

```bash
# Check Python packages
pip list

# Test database connection
python -c "import asyncpg; print('OK')"

# Check config file
cat /app/config/bot_config.yaml

# View environment variables
env | grep DISCORD
```

---

## Security Best Practices

### 1. Secure Portainer Access

#### Enable HTTPS

By default, Portainer uses HTTP. Enable HTTPS:

1. Go to **Settings** → **SSL certificate**
2. Upload your SSL certificate and key
3. Or use a reverse proxy (Nginx, Caddy, Traefik)

#### Use Strong Passwords

1. Go to **Users** → Your username → **"Change password"**
2. Use a password manager to generate strong passwords

#### Enable 2FA (Portainer Business)

If using Portainer Business Edition:
1. Go to **Users** → Your username
2. Enable **"Multi-factor authentication"**

### 2. Network Security

#### Limit Exposed Ports

In your `docker-compose.yml`, only expose necessary ports:

```yaml
services:
  bot:
    # Don't expose - internal only
    # ports:
    #   - "8080:8080"
  
  dashboard-frontend:
    # Only expose dashboard
    ports:
      - "3000:3000"
```

#### Use Docker Networks

Your stack already uses a private network. Verify:

1. Go to **Networks** → **discord-bot_default**
2. Only bot services should be listed

### 3. Secret Management

#### Use Portainer Secrets (Swarm Mode)

If using Docker Swarm:

1. Go to **Secrets** → **Add secret**
2. Name: `discord_token`
3. Secret: Your bot token
4. Update `docker-compose.yml`:

```yaml
services:
  bot:
    secrets:
      - discord_token
    environment:
      DISCORD_TOKEN_FILE: /run/secrets/discord_token

secrets:
  discord_token:
    external: true
```

#### Environment Variable Security

1. Never commit `.env` to Git
2. Use Portainer's built-in environment variables
3. Regularly rotate API keys and tokens

### 4. Access Control

#### Create Limited Users

Don't use admin for daily operations:

1. Go to **Users** → **Add user**
2. Create user: `operator`
3. Assign role: **"Standard user"**
4. Grant access only to `discord-bot` stack

#### Restrict Portainer Access

If running on VPS:

1. Use firewall to limit access:

```bash
# Only allow your IP
sudo ufw allow from YOUR_IP to any port 9443
sudo ufw deny 9443
```

2. Or use reverse proxy with authentication:

```nginx
server {
    listen 443 ssl;
    server_name portainer.yourdomain.com;
    
    location / {
        proxy_pass https://localhost:9443;
        
        # Basic auth
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

### 5. Regular Updates

Keep Portainer updated:

1. Go to **Host** → **Dashboard**
2. Check Portainer version
3. Update when new versions are released:

```bash
docker stop portainer
docker rm portainer
docker pull portainer/portainer-ce:latest

# Run install command again with new image
docker run -d -p 9000:9000 -p 9443:9443 \
  --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

---

## Advanced: Remote Access

### Access Portainer from Anywhere

#### Option 1: SSH Tunnel (Most Secure)

From your local machine:

```bash
ssh -L 9443:localhost:9443 user@your-server.com
```

Then open: `https://localhost:9443`

#### Option 2: Reverse Proxy with Cloudflare

1. Install Nginx or Caddy on your server
2. Configure reverse proxy:

**Caddy** (automatic HTTPS):
```caddy
portainer.yourdomain.com {
    reverse_proxy localhost:9443
}
```

**Nginx**:
```nginx
server {
    listen 443 ssl http2;
    server_name portainer.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass https://localhost:9443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. Point DNS to your server
4. Access via `https://portainer.yourdomain.com`

#### Option 3: Tailscale (VPN)

1. Install Tailscale on your server and local machine
2. Access Portainer via Tailscale IP: `https://100.x.x.x:9443`
3. Secure and doesn't require port forwarding

---

## Backup and Restore

### Backup Your Stack

#### Export Stack Configuration:

1. Go to **Stacks** → **discord-bot**
2. Click **"Editor"** tab
3. Copy entire `docker-compose.yml` content
4. Save to file: `discord-bot-backup.yml`

#### Backup Environment Variables:

1. In stack editor, scroll to **"Environment variables"**
2. Copy all variables
3. Save to file: `discord-bot-env-backup.txt`

#### Backup Volumes:

```bash
# Backup PostgreSQL data
docker run --rm \
  -v discord-bot_postgres_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres-backup.tar.gz /data

# Backup Redis data
docker run --rm \
  -v discord-bot_redis_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/redis-backup.tar.gz /data
```

### Restore from Backup

#### Restore Stack:

1. Go to **Stacks** → **Add stack**
2. Name: `discord-bot`
3. Select **"Web editor"**
4. Paste your backed-up `docker-compose.yml`
5. Add environment variables from backup
6. Click **"Deploy the stack"**

#### Restore Volumes:

```bash
# Restore PostgreSQL
docker run --rm \
  -v discord-bot_postgres_data:/data \
  -v $(pwd):/backup \
  ubuntu bash -c "cd /data && tar xzf /backup/postgres-backup.tar.gz --strip 1"

# Restore Redis
docker run --rm \
  -v discord-bot_redis_data:/data \
  -v $(pwd):/backup \
  ubuntu bash -c "cd /data && tar xzf /backup/redis-backup.tar.gz --strip 1"
```

---

## Quick Reference

### Common Actions

| Action | Steps |
|--------|-------|
| **View bot logs** | Containers → discord-bot_bot_1 → Logs |
| **Restart bot** | Containers → Select bot → Restart |
| **Update stack** | Stacks → discord-bot → Editor → Pull and redeploy |
| **Stop everything** | Stacks → discord-bot → Stop this stack |
| **View database** | Containers → postgres → Console → `/bin/bash` → `psql -U bot_user discord_bot` |
| **Check resources** | Containers → Select container → Stats |
| **Export config** | Stacks → discord-bot → Editor → Copy YAML |

### Useful URLs

- **Portainer**: `https://localhost:9443` or `http://localhost:9000`
- **Bot Dashboard**: `http://localhost:3000`
- **Bot API**: `http://localhost:8080`

### Keyboard Shortcuts (in Portainer)

- **G** then **H** - Go to Home
- **G** then **C** - Go to Containers
- **G** then **S** - Go to Stacks
- **/** - Focus search

---

## Summary

**Deploying with Portainer is easy:**

1. Install Portainer: `docker run ... portainer`
2. Access web UI: `https://localhost:9443`
3. Create admin account
4. Deploy stack from Git or upload `docker-compose.yml`
5. Add environment variables
6. Click "Deploy the stack"
7. Monitor and manage through web UI

**Benefits:**
- ✅ No command-line needed
- ✅ Visual management
- ✅ Real-time logs and stats
- ✅ Easy updates and rollbacks
- ✅ Remote access capability
- ✅ Backup and restore tools

**Best for:**
- Users who prefer GUIs
- Managing remote servers
- Teams with multiple admins
- Production deployments
- Quick troubleshooting

---

## Support

If you encounter issues:

1. Check Portainer logs: Containers → portainer → Logs
2. Check stack logs: Stacks → discord-bot → Logs
3. Review container status: Containers → Check status column
4. Consult Portainer docs: https://docs.portainer.io
5. Open GitHub issue with error details

For Portainer-specific help:
- Portainer Community: https://www.portainer.io/community
- Portainer Forum: https://forums.portainer.io
- GitHub Issues: https://github.com/portainer/portainer/issues

---

**Happy deploying! 🐳🚀**
