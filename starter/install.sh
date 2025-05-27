#!/bin/bash

# Football Bot Systemd Service Installation Script
# This script installs and starts the Football Bot as a systemd service

echo "=== Football Bot Systemd Service Installer ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    exit 1
fi

# Define paths
SERVICE_FILE="/etc/systemd/system/football_bot.service"
SOURCE_SERVICE="$(dirname "$0")/football_bot.service"
FOOTBALL_BOT_DIR="/root/Football_bot"

echo "📁 Checking Football Bot directory..."
if [ ! -d "$FOOTBALL_BOT_DIR" ]; then
    echo "❌ Error: Football Bot directory not found at $FOOTBALL_BOT_DIR"
    exit 1
fi

if [ ! -f "$FOOTBALL_BOT_DIR/orchestrator.py" ]; then
    echo "❌ Error: orchestrator.py not found in $FOOTBALL_BOT_DIR"
    exit 1
fi

echo "✅ Football Bot directory found"

echo "📋 Installing systemd service file..."
if [ ! -f "$SOURCE_SERVICE" ]; then
    echo "❌ Error: Service file not found at $SOURCE_SERVICE"
    exit 1
fi

# Copy service file to systemd directory
cp "$SOURCE_SERVICE" "$SERVICE_FILE"
echo "✅ Service file copied to $SERVICE_FILE"

echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

echo "🔧 Enabling football_bot service..."
systemctl enable football_bot

echo "🚀 Starting football_bot service..."
systemctl start football_bot

echo "⏳ Waiting 3 seconds for service to start..."
sleep 3

echo "📊 Checking service status..."
if systemctl is-active --quiet football_bot; then
    echo "✅ Football Bot service is running successfully!"
    echo
    echo "📋 Service Status:"
    systemctl status football_bot --no-pager -l
    echo
    echo "📝 To view logs in real-time:"
    echo "   journalctl -u football_bot -f"
    echo
    echo "📝 To view orchestrator logs:"
    echo "   tail -f $FOOTBALL_BOT_DIR/orchestrator.log"
    echo
    echo "🛠️  Service Management Commands:"
    echo "   sudo systemctl start football_bot     # Start service"
    echo "   sudo systemctl stop football_bot      # Stop service"
    echo "   sudo systemctl restart football_bot   # Restart service"
    echo "   sudo systemctl status football_bot    # Check status"
    echo "   sudo systemctl disable football_bot   # Disable auto-start"
else
    echo "❌ Error: Football Bot service failed to start"
    echo "📋 Service Status:"
    systemctl status football_bot --no-pager -l
    echo
    echo "📝 Check logs for errors:"
    echo "   journalctl -u football_bot -n 20"
    exit 1
fi

echo
echo "🎉 Installation completed successfully!"
echo "🔄 The Football Bot will now run continuously and restart automatically on boot." 