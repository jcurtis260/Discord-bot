# Discord Bot - AI-Powered Community Manager

A comprehensive Discord bot combining MEE6-like features with advanced AI conversations, complete economy system, games, giveaways, and Red-DiscordBot cog compatibility.

## Features

### Core Features
- ✅ **Moderation System** - Manual moderation commands with infraction tracking
- ✅ **Auto-Moderation** - Rule-based: spam, bad words, mass mentions, caps filter
- ✅ **AI Moderation** - AI-powered content analysis for toxicity, NSFW, spam with user whitelist
- ✅ **Leveling & XP** - Role rewards, leaderboards, rank cards
- ✅ **AI Conversations** - Natural language with OpenAI, Anthropic, local models, or ChatGPT web
- ✅ **AI Providers** - OpenAI (GPT-4), Anthropic (Claude), local models, or ChatGPT web login (no API!)
- ✅ **Economy** - Virtual currency, shop, inventory, transactions
- ✅ **Giveaways** - Full giveaway management with entry requirements
- ✅ **Games** - Trivia, gambling (coinflip, slots), fun games (RPS, dice)
- ✅ **Welcome & Goodbye** - Customizable join/leave messages with formatting
- ✅ **Reaction Roles** - Easy role assignment via reactions
- ✅ **Custom Commands** - Create server-specific commands with usage tracking
- ✅ **Reminders** - Set personal reminders with natural language time parsing
- ✅ **Web Dashboard** - Locally-hosted management interface with secure authentication
- ✅ **Dashboard Security** - Discord OAuth2, owner-only access, API keys, IP whitelisting
- ✅ **Bot Customization** - Change avatar, name, status, nickname per-server

### Advanced Features
- ✅ **Red Cog Compatibility** - Load 1000+ Red-DiscordBot cogs with Config API support
- 🔄 **Starboard** - Highlight popular messages (database ready)
- 🔄 **Birthdays** - Birthday tracking and announcements (database ready)
- 🔄 **Tickets** - Support ticket management (planned)
- 🔄 **Music System** - Play from YouTube/Spotify (planned)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for dashboard)
- Discord Bot Token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jcurtis260/Discord-bot.git
cd Discord-bot
```

2. **Set up Python environment**
```bash
cd bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure the bot**
```bash
cp config/bot_config.example.yaml config/bot_config.yaml
# Edit config/bot_config.yaml with your settings
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb discord_bot

# Run migrations
python -m alembic upgrade head
```

5. **Start the bot**
```bash
python main.py
```

6. **Set up dashboard (optional)**

**⚠️ IMPORTANT: Dashboard Security Required!**

Before accessing the dashboard, you MUST configure security settings. See [`DASHBOARD_SECURITY.md`](DASHBOARD_SECURITY.md) for detailed setup.

**Quick security setup:**

```bash
# 1. Get your Discord User ID
# Discord Settings → Advanced → Developer Mode (ON)
# Right-click your username → Copy User ID

# 2. Generate secure keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Get Discord OAuth2 credentials
# https://discord.com/developers/applications
# Your App → OAuth2 → Copy Client ID and Client Secret
# Add redirect: http://localhost:3000/auth/callback

# 4. Configure in .env or config/bot_config.yaml
BOT_OWNER_ID=your_discord_user_id
DASHBOARD_SECRET_KEY=generated_secret_key
DASHBOARD_DISCORD_CLIENT_ID=your_client_id
DASHBOARD_DISCORD_CLIENT_SECRET=your_client_secret
```

**Start dashboard:**

```bash
# Backend
cd dashboard/backend
pip install -r requirements.txt
python server.py

# Frontend (new terminal)
cd dashboard/frontend
npm install
npm run dev
```

Access dashboard at `http://localhost:3000` and log in with Discord.

**📖 Full Guide:** See [`DASHBOARD_SECURITY.md`](DASHBOARD_SECURITY.md) for complete setup, hosting options, and security best practices.

## Docker Deployment

### Option 1: Docker Compose (Command Line)

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bot
```

### Option 2: Portainer (Web UI - Recommended)

**Easy visual management of your entire bot stack!**

1. **Install Portainer:**
```bash
docker volume create portainer_data
docker run -d -p 9443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

2. **Access Portainer:** Open `https://localhost:9443`

3. **Deploy bot stack:**
   - Go to **Stacks** → **Add stack**
   - Name: `discord-bot`
   - Select **Git Repository**
   - URL: `https://github.com/jcurtis260/Discord-bot.git`
   - Branch: `cursor/discord-bot-plan-ea5f`
   - Add your environment variables
   - Click **Deploy**

**Benefits:**
- 🖥️ Web-based GUI - no command line needed
- 📊 Live monitoring - CPU, memory, logs
- 🔄 Easy updates - one-click redeploy
- 🌐 Remote access - manage from anywhere
- 📦 Stack management - start/stop/restart all services

**📖 Full Guide:** See [`PORTAINER_DEPLOYMENT.md`](PORTAINER_DEPLOYMENT.md) for complete setup, security, backups, and troubleshooting.

## Configuration

### Bot Configuration
Edit `config/bot_config.yaml`:

```yaml
bot:
  token: "YOUR_BOT_TOKEN"
  prefix: "/"

database:
  host: "localhost"
  port: 5432
  database: "discord_bot"
  user: "bot_user"
  password: "your_password"

ai:
  provider: "openai"  # or "anthropic", "local"
  api_key: "YOUR_API_KEY"
  model: "gpt-4"
```

See `config/bot_config.example.yaml` for all options.

### Dashboard Setup
1. Navigate to `http://localhost:3000`
2. Create admin account (first time)
3. Follow setup wizard
4. Configure bot settings via UI

## Commands

### Moderation
- `/warn <user> <reason>` - Warn a user
- `/mute <user> <duration> <reason>` - Mute a user
- `/unmute <user>` - Unmute a user
- `/kick <user> <reason>` - Kick a user
- `/ban <user> <duration> <reason>` - Ban a user
- `/clear <amount>` - Delete messages
- `/infractions <user>` - View user infractions

### Auto-Moderation
- `/automod-enable` - Enable auto-moderation
- `/automod-disable` - Disable auto-moderation
- `/automod-config` - View auto-mod settings
- `/automod-action <action>` - Set auto-mod action
- `/automod-badwords <action> <words>` - Manage bad words filter

### AI Moderation
- `/aimod-enable` - Enable AI-powered moderation
- `/aimod-disable` - Disable AI-powered moderation
- `/aimod-config` - View AI mod settings
- `/aimod-threshold <0-100>` - Set confidence threshold
- `/aimod-action <action>` - Set AI mod action (warn/timeout/kick/log)
- `/aimod-whitelist <action> <user>` - Manage AI mod whitelist
- `/aimod-logchannel <channel>` - Set AI mod log channel
- `/aimod-checks` - Toggle specific AI checks

### Leveling
- `/rank [@user]` - View rank card
- `/leaderboard` - Server leaderboard
- `/setxp <user> <amount>` - Set user XP (admin)
- `/addxp <user> <amount>` - Add XP to user (admin)
- `/rolereward <level> <role>` - Set role reward (admin)

### Economy
- `/balance [@user]` - Check balance
- `/daily` - Claim daily reward
- `/shop` - View shop items
- `/buy <item>` - Purchase item
- `/pay <user> <amount>` - Transfer money

### Giveaways
- `/giveaway-create <duration> <winners> <prize>` - Create giveaway

### Games
- `/trivia [category]` - Start trivia game
- `/coinflip <bet> <choice>` - Flip a coin
- `/slots <bet>` - Play slots
- `/rps <choice>` - Rock paper scissors
- `/roll [sides]` - Roll dice

### AI Conversation
- Mention the bot or reply to its messages to chat
- `/ai-config <action> [value]` - Configure AI settings
- `/chat <message>` - Chat with the AI

### Welcome & Goodbye
- `/welcome-set <channel> <message>` - Set welcome message
- `/welcome-disable` - Disable welcome messages
- `/goodbye-set <channel> <message>` - Set goodbye message
- `/goodbye-disable` - Disable goodbye messages

### Custom Commands
- `/cc-add <name> <response>` - Add custom command
- `/cc-edit <name> <response>` - Edit custom command
- `/cc-delete <name>` - Delete custom command
- `/cc-list` - List all custom commands
- `/cc-info <name>` - Get info about custom command

### Reaction Roles
- `/reactionrole-add <message_id> <emoji> <role>` - Add reaction role
- `/reactionrole-remove <message_id> <emoji>` - Remove reaction role
- `/reactionrole-list` - List all reaction roles

### Reminders
- `/remind <time> <message>` - Set a reminder
- `/reminders` - View your reminders
- `/reminder-delete <id>` - Delete a reminder

### Bot Settings
- `/botavatar <url>` - Change bot's avatar (owner only)
- `/botname <name>` - Change bot's username (owner only)
- `/botnickname [nickname]` - Change bot's server nickname (admin)
- `/botstatus <type> <text> [status]` - Change bot status (owner only)
- `/prefix <new_prefix>` - Change command prefix (admin)
- `/togglefeature <feature> <enabled>` - Enable/disable features (admin)
- `/botconfig` - View current configuration

### Red Cog Management
- `/redcog-load <cog_name>` - Load Red cog (owner only)
- `/redcog-unload <cog_name>` - Unload Red cog (owner only)
- `/redcog-reload <cog_name>` - Reload Red cog (owner only)
- `/redcog-list` - List all available Red cogs
- `/redcog-info <cog_name>` - Get info about Red cog

### Utility
- `/help` - Show help
- `/ping` - Check latency
- `/serverinfo` - Server info
- `/userinfo [@user]` - User info
- `/botinfo` - Bot statistics
- `/avatar [@user]` - View user's avatar

## Dashboard Features

- 📊 **Real-time Dashboard** - Bot status, stats, activity graphs
- 🛡️ **Moderation Panel** - Manage infractions, auto-mod settings
- 📈 **Leveling Config** - XP rates, role rewards, rank cards
- 🤖 **AI Configuration** - Personality editor, engagement rules
- 💰 **Economy Manager** - Shop editor, transaction logs
- 🎉 **Giveaway Creator** - Visual giveaway builder
- 🎮 **Game Settings** - Trivia questions, gambling limits
- 🔌 **Red Cog Browser** - Install community cogs
- 📝 **Custom Commands** - Command builder with embeds
- 📊 **Analytics** - Charts, graphs, user statistics

## Red Cog Compatibility

This bot can load Red-DiscordBot cogs for extended functionality:

```bash
# Install a cog
/redcog install <repo> <cog_name>

# List installed cogs
/redcog list

# Or use the dashboard cog browser
```

Popular Red cogs supported:
- Audio (music playback)
- Alias (command aliases)
- CustomCom (extended custom commands)
- StreamAlerts (Twitch/YouTube notifications)
- And 1000+ more!

## Development

### Project Structure
```
discord-bot/
├── bot/                    # Discord bot
│   ├── cogs/              # Command modules
│   ├── modules/           # Core functionality
│   ├── red_compat/        # Red cog compatibility
│   └── main.py            # Entry point
├── dashboard/             # Web dashboard
│   ├── frontend/          # React app
│   └── backend/           # FastAPI server
├── database/              # Database migrations
├── config/                # Configuration files
└── docker-compose.yml     # Docker setup
```

### Running Tests
```bash
# Bot tests
cd bot
pytest

# Dashboard tests
cd dashboard/backend
pytest
```

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Environment Variables

Create `.env` file:

```env
# Discord
DISCORD_TOKEN=your_bot_token_here
DISCORD_APP_ID=your_app_id_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/discord_bot
REDIS_URL=redis://localhost:6379/0

# AI (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Dashboard
DASHBOARD_SECRET_KEY=your_secret_key_here
DASHBOARD_PORT=3000
```

## Troubleshooting

### Bot won't start
- Check your bot token in config
- Ensure database is running
- Check logs in `logs/bot.log`

### Dashboard not loading
- Check if backend is running on port 8080
- Check if frontend is running on port 3000
- Clear browser cache

### AI not responding
- Verify AI API key is set
- Check AI is enabled in channel settings
- Review AI engagement rate settings

## Documentation

For detailed information, see these guides:

### Essential Setup Guides
- **[PORTAINER_DEPLOYMENT.md](PORTAINER_DEPLOYMENT.md)** - Deploy and manage your bot with Portainer's web UI (easiest method!)
- **[CUSTOM_PORTS.md](CUSTOM_PORTS.md)** - Configure custom ports for the dashboard (use any port you want!)
- **[WEB_UI_SETTINGS.md](WEB_UI_SETTINGS.md)** - **NEW!** Manage all bot settings through the web dashboard (no file editing!)
- **[DASHBOARD_SECURITY.md](DASHBOARD_SECURITY.md)** - Complete guide to securing the web dashboard
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Step-by-step installation and configuration guide

### Configuration Guides
- **[BOT_CUSTOMIZATION.md](BOT_CUSTOMIZATION.md)** - Customize bot avatar, name, status, and per-server settings
- **[AI_SETUP.md](AI_SETUP.md)** - Configure AI providers (OpenAI, Anthropic, local models)
- **[CHATGPT_WEB_SETUP.md](CHATGPT_WEB_SETUP.md)** - Use ChatGPT without API keys (unofficial method)

### Development
- **[BUGS_AND_IMPROVEMENTS.md](BUGS_AND_IMPROVEMENTS.md)** - Known issues, code review findings, and improvement roadmap
- **[dashboard/README.md](dashboard/README.md)** - Dashboard development and API documentation

## Support

- 📖 [Documentation](https://github.com/jcurtis260/Discord-bot/wiki)
- 🐛 [Issue Tracker](https://github.com/jcurtis260/Discord-bot/issues)
- 💬 [Discussions](https://github.com/jcurtis260/Discord-bot/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot) - Cog compatibility
- [FastAPI](https://fastapi.tiangolo.com/) - Dashboard backend
- [React](https://react.dev/) - Dashboard frontend

## Roadmap

- [x] Core moderation features
- [x] Leveling system
- [x] AI conversations
- [x] Economy system
- [x] Giveaway system
- [x] Games and entertainment
- [x] Web dashboard
- [x] Red cog compatibility
- [ ] Voice AI conversations
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Plugin marketplace

---

**Note**: This bot is self-hosted and requires setup. No data is collected or stored externally. All features run on your own infrastructure.
