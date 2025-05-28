#!/bin/bash

# Football Bot Systemd Service Uninstaller Script
# This script stops and removes the Football Bot systemd service

echo "=== Football Bot Systemd Service Uninstaller ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    exit 1
fi

# Define paths
SERVICE_FILE="/etc/systemd/system/football_bot.service"

echo "🛑 Stopping football_bot service..."
if systemctl is-active --quiet football_bot; then
    systemctl stop football_bot
    echo "✅ Service stopped"
else
    echo "ℹ️  Service was not running"
fi

echo "🔧 Disabling football_bot service..."
if systemctl is-enabled --quiet football_bot; then
    systemctl disable football_bot
    echo "✅ Service disabled"
else
    echo "ℹ️  Service was not enabled"
fi

echo "🗑️  Removing service file..."
if [ -f "$SERVICE_FILE" ]; then
    rm "$SERVICE_FILE"
    echo "✅ Service file removed from $SERVICE_FILE"
else
    echo "ℹ️  Service file was not found"
fi

echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

echo "🧹 Resetting failed state (if any)..."
systemctl reset-failed football_bot 2>/dev/null || true

echo
echo "✅ Football Bot systemd service has been completely removed"
echo "ℹ️  Note: The Football Bot files and logs remain in /root/Football_bot"
echo "ℹ️  Note: Any existing cron jobs are not affected by this uninstall"
echo
echo "🔄 To reinstall the service, run:"
echo "   sudo ./install.sh" 