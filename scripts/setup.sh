#!/bin/bash

# Discord Bot Setup Script

echo "🤖 Discord Bot Setup"
echo "===================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your bot token and other credentials"
    echo ""
fi

# Check if config exists
if [ ! -f config/bot_config.yaml ]; then
    echo "Creating bot config from template..."
    cp config/bot_config.example.yaml config/bot_config.yaml
    echo "✅ Created bot_config.yaml"
    echo "⚠️  Please edit config/bot_config.yaml and configure your bot"
    echo ""
fi

# Create logs directory
mkdir -p logs
echo "✅ Created logs directory"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Docker detected!"
    echo "You can start the bot with: docker-compose up -d"
    echo ""
else
    echo ""
    echo "📦 Docker not found. Setting up locally..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        echo "Python $PYTHON_VERSION detected"
        
        # Create virtual environment
        if [ ! -d "bot/venv" ]; then
            echo "Creating virtual environment..."
            cd bot
            python3 -m venv venv
            source venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
            cd ..
            echo "✅ Virtual environment created"
        fi
    else
        echo "❌ Python 3.11+ is required"
        exit 1
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Discord bot token"
echo "2. Edit config/bot_config.yaml with your settings"
echo "3. Create the database (see README.md for instructions)"
echo "4. Start the bot:"
echo "   - With Docker: docker-compose up -d"
echo "   - Without Docker: cd bot && source venv/bin/activate && python main.py"
echo ""
