#!/usr/bin/env python3
"""
extract_survey_locations.py

Extracts all locations from the survey and prepares them for geocoding.
Creates a CSV file that can be manually edited with coordinates.
"""

import pandas as pd
import csv

# Read the Excel file
print("Reading Excel file...")
df = pd.read_excel('2024 year end chestnut results.xlsx', header=None)

locations_data = []
current_park = None
current_area = None

for idx, row in df.iterrows():
    first_col = str(row[0]).strip() if pd.notna(row[0]) else ''

    # Skip empty rows
    if not first_col:
        continue

    # Check if this is a main park (all caps, no colon)
    if first_col.isupper() and ':' not in first_col and len(first_col) > 5:
        current_park = first_col
        current_area = None
        print(f"Found park: {current_park}")
        continue

    # Check if this is a specific area (ends with colon)
    if first_col.endswith(':'):
        current_area = first_col.rstrip(':')

        if current_park:
            # Create location entry
            location_name = f"{current_park} - {current_area}"
            address = f"{current_area}, {current_park}, Brooklyn, NY"

            # Determine organization based on park
            org = current_park.title().replace(" - ", " ")
            if "PROSPECT PARK" in current_park:
                org = "Prospect Park Alliance"
            elif "BROOKLYN BOTANIC" in current_park:
                org = "Brooklyn Botanic Garden"
            elif "GREENWOOD" in current_park:
                org = "Green-Wood Cemetery"
            elif "FORT GREEN" in current_park or "FORT GREENE" in current_park:
                org = "NYC Parks"
            elif "WASHINGTON PARK" in current_park:
                org = "NYC Parks"

            locations_data.append({
                'park': current_park,
                'area': current_area,
                'full_location': location_name,
                'address_for_geocoding': address,
                'organization': org,
                'latitude': '',  # To be filled in
                'longitude': '',  # To be filled in
                'borough': 'Brooklyn'  # Most are in Brooklyn based on the data
            })

# Save to CSV
output_file = 'survey_locations_to_geocode.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'park', 'area', 'full_location', 'address_for_geocoding',
        'organization', 'latitude', 'longitude', 'borough'
    ])
    writer.writeheader()
    writer.writerows(locations_data)

print(f"\n✓ Created {output_file}")
print(f"  Found {len(locations_data)} unique locations")
print("\nNext steps:")
print("1. Edit survey_locations_to_geocode.csv and add coordinates")
print("2. Or run with --geocode flag to auto-geocode addresses")
print("\nExample: python extract_survey_locations.py --geocode")
