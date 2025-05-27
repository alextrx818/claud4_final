#!/usr/bin/env python3
"""
Test script to extract and identify all JSON fields from step2.json
This will help us understand the complete structure of data coming from Step 2
"""

import json
import os
from typing import Dict, List, Set, Any
from collections import defaultdict

def extract_all_fields(obj: Any, path: str = "", fields_dict: Dict[str, Set[Any]] = None) -> Dict[str, Set[Any]]:
    """
    Recursively extract all field paths and their types from a JSON object
    """
    if fields_dict is None:
        fields_dict = defaultdict(set)
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            fields_dict[current_path].add(type(value).__name__)
            
            # Recursively process nested structures
            if isinstance(value, (dict, list)):
                extract_all_fields(value, current_path, fields_dict)
            else:
                # Store sample values for leaf nodes
                if len(fields_dict[f"{current_path}_samples"]) < 3:
                    fields_dict[f"{current_path}_samples"].add(str(value)[:100])
                    
    elif isinstance(obj, list) and obj:
        # Process first item in list to understand structure
        fields_dict[f"{path}[]"].add("list")
        if obj:
            extract_all_fields(obj[0], f"{path}[]", fields_dict)
    
    return fields_dict

def analyze_step2_json():
    """
    Main function to analyze step2.json structure
    """
    # Path to step2.json
    step2_path = "/root/Football_bot/Step2_extract_merge_summarize/step2.json"
    
    if not os.path.exists(step2_path):
        print(f"Error: {step2_path} not found!")
        return
    
    print("Loading step2.json...")
    with open(step2_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\nTop-level structure:")
    print(f"- Type: {type(data).__name__}")
    print(f"- Keys: {list(data.keys())}")
    
    # Extract all fields
    print("\nExtracting all field paths...")
    all_fields = extract_all_fields(data)
    
    # Organize fields by category
    print("\n" + "="*80)
    print("COMPLETE FIELD STRUCTURE FROM STEP2.JSON")
    print("="*80)
    
    # Group fields by main sections
    field_categories = defaultdict(list)
    for field_path in sorted(all_fields.keys()):
        if "_samples" not in field_path:
            # Categorize by top-level section
            if field_path.startswith("matches"):
                category = "Match Data Fields"
            elif field_path.startswith("timestamp"):
                category = "Metadata Fields"
            elif field_path.startswith("total_"):
                category = "Summary Fields"
            else:
                category = "Other Fields"
            
            field_categories[category].append(field_path)
    
    # Print organized field structure
    for category, fields in field_categories.items():
        print(f"\n{category}:")
        print("-" * len(category))
        
        for field in sorted(fields):
            types = all_fields[field]
            print(f"  {field} -> {', '.join(types)}")
            
            # Show sample values for leaf nodes
            samples_key = f"{field}_samples"
            if samples_key in all_fields and all_fields[samples_key]:
                samples = list(all_fields[samples_key])[:3]
                for sample in samples:
                    print(f"    Sample: {sample}")
    
    # Analyze match structure in detail
    print("\n" + "="*80)
    print("DETAILED MATCH STRUCTURE")
    print("="*80)
    
    if "matches" in data and isinstance(data["matches"], dict):
        # Get first match for detailed analysis
        first_match_id = list(data["matches"].keys())[0]
        first_match = data["matches"][first_match_id]
        
        print(f"\nAnalyzing match: {first_match_id}")
        print("\nMatch fields:")
        
        def print_structure(obj, indent=0):
            """Pretty print JSON structure"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, dict):
                        print("  " * indent + f"{key}:")
                        print_structure(value, indent + 1)
                    elif isinstance(value, list):
                        print("  " * indent + f"{key}: [{len(value)} items]")
                        if value and isinstance(value[0], dict):
                            print("  " * (indent + 1) + "Item structure:")
                            print_structure(value[0], indent + 2)
                    else:
                        print("  " * indent + f"{key}: {type(value).__name__} = {str(value)[:50]}")
        
        print_structure(first_match)
    
    # Summary statistics
    print("\n" + "="*80)
    print("FIELD STATISTICS")
    print("="*80)
    
    total_fields = len([f for f in all_fields.keys() if "_samples" not in f])
    print(f"\nTotal unique field paths: {total_fields}")
    
    # Count fields by depth
    depth_counts = defaultdict(int)
    for field in all_fields.keys():
        if "_samples" not in field:
            depth = field.count('.') + field.count('[')
            depth_counts[depth] += 1
    
    print("\nFields by depth level:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Level {depth}: {depth_counts[depth]} fields")
    
    # Save field structure to file
    output_file = "/root/Football_bot/Step3_json_summary/step2_field_structure.json"
    field_structure = {
        "total_fields": total_fields,
        "field_paths": sorted([f for f in all_fields.keys() if "_samples" not in f]),
        "field_types": {k: list(v) for k, v in all_fields.items() if "_samples" not in k},
        "sample_values": {k.replace("_samples", ""): list(v) for k, v in all_fields.items() if "_samples" in k and v}
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(field_structure, f, indent=2)
    
    print(f"\nField structure saved to: {output_file}")

if __name__ == "__main__":
    analyze_step2_json() 