#!/usr/bin/env python3
"""
build_trees_with_accuracy.py

Enhanced version that validates coordinates against park boundaries
and adds accuracy indicators to each tree.
"""

import pandas as pd
import json
from datetime import datetime
import re
import sys

# Import park boundary functions
from park_boundaries import (
    get_area_center,
    is_point_in_park,
    calculate_accuracy_level,
    generate_dispersed_coordinates,
    PARK_BOUNDARIES
)

# Read survey data
print("Reading survey data...")
df_survey = pd.read_excel('2024 year end chestnut results.xlsx', header=None)

# Read geocoded locations
print("Reading geocoded locations...")
df_locations = pd.read_csv('survey_locations_geocoded.csv')

# Update contact map
contact_map = {
    'Prospect Park Alliance': 'info@prospectpark.org',
    'Brooklyn Botanic Garden': 'conservation@bbg.org',
    'Green-Wood Cemetery': 'info@green-wood.com',
    'NYC Parks': 'forestry@parks.nyc.gov'
}

def parse_measurement(val):
    """Convert measurement string to numeric value"""
    if pd.isna(val):
        return None
    val_str = str(val).strip().replace('"', '').replace("'", '').strip()
    match = re.search(r'(\d+\.?\d*)', val_str)
    if match:
        try:
            return float(match.group(1))
        except:
            return None
    return None

def categorize_health_status(health_str):
    """Categorize health string into badge category"""
    if pd.isna(health_str) or not health_str:
        return 'unknown', None

    original = str(health_str).strip()
    lower = original.lower()

    if any(word in lower for word in ['excellent', 'very good']):
        return 'healthy', original
    if 'good' in lower and 'blight' not in lower:
        return 'healthy', original
    if any(word in lower for word in ['fair', 'ok', 'maybe ok', 'multi stem']):
        return 'fair', original
    if 'blight' in lower and not any(word in lower for word in ['died', 'dead', 'severe', 'serious', 'significant']):
        return 'fair', original
    if 'good' in lower and 'blight' in lower:
        return 'fair', original
    if any(word in lower for word in ['dead', 'died', 'gone', 'severe', 'serious', 'significant blight', 'poor']):
        return 'poor', original
    if any(word in lower for word in ['check in spring', 'not sure', 'greenhouse', 'may be', 'might be']):
        return 'unknown', original

    return 'unknown', original

# Column mapping
YEAR_COLUMNS = {
    '2021': {'height': 2, 'dbh': 3},
    '2022': {'height': 5, 'dbh': 6},
    '2023': {'height': 8, 'dbh': 9},
    '2024': {'height': 12, 'dbh': 13, 'health': 16}
}

# Build location lookup with improved coordinates
print("\nValidating and improving coordinates...")
location_lookup = {}
trees_by_location = {}  # Track how many trees per location for dispersion

for _, row in df_locations.iterrows():
    park = row['park']
    area = row['area']
    key = (park, area)

    if pd.isna(row['latitude']) or pd.isna(row['longitude']):
        print(f"  ⚠️  No coordinates for {park} > {area}")
        continue

    # Try to get better coordinates from park boundaries
    better_coords = get_area_center(park, area)

    if better_coords:
        lat, lon = better_coords
        print(f"  ✓ Using area center for {park} > {area}: ({lat:.4f}, {lon:.4f})")
    else:
        # Use geocoded coordinates but warn
        lat, lon = row['latitude'], row['longitude']
        print(f"  ⚠️  Using geocoded coords for {park} > {area}: ({lat:.4f}, {lon:.4f})")

    # Validate coordinates
    is_valid, distance = is_point_in_park(lat, lon, park)
    if not is_valid:
        print(f"      WARNING: Coordinates outside park boundary (distance: {distance}m)")

    location_lookup[key] = {
        'center_lat': lat,
        'center_lon': lon,
        'organization': row['organization'],
        'borough': row['borough'],
        'contact': contact_map.get(row['organization'], 'conservation@nyc.gov')
    }

    trees_by_location[key] = 0  # Initialize tree counter

# First pass: count trees per location
print("\nCounting trees per location...")
current_park = None
current_area = None

for idx, row in df_survey.iterrows():
    first_col = str(row[0]).strip() if pd.notna(row[0]) else ''

    if first_col.isupper() and ':' not in first_col and len(first_col) > 5:
        current_park = first_col
        current_area = None
        continue

    if first_col.endswith(':'):
        current_area = first_col.rstrip(':')
        continue

    tree_num = row[1]
    if pd.notna(tree_num) and isinstance(tree_num, (int, float)):
        if current_park and current_area:
            loc_key = (current_park, current_area)
            if loc_key in trees_by_location:
                trees_by_location[loc_key] += 1

# Generate dispersed coordinates for each location
print("\nGenerating dispersed coordinates...")
location_coords = {}

for loc_key, num_trees in trees_by_location.items():
    if loc_key in location_lookup and num_trees > 0:
        loc_data = location_lookup[loc_key]
        park_name = loc_key[0]  # Extract park name from location key

        coords_list = generate_dispersed_coordinates(
            loc_data['center_lat'],
            loc_data['center_lon'],
            num_trees,
            radius_meters=50,  # 50m dispersion radius
            park_name=park_name  # Pass park name for boundary validation
        )
        location_coords[loc_key] = coords_list

        # Count how many coords are valid
        valid_count = sum(1 for lat, lon in coords_list if is_point_in_park(lat, lon, park_name)[0])
        print(f"  {park_name} > {loc_key[1]}: {num_trees} trees, {valid_count}/{num_trees} within bounds")

# Second pass: parse and build trees with dispersed coords
print("\nParsing survey data with dispersed coordinates...")
trees = []
current_park = None
current_area = None
tree_counter = 1
location_indices = {}  # Track which coord index to use per location

for idx, row in df_survey.iterrows():
    first_col = str(row[0]).strip() if pd.notna(row[0]) else ''

    if first_col.isupper() and ':' not in first_col and len(first_col) > 5:
        current_park = first_col
        current_area = None
        continue

    if first_col.endswith(':'):
        current_area = first_col.rstrip(':')
        continue

    tree_num = row[1]
    if pd.notna(tree_num) and isinstance(tree_num, (int, float)):
        if not current_park or not current_area:
            continue

        loc_key = (current_park, current_area)
        if loc_key not in location_lookup or loc_key not in location_coords:
            continue

        loc_data = location_lookup[loc_key]

        # Get next dispersed coordinate for this location
        if loc_key not in location_indices:
            location_indices[loc_key] = 0

        coord_idx = location_indices[loc_key]
        if coord_idx >= len(location_coords[loc_key]):
            print(f"  Warning: More trees than coords for {loc_key}")
            continue

        lat, lon = location_coords[loc_key][coord_idx]
        location_indices[loc_key] += 1

        # Calculate accuracy
        accuracy = calculate_accuracy_level(current_park, current_area, lat, lon, is_confirmed=False)

        # Extract growth data
        growth_data = {}
        has_recent_data = False

        for year, cols in YEAR_COLUMNS.items():
            height = parse_measurement(row[cols['height']]) if cols['height'] < len(row) else None
            dbh = parse_measurement(row[cols['dbh']]) if cols['dbh'] < len(row) else None

            if height is not None or dbh is not None:
                growth_data[year] = {'height': height, 'dbh': dbh}
                if year == '2024':
                    has_recent_data = True

        # Get health status
        health_col = row[16] if len(row) > 16 else None
        health_category, health_detail = categorize_health_status(health_col)

        if health_category == 'unknown' and has_recent_data:
            health_category = 'healthy'

        # Create notes
        latest_year = '2024' if '2024' in growth_data else max(growth_data.keys()) if growth_data else None
        notes_parts = [f"Tree #{int(tree_num)}"]

        if latest_year and latest_year in growth_data:
            data = growth_data[latest_year]
            if data['height']:
                notes_parts.append(f"Height: {data['height']}'")
            if data['dbh']:
                notes_parts.append(f"DBH: {data['dbh']}\"")

        tree_id = f"NYC-AC-{tree_counter:03d}"
        tree_counter += 1

        tree = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]  # GeoJSON order: [lon, lat]
            },
            "properties": {
                "tree_id": tree_id,
                "organization": loc_data['organization'],
                "tree_number": int(tree_num),
                "planted_date": "2020-01-01",
                "health_status": health_category,
                "health_detail": health_detail,
                "contact": loc_data['contact'],
                "last_updated": "2024-12-20",
                "notes": ", ".join(notes_parts),
                "borough": loc_data['borough'],
                "location_description": f"{current_park} - {current_area}",
                "growth_data": growth_data,
                "location_accuracy": accuracy  # NEW: Accuracy information
            }
        }

        trees.append(tree)

print(f"\nExtracted {len(trees)} trees with validated coordinates")

# Create GeoJSON
geojson = {
    "type": "FeatureCollection",
    "metadata": {
        "title": "NYC American Chestnut Conservation Map",
        "description": "Tracking American Chestnut trees planted and maintained by various organizations across New York City",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "version": "3.0",
        "generated_from": "2024 year end chestnut results.xlsx",
        "survey_date": "2024-12-20",
        "notes": "Tree locations dispersed within park boundaries using spiral pattern. Accuracy levels indicate coordinate precision.",
        "accuracy_levels": {
            "confirmed": "GPS-verified location (±5m)",
            "area": "Geocoded to specific park area (±50m)",
            "park": "Geocoded to park center (±100m)",
            "estimated": "Estimated location outside park boundaries"
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

# Print accuracy summary
accuracy_counts = {}
for tree in trees:
    acc = tree['properties']['location_accuracy']['level']
    accuracy_counts[acc] = accuracy_counts.get(acc, 0) + 1

print("\nLocation accuracy distribution:")
for level, count in sorted(accuracy_counts.items()):
    print(f"  {level}: {count}")

# Print health summary
health_counts = {}
for tree in trees:
    health = tree['properties']['health_status']
    health_counts[health] = health_counts.get(health, 0) + 1

print("\nHealth status distribution:")
for status, count in sorted(health_counts.items()):
    print(f"  {status}: {count}")
