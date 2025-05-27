# Football Bot - Live Match Data Pipeline

A Python-based data pipeline that fetches, processes, and summarizes live football match data from TheSports API.

## Overview

This bot runs a continuous pipeline that:
1. Fetches live match data from TheSports API
2. Extracts and enriches match information with team, competition, and odds data
3. Summarizes and groups matches for easy consumption

## Architecture

The pipeline consists of 3 main steps:

### Step 1: Data Fetcher (`Step1_json_fetch_logger/`)
- Fetches live matches from TheSports API
- Retrieves detailed match information, odds history, team info, and competition data
- Logs performance metrics and API usage

### Step 2: Extract, Merge & Summarize (`Step2_extract_merge_summarize/`)
- Processes raw API responses
- Merges data from multiple endpoints
- Extracts odds with intelligent time filtering (3-6 minute window)
- Creates structured match summaries

### Step 3: JSON Summary (`Step3_json_summary/`)
- Groups matches by competition and status
- Creates statistical summaries
- Prepares data for final presentation

## Features

- **Continuous Operation**: Runs every 60 seconds to fetch latest data
- **Smart Odds Extraction**: Filters odds to early match minutes (3-6) for better accuracy
- **Comprehensive Data**: Includes scores, odds, weather, events, and more
- **Performance Logging**: Tracks API calls, response times, and data volumes
- **Error Handling**: Graceful error recovery and logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/alextrx818/claud4_final.git
cd claud4_final/Football_bot
```

2. Install dependencies:
```bash
pip install aiohttp psutil
```

## Usage

Run the orchestrator to start the pipeline:

```bash
python3 orchestrator.py
```

The bot will:
- Fetch live match data every 60 seconds
- Save outputs to JSON files in each step's directory
- Log all activities to console and files

## Output Files

- `Step1_json_fetch_logger/fetch_process.log` - API performance metrics
- `Step2_extract_merge_summarize/step2.json` - Processed match summaries
- `Step3_json_summary/step3.json` - Grouped and summarized data

## Configuration

API credentials are currently hardcoded in `step1.py`:
```python
USER = "thenecpt"
SECRET = "0c55322e8e196d6ef9066fa4252cf386"
```

## Data Structure

Each match summary includes:
- Match identification and status
- Team information (names, scores, logos)
- Competition details
- Odds data (full-time result, spread, over/under)
- Environmental conditions (weather, temperature, etc.)
- Match events (goals, cards, substitutions)

## Requirements

- Python 3.8+
- aiohttp
- psutil
- zoneinfo (Python 3.9+)

## License

This project is provided as-is for educational purposes.