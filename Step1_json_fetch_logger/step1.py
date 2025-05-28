#!/usr/bin/env python3
"""
STEP 1 – DATA FETCHER
--------------------
Fetches data from TheSports API and returns it as a dictionary.
No loops, no queues, no scheduling - runs once and exits.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import asyncio
import aiohttp
from datetime import datetime
import time
import json
import os
from zoneinfo import ZoneInfo
import psutil

# Hard-coded credentials (consider moving to env-vars)
USER = "thenecpt"
SECRET = "0c55322e8e196d6ef9066fa4252cf386"

# API base and endpoints
BASE_URL = "https://api.thesports.com/v1/football"
URLS = {
    "live":        f"{BASE_URL}/match/detail_live",
    "details":     f"{BASE_URL}/match/recent/list",
    "odds":        f"{BASE_URL}/odds/history",
    "team":        f"{BASE_URL}/team/additional/list",
    "competition": f"{BASE_URL}/competition/additional/list",
    "country":     f"{BASE_URL}/country/list",
}

# Session counter file (tracks sessions per day like legacy logger)
SESSION_COUNTER_FILE = os.path.join(os.path.dirname(__file__), "fetch_counter.txt")


def _next_session_number() -> int:
    """Return incremented session number, resetting at midnight (Eastern)."""
    tz = ZoneInfo("America/New_York")
    today = datetime.now(tz).strftime("%m/%d/%Y")

    if not os.path.exists(SESSION_COUNTER_FILE):
        with open(SESSION_COUNTER_FILE, "w") as f:
            f.write(f"{today}\n1")
        return 1

    try:
        with open(SESSION_COUNTER_FILE, "r") as f:
            lines = f.read().strip().split("\n")
        if len(lines) >= 2 and lines[0] == today:
            num = int(lines[1]) + 1
        else:
            num = 1  # new day or bad file
    except Exception:
        num = 1

    # write back
    with open(SESSION_COUNTER_FILE, "w") as f:
        f.write(f"{today}\n{num}")
    return num


async def fetch_json(session: aiohttp.ClientSession, url: str, params: dict) -> dict:
    async with session.get(url, params=params) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_live_matches(session):
    return await fetch_json(session, URLS["live"], {"user": USER, "secret": SECRET})


async def fetch_match_details(session, match_id):
    return await fetch_json(session, URLS["details"], {"user": USER, "secret": SECRET, "uuid": match_id})


async def fetch_match_odds(session, match_id):
    return await fetch_json(session, URLS["odds"], {"user": USER, "secret": SECRET, "uuid": match_id})


async def fetch_team_info(session, team_id):
    return await fetch_json(session, URLS["team"], {"user": USER, "secret": SECRET, "uuid": team_id})


async def fetch_competition_info(session, comp_id):
    return await fetch_json(session, URLS["competition"], {"user": USER, "secret": SECRET, "uuid": comp_id})


async def fetch_country_list(session):
    return await fetch_json(session, URLS["country"], {"user": USER, "secret": SECRET})


async def step1_main():
    """Fetch data once, log performance metrics, and return the data dict."""
    print("Step 1: Starting data fetch...")
    
    all_data = {
        "timestamp": datetime.now().isoformat(),
        "live_matches": {},
        "match_details": {},
        "match_odds": {},
        "team_info": {},
        "competition_info": {},
        "countries": {},
    }

    async with aiohttp.ClientSession() as session:
        # -------------------------------------------------------------------
        # Metrics setup (similar to legacy process_logger)
        # -------------------------------------------------------------------
        start_ts = time.perf_counter()
        tz = ZoneInfo("America/New_York")
        metrics = {
            "api_calls": {k: 0 for k in URLS.keys()},
            "response_times": {k: [] for k in URLS.keys()},
        }

        # --- LIVE -------------------------------------------------------
        t0 = time.perf_counter()
        live = await fetch_live_matches(session)
        metrics["api_calls"]["live"] += 1
        metrics["response_times"]["live"].append(time.perf_counter() - t0)

        all_data["live_matches"] = live

        matches = live.get("results", [])
        print(f"Step 1: Found {len(matches)} live matches")
        
        for match in matches:
            mid = match.get("id")
            # DETAILS ----------------------------------------------------
            t0 = time.perf_counter()
            detail_wrap = await fetch_match_details(session, mid)
            metrics["api_calls"]["details"] += 1
            metrics["response_times"]["details"].append(time.perf_counter() - t0)
            all_data["match_details"][mid] = detail_wrap

            # unwrap first result for richer IDs
            detail = {}
            if isinstance(detail_wrap, dict):
                res = detail_wrap.get("results") or detail_wrap.get("result") or []
                if isinstance(res, list) and res:
                    detail = res[0]

            # ODDS -------------------------------------------------------
            t0 = time.perf_counter()
            all_data["match_odds"][mid] = await fetch_match_odds(session, mid)
            metrics["api_calls"]["odds"] += 1
            metrics["response_times"]["odds"].append(time.perf_counter() - t0)

            # Team / competition caching using IDs from detail if available
            home_id = detail.get("home_team_id") or match.get("home_team_id")
            away_id = detail.get("away_team_id") or match.get("away_team_id")
            comp_id = detail.get("competition_id") or match.get("competition_id")

            if home_id and str(home_id) not in all_data["team_info"]:
                t0 = time.perf_counter()
                all_data["team_info"][str(home_id)] = await fetch_team_info(session, home_id)
                metrics["api_calls"]["team"] += 1
                metrics["response_times"]["team"].append(time.perf_counter() - t0)
            if away_id and str(away_id) not in all_data["team_info"]:
                t0 = time.perf_counter()
                all_data["team_info"][str(away_id)] = await fetch_team_info(session, away_id)
                metrics["api_calls"]["team"] += 1
                metrics["response_times"]["team"].append(time.perf_counter() - t0)
            if comp_id and str(comp_id) not in all_data["competition_info"]:
                t0 = time.perf_counter()
                all_data["competition_info"][str(comp_id)] = await fetch_competition_info(session, comp_id)
                metrics["api_calls"]["competition"] += 1
                metrics["response_times"]["competition"].append(time.perf_counter() - t0)

        t0 = time.perf_counter()
        all_data["countries"] = await fetch_country_list(session)
        metrics["api_calls"]["country"] += 1
        metrics["response_times"]["country"].append(time.perf_counter() - t0)

    # -------------------------------------------------------------------
    # Write metrics log (fetch_process.log)
    # -------------------------------------------------------------------
    total_time = time.perf_counter() - start_ts
    matches_cnt = len(all_data["match_details"])

    # Data volume (approx) in MB
    data_volume_mb = len(json.dumps(all_data).encode("utf-8")) / 1024 / 1024

    # Cache performance (simple: misses equal API calls for team/competition)  
    team_misses = metrics["api_calls"]["team"]
    comp_misses = metrics["api_calls"]["competition"]

    # Peak memory / CPU (snapshot after run)  
    proc = psutil.Process(os.getpid())
    mem_mb = proc.memory_info().rss / 1024 / 1024
    cpu_percent = proc.cpu_percent(interval=None)  # returns last measurement

    session_num = _next_session_number()

    log_path = os.path.join(os.path.dirname(__file__), "fetch_process.log")

    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write("=" * 80 + "\n")
        lf.write(f"=== FETCH PROCESS SUMMARY - SESSION #{session_num} ===\n")
        lf.write(
            f"=== {datetime.now(tz).strftime('%m/%d/%Y %I:%M:%S %p')} (Eastern Time) ===\n"
        )
        lf.write("=" * 80 + "\n")
        lf.write(f"Total execution time: {total_time:.2f}s\n")
        lf.write(f"Live matches count: {matches_cnt}\n")

        # API stats
        lf.write("API CALL STATISTICS:\n")
        for key, count in metrics["api_calls"].items():
            if count:
                avg = (
                    sum(metrics["response_times"][key]) / count
                    if metrics["response_times"][key]
                    else 0
                )
                lf.write(f"  {key.upper():8}: {count} calls, avg response: {avg:.2f}s\n")

        # Cache performance
        lf.write("CACHE PERFORMANCE:\n")
        lf.write(f"  Team cache: 0 hits, {team_misses} misses (0.0% hit rate)\n")
        lf.write(f"  Competition cache: 0 hits, {comp_misses} misses (0.0% hit rate)\n")
        lf.write(f"  Country cache: 0 hits, 0 misses (0.0% hit rate)\n")

        # Data processing
        lf.write("DATA PROCESSING:\n")
        lf.write(f"  Matches processed: {matches_cnt}\n")
        lf.write(f"  Total data volume: {data_volume_mb:.2f} MB\n")

        # Performance metrics
        lf.write("PERFORMANCE METRICS:\n")
        lf.write(f"  Peak memory usage: {mem_mb:.1f} MB\n")
        lf.write(f"  Peak CPU usage: {cpu_percent:.1f}%\n")

        # Overall summary
        total_api_calls = sum(metrics["api_calls"].values())
        average_resp = (total_time / total_api_calls) if total_api_calls else 0
        data_eff_kbps = (data_volume_mb * 1024) / total_time if total_time else 0

        lf.write("OVERALL FETCH SUMMARY:\n")
        lf.write(f"  Total API calls made: {total_api_calls}\n")
        lf.write(f"  Average response time: {average_resp:.2f}s per call\n")
        lf.write(f"  Data efficiency: {data_eff_kbps:.1f} KB/s\n")

        lf.write("=" * 80 + "\n")
        lf.write(f"=== END SESSION #{session_num} - {datetime.now(tz).strftime('%m/%d/%Y %I:%M:%S %p')} (Eastern Time) ===\n")
        lf.write("=" * 80 + "\n\n")

    print("Step 1: Data fetch completed")
    return all_data


if __name__ == "__main__":
    # For standalone testing
    result = asyncio.run(step1_main())
    print(f"Step 1: Fetched data with {len(result.get('live_matches', {}).get('results', []))} matches") 