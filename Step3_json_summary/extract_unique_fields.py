#!/usr/bin/env python3
"""
Extract all unique JSON fields from step2.json without duplicates
This gives us the general structure that applies to all matches
"""

import json
import os
from typing import Dict, Set, Any, List
from collections import defaultdict

def extract_unique_fields(obj: Any, path: str = "", fields_set: Set[str] = None, samples: Dict[str, List] = None) -> tuple:
    """
    Recursively extract unique field paths from JSON, ignoring specific match IDs
    """
    if fields_set is None:
        fields_set = set()
    if samples is None:
        samples = defaultdict(list)
    
    if isinstance(obj, dict):
        # Special handling for matches dict - normalize the path
        if path == "matches" and all(isinstance(k, str) for k in obj.keys()):
            # This is the matches container, process one match as template
            fields_set.add("matches")
            if obj:
                first_match = next(iter(obj.values()))
                extract_unique_fields(first_match, "matches.{match_id}", fields_set, samples)
        else:
            # Regular dict processing
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                fields_set.add(current_path)
                
                if isinstance(value, (dict, list)):
                    extract_unique_fields(value, current_path, fields_set, samples)
                else:
                    # Store sample values for leaf nodes
                    if len(samples[current_path]) < 3 and value is not None:
                        samples[current_path].append({
                            "value": str(value)[:100],
                            "type": type(value).__name__
                        })
                    
    elif isinstance(obj, list) and obj:
        # Process first item to understand list structure
        fields_set.add(f"{path}[]")
        if obj and isinstance(obj[0], (dict, list)):
            extract_unique_fields(obj[0], f"{path}[]", fields_set, samples)
        elif obj:
            # List of primitives
            if len(samples[f"{path}[]"]) < 3:
                samples[f"{path}[]"].append({
                    "value": str(obj[0])[:100],
                    "type": type(obj[0]).__name__
                })
    
    return fields_set, samples

def organize_fields(fields_set: Set[str]) -> Dict[str, List[str]]:
    """
    Organize fields by category for better readability
    """
    categories = {
        "Match Metadata": [],
        "Team Information": [],
        "Competition Details": [],
        "Match Status": [],
        "Scores": [],
        "Odds - Full Time Result": [],
        "Odds - Over/Under": [],
        "Odds - Spread": [],
        "Odds - Raw Data": [],
        "Environment/Weather": [],
        "Round/Stage": [],
        "Coverage": [],
        "Events": [],
        "Other": []
    }
    
    for field in sorted(fields_set):
        if "teams.{match_id}" in field:
            continue  # Skip the intermediate path
            
        # Categorize fields
        if field.startswith("matches.{match_id}.teams"):
            if ".score" in field:
                categories["Scores"].append(field)
            else:
                categories["Team Information"].append(field)
        elif field.startswith("matches.{match_id}.competition"):
            categories["Competition Details"].append(field)
        elif field.startswith("matches.{match_id}.status"):
            categories["Match Status"].append(field)
        elif field.startswith("matches.{match_id}.odds.full_time_result"):
            categories["Odds - Full Time Result"].append(field)
        elif field.startswith("matches.{match_id}.odds.over_under"):
            categories["Odds - Over/Under"].append(field)
        elif field.startswith("matches.{match_id}.odds.spread"):
            categories["Odds - Spread"].append(field)
        elif field.startswith("matches.{match_id}.odds.raw"):
            categories["Odds - Raw Data"].append(field)
        elif field.startswith("matches.{match_id}.environment"):
            categories["Environment/Weather"].append(field)
        elif field.startswith("matches.{match_id}.round"):
            categories["Round/Stage"].append(field)
        elif field.startswith("matches.{match_id}.coverage"):
            categories["Coverage"].append(field)
        elif field.startswith("matches.{match_id}.events"):
            categories["Events"].append(field)
        elif field.startswith("matches.{match_id}") and any(x in field for x in ["match_id", "fetched_at", "venue", "referee", "neutral", "start_time"]):
            categories["Match Metadata"].append(field)
        elif not field.startswith("matches"):
            categories["Other"].append(field)
        else:
            categories["Other"].append(field)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

def main():
    """
    Main function to extract unique fields from step2.json
    """
    step2_path = "/root/Football_bot/Step2_extract_merge_summarize/step2.json"
    
    if not os.path.exists(step2_path):
        print(f"Error: {step2_path} not found!")
        return
    
    print("Loading step2.json...")
    with open(step2_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract unique fields
    print("Extracting unique field structure...")
    fields_set, samples = extract_unique_fields(data)
    
    # Organize fields by category
    categorized_fields = organize_fields(fields_set)
    
    # Print results
    print("\n" + "="*80)
    print("UNIQUE FIELD STRUCTURE FROM STEP2.JSON")
    print("="*80)
    
    print(f"\nTotal unique fields: {len(fields_set)}")
    
    for category, fields in categorized_fields.items():
        if fields:  # Only show non-empty categories
            print(f"\n{category} ({len(fields)} fields):")
            print("-" * (len(category) + 15))
            
            for field in fields:
                print(f"  {field}")
                
                # Show samples if available
                if field in samples:
                    for sample in samples[field][:2]:  # Show max 2 samples
                        print(f"    → {sample['type']}: {sample['value']}")
    
    # Save clean field structure
    output_file = "/root/Football_bot/Step3_json_summary/unique_fields_structure.json"
    
    # Create a clean structure for saving
    clean_structure = {
        "total_unique_fields": len(fields_set),
        "field_categories": categorized_fields,
        "all_fields": sorted(list(fields_set)),
        "sample_values": {k: v for k, v in samples.items() if v}
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_structure, f, indent=2)
    
    print(f"\n\nUnique field structure saved to: {output_file}")
    
    # Also create a simple text file with just the field paths
    text_output = "/root/Football_bot/Step3_json_summary/unique_fields_list.txt"
    with open(text_output, 'w') as f:
        f.write("UNIQUE FIELDS FROM STEP2.JSON\n")
        f.write("="*50 + "\n\n")
        
        for category, fields in categorized_fields.items():
            if fields:
                f.write(f"\n{category}:\n")
                f.write("-" * len(category) + "\n")
                for field in fields:
                    f.write(f"{field}\n")
    
    print(f"Simple field list saved to: {text_output}")

if __name__ == "__main__":
    main() 