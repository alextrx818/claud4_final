#!/bin/bash

# Install Football Bot Pipeline as systemd service

echo "Installing Football Bot Pipeline Service..."

# Copy service file to systemd directory
sudo cp pipeline.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable pipeline.service

echo "Service installed successfully!"
echo "To start the service: sudo systemctl start pipeline.service"
echo "To check status: sudo systemctl status pipeline.service"
echo "To view logs: sudo journalctl -u pipeline.service -f" 