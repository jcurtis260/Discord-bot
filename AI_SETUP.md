# AI Configuration Guide

This bot supports three AI providers for conversations and moderation:

## 1. OpenAI (GPT-4, GPT-3.5)

Best for: High-quality conversations, accurate content moderation

```yaml
ai:
  provider: "openai"
  api_key: "sk-..."  # Your OpenAI API key
  model: "gpt-4"  # or "gpt-3.5-turbo"
```

**Setup:**
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-...`
3. Or add to `bot_config.yaml` as shown above

**Cost:** Pay per token (~$0.03/1K tokens for GPT-4)

## 2. Anthropic (Claude)

Best for: Longer context, nuanced responses

```yaml
ai:
  provider: "anthropic"
  api_key: "sk-ant-..."  # Your Anthropic API key
  model: "claude-3-sonnet-20240229"
```

**Setup:**
1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`
3. Or add to `bot_config.yaml` as shown above

**Models:**
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fastest

**Cost:** Pay per token (~$15/million tokens for Claude 3 Sonnet)

## 3. Local Models (Free, No API)

Best for: Privacy, no API costs, full control

```yaml
ai:
  provider: "local"
  local_model: "microsoft/DialoGPT-medium"
```

**Recommended Models:**

### Small (Fast, Less VRAM)
- `gpt2` - 124M parameters, ~500MB
- `microsoft/DialoGPT-small` - 117M parameters, optimized for chat

### Medium (Balanced)
- `gpt2-medium` - 355M parameters, ~1.5GB
- `microsoft/DialoGPT-medium` - 345M parameters, good quality

### Large (Best Quality, More VRAM)
- `gpt2-large` - 774M parameters, ~3GB
- `microsoft/DialoGPT-large` - 762M parameters, high quality
- `facebook/opt-1.3b` - 1.3B parameters, ~5GB
- `EleutherAI/gpt-neo-1.3B` - 1.3B parameters

**Setup:**
```bash
# Install dependencies
pip install transformers torch sentencepiece

# GPU support (optional, recommended)
# For NVIDIA GPUs:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For AMD GPUs:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
```

**Configuration:**
```yaml
ai:
  provider: "local"
  local_model: "microsoft/DialoGPT-medium"
  temperature: 0.8
  max_tokens: 150  # Lower for faster responses
```

**Hardware Requirements:**
- **CPU Only:** Works but slow (5-30s per response)
- **GPU Recommended:** 
  - Small models: 2GB+ VRAM
  - Medium models: 4GB+ VRAM
  - Large models: 8GB+ VRAM

**First Run:** Model downloads automatically (~500MB-5GB depending on model)

**Pros:**
- ✅ Free (no API costs)
- ✅ Private (runs locally)
- ✅ No rate limits
- ✅ Works offline

**Cons:**
- ❌ Lower quality than GPT-4/Claude
- ❌ Slower responses (especially CPU-only)
- ❌ Requires more setup
- ❌ Uses disk space and RAM/VRAM

## Feature Comparison

| Feature | OpenAI | Anthropic | Local |
|---------|--------|-----------|-------|
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ (GPU) / ⭐ (CPU) |
| **Cost** | $$$ | $$$ | Free |
| **Privacy** | Cloud | Cloud | Local |
| **Setup** | Easy | Easy | Medium |
| **Context Length** | 8K-128K | 200K | 1K-4K |

## AI Conversation Features

All providers support:
- ✅ Full conversations with context
- ✅ Multiple personalities (friendly, professional, humorous, casual)
- ✅ Random engagement
- ✅ Mention and reply detection
- ✅ Per-channel configuration

## AI Moderation Features

Separate from rule-based auto-mod, uses AI to analyze messages:

```yaml
ai:
  moderation:
    enabled: true
    confidence_threshold: 0.7  # 70% confidence required
    action: "warn"  # warn, timeout, kick, or log
    check_toxicity: true  # Hate speech, harassment
    check_spam: true      # Spam detection
    check_nsfw: true      # NSFW content
```

**Commands:**
- `/aimod-enable` - Enable AI moderation
- `/aimod-disable` - Disable AI moderation
- `/aimod-config` - View settings
- `/aimod-threshold <0-100>` - Set confidence threshold
- `/aimod-action <action>` - Set action (warn/timeout/kick/log)
- `/aimod-whitelist add/remove <user>` - Bypass AI mod for specific users
- `/aimod-checks` - Toggle specific checks

**Whitelist:**
Users on the whitelist bypass AI moderation entirely. Useful for:
- Moderators and admins
- Trusted members
- Bots

**How It Works:**
1. User sends a message
2. AI analyzes content for violations
3. Returns confidence score (0-1)
4. If score ≥ threshold, takes action
5. Logs to mod log channel

**Note:** AI moderation works with all providers but requires API access for OpenAI/Anthropic. Local models can be used but may be less accurate.

## Switching Providers

You can switch between providers anytime:

```bash
# In bot_config.yaml, change provider:
ai:
  provider: "local"  # Switch to local
  # or
  provider: "openai"  # Switch to OpenAI
  # or
  provider: "anthropic"  # Switch to Anthropic
```

Restart the bot for changes to take effect.

## Recommendations

**For Production/Public Bots:**
- Use OpenAI (GPT-4 or GPT-3.5-turbo)
- Best quality and reliability
- Budget for API costs

**For Privacy-Focused:**
- Use Local models
- Keep conversations on your hardware
- No data sent to third parties

**For Experimentation:**
- Start with Local (free)
- Upgrade to OpenAI if needed
- Compare quality before committing

**For AI Moderation:**
- OpenAI or Anthropic recommended
- More accurate than local models
- Lower false positive rate

## Troubleshooting

### "AI is not configured"
- Check API key is set in `.env` or `bot_config.yaml`
- Verify provider name is correct

### Local model is slow
- Use GPU if available
- Try a smaller model (gpt2 or DialoGPT-small)
- Reduce `max_tokens` in config

### Out of memory error
- Use a smaller model
- Close other applications
- Reduce batch size

### Model download fails
- Check internet connection
- Verify model name is correct
- Try manual download from HuggingFace

## Support

For more help:
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com/
- Transformers: https://huggingface.co/docs/transformers
- Local Models: https://huggingface.co/models
