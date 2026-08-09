# Quick Deploy Instructions for Portainer

## ✅ Working Method: Web Editor (Copy/Paste)

### Step-by-Step:

1. **Open Portainer** (http://localhost:9000)

2. **Create Stack**
   - Click **Stacks** in sidebar
   - Click **+ Add stack**
   - Name: `discord-bot`

3. **Choose Web editor**
   - Select **Web editor** option (NOT Repository)

4. **Copy the stack file**
   - Open this file: `portainer-stack-with-repo.yml`
   - Copy the ENTIRE contents (all ~200 lines)
   - Paste into the Web editor in Portainer

5. **Add Environment Variables**
   Scroll down and add these (click "+ Add environment variable" for each):

   ```
   DISCORD_TOKEN=your_bot_token_here
   BOT_OWNER_ID=your_discord_user_id
   DATABASE_PASSWORD=MySecurePassword123
   DASHBOARD_SECRET_KEY=generate_with_command_below
   DASHBOARD_DISCORD_CLIENT_ID=your_oauth_client_id
   DASHBOARD_DISCORD_CLIENT_SECRET=your_oauth_client_secret
   ```

   Generate secrets:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

6. **Deploy**
   - Scroll to bottom
   - Click **Deploy the stack**
   - Wait 2-3 minutes for images to build from GitHub

7. **Verify**
   - Check all containers are running (should see 5-6 containers)
   - Access dashboard at http://localhost:3000

---

## 🚫 Why Git Repository Method Failed

The error `open /data/compose/29/docker-compose.yml: no such file or directory` happens because:
- Portainer's Git integration has issues with some repository structures
- It can't always find the compose file properly
- Web editor is more reliable

## ✅ Alternative: Use docker-compose Directly

If Portainer Web editor doesn't work, use docker-compose:

```bash
# Clone repository
git clone https://github.com/jcurtis260/Discord-bot.git
cd Discord-bot

# Checkout correct branch
git checkout cursor/discord-bot-plan-ea5f

# Create .env file
cat > .env << 'EOF'
DISCORD_TOKEN=your_token
BOT_OWNER_ID=your_user_id
DATABASE_PASSWORD=secure_password
DASHBOARD_SECRET_KEY=generated_secret
DASHBOARD_DISCORD_CLIENT_ID=client_id
DASHBOARD_DISCORD_CLIENT_SECRET=client_secret
DASHBOARD_DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback
EOF

# Deploy with docker-compose
docker-compose -f portainer-stack-with-repo.yml up -d

# View logs
docker-compose -f portainer-stack-with-repo.yml logs -f
```

---

## 📝 Quick Reference

### Get Discord Credentials
1. **Bot Token**: https://discord.com/developers/applications → Your App → Bot → Token
2. **Owner ID**: Discord → User Settings → Advanced → Developer Mode → Right-click username → Copy ID
3. **OAuth Client ID & Secret**: Discord Developer Portal → OAuth2

### Generate Secrets
```bash
python3 -c "import secrets; print('DASHBOARD_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('DATABASE_PASSWORD=' + secrets.token_urlsafe(16))"
```

### After Deployment
- Dashboard: http://localhost:3000
- API: http://localhost:8080
- Database: localhost:5432 (internal only)
- Redis: localhost:6379 (internal only)

---

**Use Web editor method for guaranteed success!** ✅
