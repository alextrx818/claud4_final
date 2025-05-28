# ⚽ Football Bot - Live Match Data Pipeline

A comprehensive 4-stage pipeline system for fetching, processing, and analyzing live football match data from TheSports API.

## 🏗️ Architecture Overview

The Football Bot consists of 4 sequential steps orchestrated by a main controller:

```
Step 1 → Step 2 → Step 3 → Step 4
  ↓        ↓        ↓        ↓
Fetch   Extract   Summary  Final
Data    & Merge   & Group  Format
```

### Pipeline Flow
1. **Step 1**: Fetches live match data from TheSports API
2. **Step 2**: Extracts, merges, and summarizes match information
3. **Step 3**: Creates JSON summaries with categorization and statistics
4. **Step 4**: Generates final formatted summaries with specific field extraction

## 📁 Project Structure

```
Football_bot/
├── orchestrator.py                 # Main pipeline controller
├── Step1_json_fetch_logger/        # Data fetching module
│   ├── step1.py                   # API data fetcher
│   ├── fetch_process.log          # Performance metrics log
│   └── fetch_counter.txt          # Session counter
├── Step2_extract_merge_summarize/  # Data processing module
│   ├── step2.py                   # Data extraction and merging
│   └── step2.json                # Processed match summaries
├── Step3_json_summary/            # Summary generation module
│   ├── step3.py                   # JSON summary generator
│   ├── step3.json                # Categorized match summaries
│   └── step3_summary.log         # Summary logs
├── Step4_json_final_summary/      # Final formatting module
│   ├── step4.py                   # Final summary formatter
│   └── step4.json                # Final formatted summaries
└── README.md                      # This file
```

## 🚀 Features

### Data Collection
- **Live Match Fetching**: Real-time data from TheSports API
- **Comprehensive Coverage**: Match details, odds, team info, competitions
- **Performance Monitoring**: Detailed metrics and logging
- **Session Tracking**: Daily session counters with Eastern Time

### Data Processing
- **Smart Merging**: Combines live data with detailed match information
- **Odds Processing**: Extracts betting odds with time-based filtering
- **Environment Data**: Weather, temperature, wind, humidity information
- **Event Tracking**: Match events and timeline data

### Data Organization
- **Status Categorization**: Live, Upcoming, Finished matches
- **Competition Grouping**: Organized by leagues and tournaments
- **Statistical Analysis**: Odds coverage, event tracking, weather patterns
- **Historical Storage**: Append-only JSON files with complete history

### Output Formats
- **Match Summaries**: Structured match information with scores
- **Betting Odds**: Full-time result, spread, over/under with match timing
- **Environmental Data**: Complete weather and venue information
- **Team Details**: Names, countries, logos, and statistics

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Required packages: `aiohttp`, `psutil`, `zoneinfo`

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Football_bot

# Install dependencies
pip install aiohttp psutil

# Configure API credentials in Step1_json_fetch_logger/step1.py
USER = "your_username"
SECRET = "your_api_secret"
```

## 🎯 Usage

### Running the Pipeline
```bash
# Start the orchestrator (runs continuously every 60 seconds)
python3 orchestrator.py

# Run individual steps for testing
python3 Step1_json_fetch_logger/step1.py
python3 Step2_extract_merge_summarize/step2.py
python3 Step3_json_summary/step3.py
python3 Step4_json_final_summary/step4.py
```

### Output Files
- **step2.json**: Raw processed match data with full details
- **step3.json**: Categorized summaries with statistics
- **step4.json**: Final formatted summaries for consumption
- **fetch_process.log**: Performance metrics and API statistics
- **step3_summary.log**: Summary generation logs

## 📊 Data Structure

### Step 4 Final Output Format
```json
{
  "match_id": "abc123",
  "competition_id": "xyz789",
  "competition": "Premier League",
  "country": "England",
  "home_team": "Team A",
  "away_team": "Team B",
  "score": "2 - 1 (HT: 1 - 0)",
  "status": "Live",
  "full_time_result": {
    "home": 2.5,
    "draw": 3.2,
    "away": 2.8,
    "match_time": "45"
  },
  "spread": {
    "handicap": -0.5,
    "home": 1.9,
    "away": 1.9,
    "match_time": "45"
  },
  "over_under": {
    "2.5": {
      "line": 2.5,
      "over": 1.8,
      "under": 2.0,
      "match_time": "45"
    }
  },
  "environment": {
    "weather_description": "Clear",
    "temperature_value": 22.0,
    "wind_description": "Light Breeze",
    "humidity_value": 65.0
  }
}
```

## ⚙️ Configuration

### API Settings
- **Base URL**: `https://api.thesports.com/v1/football`
- **Endpoints**: Live matches, details, odds, teams, competitions
- **Rate Limiting**: Built-in response time monitoring
- **Caching**: Team and competition data caching

### Timing Configuration
- **Pipeline Cycle**: 60 seconds
- **Odds Time Window**: Minutes 3-6 for stability
- **Timezone**: Eastern Time (America/New_York)
- **Session Reset**: Daily at midnight Eastern

### Logging Configuration
- **Orchestrator**: Centralized logging with timestamps
- **Step 1**: Performance metrics to fetch_process.log
- **Step 3**: Summary logs to step3_summary.log
- **Format**: MM/DD/YYYY HH:MM:SS AM/PM EDT

## 🔧 Monitoring & Debugging

### Performance Metrics
- API call statistics and response times
- Memory and CPU usage tracking
- Data volume and processing efficiency
- Cache hit rates for teams/competitions

### Log Analysis
```bash
# Monitor orchestrator logs
tail -f orchestrator_output.log

# Check performance metrics
tail -f Step1_json_fetch_logger/fetch_process.log

# View summary statistics
tail -f Step3_json_summary/step3_summary.log
```

### Health Checks
```bash
# Check file update timestamps
ls -la Step*/*.json

# Verify data flow
python3 -c "import json; data=json.load(open('Step4_json_final_summary/step4.json')); print(f'Latest: {data[\"total_entries\"]} entries')"
```

## 🐛 Troubleshooting

### Common Issues
1. **API Rate Limiting**: Check response times in fetch_process.log
2. **File Permissions**: Ensure write access to all directories
3. **Memory Usage**: Monitor with performance metrics
4. **Data Corruption**: Check JSON file validity

### Debug Mode
```bash
# Run individual steps with debug output
python3 -c "import asyncio; from step1 import step1_main; print(asyncio.run(step1_main()))"
```

## 📈 Performance

### Typical Metrics
- **Matches Processed**: 10-20 live matches per cycle
- **API Calls**: 50-100 calls per cycle
- **Processing Time**: 15-30 seconds per cycle
- **Data Volume**: 1-2 MB per cycle
- **Memory Usage**: 50-100 MB peak

### Optimization Features
- **Async Processing**: Non-blocking API calls
- **Data Caching**: Reduced redundant API calls
- **Efficient JSON**: Structured data with minimal overhead
- **Time-based Filtering**: Optimal odds data selection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 API Documentation

For TheSports API documentation and credentials, visit: https://api.thesports.com

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Open an issue on GitHub
4. Contact the development team

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅