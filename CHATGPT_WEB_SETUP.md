# ChatGPT Web Authentication Setup Guide

This bot supports using ChatGPT without API costs by logging in with your ChatGPT account.

**⚠️ IMPORTANT WARNINGS:**
- This method violates OpenAI's Terms of Service
- Your ChatGPT account may be banned
- Sessions expire regularly (need to refresh tokens)
- Not suitable for production bots
- Can break when OpenAI updates their website

**Recommended:** Use official OpenAI API or free local models instead

## Method 1: revChatGPT (ChatGPT Web Interface)

Uses your ChatGPT session to access GPT-4/GPT-3.5.

### Step 1: Install Dependencies

```bash
pip install revChatGPT
```

### Step 2: Get Your Session Token

**Option A: Session Token (Easiest, expires in ~2 weeks)**

1. Go to https://chat.openai.com/ and login
2. Open browser DevTools (Press F12)
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Click **Cookies** → `https://chat.openai.com`
5. Find cookie named `__Secure-next-auth.session-token`
6. Copy its **Value**

**Option B: Access Token (More reliable, expires in ~2 months)**

1. Go to https://chat.openai.com/ and login
2. Open new tab and go to: `https://chat.openai.com/api/auth/session`
3. Copy the `accessToken` value from the JSON response

### Step 3: Configure Bot

Edit `bot_config.yaml`:

```yaml
ai:
  provider: "chatgpt_web"
  web_method: "revchatgpt"
  
  # Use ONE of these:
  chatgpt_session_token: "YOUR_SESSION_TOKEN_HERE"  # Method A
  # OR
  chatgpt_access_token: "YOUR_ACCESS_TOKEN_HERE"    # Method B (recommended)
```

### Step 4: Start Bot

```bash
python bot/main.py
```

The bot will use your ChatGPT session for conversations!

### Troubleshooting

**"Session expired" error:**
- Tokens expire after 1-2 weeks/months
- Get a new token following steps above
- Update config and restart bot

**"Unauthorized" error:**
- Your ChatGPT account may be flagged
- Token may be invalid
- Try logging out and back into ChatGPT
- Get a fresh token

**Rate limited:**
- Free ChatGPT accounts have strict limits
- ChatGPT Plus accounts have higher limits
- Consider using local models or official API instead

## Method 2: Poe.com (Multiple AI Models)

Access ChatGPT, Claude, and other models through Poe.com.

### Why Poe?

- Access to **multiple AI models** in one place
- ChatGPT (GPT-3.5, GPT-4)
- Claude (Instant, 2, 3, Opus)
- Many community models
- More reliable than direct ChatGPT scraping

### Step 1: Install Dependencies

```bash
pip install poe-api
```

### Step 2: Get Poe Token

1. Go to https://poe.com/ and sign up/login
2. Open browser DevTools (F12)
3. Go to **Application** → **Cookies** → `https://poe.com`
4. Find cookie named `p-b`
5. Copy its **Value**

### Step 3: Configure Bot

Edit `bot_config.yaml`:

```yaml
ai:
  provider: "chatgpt_web"
  web_method: "poe"
  poe_token: "YOUR_POE_TOKEN_HERE"
  poe_bot: "GPT-4"  # See available bots below
```

### Available Poe Bots

**Free Bots:**
- `ChatGPT` - GPT-3.5-turbo
- `Claude-instant` - Fast Claude model
- Many community bots

**Subscription Required ($20/month):**
- `GPT-4` - OpenAI GPT-4
- `Claude-2` - Anthropic Claude 2
- `Claude-3-Opus` - Most capable Claude
- `Claude-3-Sonnet` - Balanced Claude

### Step 4: Start Bot

```bash
python bot/main.py
```

### Troubleshooting

**"Token expired":**
- Poe tokens expire after a few weeks
- Get a new token from Poe website
- Update config

**Bot not available:**
- Check bot name spelling (case-sensitive)
- Some bots require Poe subscription
- Use `/poebot list` to see available bots

## Comparison: Web Auth vs API vs Local

| Feature | ChatGPT Web | Poe.com | OpenAI API | Local Models |
|---------|-------------|---------|------------|--------------|
| **Cost** | Free* | Free/Paid | Pay-per-use | Free |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Reliability** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Against ToS** | ❌ Yes | ❌ Yes | ✅ No | ✅ No |
| **Ban Risk** | High | Medium | None | None |
| **Setup** | Hard | Medium | Easy | Medium |
| **Maintenance** | High | Medium | Low | Low |

*Free ChatGPT accounts have strict rate limits

## Commands to Manage Web Auth

```bash
# View current AI provider
/ai-config view

# Test AI conversation
/chat message: Hello!

# Check if web auth is working
# Bot will respond with error if session expired
```

## Refreshing Tokens

You'll need to refresh tokens periodically:

**ChatGPT Session Token:**
- Expires: ~1-2 weeks
- Refresh: Follow Step 2 above

**ChatGPT Access Token:**
- Expires: ~1-2 months  
- Refresh: Follow Step 2 Option B above

**Poe Token:**
- Expires: ~2-4 weeks
- Refresh: Follow Poe Step 2 above

## Security Notes

1. **Never share your tokens** - They give full access to your account
2. **Use a dedicated account** - Don't use your main ChatGPT/Poe account
3. **Monitor for bans** - Check if your account gets flagged
4. **Have backups ready** - Keep API keys or local models as fallback

## Better Alternatives

Instead of web auth, consider:

### 1. OpenAI API (Recommended for Production)
```yaml
ai:
  provider: "openai"
  api_key: "sk-..."
  model: "gpt-3.5-turbo"  # Cheap: $0.001 per conversation
```

### 2. Local Models (Free & Private)
```yaml
ai:
  provider: "local"
  local_model: "microsoft/DialoGPT-medium"
```

### 3. Anthropic Claude (Alternative)
```yaml
ai:
  provider: "anthropic"
  api_key: "sk-ant-..."
  model: "claude-3-sonnet-20240229"
```

## Support

- **revChatGPT Issues:** https://github.com/acheong08/ChatGPT/issues
- **poe-api Issues:** https://github.com/ading2210/poe-api/issues
- **Bot Issues:** Check bot logs in `logs/bot.log`

## Disclaimer

**Use at your own risk.** Web authentication methods:
- Violate Terms of Service
- May result in account bans
- Can break without notice
- Are not supported officially

The bot developers are not responsible for any account bans or issues arising from using these methods.

**Recommended:** Use official APIs or local models for legitimate, long-term bot operation.
