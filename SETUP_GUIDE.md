# Discord Bot Setup Guide

Complete guide to setting up and running your Discord bot.

## Prerequisites

Before you begin, ensure you have:

- **Discord Bot Token** - [Create a bot on Discord Developer Portal](https://discord.com/developers/applications)
- **Python 3.11+** (for local setup) or **Docker** (for container setup)
- **PostgreSQL 14+** database
- **Redis 7+** (optional but recommended)
- **(Optional) OpenAI or Anthropic API key** for AI features

## Quick Start (Docker - Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/jcurtis260/Discord-bot.git
cd Discord-bot
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use any text editor
```

Required variables in `.env`:
```env
DISCORD_TOKEN=your_bot_token_here
DISCORD_APP_ID=your_application_id
DATABASE_PASSWORD=secure_password_here
```

Optional variables:
```env
OPENAI_API_KEY=your_openai_key  # For AI features
ANTHROPIC_API_KEY=your_anthropic_key  # Alternative AI provider
```

### 3. Configure Bot Settings

```bash
cp config/bot_config.example.yaml config/bot_config.yaml
nano config/bot_config.yaml
```

Adjust settings as needed (most defaults are fine for testing).

### 4. Start the Bot

```bash
# Start all services (bot, database, redis)
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down
```

The bot will automatically:
- Create the database schema
- Connect to Discord
- Load all commands
- Start accepting commands

## Manual Setup (Without Docker)

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create user and database
CREATE USER bot_user WITH PASSWORD 'your_password';
CREATE DATABASE discord_bot OWNER bot_user;
\q

# Import schema
psql -U bot_user -d discord_bot -f database/schema.sql
```

### 3. Install Redis (Optional)

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### 4. Set Up Python Environment

```bash
cd bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure

```bash
# Copy templates
cp ../.env.example ../.env
cp ../config/bot_config.example.yaml ../config/bot_config.yaml

# Edit configuration
nano ../.env
nano ../config/bot_config.yaml
```

### 6. Run the Bot

```bash
# Make sure you're in the bot directory with venv activated
python main.py
```

## Creating a Discord Bot

### 1. Create Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name
4. Click "Create"

### 2. Create Bot User

1. Go to "Bot" section
2. Click "Add Bot"
3. Confirm "Yes, do it!"
4. Copy the bot token (you'll need this for `.env`)

### 3. Enable Intents

1. In Bot section, scroll to "Privileged Gateway Intents"
2. Enable:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
3. Save changes

### 4. Get Application ID

1. Go to "General Information"
2. Copy "Application ID"
3. This is your `DISCORD_APP_ID`

### 5. Invite Bot to Server

Generate invite URL:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_APP_ID&permissions=8&scope=bot%20applications.commands
```

Replace `YOUR_APP_ID` with your Application ID.

**Permissions Explanation:**
- `permissions=8` = Administrator (recommended for full features)
- For specific permissions, use Discord's permission calculator

Alternatively, use this permission integer for essential permissions:
- `permissions=1099511627775` (Manage roles, channels, messages, kick/ban, etc.)

## Configuration Guide

### Bot Configuration (`config/bot_config.yaml`)

#### Essential Settings

```yaml
bot:
  token: "YOUR_BOT_TOKEN"  # Can use env var instead
  prefix: "/"              # Command prefix
  status: "online"         # online, idle, dnd, invisible
  activity: "your server"  # Status message
```

#### Database Settings

```yaml
database:
  host: "localhost"
  port: 5432
  database: "discord_bot"
  user: "bot_user"
  password: "your_password"  # Can use env var
```

#### Feature Toggles

```yaml
leveling:
  enabled: true
  xp_per_message: 15
  xp_cooldown: 60  # seconds

economy:
  enabled: true
  currency_name: "Credits"
  currency_emoji: "💰"
  starting_balance: 100

giveaways:
  enabled: true
  default_emoji: "🎉"
```

#### AI Settings (Optional)

```yaml
ai:
  enabled: true
  provider: "openai"  # or "anthropic"
  api_key: "YOUR_API_KEY"  # Can use env var
  model: "gpt-4"
  temperature: 0.8
  default_personality: "friendly"
```

## Testing the Bot

### 1. Basic Test

Once the bot is running:

1. Check bot is online in your server
2. Type `/ping` - should respond with latency
3. Type `/help` - should show command list

### 2. Test Core Features

**Moderation:**
```
/warn @user Being rude
/mute @user 10m Spam
/infractions @user
```

**Leveling:**
```
/rank
/leaderboard
```

**Economy:**
```
/balance
/daily
```

**Utility:**
```
/serverinfo
/userinfo
/botinfo
```

### 3. Check Logs

```bash
# Docker
docker-compose logs -f bot

# Manual
tail -f ../logs/bot.log
```

## Troubleshooting

### Bot Won't Start

**Check token:**
```bash
# Verify token is set
echo $DISCORD_TOKEN

# Or check .env file
cat .env | grep DISCORD_TOKEN
```

**Check database connection:**
```bash
# Docker
docker-compose ps postgres

# Manual
psql -U bot_user -d discord_bot -c "SELECT 1;"
```

### Commands Not Working

**Sync commands:**
The bot auto-syncs slash commands on startup. Wait 5-10 minutes after first start.

**Check bot permissions:**
Ensure bot has these permissions in Discord:
- Send Messages
- Read Message History
- Embed Links
- Add Reactions
- Manage Roles (for leveling)
- Kick Members (for moderation)
- Ban Members (for moderation)
- Manage Messages (for /clear)

### Database Errors

**Reset database:**
```bash
# Docker
docker-compose down
docker volume rm discord-bot_postgres_data
docker-compose up -d

# Manual
dropdb -U bot_user discord_bot
createdb -U bot_user discord_bot
psql -U bot_user -d discord_bot -f database/schema.sql
```

### High Memory Usage

**Check for memory leaks:**
```bash
docker stats discord-bot
```

**Restart bot:**
```bash
docker-compose restart bot
```

### Port Conflicts

If ports 5432 or 6379 are already in use:

Edit `docker-compose.yml`:
```yaml
postgres:
  ports:
    - "15432:5432"  # Changed from 5432

redis:
  ports:
    - "16379:6379"  # Changed from 6379
```

## Advanced Configuration

### Per-Server Settings

Most settings can be configured per server using commands or the database:

```sql
-- Example: Disable XP in a specific server
UPDATE guild_config SET xp_enabled = false WHERE guild_id = 123456789;

-- Example: Change currency name
UPDATE guild_config SET currency_name = 'Coins' WHERE guild_id = 123456789;
```

### Custom Emoji Currency

Use any emoji as currency:
```yaml
economy:
  currency_emoji: "🪙"  # or any other emoji
```

### Role Rewards

```
/rolereward 5 @Member
/rolereward 10 @Active
/rolereward 20 @Veteran
```

### Shop Items

Add items via database:
```sql
INSERT INTO shop_items (guild_id, name, description, price, item_type, item_data)
VALUES (
  123456789,
  'VIP Role',
  'Get VIP status for 7 days',
  1000,
  'role',
  '{"role_id": 987654321, "duration": 604800}'
);
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong bot token (never share!)
- [ ] Enable HTTPS for dashboard (when implemented)
- [ ] Set up regular database backups
- [ ] Configure firewall rules
- [ ] Use environment variables (never commit secrets)
- [ ] Enable Discord 2FA for bot account

### Backup Strategy

**Automated backups:**
```bash
# Add to crontab (crontab -e)
0 2 * * * docker exec discord-bot-postgres pg_dump -U bot_user discord_bot > /backups/discord_bot_$(date +\%Y\%m\%d).sql
```

**Manual backup:**
```bash
# Docker
docker exec discord-bot-postgres pg_dump -U bot_user discord_bot > backup.sql

# Manual
pg_dump -U bot_user discord_bot > backup.sql
```

**Restore backup:**
```bash
# Docker
docker exec -i discord-bot-postgres psql -U bot_user discord_bot < backup.sql

# Manual
psql -U bot_user discord_bot < backup.sql
```

### Monitoring

**View bot status:**
```bash
docker-compose ps
docker-compose logs --tail=50 bot
```

**Check resource usage:**
```bash
docker stats discord-bot
```

**Monitor with systemd (for non-Docker):**
```bash
# Create service file: /etc/systemd/system/discord-bot.service
[Unit]
Description=Discord Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=discord
WorkingDirectory=/opt/discord-bot/bot
ExecStart=/opt/discord-bot/bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Getting Help

- 📖 [Full Documentation](https://github.com/jcurtis260/Discord-bot/wiki)
- 🐛 [Report Issues](https://github.com/jcurtis260/Discord-bot/issues)
- 💬 [Discussions](https://github.com/jcurtis260/Discord-bot/discussions)

## Next Steps

Once your bot is running:

1. Configure role rewards for leveling
2. Set up shop items for economy
3. Create custom commands per server
4. Enable AI features (if desired)
5. Explore the dashboard (when available)
6. Check out the full documentation

Happy botting! 🤖
