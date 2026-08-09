# Discord Bot - AI-Powered Community Manager

A comprehensive Discord bot combining MEE6-like features with advanced AI conversations, complete economy system, games, giveaways, and Red-DiscordBot cog compatibility.

## Features

### Core Features
- ✅ **Moderation System** - Auto-mod, manual commands, infraction tracking
- ✅ **Leveling & XP** - Role rewards, leaderboards, rank cards
- ✅ **AI Conversations** - Natural language, random engagement, personality system
- ✅ **Economy** - Virtual currency, shop, inventory, transactions
- ✅ **Giveaways** - Full giveaway management with entry requirements
- ✅ **Games** - Trivia, gambling (slots, blackjack, roulette), fun games
- ✅ **Welcome/Farewell** - Customizable messages and auto-roles
- ✅ **Reaction Roles** - Easy role assignment via reactions
- ✅ **Custom Commands** - Create server-specific commands
- ✅ **Web Dashboard** - Locally-hosted management interface

### Advanced Features
- 🎮 **Red Cog Compatibility** - Load 1000+ Red-DiscordBot cogs
- 🎵 **Music System** - Play from YouTube/Spotify (optional)
- 🎫 **Tickets** - Support ticket management
- ⭐ **Starboard** - Highlight popular messages
- ⏰ **Reminders** - User reminder system
- 🎂 **Birthdays** - Birthday tracking and announcements

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

Access dashboard at `http://localhost:3000`

## Docker Deployment

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bot
```

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
- `/kick <user> <reason>` - Kick a user
- `/ban <user> <duration> <reason>` - Ban a user
- `/clear <amount>` - Delete messages

### Leveling
- `/rank [@user]` - View rank card
- `/leaderboard` - Server leaderboard
- `/setxp <user> <amount>` - Set user XP (admin)

### Economy
- `/balance [@user]` - Check balance
- `/daily` - Claim daily reward
- `/shop` - View shop items
- `/buy <item>` - Purchase item
- `/pay <user> <amount>` - Transfer money

### Giveaways
- `/giveaway create` - Create giveaway
- `/giveaway end <id>` - End giveaway
- `/giveaway reroll <id>` - Reroll winner

### Games
- `/trivia [category]` - Start trivia game
- `/slots <bet>` - Play slots
- `/blackjack <bet>` - Play blackjack
- `/coinflip <bet>` - Flip a coin
- `/rps [@user]` - Rock paper scissors

### AI
- Mention the bot to chat
- Reply to bot messages to continue conversation
- `/ai enable` - Enable AI in channel (admin)
- `/ai personality <type>` - Set personality (admin)

### Bot Customization
- `/botavatar <url>` - Change bot's avatar (owner only)
- `/botname <name>` - Change bot's username (owner only)
- `/botnickname [nickname]` - Change bot's server nickname (admin)
- `/botstatus <type> <text> [status]` - Change bot status (owner only)
- `/prefix <new_prefix>` - Change command prefix (admin)
- `/togglefeature <feature> <enabled>` - Enable/disable features (admin)
- `/botconfig` - View current configuration

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
