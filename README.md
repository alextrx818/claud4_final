# Football Bot

A real-time football (soccer) match data aggregation and processing system that fetches live match data, processes it through multiple stages, and generates organized JSON summaries.

## Overview

The Football Bot operates as a three-stage pipeline:

1. **Step 1 - Data Fetching**: Fetches live match data from TheSports API
2. **Step 2 - Extract, Merge & Summarize**: Processes raw data and enriches it with team, competition, and odds information
3. **Step 3 - JSON Summary**: Organizes and categorizes matches, generating final formatted output

## Project Structure

```
Football_bot/
├── orchestrator.py                    # Main pipeline orchestrator
├── Step1_json_fetch_logger/          # Data fetching module
│   ├── step1.py                      # Main fetch logic
│   ├── process_logger.py             # Legacy logger (optional)
│   └── cron_timer.py                 # Legacy timer (optional)
├── Step2_extract_merge_summarize/    # Data processing module
│   └── step2.py                      # Extract and merge logic
├── Step3_json_summary/               # Summary generation module
│   └── step3.py                      # JSON formatting logic
└── starter/                          # Service management scripts
    ├── install.sh                    # Install as systemd service
    ├── start.sh                      # Start the service
    ├── stop.sh                       # Stop the service
    └── uninstall.sh                  # Remove the service
```

## Installation

### Prerequisites

- Python 3.8+
- pip
- systemd (for service installation)

### Required Python Packages

```bash
pip install aiohttp asyncio psutil
```

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd Football_bot
```

2. Run directly:
```bash
python3 orchestrator.py
```

### Install as System Service

For production deployment, install as a systemd service:

```bash
cd starter
sudo ./install.sh
```

This will:
- Create a systemd service that runs automatically
- Start on system boot
- Restart on failures
- Log to system journal

## Usage

### Running Manually

```bash
python3 orchestrator.py
```

The orchestrator will:
- Run the complete pipeline every 60 seconds
- Log progress to console
- Save data to JSON files in each step's directory

### Service Management

```bash
# Start the service
./starter/start.sh

# Stop the service
./starter/stop.sh

# Check service status
systemctl status football_bot

# View logs
journalctl -u football_bot -f
```

## Data Flow

1. **Step 1** fetches from TheSports API:
   - Live matches
   - Match details
   - Odds history
   - Team information
   - Competition details

2. **Step 2** processes and enriches:
   - Merges data from multiple endpoints
   - Extracts scores, odds, and events
   - Normalizes team and competition info
   - Saves to `step2.json`

3. **Step 3** organizes and summarizes:
   - Groups matches by status (live/upcoming/finished)
   - Groups by competition
   - Generates statistics
   - Saves to `step3.json`

## Output Files

- `Step1_json_fetch_logger/fetch_process.log` - API fetch metrics
- `Step2_extract_merge_summarize/step2.json` - Processed match data
- `Step3_json_summary/step3.json` - Final organized output
- `Step3_json_summary/step3_summary.log` - Summary statistics

## Configuration

API credentials are currently hardcoded in `step1.py`. For production use, consider:
- Moving to environment variables
- Using a configuration file
- Implementing secure credential storage

## Logging

All timestamps use US Eastern Time (ET) in MM/DD/YYYY format.

## Development

To modify the pipeline:

1. Each step is independent and can be tested separately
2. Steps communicate through return values, not queues
3. The orchestrator manages the flow between steps
4. Add new steps by:
   - Creating a new directory `Step4_<purpose>/`
   - Adding an async function that accepts data and returns results
   - Importing and calling it in `orchestrator.py`

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]