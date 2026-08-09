# Portainer Stack Files Comparison

## Two Stack Files Provided

### 1. `portainer-stack-with-repo.yml` ⭐ RECOMMENDED

**Use this when deploying via Portainer Stacks**

- ✅ Pulls code directly from GitHub
- ✅ Builds images from repository
- ✅ Includes automatic database initialization
- ✅ No local files needed
- ✅ Works with Portainer Web Editor (copy/paste)
- ✅ Works with Portainer Git deployment

**How it works:**
- Bot: Builds from `https://github.com/jcurtis260/Discord-bot.git#cursor/discord-bot-plan-ea5f`
- Backend: Builds from `https://github.com/jcurtis260/Discord-bot.git#cursor/discord-bot-plan-ea5f:dashboard/backend`
- Frontend: Builds from `https://github.com/jcurtis260/Discord-bot.git#cursor/discord-bot-plan-ea5f:dashboard/frontend`
- DB Init: Clones repo and runs SQL scripts automatically

**Deployment:**
```bash
# Copy contents of portainer-stack-with-repo.yml
# Paste into Portainer → Stacks → Web editor
# Set environment variables
# Deploy!
```

### 2. `portainer-stack.yml`

**Use this when deploying locally with docker-compose**

- ✅ Uses local build contexts
- ✅ Mounts local volumes
- ✅ Good for development
- ⚠️ Requires repository cloned locally
- ⚠️ Not suitable for remote Portainer deployment

**How it works:**
- Expects repository cloned to local machine
- Builds from local directories (`.`, `./dashboard/backend`, etc.)
- Mounts local files (`./config`, `./logs`, etc.)

**Deployment:**
```bash
git clone https://github.com/jcurtis260/Discord-bot.git
cd Discord-bot
cp .env.example .env
# Edit .env
docker-compose -f portainer-stack.yml up -d
```

## Which One Should I Use?

### Use `portainer-stack-with-repo.yml` if:
- ✅ Deploying via Portainer web UI
- ✅ Portainer is on a remote server
- ✅ You want automatic updates from Git
- ✅ You don't want to clone the repo manually
- ✅ You want one-click deployment

### Use `portainer-stack.yml` if:
- ✅ Running docker-compose locally
- ✅ You want to modify code locally
- ✅ You're developing/testing
- ✅ You need to customize files before deployment

## Key Differences

| Feature | portainer-stack-with-repo.yml | portainer-stack.yml |
|---------|-------------------------------|---------------------|
| Build Context | GitHub URL | Local directory |
| Database Init | Automatic (db-init service) | Manual (mounted files) |
| Config Files | Docker volumes | Local mounts |
| Local Clone | Not needed | Required |
| Best For | Production deployment | Local development |
| Portainer UI | ✅ Perfect | ⚠️ Needs local files |
| Docker Compose | ✅ Works | ✅ Works |
| Auto-update | ✅ Yes (via Portainer) | ❌ Manual |

## Deployment Examples

### Portainer Web UI (Recommended)

1. Open Portainer
2. Stacks → + Add stack
3. Name: `discord-bot`
4. Choose **Web editor**
5. Copy entire contents of `portainer-stack-with-repo.yml`
6. Paste into editor
7. Add environment variables
8. Click **Deploy**

### Portainer from Git Repository

1. Open Portainer
2. Stacks → + Add stack
3. Name: `discord-bot`
4. Choose **Repository**
5. Repository URL: `https://github.com/jcurtis260/Discord-bot`
6. Branch: `cursor/discord-bot-plan-ea5f`
7. Compose file: `portainer-stack-with-repo.yml`
8. Add environment variables
9. Click **Deploy**

### Local Docker Compose

```bash
# Clone repository
git clone https://github.com/jcurtis260/Discord-bot.git
cd Discord-bot

# Setup environment
cp .env.example .env
nano .env

# Deploy with portainer-stack.yml
docker-compose -f portainer-stack.yml up -d

# Or deploy with portainer-stack-with-repo.yml
docker-compose -f portainer-stack-with-repo.yml up -d
```

## Environment Variables

Both files use the same environment variables:

**Required:**
```env
DISCORD_TOKEN=your_bot_token
BOT_OWNER_ID=your_discord_user_id
DATABASE_PASSWORD=secure_password
DASHBOARD_SECRET_KEY=generated_secret
DASHBOARD_DISCORD_CLIENT_ID=oauth_client_id
DASHBOARD_DISCORD_CLIENT_SECRET=oauth_client_secret
```

**Optional:**
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DASHBOARD_FRONTEND_PORT=3000
DASHBOARD_BACKEND_PORT=8080
```

## Updating Branch Reference

If deploying from `main` branch after merge, update the Git URLs:

```yaml
# Change this:
context: https://github.com/jcurtis260/Discord-bot.git#cursor/discord-bot-plan-ea5f

# To this:
context: https://github.com/jcurtis260/Discord-bot.git#main
```

Or use the default branch (omit `#branch`):

```yaml
context: https://github.com/jcurtis260/Discord-bot.git
```

## Summary

**For most users deploying via Portainer:** Use `portainer-stack-with-repo.yml`

**For local development:** Use `portainer-stack.yml` or regular `docker-compose.yml`

Both files are functionally equivalent - they just differ in how they source the code!
