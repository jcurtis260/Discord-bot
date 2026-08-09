# Portainer Stack Deployment Guide

## Quick Deploy in Portainer

### Method 1: Deploy from Web UI

1. **Login to Portainer**
   - Navigate to your Portainer instance (e.g., `http://localhost:9000`)
   - Login with your credentials

2. **Create New Stack**
   - Go to **Stacks** in the sidebar
   - Click **+ Add stack**
   - Name: `discord-bot`

3. **Upload Stack File**
   - Choose **Upload** or **Repository**
   - If Upload: Select `portainer-stack.yml`
   - If Repository: 
     - Repository URL: `https://github.com/jcurtis260/Discord-bot`
     - Repository reference: `refs/heads/main`
     - Compose path: `portainer-stack.yml`

4. **Set Environment Variables**
   Click **Add an environment variable** for each required value:

   **Required:**
   ```
   DISCORD_TOKEN=your_discord_bot_token
   BOT_OWNER_ID=your_discord_user_id
   DATABASE_PASSWORD=secure_database_password
   DASHBOARD_SECRET_KEY=generate_with_python_secrets
   DASHBOARD_DISCORD_CLIENT_ID=discord_oauth_client_id
   DASHBOARD_DISCORD_CLIENT_SECRET=discord_oauth_client_secret
   ```

   **Optional:**
   ```
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   CHATGPT_SESSION_TOKEN=your_chatgpt_session
   POE_TOKEN=your_poe_token
   DASHBOARD_API_KEY=generate_api_key
   DASHBOARD_FRONTEND_PORT=3000
   DASHBOARD_BACKEND_PORT=8080
   DASHBOARD_BACKEND_INTERNAL_PORT=8080
   DASHBOARD_API_URL=http://localhost:8080
   DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback
   ```

5. **Deploy Stack**
   - Click **Deploy the stack**
   - Wait for all containers to start
   - Check logs if any issues

### Method 2: Deploy from Git Repository

1. **In Portainer Stacks**
   - Click **+ Add stack**
   - Name: `discord-bot`
   - Choose **Repository**

2. **Configure Git**
   ```
   Repository URL: https://github.com/jcurtis260/Discord-bot
   Repository reference: refs/heads/main (or your branch)
   Compose path: portainer-stack.yml
   ```

3. **Authentication (if private repo)**
   - Enable authentication
   - Choose method: Personal Access Token
   - Enter your GitHub token

4. **Set Environment Variables** (same as Method 1)

5. **Enable Auto-Update** (Optional)
   - Enable automatic updates from repository
   - Set polling interval (e.g., 5 minutes)
   - This will auto-deploy when you push changes

6. **Deploy Stack**

### Method 3: Deploy via Portainer API

```bash
# Get your Portainer API token first
PORTAINER_URL="http://localhost:9000"
PORTAINER_TOKEN="your_portainer_api_token"
ENDPOINT_ID="1"  # Usually 1 for local Docker

# Create stack from Git
curl -X POST "${PORTAINER_URL}/api/stacks?type=2&method=repository&endpointId=${ENDPOINT_ID}" \
  -H "X-API-Key: ${PORTAINER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "discord-bot",
    "repositoryURL": "https://github.com/jcurtis260/Discord-bot",
    "repositoryReferenceName": "refs/heads/main",
    "composeFile": "portainer-stack.yml",
    "env": [
      {"name": "DISCORD_TOKEN", "value": "your_token"},
      {"name": "BOT_OWNER_ID", "value": "your_id"},
      {"name": "DATABASE_PASSWORD", "value": "secure_password"},
      {"name": "DASHBOARD_SECRET_KEY", "value": "secret_key"},
      {"name": "DASHBOARD_DISCORD_CLIENT_ID", "value": "client_id"},
      {"name": "DASHBOARD_DISCORD_CLIENT_SECRET", "value": "client_secret"}
    ]
  }'
```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Bot token from Discord Developer Portal | `MTk4NjIyNDgzN...` |
| `BOT_OWNER_ID` | Your Discord user ID | `123456789012345678` |
| `DATABASE_PASSWORD` | PostgreSQL password | `MySecurePass123!` |
| `DASHBOARD_SECRET_KEY` | JWT secret (generate with Python) | `Xw9vR3kT...` |
| `DASHBOARD_DISCORD_CLIENT_ID` | OAuth2 Client ID | `987654321098765432` |
| `DASHBOARD_DISCORD_CLIENT_SECRET` | OAuth2 Client Secret | `AbCdEf123...` |

### Generate Secrets

```bash
# Generate DASHBOARD_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate DASHBOARD_API_KEY (optional)
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT | None |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | None |
| `CHATGPT_SESSION_TOKEN` | ChatGPT web session token | None |
| `POE_TOKEN` | Poe.com authentication token | None |
| `DASHBOARD_API_KEY` | API key for programmatic access | None |
| `DASHBOARD_FRONTEND_PORT` | Frontend external port | `3000` |
| `DASHBOARD_BACKEND_PORT` | Backend external port | `8080` |
| `DASHBOARD_API_URL` | Backend URL for frontend | `http://localhost:8080` |

## Post-Deployment

### Access the Dashboard
1. Navigate to `http://localhost:3000` (or your configured port)
2. Click "Login with Discord"
3. Authorize the application
4. You'll be redirected to the dashboard

### Check Container Status
In Portainer:
1. Go to **Stacks** → **discord-bot**
2. View all containers and their status
3. Check logs for any container by clicking on it

### View Logs
- **Bot Logs**: Click on `discord-bot` container → Logs
- **API Logs**: Click on `discord-bot-dashboard-backend` container → Logs
- **Frontend Logs**: Click on `discord-bot-dashboard-frontend` container → Logs
- **Database Logs**: Click on `discord-bot-postgres` container → Logs

### Container Management
- **Restart**: Click container → Quick actions → Restart
- **Stop**: Click container → Quick actions → Stop
- **Console Access**: Click container → Console → Connect

## Stack Management

### Update Stack
1. Go to **Stacks** → **discord-bot**
2. Click **Editor**
3. Make changes or pull latest from Git
4. Click **Update the stack**

### Stop Stack
1. Go to **Stacks** → **discord-bot**
2. Click **Stop this stack**

### Remove Stack
1. Go to **Stacks** → **discord-bot**
2. Click **Delete this stack**
3. Optionally check "Remove associated volumes" if you want to delete data

### Backup Stack
1. Go to **Stacks** → **discord-bot**
2. Click **Duplicate/Migrate**
3. Create a backup stack configuration

## Data Persistence

The stack uses Docker volumes for persistence:
- `discord-bot_postgres_data` - Database data
- `discord-bot_redis_data` - Redis cache data

### Backup Volumes
```bash
# Backup database
docker run --rm -v discord-bot_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz /data

# Backup Redis
docker run --rm -v discord-bot_redis_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup-$(date +%Y%m%d).tar.gz /data
```

### Restore Volumes
```bash
# Restore database
docker run --rm -v discord-bot_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup-YYYYMMDD.tar.gz -C /

# Restore Redis
docker run --rm -v discord-bot_redis_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/redis-backup-YYYYMMDD.tar.gz -C /
```

## Troubleshooting

### Stack Won't Deploy
1. **Check environment variables** - All required vars must be set
2. **Check Docker resources** - Ensure enough memory/CPU
3. **Check port conflicts** - Ensure ports aren't already in use
4. **View Portainer logs** - Check Portainer container logs

### Container Keeps Restarting
1. Click on the container
2. Check **Logs** for error messages
3. Check **Inspect** → **State** for exit codes
4. Verify environment variables are correct

### Can't Access Dashboard
1. **Check frontend container is running**
2. **Verify port mapping** - Should be exposed on configured port
3. **Check browser console** - Look for API connection errors
4. **Verify backend is accessible** - Try `http://localhost:8080/api/bot/status`

### Database Connection Issues
1. **Check postgres container is healthy** - Should show green in Portainer
2. **Verify DATABASE_PASSWORD** - Must match in all services
3. **Check network** - All containers should be on `bot-network`
4. **View postgres logs** - Look for authentication errors

### Bot Not Starting
1. **Check DISCORD_TOKEN** - Must be valid bot token
2. **Check bot logs** - Look for specific error messages
3. **Verify database connection** - Bot needs postgres to be healthy
4. **Check intents** - Ensure privileged intents are enabled in Discord

## Security Best Practices

### In Portainer
1. **Use strong passwords** - For Portainer itself
2. **Enable 2FA** - If available in your Portainer version
3. **Restrict access** - Use Portainer teams and RBAC
4. **Use secrets** - Store sensitive values in Portainer secrets (Business Edition)

### For the Stack
1. **Change default passwords** - Never use default DATABASE_PASSWORD
2. **Generate strong keys** - Use cryptographically secure random values
3. **Limit network exposure** - Don't expose database/redis ports publicly
4. **Use reverse proxy** - Put dashboard behind Nginx/Traefik with SSL
5. **Regular updates** - Keep Docker images updated

## Advanced Configuration

### Custom Ports
Set different ports in environment variables:
```
DASHBOARD_FRONTEND_PORT=8080
DASHBOARD_BACKEND_PORT=8081
```

### Resource Limits
Add to each service in the stack:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      memory: 512M
```

### Custom Networks
Replace `bot-network` with existing Portainer network to integrate with other stacks.

### Logging Configuration
Add to each service:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Monitoring

### Portainer Stats
- View real-time resource usage in container details
- Monitor CPU, memory, network, disk I/O
- Set up alerts (Business Edition)

### External Monitoring
Connect to containers:
- Prometheus + Grafana
- ELK Stack
- Datadog
- New Relic

## Support

For issues:
1. Check container logs in Portainer
2. Review this documentation
3. Check main repository README
4. Open GitHub issue with logs

---

**Stack deployed and ready to manage your Discord bot with Portainer! 🚀**
