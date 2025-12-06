#!/usr/bin/env python3
"""
build_trees_with_growth_data.py

Enhanced parser that extracts health status and multi-year growth measurements
from the survey to create interactive growth charts.
"""

import pandas as pd
import json
from datetime import datetime
import re

# Read survey data
print("Reading survey data...")
df_survey = pd.read_excel('2024 year end chestnut results.xlsx', header=None)

# Read geocoded locations
print("Reading geocoded locations...")
df_locations = pd.read_csv('survey_locations_geocoded.csv')

# Create lookup dictionary
location_lookup = {}
for _, row in df_locations.iterrows():
    key = (row['park'], row['area'])
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        location_lookup[key] = {
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'organization': row['organization'],
            'borough': row['borough'],
            'contact': 'conservation@nyc.gov'
        }

# Update contacts
contact_map = {
    'Prospect Park Alliance': 'info@prospectpark.org',
    'Brooklyn Botanic Garden': 'conservation@bbg.org',
    'Green-Wood Cemetery': 'info@green-wood.com',
    'NYC Parks': 'forestry@parks.nyc.gov'
}

for loc_data in location_lookup.values():
    org = loc_data['organization']
    if org in contact_map:
        loc_data['contact'] = contact_map[org]

def parse_measurement(val):
    """Convert measurement string to numeric value in inches or None"""
    if pd.isna(val):
        return None

    val_str = str(val).strip()

    # Try to extract numeric value
    # Handle formats like: "8'", ".5\"", "1.5", "11.7'"

    # Remove quotes and clean
    val_str = val_str.replace('"', '').replace("'", '').strip()

    # Try to extract number
    match = re.search(r'(\d+\.?\d*)', val_str)
    if match:
        try:
            return float(match.group(1))
        except:
            return None

    return None

def categorize_health_status(health_str):
    """
    Categorize detailed health string into badge category.

    Returns: (category, original_string)
    category: 'healthy', 'fair', 'poor', 'unknown'
    original_string: the actual text from the survey
    """
    if pd.isna(health_str) or not health_str:
        return 'unknown', None

    original = str(health_str).strip()
    lower = original.lower()

    # HEALTHY: Excellent/very good/good condition
    if any(word in lower for word in ['excellent', 'very good']):
        return 'healthy', original

    if 'good' in lower and 'blight' not in lower:
        return 'healthy', original

    # FAIR: Some issues but surviving
    if any(word in lower for word in ['fair', 'ok', 'maybe ok', 'multi stem']):
        return 'fair', original

    # FAIR: Has blight but still alive
    if 'blight' in lower and not any(word in lower for word in ['died', 'dead', 'severe', 'serious', 'significant']):
        return 'fair', original

    if 'good' in lower and 'blight' in lower:  # "good, may have blight"
        return 'fair', original

    # POOR: Severe issues, blight damage, or dead
    if any(word in lower for word in ['dead', 'died', 'gone', 'severe', 'serious', 'significant blight', 'poor']):
        return 'poor', original

    # UNKNOWN: Uncertain status
    if any(word in lower for word in ['check in spring', 'not sure', 'greenhouse', 'may be', 'might be']):
        return 'unknown', original

    # Default to unknown for anything else
    return 'unknown', original

# Column mapping based on header structure
# Row 7-8 shows: 2021 (cols 2-4), 2022 (cols 5-7), 2023 (cols 8-10), 2024 (cols 12-16)
YEAR_COLUMNS = {
    '2021': {'height': 2, 'dbh': 3},
    '2022': {'height': 5, 'dbh': 6},
    '2023': {'height': 8, 'dbh': 9},
    '2024': {'height': 12, 'dbh': 13, 'health': 16}
}

# Parse survey data
trees = []
current_park = None
current_area = None
tree_counter = 1

print("\nParsing survey data with growth measurements...")
for idx, row in df_survey.iterrows():
    first_col = str(row[0]).strip() if pd.notna(row[0]) else ''

    # Check for park header
    if first_col.isupper() and ':' not in first_col and len(first_col) > 5:
        current_park = first_col
        current_area = None
        continue

    # Check for area header
    if first_col.endswith(':'):
        current_area = first_col.rstrip(':')
        continue

    # Check for tree data row (has tree number in column 1)
    tree_num = row[1]
    if pd.notna(tree_num) and isinstance(tree_num, (int, float)):
        # Get location data
        if not current_park or not current_area:
            continue

        loc_key = (current_park, current_area)
        if loc_key not in location_lookup:
            continue

        loc_data = location_lookup[loc_key]

        # Extract measurements for all years
        growth_data = {}
        has_recent_data = False

        for year, cols in YEAR_COLUMNS.items():
            height = parse_measurement(row[cols['height']]) if cols['height'] < len(row) else None
            dbh = parse_measurement(row[cols['dbh']]) if cols['dbh'] < len(row) else None

            if height is not None or dbh is not None:
                growth_data[year] = {
                    'height': height,
                    'dbh': dbh
                }

                if year == '2024':
                    has_recent_data = True

        # Get health status from 2024 column
        health_col = row[16] if len(row) > 16 else None
        health_category, health_detail = categorize_health_status(health_col)

        # Infer category from data if no explicit status
        if health_category == 'unknown' and has_recent_data:
            health_category = 'healthy'

        # Create measurement summary for notes
        latest_year = '2024' if '2024' in growth_data else max(growth_data.keys()) if growth_data else None
        notes_parts = [f"Tree #{int(tree_num)}"]

        if latest_year and latest_year in growth_data:
            data = growth_data[latest_year]
            if data['height']:
                notes_parts.append(f"Height: {data['height']}'")
            if data['dbh']:
                notes_parts.append(f"DBH: {data['dbh']}\"")

        # Don't add status to notes - will be displayed separately in popup

        tree_id = f"NYC-AC-{tree_counter:03d}"
        tree_counter += 1

        # Add small offset to coordinates
        lat_offset = (hash(f"{tree_num}{current_area}") % 100) / 100000
        lon_offset = (hash(f"{tree_num}{current_park}") % 100) / 100000

        tree = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    loc_data['longitude'] + lon_offset,
                    loc_data['latitude'] + lat_offset
                ]
            },
            "properties": {
                "tree_id": tree_id,
                "organization": loc_data['organization'],
                "tree_number": int(tree_num),
                "planted_date": "2020-01-01",
                "health_status": health_category,  # Badge category: healthy/fair/poor/unknown
                "health_detail": health_detail,     # Original survey text
                "contact": loc_data['contact'],
                "last_updated": "2024-12-20",
                "notes": ", ".join(notes_parts),
                "borough": loc_data['borough'],
                "location_description": f"{current_park} - {current_area}",
                "growth_data": growth_data  # Add multi-year growth data
            }
        }

        trees.append(tree)

print(f"\nExtracted {len(trees)} trees with growth data")

# Count trees with growth measurements
trees_with_data = sum(1 for t in trees if t['properties']['growth_data'])
print(f"  Trees with measurement data: {trees_with_data}")

# Create GeoJSON
geojson = {
    "type": "FeatureCollection",
    "metadata": {
        "title": "NYC American Chestnut Conservation Map",
        "description": "Tracking American Chestnut trees planted and maintained by various organizations across New York City",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "version": "2.0",
        "generated_from": "2024 year end chestnut results.xlsx",
        "survey_date": "2024-12-20",
        "notes": "Includes multi-year growth data (2021-2024) and health status assessments",
        "data_fields": {
            "growth_data": "Object with yearly height (feet) and DBH (inches) measurements",
            "health_status": "Current assessment: healthy, fair, poor, or unknown"
        }
    },
    "features": trees
}

# Save
output_file = "data/trees.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"\n✓ Successfully created {output_file}")
print(f"  Total trees: {len(trees)}")

# Print summary statistics
health_counts = {}
for tree in trees:
    health = tree['properties']['health_status']
    health_counts[health] = health_counts.get(health, 0) + 1

print("\nHealth status distribution:")
for status, count in sorted(health_counts.items()):
    print(f"  {status}: {count}")

# Print summary by organization
orgs = {}
for tree in trees:
    org = tree['properties']['organization']
    orgs[org] = orgs.get(org, 0) + 1

print("\nTrees by organization:")
for org, count in sorted(orgs.items(), key=lambda x: x[1], reverse=True):
    print(f"  {org}: {count}")
