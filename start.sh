#!/bin/bash

# CineFlix Bot - Quick Start Script
# This script helps you set up the bot quickly

echo "🎬 CineFlix Bot - Quick Start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your credentials:"
    echo "   - BOT_TOKEN"
    echo "   - ADMIN_ID"
    echo "   - CHANNEL_IDS"
    echo "   - MONGODB_URI"
    echo ""
    echo "Press Enter after editing .env file..."
    read
else
    echo "✅ .env file found!"
fi

echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo ""
echo "🚀 Starting CineFlix Bot..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 main.py
