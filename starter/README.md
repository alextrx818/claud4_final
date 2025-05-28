# FOOTBALL BOT STARTER

## 📁 FOLDER PURPOSE

The `starter` folder contains **systemd service configuration** for running the Football Bot as a **production system service**. This is the **recommended way** to run the Football Bot in production environments.

### 🆚 Systemd vs Cron

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **Systemd Service** | Production | Auto-restart, better logging, service management | Requires root setup |
| **Cron Job** | Development/Testing | Simple setup | No auto-restart, limited logging |

---

## 📋 FILES IN THIS FOLDER

### `football_bot.service`
- **Systemd unit file** that defines how the Football Bot service runs
- Configures automatic restart, logging, and user permissions
- **Pre-configured** for the current system paths

### `install.sh`
- **Automated installation script** for the systemd service
- Copies service file, enables auto-start, and starts the service
- **Must be run as root** (`sudo ./install.sh`)

### `uninstall.sh`
- **Automated removal script** for the systemd service
- Stops service, disables auto-start, and removes service file
- **Must be run as root** (`sudo ./uninstall.sh`)

---

## 🚀 HOW TO START THE PROGRAM

### 1 — Install Service (ONE-TIME)

```bash
# Navigate to the starter folder
cd /root/Football_bot/starter

# Make scripts executable (first time only)
chmod +x install.sh uninstall.sh start.sh stop.sh

# Run the installer (requires sudo/root; ONE-TIME)
sudo ./install.sh
```

### 2 — Daily Usage (Start / Stop / Status)

Once installed you rarely need to touch `install.sh` again.  Instead use the tiny convenience wrappers:

```bash
# Start the service manually (if not already running)
./start.sh

# Stop the service
./stop.sh

# Check status (built-in systemd)
sudo systemctl status football_bot
```

These wrappers simply execute `systemctl start|stop football_bot` for you.

### 3 — Manual Installation (Alternative)

```bash
# Copy service file
sudo cp /root/Football_bot/starter/football_bot.service /etc/systemd/system/
# Reload & enable
sudo systemctl daemon-reload
sudo systemctl enable football_bot
sudo systemctl start football_bot
```

---

## 🛠️ SERVICE MANAGEMENT

### Basic Commands

```bash
# Start the service
sudo systemctl start football_bot

# Stop the service
sudo systemctl stop football_bot

# Restart the service
sudo systemctl restart football_bot

# Check service status
sudo systemctl status football_bot

# Enable auto-start on boot
sudo systemctl enable football_bot

# Disable auto-start on boot
sudo systemctl disable football_bot
```

### Monitoring & Logs

```bash
# View real-time system logs
sudo journalctl -u football_bot -f

# View last 50 log entries
sudo journalctl -u football_bot -n 50

# View orchestrator application logs
tail -f /root/Football_bot/orchestrator.log

# Check if service is running
sudo systemctl is-active football_bot

# Check if service is enabled for auto-start
sudo systemctl is-enabled football_bot
```

---

## 🔧 SERVICE CONFIGURATION

### Current Configuration (`football_bot.service`)

```ini
[Unit]
Description=Football Bot Orchestrator
After=network.target                    # Start after network is available

[Service]
Type=simple                            # Simple long-running process
User=root                              # Run as root user
WorkingDirectory=/root/Football_bot    # Set working directory
ExecStart=/usr/bin/python3 /root/Football_bot/orchestrator.py
Restart=always                         # Always restart on failure
RestartSec=5                          # Wait 5 seconds before restart
StandardOutput=append:/root/Football_bot/orchestrator.log
StandardError=inherit                  # Inherit error output

[Install]
WantedBy=multi-user.target            # Start in multi-user mode
```

### Key Features

- ✅ **Automatic restart** on failure or crash
- ✅ **Auto-start on boot** (when enabled)
- ✅ **Proper logging** to both systemd journal and orchestrator.log
- ✅ **Network dependency** - waits for network before starting
- ✅ **5-second restart delay** to prevent rapid restart loops

---

## 🔍 TROUBLESHOOTING

### Service Won't Start

```bash
# Check detailed status
sudo systemctl status football_bot -l

# Check recent logs
sudo journalctl -u football_bot -n 20

# Check if orchestrator.py exists
ls -la /root/Football_bot/orchestrator.py

# Check Python path
which python3
```

### Service Keeps Restarting

```bash
# Check application logs
tail -20 /root/Football_bot/orchestrator.log

# Check for Python errors
sudo journalctl -u football_bot | grep -i error

# Test orchestrator manually
cd /root/Football_bot && python3 orchestrator.py
```

### Permission Issues

```bash
# Check file ownership
ls -la /root/Football_bot/

# Fix ownership if needed
sudo chown -R root:root /root/Football_bot/

# Check service file permissions
ls -la /etc/systemd/system/football_bot.service
```

---

## 🎯 QUICK REFERENCE

| Task | Command |
|------|---------|
| **Install Service** | `sudo ./install.sh` |
| **Uninstall Service** | `sudo ./uninstall.sh` |
| **Start Service** | `sudo systemctl start football_bot` |
| **Stop Service** | `sudo systemctl stop football_bot` |
| **Check Status** | `sudo systemctl status football_bot` |
| **View Logs** | `sudo journalctl -u football_bot -f` |
| **Enable Auto-Start** | `sudo systemctl enable football_bot` |
| **Disable Auto-Start** | `sudo systemctl disable football_bot` |

---

**🎉 The systemd service provides a robust, production-ready way to run the Football Bot with automatic restart, proper logging, and easy management!** 