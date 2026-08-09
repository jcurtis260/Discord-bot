# Web UI Settings Management Guide

Complete guide to managing all bot settings through the web dashboard.

## Overview

The web dashboard provides a comprehensive admin panel where you can configure **all bot settings** without editing files or restarting services. All changes are applied immediately or explained if a restart is needed.

## Table of Contents

1. [Accessing Settings](#accessing-settings)
2. [Global Bot Settings](#global-bot-settings)
3. [AI Configuration](#ai-configuration)
4. [Moderation Settings](#moderation-settings)
5. [Leveling System](#leveling-system)
6. [Economy System](#economy-system)
7. [Feature Toggles](#feature-toggles)
8. [Guild-Specific Settings](#guild-specific-settings)
9. [API Endpoints](#api-endpoints)

---

## Accessing Settings

1. **Login** to dashboard at `http://localhost:3000` (or your custom port)
2. Navigate to **Settings** in the main menu
3. All settings require **owner authentication**

---

## Global Bot Settings

### Bot Status & Activity

Configure how your bot appears to users:

**Settings:**
- **Status**: online, idle, dnd (do not disturb), invisible
- **Activity Text**: Custom status message
- **Activity Type**: playing, watching, listening, streaming

**Example:**
```
Status: online
Activity: Watching your server
Activity Type: watching
```

Result: Bot shows as "Watching your server"

**How to Change:**
1. Go to Settings → Bot Configuration
2. Update status, activity text, or activity type
3. Click "Save Changes"
4. **Note**: Requires bot restart to apply

**API Endpoint:**
```http
GET  /api/settings/bot/global
PUT  /api/settings/bot/global

Body:
{
  "status": "online",
  "activity": "with 1000 users",
  "activity_type": "playing"
}
```

---

## AI Configuration

### AI Provider Settings

Control AI conversation behavior:

**Settings:**
- **Enabled**: Toggle AI features on/off
- **Provider**: openai, anthropic, local, chatgpt_web
- **Model**: Model name (gpt-4, claude-3-sonnet, etc.)
- **Temperature**: 0.0-2.0 (creativity level)
- **Max Tokens**: 1-4000 (response length)
- **Default Personality**: friendly, professional, casual, helpful
- **Conversation Memory**: 1-50 messages
- **Random Engage Rate**: 0.0-1.0 (how often bot randomly joins conversations)

**How to Change:**
1. Settings → AI Configuration
2. Toggle "AI Enabled"
3. Select provider from dropdown
4. Adjust sliders for temperature, tokens, memory
5. Set engagement rate (0.05 = 5% of messages)
6. Click "Save"

**API Endpoint:**
```http
GET  /api/settings/ai
PUT  /api/settings/ai

Body:
{
  "enabled": true,
  "provider": "openai",
  "model": "gpt-4",
  "temperature": 0.8,
  "max_tokens": 500,
  "default_personality": "friendly",
  "conversation_memory": 10,
  "random_engage_rate": 0.05
}
```

---

## Moderation Settings

### Auto-Moderation

Configure automatic rule-based moderation:

**Settings:**
- **Enabled**: Toggle auto-mod on/off
- **Spam Threshold**: Messages per 5 seconds (1-20)
- **Mention Threshold**: Max mentions per message (1-20)
- **Caps Threshold**: Max % uppercase (0.0-1.0)
- **Action**: warn, timeout, kick

**How to Change:**
1. Settings → Moderation → Auto-Moderation
2. Toggle "Auto-Mod Enabled"
3. Adjust thresholds with sliders
4. Select action from dropdown
5. Click "Save"

**Example:**
```
Spam Threshold: 5 (more than 5 messages in 5 seconds = spam)
Mention Threshold: 5 (more than 5 @mentions = spam)
Caps Threshold: 0.7 (more than 70% CAPS = yelling)
Action: timeout (violators get 5-min timeout)
```

**API Endpoint:**
```http
GET  /api/settings/moderation
PUT  /api/settings/moderation

Body:
{
  "auto_mod_enabled": true,
  "spam_threshold": 5,
  "mention_threshold": 5,
  "caps_threshold": 0.7,
  "automod_action": "timeout"
}
```

### AI Moderation

Configure AI-powered content moderation:

**Settings:**
- **Enabled**: Toggle AI mod on/off
- **Confidence Threshold**: 0.0-1.0 (how confident AI must be)
- **Action**: warn, timeout, kick, log
- **Check Toxicity**: Detect toxic/hateful content
- **Check Spam**: Detect spam patterns
- **Check NSFW**: Detect inappropriate content
- **Log Channel**: Channel ID for moderation logs

**How to Change:**
1. Settings → Moderation → AI Moderation
2. Toggle "AI Mod Enabled"
3. Set confidence slider (0.7 = 70% sure before acting)
4. Check boxes for what to monitor
5. Select action
6. Optional: Set log channel ID
7. Click "Save"

**API Endpoint:**
```http
GET  /api/settings/ai-moderation
PUT  /api/settings/ai-moderation

Body:
{
  "enabled": true,
  "threshold": 0.7,
  "action": "warn",
  "check_toxicity": true,
  "check_spam": true,
  "check_nsfw": true,
  "log_channel": 123456789
}
```

---

## Leveling System

### XP & Progression

Configure the leveling/XP system:

**Settings:**
- **Enabled**: Toggle leveling on/off
- **XP Rate**: XP per message (1-100)
- **XP Cooldown**: Seconds between XP gains (0-300)
- **Announce Level Up**: Show level-up messages
- **Level Up Channel**: Optional channel for announcements

**How to Change:**
1. Settings → Leveling System
2. Toggle "Leveling Enabled"
3. Set XP per message (15 is balanced)
4. Set cooldown (60s prevents spam farming)
5. Toggle "Announce Level Ups"
6. Optional: Set announcement channel ID
7. Click "Save"

**Example:**
```
XP Rate: 15 (users get 15 XP per message)
Cooldown: 60 (can only earn XP once per minute)
Announce: true (show "You leveled up!" messages)
```

**API Endpoint:**
```http
GET  /api/settings/leveling
PUT  /api/settings/leveling

Body:
{
  "enabled": true,
  "xp_rate": 15,
  "xp_cooldown": 60,
  "announce_level_up": true,
  "level_up_channel": null
}
```

---

## Economy System

### Virtual Currency

Configure the economy system:

**Settings:**
- **Enabled**: Toggle economy on/off
- **Currency Name**: Name of your currency (max 20 chars)
- **Currency Emoji**: Emoji to display (💰, 🪙, 💵, etc.)
- **Starting Balance**: Initial coins for new users (0-100000)
- **Daily Reward**: Coins for /daily command (0-10000)
- **Daily Streak Bonus**: Bonus per consecutive day (0-1000)
- **Message Earn Rate**: Coins per message (0-100)
- **Message Earn Cooldown**: Seconds between earning (0-300)

**How to Change:**
1. Settings → Economy System
2. Toggle "Economy Enabled"
3. Set currency name (e.g., "Credits", "Gold", "Coins")
4. Pick emoji from emoji picker
5. Set starting balance (100 is typical)
6. Configure daily rewards and streaks
7. Set message earnings and cooldown
8. Click "Save"

**Example:**
```
Currency Name: Credits
Currency Emoji: 💰
Starting Balance: 100
Daily Reward: 50
Daily Streak Bonus: 10 (60 coins on day 2, 70 on day 3, etc.)
Message Earn Rate: 5
Message Cooldown: 60
```

**API Endpoint:**
```http
GET  /api/settings/economy
PUT  /api/settings/economy

Body:
{
  "enabled": true,
  "currency_name": "Credits",
  "currency_emoji": "💰",
  "starting_balance": 100,
  "daily_reward": 50,
  "daily_streak_bonus": 10,
  "message_earn_rate": 5,
  "message_earn_cooldown": 60
}
```

---

## Feature Toggles

### Enable/Disable Features

Toggle entire feature modules on/off:

**Features:**
- **Welcome Messages**: Join messages
- **Farewell Messages**: Leave messages
- **Reaction Roles**: Self-assign roles via reactions
- **Custom Commands**: User-created commands
- **Reminders**: Personal reminder system
- **Giveaways**: Giveaway management
- **Games**: Trivia, gambling, fun games

**How to Change:**
1. Settings → Features
2. Toggle switches for each feature
3. Click "Save"
4. Changes apply immediately

**Use Cases:**
- Disable features you don't need
- Test features individually
- Reduce bot complexity
- Comply with server rules (e.g., disable gambling games)

**API Endpoint:**
```http
GET  /api/settings/features
PUT  /api/settings/features

Body:
{
  "welcome_messages": true,
  "farewell_messages": true,
  "reaction_roles": true,
  "custom_commands": true,
  "reminders": true,
  "giveaways": true,
  "games": true
}
```

---

## Guild-Specific Settings

### Per-Server Configuration

Each Discord server can have different settings:

**Settings:**
- **Prefix**: Command prefix (default: /)
- **XP Enabled**: Leveling for this server
- **Economy Enabled**: Economy for this server
- **AI Enabled**: AI features for this server

**How to Change:**
1. Settings → Guild Settings
2. Select server from dropdown
3. Set custom prefix
4. Toggle features for this specific server
5. Click "Save"

**Example:**
```
Server: My Cool Server
Prefix: ! (use !rank instead of /rank)
XP Enabled: true
Economy Enabled: true
AI Enabled: false (disable AI in this specific server)
```

**API Endpoint:**
```http
GET  /api/settings/guild/{guild_id}
PUT  /api/settings/guild/{guild_id}

Body:
{
  "prefix": "!",
  "xp_enabled": true,
  "economy_enabled": true,
  "ai_enabled": false
}
```

---

## API Endpoints Reference

All settings are accessible via REST API:

### Authentication

All endpoints require authentication:
- **Header**: `Authorization: Bearer <jwt_token>`
- **Or**: `X-API-Key: <api_key>`

### Endpoints Summary

| Category | GET | PUT |
|----------|-----|-----|
| Bot Global | `/api/settings/bot/global` | `/api/settings/bot/global` |
| AI | `/api/settings/ai` | `/api/settings/ai` |
| Moderation | `/api/settings/moderation` | `/api/settings/moderation` |
| Leveling | `/api/settings/leveling` | `/api/settings/leveling` |
| Economy | `/api/settings/economy` | `/api/settings/economy` |
| Features | `/api/settings/features` | `/api/settings/features` |
| Guild | `/api/settings/guild/{id}` | `/api/settings/guild/{id}` |

### Response Format

**Success:**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

**Error:**
```json
{
  "detail": "Error message here"
}
```

---

## Best Practices

### 1. Test Settings on Test Server First

Before changing production settings:
1. Create a test Discord server
2. Add bot to test server
3. Test new settings there
4. Apply to production once verified

### 2. Document Changes

Keep a changelog of setting changes:
```
2026-08-09: Increased XP rate from 10 to 15
2026-08-09: Enabled AI moderation with 0.7 threshold
2026-08-09: Changed currency from Coins to Credits
```

### 3. Monitor After Changes

After changing settings:
1. Check bot behavior in Discord
2. Review logs for errors
3. Watch user reactions
4. Adjust as needed

### 4. Backup Configuration

Before major changes:
```bash
# Backup config file
cp config/bot_config.yaml config/bot_config.backup.yaml
```

### 5. Use Appropriate Values

**XP System:**
- XP Rate: 10-20 (balanced)
- Cooldown: 60s (prevents farming)

**Economy:**
- Starting Balance: 50-100
- Daily Reward: 50-100
- Message Earn: 1-10

**AI:**
- Temperature: 0.7-0.9 (creative)
- Max Tokens: 300-800 (conversational)
- Engage Rate: 0.03-0.10 (3-10%)

**Moderation:**
- AI Threshold: 0.6-0.8 (balanced)
- Spam Threshold: 5-10 messages
- Caps Threshold: 0.7-0.8 (70-80%)

---

## Troubleshooting

### Settings Not Saving

**Check:**
1. You're logged in as owner
2. Config file is writable
3. Check browser console for errors
4. Check API response in Network tab

**Solution:**
```bash
# Check file permissions
ls -la config/bot_config.yaml

# Make writable
chmod 644 config/bot_config.yaml
```

### Changes Not Applying

Some changes require bot restart:
- Bot status/activity
- AI provider/model
- Feature toggles (first time)

**To restart:**
```bash
# Docker
docker-compose restart bot

# Portainer
Containers → discord-bot → Restart

# Manual
# Stop bot (Ctrl+C)
python bot/main.py
```

### API Returns 403 Forbidden

You're not authenticated as owner:
1. Log out and log back in
2. Verify `BOT_OWNER_ID` in config matches your Discord ID
3. Check Discord OAuth is configured correctly

### Settings Reset After Restart

Settings are saved to `config/bot_config.yaml`:
1. Ensure file exists and is writable
2. Check Docker volume mounts
3. Verify config path in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./config:/app/config
   ```

---

## Security Notes

### Who Can Change Settings?

**Only bot owner** can change settings via web UI:
- Set `BOT_OWNER_ID` in config
- Owner-only endpoints return 403 for others
- API key also has full access

### Audit Trail

Changes are logged:
- Check `logs/bot.log` for setting changes
- Each change records who made it and when
- Keep logs for compliance/troubleshooting

### Sensitive Settings

Some settings affect bot security:
- **AI API Keys**: Never display in UI
- **Database URL**: Never exposed via API
- **Dashboard Secrets**: Never returned in responses

---

## Summary

**All bot settings are now configurable via web UI:**

✅ Bot status and activity
✅ AI provider and behavior
✅ Moderation thresholds and actions
✅ Leveling rates and announcements
✅ Economy currency and rewards
✅ Feature toggles
✅ Per-server customization

**No more editing YAML files or restarting services!** (Except for bot status/activity changes)

**Access:** `http://localhost:3000/settings` (or your custom port)

**Requires:** Owner authentication via Discord OAuth2
