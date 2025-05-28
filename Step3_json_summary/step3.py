#!/usr/bin/env python3
"""
Step 3 - JSON Summary Generator
Generates JSON summaries of matches with structured field organization

This module creates a JSON representation of all match data, making it easier to:
1. Reference exact field paths for alert criteria
2. Debug which fields are available for scanning
3. Ensure consistent data representation between steps

The generated JSON is saved to step3.json and logged to step3_summary.log
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Use the same timezone as other modules
TZ = ZoneInfo("America/New_York")

# Path constants
BASE_DIR = Path(__file__).parent
SUMMARY_JSON_FILE = BASE_DIR / "step3.json"
SUMMARY_LOG_FILE = BASE_DIR / "step3_summary.log"

def setup_summary_logger():
    """Set up a logger for the summary data"""
    logger = logging.getLogger("step3_summary")
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers to prevent duplicates
    while logger.handlers:
        logger.handlers.pop()
    
    # Create a file handler
    file_handler = logging.FileHandler(SUMMARY_LOG_FILE)
    file_handler.setLevel(logging.INFO)
    
    # Create a simple formatter with just the message
    fmt = logging.Formatter("%(message)s")
    file_handler.setFormatter(fmt)
    
    logger.addHandler(file_handler)
    
    return logger

def get_eastern_time():
    """Get current time in Eastern timezone with MM/DD/YYYY format"""
    now = datetime.now(TZ)
    return now.strftime("%m/%d/%Y %I:%M:%S %p %Z")

def organize_match_summary(match):
    """
    Organize match data into a clean, structured format
    This takes the already processed data from step2 and reorganizes it
    """
    # The match data from step2 is already well-structured, so we'll enhance it
    summary = {
        "match_id": match.get("match_id"),
        "fetched_at": match.get("fetched_at"),
        
        # Basic match info
        "match_info": {
            "status": match.get("status", {}),
            "venue": match.get("venue"),
            "referee": match.get("referee"),
            "neutral": match.get("neutral"),
            "start_time": match.get("start_time"),
        },
        
        # Teams with scores
        "teams": match.get("teams", {}),
        
        # Competition details
        "competition": match.get("competition", {}),
        
        # Round/Stage info
        "round": match.get("round", {}),
        
        # Coverage info
        "coverage": match.get("coverage", {}),
        
        # Odds summary
        "odds_summary": extract_odds_summary(match.get("odds", {})),
        
        # Full odds data
        "odds_detailed": match.get("odds", {}),
        
        # Environment/Weather
        "environment": match.get("environment", {}),
        
        # Match events
        "events": match.get("events", []),
    }
    
    return summary

def extract_odds_summary(odds):
    """Extract a summary of the most important odds"""
    summary = {
        "has_odds": False,
        "full_time_result": odds.get("full_time_result", {}),
        "primary_over_under": odds.get("primary_over_under", {}),
        "spread": odds.get("spread", {}),
        "both_teams_to_score": odds.get("both_teams_to_score", {})
    }
    
    # Check if we have any odds data
    if (summary["full_time_result"].get("home") is not None or
        summary["primary_over_under"].get("line") is not None or
        summary["spread"].get("handicap") is not None):
        summary["has_odds"] = True
    
    return summary

def categorize_matches(matches):
    """Categorize matches by status and competition"""
    categories = {
        "by_status": {
            "live": [],
            "upcoming": [],
            "finished": [],
            "other": []
        },
        "by_competition": {},
        "statistics": {
            "total": len(matches),
            "with_odds": 0,
            "with_events": 0,
            "by_weather": {}
        }
    }
    
    for match_id, match in matches.items():
        # Categorize by status
        status_id = match.get("status", {}).get("id")
        if status_id in [2, 3, 4, 5, 6, 7]:  # Live statuses
            categories["by_status"]["live"].append(match_id)
        elif status_id == 1:  # Upcoming
            categories["by_status"]["upcoming"].append(match_id)
        elif status_id in [8, 9, 10, 11, 12, 13]:  # Finished
            categories["by_status"]["finished"].append(match_id)
        else:
            categories["by_status"]["other"].append(match_id)
        
        # Categorize by competition
        comp_name = match.get("competition", {}).get("name", "Unknown")
        if comp_name not in categories["by_competition"]:
            categories["by_competition"][comp_name] = []
        categories["by_competition"][comp_name].append(match_id)
        
        # Statistics
        if match.get("odds", {}).get("full_time_result", {}).get("home") is not None:
            categories["statistics"]["with_odds"] += 1
        
        if match.get("events", []):
            categories["statistics"]["with_events"] += 1
        
        # Weather statistics
        weather_desc = match.get("environment", {}).get("weather_description", "Unknown")
        if weather_desc not in categories["statistics"]["by_weather"]:
            categories["statistics"]["by_weather"][weather_desc] = 0
        categories["statistics"]["by_weather"][weather_desc] += 1
    
    return categories

def generate_summary_json(step2_data):
    """Generate comprehensive summary JSON data"""
    matches = step2_data.get("matches", {})
    
    # Process each match
    processed_matches = {}
    for match_id, match in matches.items():
        processed_matches[match_id] = organize_match_summary(match)
    
    # Generate categories and statistics
    categories = categorize_matches(matches)
    
    # Create the final summary structure
    summary_data = {
        "generated_at": get_eastern_time(),
        "source_timestamp": step2_data.get("timestamp"),
        "match_count": len(matches),
        "categories": categories,
        "matches": processed_matches
    }
    
    return summary_data

def write_summary_json(step2_data):
    """Write the summary JSON to file and log"""
    logger = setup_summary_logger()
    
    # Generate the summary data
    summary_data = generate_summary_json(step2_data)
    
    # Append to JSON file (build history)
    try:
        # Load existing data if file exists
        existing_data = {"history": []}
        if os.path.exists(SUMMARY_JSON_FILE):
            try:
                with open(SUMMARY_JSON_FILE, 'r') as f:
                    existing_data = json.load(f)
                    if "history" not in existing_data:
                        existing_data = {"history": [existing_data] if existing_data else []}
            except (json.JSONDecodeError, Exception):
                existing_data = {"history": []}
        
        # Add current summary to history
        existing_data["history"].append(summary_data)
        
        # Update metadata
        existing_data["last_updated"] = summary_data.get("generated_at")
        existing_data["total_entries"] = len(existing_data["history"])
        existing_data["latest_match_count"] = summary_data.get("match_count", 0)
        
        # Save updated data
        with open(SUMMARY_JSON_FILE, 'w') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully appended summary JSON with {summary_data['match_count']} matches to history")
    except Exception as e:
        logger.error(f"Error writing summary JSON file: {e}")
        return None
    
    # Create header for log
    header = "\n" + "="*80 + "\n"
    header += f"STEP 3 SUMMARY - {get_eastern_time()}\n"
    header += "="*80 + "\n"
    header += f"Total Matches: {summary_data['match_count']}\n"
    header += f"Live: {len(summary_data['categories']['by_status']['live'])}\n"
    header += f"Upcoming: {len(summary_data['categories']['by_status']['upcoming'])}\n"
    header += f"Finished: {len(summary_data['categories']['by_status']['finished'])}\n"
    header += f"With Odds: {summary_data['categories']['statistics']['with_odds']}\n"
    header += f"With Events: {summary_data['categories']['statistics']['with_events']}\n"
    header += "="*80 + "\n\n"
    
    # Log the summary (append to log file)
    try:
        with open(SUMMARY_LOG_FILE, 'a') as f:
            f.write(header)
            # Write a condensed version to the log
            f.write(f"Competitions ({len(summary_data['categories']['by_competition'])}):\n")
            for comp, match_ids in summary_data['categories']['by_competition'].items():
                f.write(f"  - {comp}: {len(match_ids)} matches\n")
            f.write("\n")
    except Exception as e:
        logger.error(f"Error writing to summary log: {e}")
    
    return summary_data

# Main async function to be called from orchestrator
async def json_summary(summaries):
    """
    Main entry point for Step 3 - called from orchestrator
    
    Args:
        summaries: List of match summaries from Step 2
    
    Returns:
        Dictionary containing the processed summary data
    """
    print("Step 3: Starting json_summary...")
    
    # Since we receive summaries as a list, we need to check if it's already
    # the step2 data structure or if we need to load it
    if isinstance(summaries, list):
        # If it's a list, we need to load the step2.json file
        step2_file = Path(__file__).parent.parent / "Step2_extract_merge_summarize" / "step2.json"
        
        try:
            with open(step2_file, 'r') as f:
                file_data = json.load(f)
            
            # Handle history structure - get the latest entry
            if isinstance(file_data, dict) and "history" in file_data:
                if file_data["history"]:
                    step2_data = file_data["history"][-1]  # Get latest entry
                    print(f"Step 3: Loaded latest step2 entry with {step2_data.get('total_matches', 0)} matches")
                else:
                    print("Step 3: No history entries found in step2.json")
                    return {}
            else:
                # Legacy format without history
                step2_data = file_data
                print(f"Step 3: Loaded step2.json with {step2_data.get('total_matches', 0)} matches")
        except Exception as e:
            print(f"Step 3: Error loading step2.json: {e}")
            return {}
    else:
        # It's already the data structure we need
        step2_data = summaries
    
    # Process and write the summary
    try:
        result = write_summary_json(step2_data)
        if result:
            print(f"Step 3: Successfully generated summary with {result['match_count']} matches")
            print(f"Step 3: Summary saved to {SUMMARY_JSON_FILE}")
        else:
            print("Step 3: Failed to generate summary")
        
        return result or {}
    except Exception as e:
        print(f"Step 3: Error in json_summary: {e}")
        return {}

if __name__ == "__main__":
    # For testing directly
    import sys
    import asyncio
    
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
            result = asyncio.run(json_summary(data))
            print(f"Generated summary JSON with {result.get('match_count', 0)} matches")
    else:
        # Try to load step2.json from default location
        step2_file = Path(__file__).parent.parent / "Step2_extract_merge_summarize" / "step2.json"
        if step2_file.exists():
            with open(step2_file, 'r') as f:
                data = json.load(f)
                result = asyncio.run(json_summary(data))
                print(f"Generated summary JSON with {result.get('match_count', 0)} matches")
        else:
            print("Please provide a path to step2.json or ensure step2.json exists")
            print("Usage: python step3.py [path/to/step2.json]")
