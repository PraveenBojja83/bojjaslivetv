#!/usr/bin/env python3
"""
Remove all 'adult' category entries from LiveTV JSON files.
This ensures adult content is completely removed and won't show in category dropdown.
"""

import json
import os
from pathlib import Path

livetv_dir = Path(__file__).parent.parent / 'LiveTV'

def clean_adult_from_file(filepath):
    """Remove all entries with 'adult' group from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return 0
    
    removed_count = 0
    
    if isinstance(data, dict) and 'channels' in data:
        channels = data['channels']
        
        # Remove 'adult' group entirely
        if 'adult' in channels:
            removed_count += len(channels['adult'])
            del channels['adult']
        
        # Also check for case variations (Adult, ADULT, etc)
        keys_to_remove = [k for k in channels.keys() if k.lower() == 'adult']
        for k in keys_to_remove:
            removed_count += len(channels[k])
            del channels[k]
        
        # Write back the cleaned data
        if removed_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    return removed_count

# Process all country JSON files
total_removed = 0
for country_dir in livetv_dir.iterdir():
    if country_dir.is_dir():
        json_file = country_dir / 'LiveTV.json'
        if json_file.exists():
            count = clean_adult_from_file(json_file)
            if count > 0:
                print(f"✓ {country_dir.name}: removed {count} adult channels")
                total_removed += count

print(f"\nTotal adult channels removed: {total_removed}")
print("Adult content has been completely purged from all LiveTV folders!")
