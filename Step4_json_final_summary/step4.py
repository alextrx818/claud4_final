#!/usr/bin/env python3
"""
Step 4 - JSON Final Summary
Creates a clean, formatted summary of matches with specific fields

This module extracts key information from Step 3's output and creates
a simplified summary focusing on essential match data, odds, and environment.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Use the same timezone as other modules
TZ = ZoneInfo("America/New_York")

# Path constants
BASE_DIR = Path(__file__).parent
STEP3_JSON = BASE_DIR.parent / "Step3_json_summary" / "step3.json"
STEP4_JSON = BASE_DIR / "step4.json"

def get_eastern_time():
    """Get current time in Eastern timezone with MM/DD/YYYY format"""
    now = datetime.now(TZ)
    return now.strftime("%m/%d/%Y %I:%M:%S %p %Z")

def format_score(home_current, away_current, home_halftime=0, away_halftime=0):
    """Format score in the requested format"""
    return f"{home_current} - {away_current} (HT: {home_halftime} - {away_halftime})"

def extract_match_summary(match_id, match_data):
    """Extract the specific fields requested for each match"""
    
    # Basic match information
    summary = {
        "match_id": match_id,
        "competition_id": match_data.get("competition", {}).get("id", ""),
        "competition": match_data.get("competition", {}).get("name", ""),
        "country": match_data.get("competition", {}).get("country", ""),
        "home_team": match_data.get("teams", {}).get("home", {}).get("name", ""),
        "away_team": match_data.get("teams", {}).get("away", {}).get("name", ""),
    }
    
    # Calculate score using the provided logic
    home_score = match_data.get("teams", {}).get("home", {}).get("score", {})
    away_score = match_data.get("teams", {}).get("away", {}).get("score", {})
    
    home_current = home_score.get("current", 0)
    home_halftime = home_score.get("halftime", 0)
    away_current = away_score.get("current", 0)
    away_halftime = away_score.get("halftime", 0)
    
    summary["score"] = format_score(home_current, away_current, home_halftime, away_halftime)
    
    # Status
    match_info = match_data.get("match_info", {})
    status_info = match_info.get("status", {})
    status_id = status_info.get("id", 0)
    
    # Determine status based on ID
    if status_id == 1:
        status = "Upcoming"
    elif 2 <= status_id <= 7:
        status = "Live"
    elif status_id >= 8:
        status = "Finished"
    else:
        status = "Unknown"
    
    summary["status"] = status
    
    # Odds fields - check both odds_detailed and odds_summary
    odds = match_data.get("odds_detailed") or match_data.get("odds_summary") or match_data.get("odds", {})
    
    # Full time result odds
    full_time_result = odds.get("full_time_result", {})
    if full_time_result and full_time_result.get("home") is not None:
        summary["full_time_result"] = {
            "home": full_time_result.get("home"),
            "draw": full_time_result.get("draw"),
            "away": full_time_result.get("away"),
            "match_time": full_time_result.get("match_time")
        }
    else:
        summary["full_time_result"] = None
    
    # Spread odds
    spread = odds.get("spread", {})
    if spread and spread.get("handicap") is not None:
        summary["spread"] = {
            "handicap": spread.get("handicap"),
            "home": spread.get("home"),
            "away": spread.get("away"),
            "match_time": spread.get("match_time")
        }
    else:
        summary["spread"] = None
    
    # Over/Under odds - get the primary line or first available
    over_under_data = odds.get("over_under", {})
    primary_ou = odds.get("primary_over_under", {})
    
    # Check if we have over_under data with lines
    if over_under_data:
        # Get the first available line
        first_line_key = next(iter(over_under_data.keys()), None)
        if first_line_key:
            first_line = over_under_data[first_line_key]
            line = first_line.get("line", first_line_key)
            summary["over_under"] = {
                str(line): {
                    "line": float(line) if isinstance(line, str) else line,
                    "over": first_line.get("over"),
                    "under": first_line.get("under"),
                    "match_time": first_line.get("match_time")
                }
            }
        else:
            summary["over_under"] = None
    elif primary_ou and primary_ou.get("line") is not None:
        # Fallback to primary_over_under if no detailed data
        line = primary_ou.get("line")
        summary["over_under"] = {
            str(line): {
                "line": line,
                "over": primary_ou.get("over"),
                "under": primary_ou.get("under")
            }
        }
    else:
        summary["over_under"] = None
    
    # Environment data
    env = match_data.get("environment", {})
    if env:
        summary["environment"] = {
            "raw": env.get("raw", {}),
            "weather": env.get("weather"),
            "weather_description": env.get("weather_description", "Unknown"),
            "temperature": env.get("temperature"),
            "temperature_value": env.get("temperature_value"),
            "temperature_unit": env.get("temperature_unit"),
            "wind": env.get("wind"),
            "wind_value": env.get("wind_value"),
            "wind_unit": env.get("wind_unit"),
            "pressure": env.get("pressure"),
            "pressure_value": env.get("pressure_value"),
            "pressure_unit": env.get("pressure_unit"),
            "humidity": env.get("humidity"),
            "humidity_value": env.get("humidity_value"),
            "wind_description": env.get("wind_description", "Calm")
        }
    else:
        summary["environment"] = None
    
    return summary

# ---------------------------------------------------------------------------
# Helper: Normalize Step-3 data snapshot into list[match]
# ---------------------------------------------------------------------------

def _get_snapshot_matches(step3_snapshot: dict) -> list:
    """Return list of per-match dicts from a single Step-3 snapshot.

    Handles both list and dict representations ("matches" may be a dict
    keyed by match_id or it may already be a list).
    """
    if not step3_snapshot:
        return []

    # Common representation in Step-3 is a dict under key "matches"
    matches_blob = step3_snapshot.get("matches") or step3_snapshot.get("all_matches")

    if isinstance(matches_blob, dict):
        return list(matches_blob.values())
    if isinstance(matches_blob, list):
        return matches_blob

    return []


def process_step3_data(step3_data: dict | None = None):
    """Convert Step-3 output (or file contents) into final summaries.

    This function now supports three input variants:
      1. *step3_data* passed directly from orchestrator (preferred)
      2. Latest snapshot inside *step3.json* when it stores a history list
      3. Legacy *step3.json* file with single snapshot
    """

    # -------------------------------------------------------------------
    # 1. Determine the snapshot to use
    # -------------------------------------------------------------------
    snapshot = None

    if step3_data:
        snapshot = step3_data
    else:
        # Load from disk
        if not STEP3_JSON.exists():
            print(f"Error: {STEP3_JSON} not found!")
            return None

        try:
            with open(STEP3_JSON, "r", encoding="utf-8") as f:
                file_data = json.load(f)
        except Exception as exc:
            print(f"Step 4: Failed to read step3.json – {exc}")
            return None

        # If history structure present, grab the latest entry
        if isinstance(file_data, dict) and "history" in file_data:
            hist = file_data.get("history", [])
            if hist:
                snapshot = hist[-1]
        else:
            snapshot = file_data

    if not snapshot:
        print("Step 4: No valid Step-3 snapshot found")
        return None

    # -------------------------------------------------------------------
    # 2. Extract matches list from snapshot
    # -------------------------------------------------------------------
    all_matches = _get_snapshot_matches(snapshot)

    # -------------------------------------------------------------------
    # 3. Build final summaries list
    # -------------------------------------------------------------------
    final_summaries = {
        "generated_at": get_eastern_time(),
        "total_matches": len(all_matches),
        "matches": []
    }

    for match_data in all_matches:
        match_id = match_data.get("match_id", "")
        summary = extract_match_summary(match_id, match_data)
        final_summaries["matches"].append(summary)

    # Sort matches by status priority
    status_order = {"Live": 0, "Upcoming": 1, "Finished": 2, "Unknown": 3}
    final_summaries["matches"].sort(key=lambda x: status_order.get(x["status"], 3))

    return final_summaries

def save_final_summary(summary_data):
    """Append the final summary to step4.json as a growing history"""

    if not summary_data:
        return False

    try:
        # Load existing data if file exists
        existing_data = {"history": []}
        if STEP4_JSON.exists():
            try:
                with open(STEP4_JSON, 'r', encoding='utf-8') as f:
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
        existing_data["latest_match_count"] = summary_data.get("total_matches", 0)
        
        # Save updated data
        with open(STEP4_JSON, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving step4 summary: {e}")
        return False

# Main async function to be called from orchestrator
async def json_final_summary(step3_data):
    """
    Main entry point for Step 4 - called from orchestrator
    
    Args:
        step3_data: Data from Step 3 (can be dict or will load from file)
    
    Returns:
        Dictionary containing the final summary data
    """
    print("Step 4: Starting json_final_summary...")
    
    try:
        # Process the data – pass in-memory *step3_data* when available
        final_summaries = process_step3_data(step3_data)
        
        if final_summaries:
            # Save to file
            success = save_final_summary(final_summaries)
            
            if success:
                print(f"Step 4: Successfully generated final summary with {final_summaries['total_matches']} matches")
                print(f"Step 4: Summary appended to history in {STEP4_JSON}")
            else:
                print("Step 4: Failed to save final summary")
            
            return final_summaries
        else:
            print("Step 4: Failed to process data")
            return {}
            
    except Exception as e:
        print(f"Step 4: Error in json_final_summary: {e}")
        return {}

if __name__ == "__main__":
    # For testing directly
    import asyncio
    
    result = asyncio.run(json_final_summary(None))
    if result:
        print(f"\nGenerated final summary with {result.get('total_matches', 0)} matches")
        print(f"Sample match summary:")
        if result.get('matches'):
            print(json.dumps(result['matches'][0], indent=2)) 