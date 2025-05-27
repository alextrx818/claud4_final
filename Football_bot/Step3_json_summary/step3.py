#!/usr/bin/env python3
# Step 3 - JSON Summary

"""Step 3 – JSON Summary
This module takes the cleaned match summaries from Step 2 and
groups/summarizes them for final presentation.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import logging

# Timezone constant for Eastern Time
TZ = ZoneInfo("America/New_York")


def setup_summary_logger():
    """Setup basic logger for Step 3"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger("step3")


def get_eastern_time():
    now = datetime.now(TZ)
    return now.strftime("%d/%m/%Y %I:%M:%S %p %Z")


# ---------------------------------------------------------------------------
# Summary and grouping functions
# ---------------------------------------------------------------------------

def group_by_competition(summaries: list) -> dict:
    """Group matches by competition."""
    grouped = {}
    for match in summaries:
        comp_name = match.get("competition", {}).get("name", "Unknown")
        comp_id = match.get("competition", {}).get("id", "unknown")
        key = f"{comp_name}_{comp_id}"
        
        if key not in grouped:
            grouped[key] = {
                "competition_name": comp_name,
                "competition_id": comp_id,
                "country": match.get("competition", {}).get("country"),
                "logo_url": match.get("competition", {}).get("logo_url"),
                "matches": []
            }
        grouped[key]["matches"].append(match)
    
    return grouped


def group_by_status(summaries: list) -> dict:
    """Group matches by status (live, upcoming, finished)."""
    grouped = {
        "live": [],
        "upcoming": [],
        "finished": []
    }
    
    for match in summaries:
        status_id = match.get("status", {}).get("id")
        # Status IDs: 1=upcoming, 2-7=live, 8+=finished (approximate)
        if status_id == 1:
            grouped["upcoming"].append(match)
        elif 2 <= status_id <= 7:
            grouped["live"].append(match)
        else:
            grouped["finished"].append(match)
    
    return grouped


def create_summary_stats(summaries: list) -> dict:
    """Create overall statistics from all matches."""
    stats = {
        "total_matches": len(summaries),
        "by_status": {},
        "by_competition": {},
        "matches_with_odds": 0,
        "matches_with_events": 0,
        "timestamp": get_eastern_time()
    }
    
    # Count by status
    status_groups = group_by_status(summaries)
    for status, matches in status_groups.items():
        stats["by_status"][status] = len(matches)
    
    # Count by competition
    comp_groups = group_by_competition(summaries)
    for comp_key, comp_data in comp_groups.items():
        stats["by_competition"][comp_data["competition_name"]] = len(comp_data["matches"])
    
    # Count matches with odds and events
    for match in summaries:
        odds = match.get("odds", {})
        if odds.get("full_time_result", {}).get("home") is not None:
            stats["matches_with_odds"] += 1
        if match.get("events", []):
            stats["matches_with_events"] += 1
    
    return stats


def save_summary_json(summary_data: dict, output_file: str = "step3.json"):
    """Save summarized data to JSON file."""
    # Ensure we save in the Step3_json_summary directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, output_file)
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main processing function
# ---------------------------------------------------------------------------

async def json_summary(summaries: list):
    """Process match summaries and create grouped/summarized output."""
    print("Step 3: Starting json_summary...")
    
    # Try to setup logger, fallback to print if it fails
    try:
        log = setup_summary_logger()
        print("Step 3: Logger setup successful")
    except Exception as e:
        print(f"Step 3: Logger setup failed: {e}")
        log = None

    try:
        print(f"Step 3: Processing {len(summaries)} match summaries")
        
        # Create different groupings and summaries
        summary_data = {
            "timestamp": datetime.now(TZ).isoformat(),
            "statistics": create_summary_stats(summaries),
            "by_competition": group_by_competition(summaries),
            "by_status": group_by_status(summaries),
            "all_matches": summaries  # Keep raw data too
        }
        
        # Save to JSON file
        success = save_summary_json(summary_data)
        if success:
            msg = f"Step 3 produced summary with {len(summaries)} matches and saved to step3.json"
            print(msg)
            if log:
                log.info(msg)
        else:
            msg = f"Step 3 produced summary but failed to save JSON file"
            print(msg)
            if log:
                log.warning(msg)
        
        print("Step 3: Processing completed")
        return summary_data

    except Exception as exc:
        print(f"Step 3: Error occurred: {exc}")
        try:
            if log:
                log.exception("Error in Step 3: %s", exc)
        except Exception:
            pass
        return {}


if __name__ == "__main__":
    # For standalone testing - would need sample data
    print("Step 3: This module should be called from orchestrator.py") 