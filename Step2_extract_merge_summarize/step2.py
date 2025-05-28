#!/usr/bin/env python3
# Renamed from step2_extract_merge_summarize.py

"""Step 2 – Extract, Merge, Summarize
This module consumes raw match payloads from an asyncio.Queue and
produces cleaned-up summary dictionaries ready for downstream steps.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import re
import asyncio
import json
import os
import logging

# Timezone constant for Eastern Time
TZ = ZoneInfo("America/New_York")


def setup_summary_json_logger():
    """Setup basic logger for Step 2"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger("step2")


def get_eastern_time():
    now = datetime.now(TZ)
    return now.strftime("%m/%d/%Y %I:%M:%S %p %Z")


# ---------------------------------------------------------------------------
# Field-extraction helpers
# ---------------------------------------------------------------------------

def extract_summary_fields(match: dict) -> dict:
    """Return a compact summary structure for a single match."""
    # Score extraction
    home_live = home_ht = away_live = away_ht = 0
    sd = match.get("score", [])
    if isinstance(sd, list) and len(sd) > 3:
        hs, as_ = sd[2], sd[3]
        if isinstance(hs, list) and len(hs) > 1:
            home_live, home_ht = hs[0], hs[1]
        if isinstance(as_, list) and len(as_) > 1:
            away_live, away_ht = as_[0], as_[1]

    # Fallback scores
    home_scores = match.get("home_scores", [])
    away_scores = match.get("away_scores", [])
    if home_scores and home_live == 0:
        home_live = sum(home_scores)
    if away_scores and away_live == 0:
        away_live = sum(away_scores)

    summary_data = {
        "match_id": match.get("match_id") or match.get("id"),
        "status": {
            "id": match.get("status_id"),
            "description": match.get("status", ""),
            "match_time": match.get("match_time", 0),
        },
        "teams": {
            "home": {
                "name": match.get("home_team", "Unknown"),
                "score": {"current": home_live, "halftime": home_ht, "detailed": home_scores},
                "position": match.get("home_position"),
                "country": match.get("home_country"),
                "logo_url": match.get("home_logo"),
            },
            "away": {
                "name": match.get("away_team", "Unknown"),
                "score": {"current": away_live, "halftime": away_ht, "detailed": away_scores},
                "position": match.get("away_position"),
                "country": match.get("away_country"),
                "logo_url": match.get("away_logo"),
            },
        },
        "competition": {
            "name": match.get("competition", "Unknown"),
            "id": match.get("competition_id"),
            "country": match.get("country"),
            "logo_url": match.get("competition_logo"),
        },
        "round": match.get("round", {}),
        "venue": match.get("venue_id"),
        "referee": match.get("referee_id"),
        "neutral": match.get("neutral") == 1,
        "coverage": match.get("coverage", {}),
        "start_time": match.get("scheduled"),
        "odds": extract_odds(match),
        "environment": extract_environment(match),
        "events": extract_events(match),
        "fetched_at": get_eastern_time(),
    }
    return summary_data


def extract_odds(match: dict) -> dict:
    odds_data = {
        "full_time_result": {"home": None, "draw": None, "away": None, "timestamp": None, "match_time": None},
        "both_teams_to_score": {"yes": None, "no": None},
        "over_under": {},
        "spread": {},
        "raw": {},
    }
    raw_odds = match.get("odds", {}) or {}
    odds_data["raw"] = raw_odds

    # -------------------------------------------------------------------
    # Helper to select entries captured at an early match minute
    # -------------------------------------------------------------------
    def _safe_minute(value):
        """Return integer minute if parsable else None."""
        if value is None:
            return None
        m = re.match(r"(\d+)", str(value))
        return int(m.group(1)) if m else None

    def filter_by_time(entries):
        """Return entries recorded between minutes 3-6 inclusive.

        If none exist, fall back to the single entry (under 10′) whose
        minute is closest to 4.5.  An empty list is returned if no minute
        information is available.
        """
        processed = []  # (minute, entry)
        for ent in entries:
            if not isinstance(ent, (list, tuple)) or len(ent) < 2:
                continue
            minute = _safe_minute(ent[1])
            if minute is None:
                continue
            processed.append((minute, ent))

        # First preference: all entries within 3-6 (inclusive)
        in_window = [e for m, e in processed if 3 <= m <= 6]
        if in_window:
            return in_window

        # Fallback: pick single entry <10 with minute closest to 4.5
        under_ten = [(m, e) for m, e in processed if m < 10]
        if not under_ten:
            return []
        best_m, best_e = min(under_ten, key=lambda t: abs(t[0] - 4.5))
        return [best_e]

    # -------------------------------------------------------------------
    # Full-time result (European odds) -----------------------------------
    # -------------------------------------------------------------------
    best_eu_list = filter_by_time(raw_odds.get("eu", []))
    best_eu = best_eu_list[0] if best_eu_list else None
    if best_eu and len(best_eu) >= 5:
        odds_data["full_time_result"] = {
            "home": best_eu[2],
            "draw": best_eu[3],
            "away": best_eu[4],
            "timestamp": best_eu[0],
            "match_time": best_eu[1],
        }

    # -------------------------------------------------------------------
    # Asian Handicap (spread) -------------------------------------------
    # -------------------------------------------------------------------
    best_asia_list = filter_by_time(raw_odds.get("asia", []))
    best_asia = best_asia_list[0] if best_asia_list else None
    if best_asia and len(best_asia) >= 5:
        odds_data["spread"] = {
            "handicap": best_asia[3],
            "home": best_asia[2],
            "away": best_asia[4],
            "timestamp": best_asia[0],
            "match_time": best_asia[1],
        }

    # -------------------------------------------------------------------
    # Over/Under (totals) -----------------------------------------------
    # -------------------------------------------------------------------
    best_bs_list = filter_by_time(raw_odds.get("bs", []))
    best_bs = best_bs_list[0] if best_bs_list else None
    if best_bs and len(best_bs) >= 5:
        line = best_bs[3]
        odds_data["over_under"][str(line)] = {
            "line": line,
            "over": best_bs[2],
            "under": best_bs[4],
            "timestamp": best_bs[0],
            "match_time": best_bs[1],
        }
        odds_data["primary_over_under"] = {"line": line, "over": best_bs[2], "under": best_bs[4]}

    for market in match.get("betting", {}).get("markets", []):
        if market.get("name") == "Both Teams to Score":
            for sel in market.get("selections", []):
                nm = sel.get("name", "").lower()
                if nm in ("yes", "no"):
                    odds_data["both_teams_to_score"][nm] = sel.get("odds")
    return odds_data


def extract_environment(match: dict) -> dict:
    env = match.get("environment", {}) or {}
    data = {"raw": env}

    wc = env.get("weather")
    if isinstance(wc, str) and wc.isdigit():
        wc = int(wc)
    data["weather"] = wc
    data["weather_description"] = {
        1: "Sunny",
        2: "Partly Cloudy",
        3: "Cloudy",
        4: "Overcast",
        5: "Foggy",
        6: "Light Rain",
        7: "Rain",
        8: "Heavy Rain",
        9: "Snow",
        10: "Thunder",
    }.get(wc, "Unknown")

    def parse(val):
        m = re.match(r"([\d.-]+)\s*([^\d]*)", str(val))
        return (float(m[1]), m[2].strip()) if m else (None, None)

    for key in ("temperature", "wind", "pressure"):
        v = env.get(key)
        data[key] = v
        num, unit = parse(v)
        data[f"{key}_value"] = num
        data[f"{key}_unit"] = unit

    hum = env.get("humidity")
    data["humidity"] = hum
    m = re.match(r"([\d.]+)", str(hum))
    data["humidity_value"] = float(m[1]) if m else None

    wv = data.get("wind_value") or 0
    mph = wv * 2.237 if "m/s" in str(env.get("wind", "")).lower() else wv
    data["wind_description"] = (
        "Calm"
        if mph < 1
        else "Light Air"
        if mph < 4
        else "Light Breeze"
        if mph < 8
        else "Gentle Breeze"
        if mph < 13
        else "Moderate Breeze"
        if mph < 19
        else "Fresh Breeze"
        if mph < 25
        else "Strong Breeze"
        if mph < 32
        else "Near Gale"
        if mph < 39
        else "Gale"
        if mph < 47
        else "Strong Gale"
        if mph < 55
        else "Storm"
        if mph < 64
        else "Violent Storm"
        if mph < 73
        else "Hurricane"
    )
    return data


def extract_events(match: dict) -> list:
    events = []
    for ev in match.get("events", []):
        t = ev.get("type")
        if t in {"goal", "yellowcard", "redcard", "penalty", "substitution"}:
            events.append(
                {
                    "type": t,
                    "time": ev.get("time"),
                    "team": ev.get("team"),
                    "player": ev.get("player"),
                    "detail": ev.get("detail"),
                }
            )
    return events


def save_match_summaries(summaries: list, output_file: str = "step2.json"):
    """Append match summaries to JSON file as growing history."""
    # Group summaries by match_id
    grouped_summaries = {}
    for summary in summaries:
        match_id = summary.get("match_id")
        if match_id:
            grouped_summaries[str(match_id)] = summary
    
    # Create current batch data
    current_data = {
        "timestamp": datetime.now(TZ).isoformat(),
        "total_matches": len(grouped_summaries),
        "matches": grouped_summaries
    }
    
    # Ensure we save in the Step2_extract_merge_summarize directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, output_file)
    
    # Append to existing history
    try:
        # Load existing data if file exists
        existing_data = {"history": []}
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if "history" not in existing_data:
                        existing_data = {"history": [existing_data] if existing_data else []}
            except (json.JSONDecodeError, Exception):
                existing_data = {"history": []}
        
        # Add current batch to history
        existing_data["history"].append(current_data)
        
        # Update metadata
        existing_data["last_updated"] = current_data.get("timestamp")
        existing_data["total_entries"] = len(existing_data["history"])
        existing_data["latest_match_count"] = current_data.get("total_matches", 0)
        
        # Save updated data
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Utility to unwrap <map>[key]["results"][0]
# ---------------------------------------------------------------------------

def first_result(mapping: dict, key):
    """Return mapping[str(key)]['results'][0] if present, else {}."""
    wrapper = mapping.get(str(key)) if key is not None else None
    if isinstance(wrapper, dict):
        res = wrapper.get("results") or wrapper.get("result") or []
        if isinstance(res, list) and res:
            return res[0]
    return {}


# ---------------------------------------------------------------------------
# Helper to merge auxiliary maps and create richer summary
# ---------------------------------------------------------------------------

def merge_and_summarize(live: dict, payload: dict) -> dict:
    """Return summary for a single live match using auxiliary maps."""

    mid = live.get("id") or live.get("match_id")
    details_map = payload.get("match_details", {})
    odds_map = payload.get("match_odds", {})
    team_map = payload.get("team_info", {})
    comp_map = payload.get("competition_info", {})
    # Countries map (id -> name)
    countries_wrap = payload.get("countries", {})
    countries_list = []
    if isinstance(countries_wrap, dict):
        countries_list = countries_wrap.get("results") or countries_wrap.get("result") or []
    countries = {c.get("id"): c.get("name") for c in countries_list if isinstance(c, dict)}

    detail = first_result(details_map, mid)
    
    # Extract odds - the API returns results as a dict of bookmakers
    odds_wrapper = odds_map.get(mid, {})
    odds_struct = {}
    
    if isinstance(odds_wrapper, dict) and 'results' in odds_wrapper:
        bookmaker_odds = odds_wrapper['results']
        if isinstance(bookmaker_odds, dict):
            # Merge all bookmaker odds into a single structure
            # We'll take the first available bookmaker's odds for each market
            for bookmaker_id, markets in bookmaker_odds.items():
                if isinstance(markets, dict):
                    for market_type, odds_list in markets.items():
                        if market_type not in odds_struct and isinstance(odds_list, list):
                            odds_struct[market_type] = odds_list

    # Resolve teams
    home_id = live.get("home_team_id") or detail.get("home_team_id")
    away_id = live.get("away_team_id") or detail.get("away_team_id")

    home_team = first_result(team_map, home_id)
    away_team = first_result(team_map, away_id)

    # Resolve competition
    comp_id = live.get("competition_id") or detail.get("competition_id")
    comp_info = first_result(comp_map, comp_id)

    # Build a convenience merged dict so existing extract_summary_fields works
    merged = {
        **live,
        **detail,  # detail overrides live where present

        # Core enrichments ------------------------------------------------
        "odds": odds_struct or {},
        "environment": detail.get("environment", live.get("environment", {})),
        "events": detail.get("events", live.get("events", [])),

        # Team & competition overlay -------------------------------------
        "home_team": home_team.get("name") or live.get("home_name") or detail.get("home_name"),
        "home_logo": home_team.get("logo") or home_team.get("team_logo"),
        "home_country": home_team.get("country") or countries.get(home_team.get("country_id")),

        "away_team": away_team.get("name") or live.get("away_name") or detail.get("away_name"),
        "away_logo": away_team.get("logo") or away_team.get("team_logo"),
        "away_country": away_team.get("country") or countries.get(away_team.get("country_id")),

        "competition": comp_info.get("name") or live.get("competition_name"),
        "competition_logo": comp_info.get("logo") or comp_info.get("competition_logo"),
        "country": comp_info.get("country") or countries.get(comp_info.get("country_id")),
    }

    # attach full odds wrapper as raw too
    merged["odds_raw"] = odds_wrapper

    return extract_summary_fields(merged)


# ---------------------------------------------------------------------------
# Main processing function (no longer async consumer)
# ---------------------------------------------------------------------------

async def extract_merge_summarize(data: dict):
    """Process match data and return summaries. No loops, no queues."""
    print("Step 2: Starting extract_merge_summarize...")
    
    # Try to setup logger, fallback to print if it fails
    try:
        log = setup_summary_json_logger()
        print("Step 2: Logger setup successful")
    except Exception as e:
        print(f"Step 2: Logger setup failed: {e}")
        log = None

    try:
        live_container = data.get("live_matches", {})
        matches = live_container.get("results") or live_container.get("matches") or []
        print(f"Step 2: Found {len(matches)} matches to process")
        
        summaries = [merge_and_summarize(m, data) for m in matches]
        print(f"Step 2: Created {len(summaries)} summaries")
        
        # Save summaries to JSON file
        if summaries:
            success = save_match_summaries(summaries)
            if success:
                msg = f"Step 2 produced {len(summaries)} summaries and saved to step2.json"
                print(msg)
                if log:
                    log.info(msg)
            else:
                msg = f"Step 2 produced {len(summaries)} summaries but failed to save JSON file"
                print(msg)
                if log:
                    log.warning(msg)
        else:
            msg = "Step 2 processed payload but found no matches to summarize"
            print(msg)
            if log:
                log.info(msg)

        print("Step 2: Processing completed")
        return summaries

    except Exception as exc:
        print(f"Step 2: Error occurred: {exc}")
        try:
            if log:
                log.exception("Error in Step 2: %s", exc)
        except Exception:
            pass
        return []


if __name__ == "__main__":
    # For standalone testing - would need sample data
    print("Step 2: This module should be called from orchestrator.py")

