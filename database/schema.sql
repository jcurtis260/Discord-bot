-- Discord Bot Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Guild (Server) Configuration
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(10) DEFAULT '/',
    
    -- Feature toggles
    xp_enabled BOOLEAN DEFAULT TRUE,
    ai_enabled BOOLEAN DEFAULT FALSE,
    economy_enabled BOOLEAN DEFAULT TRUE,
    giveaways_enabled BOOLEAN DEFAULT TRUE,
    games_enabled BOOLEAN DEFAULT TRUE,
    
    -- Channels
    welcome_channel BIGINT,
    farewell_channel BIGINT,
    log_channel BIGINT,
    starboard_channel BIGINT,
    
    -- Messages
    welcome_message TEXT,
    farewell_message TEXT,
    
    -- XP Settings
    xp_rate INT DEFAULT 15,
    xp_cooldown INT DEFAULT 60,
    voice_xp_rate INT DEFAULT 5,
    announce_level_up BOOLEAN DEFAULT TRUE,
    
    -- AI Settings
    ai_personality VARCHAR(50) DEFAULT 'friendly',
    ai_engagement_rate FLOAT DEFAULT 0.1,
    
    -- Economy Settings
    currency_name VARCHAR(50) DEFAULT 'Credits',
    currency_emoji VARCHAR(20) DEFAULT '💰',
    starting_balance BIGINT DEFAULT 100,
    daily_reward BIGINT DEFAULT 50,
    weekly_reward BIGINT DEFAULT 500,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (Discord Members)
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    discriminator VARCHAR(10),
    avatar_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guild Members (User per Guild)
CREATE TABLE IF NOT EXISTS guild_members (
    guild_id BIGINT,
    user_id BIGINT,
    
    -- XP and Leveling
    xp BIGINT DEFAULT 0,
    level INT DEFAULT 0,
    message_count INT DEFAULT 0,
    voice_time INT DEFAULT 0,
    last_xp_gain TIMESTAMP,
    
    -- Economy
    balance BIGINT DEFAULT 0,
    total_earned BIGINT DEFAULT 0,
    total_spent BIGINT DEFAULT 0,
    last_daily TIMESTAMP,
    last_weekly TIMESTAMP,
    daily_streak INT DEFAULT 0,
    
    -- Timestamps
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (guild_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================================
-- MODERATION TABLES
-- ============================================================================

-- Infractions (Warnings, Mutes, Bans, Kicks)
CREATE TABLE IF NOT EXISTS infractions (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    type VARCHAR(50) NOT NULL, -- warn, mute, kick, ban
    reason TEXT,
    duration INT, -- in seconds, NULL for permanent
    expires_at TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_infractions_guild_user ON infractions(guild_id, user_id);
CREATE INDEX idx_infractions_active ON infractions(active) WHERE active = TRUE;

-- Moderation Log
CREATE TABLE IF NOT EXISTS mod_log (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL,
    moderator_id BIGINT,
    target_user_id BIGINT,
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mod_log_guild ON mod_log(guild_id);
CREATE INDEX idx_mod_log_created_at ON mod_log(created_at DESC);

-- ============================================================================
-- LEVELING TABLES
-- ============================================================================

-- Role Rewards
CREATE TABLE IF NOT EXISTS role_rewards (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    required_level INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (guild_id, role_id),
    UNIQUE (guild_id, required_level)
);

-- ============================================================================
-- AI TABLES
-- ============================================================================

-- AI Conversation Context
CREATE TABLE IF NOT EXISTS ai_context (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_history JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (guild_id, channel_id)
);

CREATE INDEX idx_ai_context_updated ON ai_context(last_updated);

-- AI Channel Settings
CREATE TABLE IF NOT EXISTS ai_channels (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    engagement_rate FLOAT DEFAULT 0.1,
    personality VARCHAR(50),
    
    PRIMARY KEY (guild_id, channel_id)
);

-- ============================================================================
-- ECONOMY TABLES
-- ============================================================================

-- Shop Items
CREATE TABLE IF NOT EXISTS shop_items (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price BIGINT NOT NULL,
    stock INT, -- NULL for unlimited
    item_type VARCHAR(50) NOT NULL, -- role, perk, physical, cosmetic
    item_data JSONB,
    image_url TEXT,
    purchasable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shop_items_guild ON shop_items(guild_id);
CREATE INDEX idx_shop_items_purchasable ON shop_items(guild_id, purchasable);

-- User Inventory
CREATE TABLE IF NOT EXISTS user_inventory (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    item_id INT REFERENCES shop_items(id) ON DELETE CASCADE,
    quantity INT DEFAULT 1,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (guild_id, user_id, item_id)
);

CREATE INDEX idx_inventory_user ON user_inventory(guild_id, user_id);

-- Transaction History
CREATE TABLE IF NOT EXISTS economy_transactions (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    amount BIGINT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- earn, spend, transfer, daily, weekly
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_transactions_user ON economy_transactions(guild_id, user_id);
CREATE INDEX idx_transactions_created_at ON economy_transactions(created_at DESC);

-- ============================================================================
-- GIVEAWAY TABLES
-- ============================================================================

-- Giveaways
CREATE TABLE IF NOT EXISTS giveaways (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_id BIGINT,
    prize TEXT NOT NULL,
    winner_count INT DEFAULT 1,
    duration INT NOT NULL, -- in seconds
    ends_at TIMESTAMP NOT NULL,
    created_by BIGINT NOT NULL,
    requirements JSONB, -- entry requirements
    status VARCHAR(20) DEFAULT 'active', -- active, ended, cancelled
    emoji VARCHAR(20) DEFAULT '🎉',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_giveaways_guild ON giveaways(guild_id);
CREATE INDEX idx_giveaways_status ON giveaways(status);
CREATE INDEX idx_giveaways_ends_at ON giveaways(ends_at) WHERE status = 'active';

-- Giveaway Entries
CREATE TABLE IF NOT EXISTS giveaway_entries (
    id SERIAL PRIMARY KEY,
    giveaway_id INT REFERENCES giveaways(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    entries INT DEFAULT 1, -- for weighted entries
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (giveaway_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_giveaway_entries_giveaway ON giveaway_entries(giveaway_id);

-- Giveaway Winners
CREATE TABLE IF NOT EXISTS giveaway_winners (
    id SERIAL PRIMARY KEY,
    giveaway_id INT REFERENCES giveaways(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    claimed BOOLEAN DEFAULT FALSE,
    notified BOOLEAN DEFAULT FALSE,
    won_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================================
-- GAMES TABLES
-- ============================================================================

-- Trivia Questions
CREATE TABLE IF NOT EXISTS trivia_questions (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT, -- NULL for global questions
    category VARCHAR(100) NOT NULL,
    difficulty VARCHAR(20) NOT NULL, -- easy, medium, hard
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    incorrect_answers TEXT[], -- Array of wrong answers
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trivia_category ON trivia_questions(category);
CREATE INDEX idx_trivia_difficulty ON trivia_questions(difficulty);

-- Trivia Leaderboard
CREATE TABLE IF NOT EXISTS trivia_stats (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    questions_answered INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    total_points INT DEFAULT 0,
    
    PRIMARY KEY (guild_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Game Statistics
CREATE TABLE IF NOT EXISTS game_stats (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    game_type VARCHAR(50) NOT NULL, -- slots, blackjack, coinflip, roulette, etc.
    games_played INT DEFAULT 0,
    games_won INT DEFAULT 0,
    total_wagered BIGINT DEFAULT 0,
    total_won BIGINT DEFAULT 0,
    
    PRIMARY KEY (guild_id, user_id, game_type),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================================
-- CUSTOM COMMANDS TABLES
-- ============================================================================

-- Custom Commands
CREATE TABLE IF NOT EXISTS custom_commands (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    command_name VARCHAR(100) NOT NULL,
    response TEXT NOT NULL,
    response_type VARCHAR(50) DEFAULT 'text', -- text, embed, image
    embed_data JSONB,
    required_role BIGINT,
    usage_count INT DEFAULT 0,
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (guild_id, command_name)
);

CREATE INDEX idx_custom_commands_guild ON custom_commands(guild_id);

-- ============================================================================
-- REACTION ROLES TABLES
-- ============================================================================

-- Reaction Roles
CREATE TABLE IF NOT EXISTS reaction_roles (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    emoji VARCHAR(100) NOT NULL,
    role_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (message_id, emoji)
);

CREATE INDEX idx_reaction_roles_message ON reaction_roles(message_id);

-- ============================================================================
-- OTHER FEATURES TABLES
-- ============================================================================

-- Reminders
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    guild_id BIGINT,
    message TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    recurring BOOLEAN DEFAULT FALSE,
    interval_seconds INT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_reminders_remind_at ON reminders(remind_at) WHERE completed = FALSE;

-- Birthdays
CREATE TABLE IF NOT EXISTS birthdays (
    user_id BIGINT PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    birth_month INT NOT NULL CHECK (birth_month BETWEEN 1 AND 12),
    birth_day INT NOT NULL CHECK (birth_day BETWEEN 1 AND 31),
    birth_year INT, -- Optional
    show_age BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_birthdays_guild ON birthdays(guild_id);
CREATE INDEX idx_birthdays_date ON birthdays(birth_month, birth_day);

-- Starboard
CREATE TABLE IF NOT EXISTS starboard_messages (
    guild_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    starboard_message_id BIGINT,
    star_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (guild_id, message_id)
);

CREATE INDEX idx_starboard_count ON starboard_messages(star_count DESC);

-- ============================================================================
-- DASHBOARD TABLES
-- ============================================================================

-- Dashboard Users
CREATE TABLE IF NOT EXISTS dashboard_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer', -- admin, moderator, viewer
    two_fa_secret VARCHAR(255),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dashboard Sessions
CREATE TABLE IF NOT EXISTS dashboard_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INT REFERENCES dashboard_users(id) ON DELETE CASCADE,
    token VARCHAR(500),
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user ON dashboard_sessions(user_id);
CREATE INDEX idx_sessions_expires ON dashboard_sessions(expires_at);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    dashboard_user_id INT REFERENCES dashboard_users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id VARCHAR(255),
    changes JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);

-- ============================================================================
-- RED COG COMPATIBILITY TABLES
-- ============================================================================

-- Red Cog Registry
CREATE TABLE IF NOT EXISTS red_cogs (
    id SERIAL PRIMARY KEY,
    cog_name VARCHAR(100) UNIQUE NOT NULL,
    repository_url TEXT,
    version VARCHAR(50),
    enabled BOOLEAN DEFAULT TRUE,
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Red Config Storage (Emulation)
CREATE TABLE IF NOT EXISTS red_config (
    id SERIAL PRIMARY KEY,
    cog_name VARCHAR(100) NOT NULL,
    scope VARCHAR(50) NOT NULL, -- global, guild, member, etc.
    scope_id BIGINT,
    config_key VARCHAR(255) NOT NULL,
    config_value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (cog_name, scope, scope_id, config_key)
);

CREATE INDEX idx_red_config_cog ON red_config(cog_name);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_guild_config_updated_at
    BEFORE UPDATE ON guild_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_custom_commands_updated_at
    BEFORE UPDATE ON custom_commands
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dashboard_users_updated_at
    BEFORE UPDATE ON dashboard_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert some default trivia questions (optional)
-- Will be populated separately via seed file
