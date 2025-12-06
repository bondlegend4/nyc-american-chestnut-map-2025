#!/usr/bin/env python3
"""
build_trees_from_survey.py

Combines survey data with geocoded locations to create final trees.json
"""

import pandas as pd
import json
from datetime import datetime

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
            'contact': 'conservation@nyc.gov'  # Default
        }

# Update contacts based on organization
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

# Parse survey data
trees = []
current_park = None
current_area = None
tree_counter = 1

print("\nParsing survey data...")
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
            print(f"  Warning: No coordinates for {current_park} > {current_area}")
            continue

        loc_data = location_lookup[loc_key]

        # Extract most recent measurement data
        # Try to find 2024 columns (usually near the end)
        height_2024 = None
        dbh_2024 = None
        notes = ""

        # Look for measurements in recent columns (20-26)
        for col_idx in range(20, min(27, len(row))):
            val = row[col_idx]
            if pd.notna(val):
                val_str = str(val).strip()
                if "'" in val_str or '"' in val_str or 'cm' in val_str.lower():
                    if not height_2024:
                        height_2024 = val_str
                    elif not dbh_2024:
                        dbh_2024 = val_str

        # Determine health status
        health_status = "unknown"
        if height_2024 or dbh_2024:
            health_status = "healthy"

        # Create measurement notes
        measurements = []
        if height_2024:
            measurements.append(f"Height: {height_2024}")
        if dbh_2024:
            measurements.append(f"DBH: {dbh_2024}")

        notes = f"Tree #{int(tree_num)}. " + ", ".join(measurements) if measurements else f"Tree #{int(tree_num)}"

        tree_id = f"NYC-AC-{tree_counter:03d}"
        tree_counter += 1

        # Add small offset to coordinates for trees in same location
        lat_offset = (hash(f"{tree_num}{current_area}") % 100) / 100000  # Small random offset
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
                "planted_date": "2020-01-01",  # Approximate
                "health_status": health_status,
                "contact": loc_data['contact'],
                "last_updated": "2024-12-20",
                "notes": notes,
                "borough": loc_data['borough'],
                "location_description": f"{current_park} - {current_area}"
            }
        }

        trees.append(tree)

print(f"\nExtracted {len(trees)} trees with valid coordinates")

# Create GeoJSON
geojson = {
    "type": "FeatureCollection",
    "metadata": {
        "title": "NYC American Chestnut Conservation Map",
        "description": "Tracking American Chestnut trees planted and maintained by various organizations across New York City",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "version": "1.0",
        "generated_from": "2024 year end chestnut results.xlsx",
        "survey_date": "2024-12-20",
        "notes": "Tree locations are approximate geocoded coordinates with small offsets for visualization"
    },
    "features": trees
}

# Save
output_file = "data/trees.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"\n✓ Successfully created {output_file}")
print(f"  Total trees: {len(trees)}")

# Print summary by organization
orgs = {}
for tree in trees:
    org = tree['properties']['organization']
    orgs[org] = orgs.get(org, 0) + 1

print("\nTrees by organization:")
for org, count in sorted(orgs.items(), key=lambda x: x[1], reverse=True):
    print(f"  {org}: {count}")
