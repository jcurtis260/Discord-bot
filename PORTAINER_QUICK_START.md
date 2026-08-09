# Quick Portainer Deployment

## 🚀 One-Command Deploy

### Prerequisites
- Portainer installed and running
- Discord bot token ready
- Discord OAuth2 app configured

### Deploy Steps

1. **Copy Environment Variables**
   ```bash
   # Generate secrets
   python3 -c "import secrets; print('DASHBOARD_SECRET_KEY=' + secrets.token_urlsafe(32))"
   python3 -c "import secrets; print('DATABASE_PASSWORD=' + secrets.token_urlsafe(16))"
   ```

2. **Get Discord Credentials**
   - Bot Token: https://discord.com/developers/applications → Your App → Bot → Token
   - Owner ID: Discord → Settings → Advanced → Developer Mode → Right-click username → Copy ID
   - OAuth2 Client ID: Discord Developer Portal → OAuth2 → Client ID
   - OAuth2 Secret: Discord Developer Portal → OAuth2 → Client Secret

3. **Deploy in Portainer**
   - Open Portainer UI (http://localhost:9000)
   - Stacks → + Add stack
   - Name: `discord-bot`
   - Repository: `https://github.com/jcurtis260/Discord-bot`
   - Branch: `main` (or your branch)
   - Compose file: `portainer-stack.yml`
   
4. **Set Environment Variables**
   Required:
   ```
   DISCORD_TOKEN=your_bot_token_here
   BOT_OWNER_ID=your_discord_user_id
   DATABASE_PASSWORD=generated_above
   DASHBOARD_SECRET_KEY=generated_above
   DASHBOARD_DISCORD_CLIENT_ID=from_discord_portal
   DASHBOARD_DISCORD_CLIENT_SECRET=from_discord_portal
   ```

5. **Click Deploy**

6. **Access Dashboard**
   - Open: http://localhost:3000
   - Login with Discord
   - Manage your bot!

## 📋 Environment Variables Template

Copy this and fill in your values:

```env
# Required
DISCORD_TOKEN=
BOT_OWNER_ID=
DATABASE_PASSWORD=
DASHBOARD_SECRET_KEY=
DASHBOARD_DISCORD_CLIENT_ID=
DASHBOARD_DISCORD_CLIENT_SECRET=

# Optional - AI Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Optional - Ports (defaults shown)
DASHBOARD_FRONTEND_PORT=3000
DASHBOARD_BACKEND_PORT=8080
```

## 🔍 Verify Deployment

Check each service is running in Portainer:
- ✅ `discord-bot-postgres` - Database (healthy)
- ✅ `discord-bot-redis` - Cache (healthy)
- ✅ `discord-bot` - Bot (running)
- ✅ `discord-bot-dashboard-backend` - API (running)
- ✅ `discord-bot-dashboard-frontend` - UI (running)

## 🐛 Quick Troubleshooting

**Stack won't deploy?**
- Check all required environment variables are set
- Ensure ports 3000, 8080, 5432, 6379 aren't in use

**Bot not online?**
- View logs: Stacks → discord-bot → discord-bot container → Logs
- Verify DISCORD_TOKEN is correct

**Can't access dashboard?**
- Check frontend container is running
- Verify DASHBOARD_DISCORD_REDIRECT_URI matches your setup
- Default: http://localhost:3000/auth/callback

**Database connection failed?**
- Ensure postgres container is healthy (green indicator)
- Verify DATABASE_PASSWORD matches in all services

## 📚 Full Documentation

For detailed setup, troubleshooting, and advanced configuration:
- [PORTAINER_STACK_DEPLOY.md](PORTAINER_STACK_DEPLOY.md) - Complete guide
- [PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md) - Original Portainer guide
- [README.md](README.md) - Main documentation

---

**Total deployment time: ~5 minutes** ⚡
