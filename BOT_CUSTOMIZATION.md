# Bot Customization Guide

Complete guide to customizing your Discord bot's appearance and settings.

## Overview

The bot includes powerful customization features that allow you to:
- 🎨 Change bot's avatar and username
- 📝 Set custom nicknames per server
- 🎭 Customize status and activity
- ⚙️ Configure features per server
- 🎯 Set custom command prefix

---

## Bot Owner Commands

These commands can **only be used by the bot owner** (the person who owns the Discord application).

### Change Bot Avatar

```
/botavatar <url>
```

**Example:**
```
/botavatar https://i.imgur.com/example.png
```

**Notes:**
- Image must be a direct URL to PNG, JPG, or GIF
- Max file size: 10MB
- Animated avatars require Discord Nitro on the bot account

**Supported formats:**
- PNG, JPG, JPEG, GIF, WEBP

### Change Bot Username

```
/botname <name>
```

**Example:**
```
/botname Community Manager
```

**Restrictions:**
- 2-32 characters
- Can only change twice per hour (Discord limitation)
- Cannot use "Discord", "Clyde", or other reserved names

### Change Bot Status

```
/botstatus <activity_type> <activity_text> [status]
```

**Activity Types:**
- `Playing` - Shows as "Playing [text]"
- `Streaming` - Shows as "Streaming [text]"
- `Listening to` - Shows as "Listening to [text]"
- `Watching` - Shows as "Watching [text]"
- `Competing in` - Shows as "Competing in [text]"

**Status Types:**
- `Online` (green) - Default
- `Idle` (orange) - Away
- `Do Not Disturb` (red) - DND
- `Invisible` (gray) - Offline appearance

**Examples:**
```
/botstatus activity_type:Playing activity_text:with 1000 members status:Online
/botstatus activity_type:Watching activity_text:for new members status:Idle
/botstatus activity_type:Listening to activity_text:your commands status:Online
```

**Notes:**
- Status persists across bot restarts
- Changes are visible globally across all servers

---

## Server Admin Commands

These commands can be used by **administrators** in your server.

### Change Bot Nickname

```
/botnickname [nickname]
```

**Examples:**
```
/botnickname Server Helper
/botnickname ModBot
/botnickname     (resets to default name)
```

**Notes:**
- Only affects the current server
- Leave blank to reset to default username
- Bot must have "Change Nickname" permission

### Change Command Prefix

```
/prefix <new_prefix>
```

**Examples:**
```
/prefix !
/prefix ?
/prefix bot.
```

**Restrictions:**
- 1-10 characters
- Cannot contain spaces (for multi-word, use underscores)
- Affects text commands (slash commands always use `/`)

**Note:** This is per-server. Each server can have its own prefix.

### Toggle Features

```
/togglefeature <feature> <enabled>
```

**Available Features:**
- `Leveling/XP` - XP gain from messages
- `Economy` - Virtual currency system
- `AI Conversations` - AI chat features
- `Giveaways` - Giveaway system
- `Games` - Trivia, gambling, etc.

**Examples:**
```
/togglefeature feature:Leveling/XP enabled:True
/togglefeature feature:Economy enabled:False
/togglefeature feature:AI_Conversations enabled:True
```

**Use Cases:**
- Disable XP in casual/spam channels
- Turn off economy for specific servers
- Enable AI only in certain communities

### View Configuration

```
/botconfig
```

Shows:
- Current bot name and nickname
- Enabled/disabled features
- Server settings (prefix, XP rate, currency)
- Configured channels (welcome, logs, starboard)

**Example Output:**
```
⚙️ Bot Configuration - My Server

🤖 Bot Information
Name: Community Bot
Nickname: Helper
ID: 123456789

🎯 Features
✅ Leveling
✅ Economy
❌ AI
✅ Giveaways
✅ Games

⚙️ Settings
Prefix: /
XP Rate: 15
Currency: 💰 Credits

📺 Channels
Welcome: #welcome
Logs: #mod-logs
```

---

## Configuration Examples

### Professional Server Setup

```bash
# Set professional name and avatar
/botname Professional Manager
/botavatar https://example.com/professional-avatar.png

# Set status
/botstatus activity_type:Watching activity_text:server activity status:Online

# Configure per server
/botnickname Manager
/prefix !

# Enable core features only
/togglefeature feature:Leveling/XP enabled:True
/togglefeature feature:Economy enabled:True
/togglefeature feature:Games enabled:False
```

### Gaming Community Setup

```bash
# Gaming themed
/botname GameBot
/botavatar https://example.com/gaming-avatar.png

# Fun status
/botstatus activity_type:Playing activity_text:with members status:Online

# Per server nickname
/botnickname GameMaster
/prefix !

# Enable all features
/togglefeature feature:Leveling/XP enabled:True
/togglefeature feature:Economy enabled:True
/togglefeature feature:Games enabled:True
/togglefeature feature:Giveaways enabled:True
```

### Study Group Setup

```bash
# Professional and helpful
/botname Study Assistant
/botavatar https://example.com/book-avatar.png

# Appropriate status
/botstatus activity_type:Watching activity_text:study sessions status:Online

# Clear nickname
/botnickname Study Bot
/prefix ?

# Focus features
/togglefeature feature:Leveling/XP enabled:True
/togglefeature feature:Economy enabled:False
/togglefeature feature:Games enabled:False
```

---

## Per-Server Customization

### Why Per-Server Settings?

Different communities need different configurations:

**Casual Server:**
- Nickname: "Chill Bot"
- All features enabled
- Fun currency name

**Professional Server:**
- Nickname: "Manager"
- Limited features
- Serious currency name

### How to Configure Multiple Servers

1. Join each server with the bot
2. In each server, run:
   ```
   /botnickname <server-specific-name>
   /prefix <server-specific-prefix>
   /togglefeature <as needed>
   ```

3. Configure currency and XP in database:
   ```sql
   -- Example: Change currency per server
   UPDATE guild_config 
   SET currency_name = 'Coins', currency_emoji = '🪙'
   WHERE guild_id = 123456789;
   
   -- Example: Change XP rates
   UPDATE guild_config 
   SET xp_rate = 20, xp_cooldown = 30
   WHERE guild_id = 123456789;
   ```

---

## Advanced Configuration

### Database Configuration

For advanced settings, you can directly modify the database:

```sql
-- View current settings for a server
SELECT * FROM guild_config WHERE guild_id = 123456789;

-- Change welcome message
UPDATE guild_config 
SET welcome_message = 'Welcome {mention} to {server}! 🎉'
WHERE guild_id = 123456789;

-- Set channels
UPDATE guild_config 
SET welcome_channel = 987654321, log_channel = 876543210
WHERE guild_id = 123456789;

-- AI settings
UPDATE guild_config 
SET ai_personality = 'friendly', ai_engagement_rate = 0.2
WHERE guild_id = 123456789;
```

### Configuration File

Edit `config/bot_config.yaml` for global defaults:

```yaml
bot:
  status: "online"
  activity: "your server"
  activity_type: "watching"

leveling:
  enabled: true
  xp_per_message: 15
  xp_cooldown: 60
  announce_level_up: true

economy:
  enabled: true
  currency_name: "Credits"
  currency_emoji: "💰"
  starting_balance: 100
  daily_reward: 50
```

---

## Troubleshooting

### "Only the bot owner can change..."

**Problem:** You're not recognized as the bot owner.

**Solution:**
1. Make sure you're logged into Discord as the owner of the Discord application
2. Check Discord Developer Portal → Your Application → General Information
3. The "Owner" field should show your Discord username

### "Failed to update avatar/name"

**Problem:** Discord rate limits or invalid input.

**Solutions:**
- **Avatar:** Make sure URL is direct image link (ends in .png, .jpg, etc.)
- **Name:** Can only change twice per hour
- **Name:** Must be 2-32 characters
- **Name:** Cannot use reserved names

### "I don't have permission to change my nickname"

**Problem:** Bot lacks permissions in the server.

**Solution:**
Grant bot these permissions:
- "Change Nickname" - For `/botnickname`
- "Manage Nicknames" - If bot needs to change others' nicknames

### Status Not Persisting

**Problem:** Status resets after bot restart.

**Solution:**
The `/botstatus` command saves to database. Make sure:
1. Database is connected
2. `bot_settings` table exists
3. Check logs for any database errors

---

## Best Practices

### Naming

✅ **Do:**
- Use clear, descriptive names
- Match your community's theme
- Keep it professional for business servers

❌ **Don't:**
- Use offensive names
- Impersonate Discord/Discord staff
- Use excessively long names

### Status Messages

✅ **Do:**
- Keep it relevant to your bot's purpose
- Update seasonally for events
- Use appropriate activity types

❌ **Don't:**
- Use excessive emojis
- Include advertisements
- Use misleading information

### Server Configuration

✅ **Do:**
- Disable unused features
- Set appropriate XP rates
- Configure welcome/log channels

❌ **Don't:**
- Enable all features unnecessarily
- Set XP too high (causes fast leveling)
- Forget to configure channels

---

## Quick Reference

### Owner Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/botavatar` | Change avatar | `/botavatar <url>` |
| `/botname` | Change username | `/botname <name>` |
| `/botstatus` | Change status | `/botstatus <type> <text>` |

### Admin Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/botnickname` | Change nickname | `/botnickname [name]` |
| `/prefix` | Change prefix | `/prefix <prefix>` |
| `/togglefeature` | Toggle features | `/togglefeature <feature> <bool>` |
| `/botconfig` | View config | `/botconfig` |

---

## Examples Gallery

### Community Bot
```
Name: Community Helper
Avatar: [Friendly robot]
Status: Watching community chat
Nickname: Helper
Prefix: !
Features: All enabled
```

### Support Bot
```
Name: Support Assistant
Avatar: [Headset icon]
Status: Listening to support requests
Nickname: Support
Prefix: ?
Features: Tickets, Leveling
```

### Game Server Bot
```
Name: GameMaster
Avatar: [Game controller]
Status: Playing with 1000 members
Nickname: GM
Prefix: /
Features: All + Economy
```

---

## Need Help?

- Check `/botconfig` to see current settings
- View logs for any errors
- See main documentation for more features
- Report issues on GitHub

---

**Pro Tip:** Set up a test server to experiment with different configurations before applying to your main community!
