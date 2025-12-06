#!/usr/bin/env python3
"""
parse_survey.py

Custom parser for the "2024 year end chestnut results.xlsx" survey format.
Extracts tree data and creates a properly formatted trees.json file.
"""

import pandas as pd
import json
from datetime import datetime

# Read the Excel file
print("Reading Excel file...")
df = pd.read_excel('2024 year end chestnut results.xlsx', header=None)

# Manual location data (since it's not in the Excel file)
# This will need to be filled in with actual coordinates
LOCATION_DATA = {
    "PROSPECT PARK": {
        "Sugar Bowl": {
            "latitude": 40.6551,
            "longitude": -73.9509,
            "borough": "Brooklyn",
            "organization": "Prospect Park Alliance"
        }
    }
}

# Parse the data
trees = []
current_location = None
current_sublocation = None
tree_counter = 1

print("\nParsing survey data...")
for idx, row in df.iterrows():
    # Check if this is a location header (all caps in first column)
    first_col = str(row[0]).strip() if pd.notna(row[0]) else ""

    if first_col.isupper() and len(first_col) > 3:
        current_location = first_col
        print(f"Found location: {current_location}")
        continue

    # Check if this is a sublocation (ends with colon)
    if first_col.endswith(":"):
        current_sublocation = first_col.rstrip(":")
        print(f"  Found sublocation: {current_sublocation}")
        continue

    # Check if this row has tree data (has a tree number in column 1)
    tree_num = row[1]
    if pd.notna(tree_num) and isinstance(tree_num, (int, float)):
        # Extract 2024 data (latest columns)
        # Columns around 20-26 should have 2024 data
        height_2024 = row[20] if len(row) > 20 and pd.notna(row[20]) else None
        dbh_2024 = row[21] if len(row) > 21 and pd.notna(row[21]) else None
        notes_2024 = row[22] if len(row) > 22 and pd.notna(row[22]) else ""

        # Determine health status based on available data
        health_status = "unknown"
        if height_2024 or dbh_2024:
            health_status = "healthy"  # Has recent measurements

        # Get location data
        loc_data = None
        if current_location in LOCATION_DATA:
            if current_sublocation in LOCATION_DATA[current_location]:
                loc_data = LOCATION_DATA[current_location][current_sublocation]

        if not loc_data:
            # Default to unknown location
            print(f"  Warning: No coordinates for {current_location} > {current_sublocation}, tree {tree_num}")
            continue

        tree_id = f"NYC-AC-{tree_counter:03d}"
        tree_counter += 1

        tree = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc_data["longitude"], loc_data["latitude"]]
            },
            "properties": {
                "tree_id": tree_id,
                "organization": loc_data["organization"],
                "tree_number": int(tree_num),
                "planted_date": "2021-01-01",  # Approximate based on survey start
                "health_status": health_status,
                "contact": "info@prospectpark.org",  # Default contact
                "last_updated": "2024-12-20",
                "notes": f"Survey tree #{int(tree_num)}. Height: {height_2024}, DBH: {dbh_2024}. {notes_2024}".strip(),
                "borough": loc_data["borough"],
                "location_description": f"{current_location} - {current_sublocation}"
            }
        }

        trees.append(tree)

print(f"\nExtracted {len(trees)} trees from survey")

# Create GeoJSON structure
geojson = {
    "type": "FeatureCollection",
    "metadata": {
        "title": "NYC American Chestnut Conservation Map",
        "description": "Tracking American Chestnut trees planted and maintained by various organizations across New York City",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "version": "1.0",
        "generated_from": "2024 year end chestnut results.xlsx",
        "survey_date": "2024-12-20"
    },
    "features": trees
}

# Save to file
output_file = "data/trees_from_survey.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"\n✓ Successfully created {output_file}")
print(f"  Total trees: {len(trees)}")
print("\nNOTE: This file only includes trees with known coordinates.")
print("You need to add location data for other survey sites in the LOCATION_DATA dictionary.")
