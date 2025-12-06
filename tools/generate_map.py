#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_map.py

Converts CSV or Excel data to GeoJSON format for the NYC American Chestnut Map.
Optionally geocodes addresses if coordinates are not provided.

Usage:
    python generate_map.py input.csv
    python generate_map.py input.xlsx --geocode
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Optional dependencies - will gracefully degrade if not installed
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not installed. Install with: pip install pandas")

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    import time
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False
    print("Warning: geopy not installed. Geocoding disabled. Install with: pip install geopy")


def geocode_address(address, geolocator):
    """
    Geocodes an address to latitude/longitude coordinates.

    Args:
        address (str): Address to geocode
        geolocator: Nominatim geolocator instance

    Returns:
        tuple: (latitude, longitude) or (None, None) on failure
    """
    if not HAS_GEOPY or not address:
        return None, None

    try:
        print(f"  Geocoding: {address}")
        location = geolocator.geocode(address + ", New York City, NY", timeout=10)
        if location:
            print(f"    ✓ Found: ({location.latitude}, {location.longitude})")
            time.sleep(1)  # Respect rate limits
            return location.latitude, location.longitude
        else:
            print(f"    ✗ Not found")
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"    ✗ Geocoding error: {e}")
        return None, None


def csv_to_geojson(input_file, output_file='data/trees.json', geocode=False):
    """
    Converts CSV/Excel file to GeoJSON format.

    Expected CSV columns:
        - tree_id (required)
        - organization (required)
        - latitude (required if not geocoding)
        - longitude (required if not geocoding)
        - address (required if geocoding)
        - planted_date (YYYY-MM-DD format)
        - health_status (healthy/fair/poor/unknown)
        - contact (email)
        - notes (optional)
        - borough (optional)
        - location_description (optional)
    """
    if not HAS_PANDAS:
        print("Error: pandas is required. Install with: pip install pandas openpyxl")
        return False

    # Read input file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        return False

    print(f"Reading {input_file}...")
    try:
        if input_path.suffix.lower() == '.csv':
            df = pd.read_csv(input_file)
        elif input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        else:
            print(f"Error: Unsupported file format: {input_path.suffix}")
            return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    print(f"  Loaded {len(df)} rows")

    # Initialize geocoder if needed
    geolocator = None
    if geocode and HAS_GEOPY:
        geolocator = Nominatim(user_agent="nyc_chestnut_map_generator")
        print("Geocoding enabled")

    # Build GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "NYC American Chestnut Conservation Map",
            "description": "Tracking American Chestnut trees planted and maintained by various organizations across New York City",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0",
            "generated_from": input_file
        },
        "features": []
    }

    skipped = 0
    geocoded_count = 0

    for idx, row in df.iterrows():
        # Required fields
        tree_id = row.get('tree_id')
        organization = row.get('organization')

        if pd.isna(tree_id) or pd.isna(organization):
            print(f"  Warning: Row {idx+2} missing required fields (tree_id or organization), skipping")
            skipped += 1
            continue

        # Get coordinates
        lat = row.get('latitude')
        lon = row.get('longitude')

        # Try geocoding if coordinates missing
        if (pd.isna(lat) or pd.isna(lon)) and geocode and geolocator:
            address = row.get('address') or row.get('location_description')
            if not pd.isna(address):
                lat, lon = geocode_address(str(address), geolocator)
                if lat and lon:
                    geocoded_count += 1

        # Skip if still no coordinates
        if pd.isna(lat) or pd.isna(lon):
            print(f"  Warning: Row {idx+2} (ID: {tree_id}) has no coordinates, skipping")
            skipped += 1
            continue

        # Build feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon), float(lat)]  # GeoJSON is [lon, lat]
            },
            "properties": {
                "tree_id": str(tree_id),
                "organization": str(organization),
                "species": "Castanea dentata",  # American Chestnut
                "health_status": str(row.get('health_status', 'unknown')).lower(),
                "contact": str(row.get('contact', 'conservation@nyc.gov')),
                "planted_date": str(row.get('planted_date', '')),
                "last_updated": str(row.get('last_updated', datetime.now().strftime("%Y-%m-%d"))),
                "notes": str(row.get('notes', '')) if not pd.isna(row.get('notes')) else '',
                "borough": str(row.get('borough', '')) if not pd.isna(row.get('borough')) else '',
                "location_description": str(row.get('location_description', '')) if not pd.isna(row.get('location_description')) else ''
            }
        }

        geojson["features"].append(feature)

    # Write output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully created {output_file}")
    print(f"  Total trees: {len(geojson['features'])}")
    print(f"  Skipped rows: {skipped}")
    if geocoded_count > 0:
        print(f"  Geocoded addresses: {geocoded_count}")

    return True


def create_sample_csv():
    """Creates a sample CSV template for user reference."""
    sample_data = """tree_id,organization,latitude,longitude,planted_date,health_status,contact,notes,borough,location_description
NYC-AC-001,NYC Parks,40.7831,-73.9712,2023-04-15,healthy,forestry@parks.nyc.gov,Young sapling showing strong growth,Manhattan,Central Park North Woods
NYC-AC-002,Million Trees NYC,40.8033,-73.9626,2022-10-08,healthy,info@milliontreesnyc.org,Community planting event,Manhattan,Morningside Park
NYC-AC-003,Brooklyn Botanic Garden,40.6829,-73.9654,2021-05-12,healthy,conservation@bbg.org,Part of native plant collection,Brooklyn,Brooklyn Botanic Garden grounds
"""

    with open('sample_trees.csv', 'w') as f:
        f.write(sample_data)

    print("Created sample_trees.csv template")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert CSV/Excel tree data to GeoJSON for NYC American Chestnut Map"
    )
    parser.add_argument('input_file', nargs='?', help='Input CSV or Excel file')
    parser.add_argument('-o', '--output', default='data/trees.json',
                       help='Output GeoJSON file (default: data/trees.json)')
    parser.add_argument('--geocode', action='store_true',
                       help='Geocode addresses to coordinates (requires geopy)')
    parser.add_argument('--sample', action='store_true',
                       help='Create sample CSV template')

    args = parser.parse_args()

    if args.sample:
        create_sample_csv()
        sys.exit(0)

    if not args.input_file:
        parser.print_help()
        print("\nExample usage:")
        print("  python generate_map.py trees.csv")
        print("  python generate_map.py trees.xlsx --geocode")
        print("  python generate_map.py --sample  # Create template CSV")
        sys.exit(1)

    success = csv_to_geojson(args.input_file, args.output, args.geocode)
    sys.exit(0 if success else 1)
