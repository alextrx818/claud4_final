#!/usr/bin/env python3
"""Test script to check odds API response structure"""

import asyncio
import aiohttp
import json

USER = "thenecpt"
SECRET = "0c55322e8e196d6ef9066fa4252cf386"
BASE_URL = "https://api.thesports.com/v1/football"

async def test_odds_api():
    async with aiohttp.ClientSession() as session:
        # First get live matches
        async with session.get(f"{BASE_URL}/match/detail_live", 
                             params={"user": USER, "secret": SECRET}) as resp:
            live_data = await resp.json()
            
        matches = live_data.get("results", [])
        if matches:
            match_id = matches[0].get("id")
            print(f"Testing odds API for match ID: {match_id}")
            
            # Fetch odds
            async with session.get(f"{BASE_URL}/odds/history",
                                 params={"user": USER, "secret": SECRET, "uuid": match_id}) as resp:
                odds_data = await resp.json()
                
            print("\nOdds API Response Structure:")
            print(f"Type: {type(odds_data)}")
            print(f"Keys: {list(odds_data.keys()) if isinstance(odds_data, dict) else 'Not a dict'}")
            
            if isinstance(odds_data, dict):
                for key, value in odds_data.items():
                    print(f"\n{key}:")
                    if isinstance(value, list):
                        print(f"  - List with {len(value)} items")
                        if value and len(value) > 0:
                            print(f"  - First item type: {type(value[0])}")
                            if isinstance(value[0], list):
                                print(f"  - First item length: {len(value[0])}")
                                print(f"  - First item sample: {value[0][:5] if len(value[0]) > 5 else value[0]}")
                    elif isinstance(value, dict):
                        print(f"  - Dict with keys: {list(value.keys())}")
                    else:
                        print(f"  - Type: {type(value)}, Value: {value}")
                        
            # Save full response for inspection
            with open("test_odds_response.json", "w") as f:
                json.dump(odds_data, f, indent=2)
            print("\nFull response saved to test_odds_response.json")

if __name__ == "__main__":
    asyncio.run(test_odds_api()) 