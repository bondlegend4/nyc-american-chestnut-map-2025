#!/usr/bin/env python3
"""
ArcGIS Feature Service Importer for NYC American Chestnut Map

This script imports tree data from an ArcGIS Feature Service and converts it
to the trees.json format used by the interactive map.

Supports:
- ArcGIS Online Feature Services
- ArcGIS Enterprise REST API
- GeoJSON from ArcGIS
- Shapefile exports from ArcGIS

Usage:
    python3 scripts/import_from_arcgis.py --url <feature-service-url>
    python3 scripts/import_from_arcgis.py --file arcgis_export.geojson
    python3 scripts/import_from_arcgis.py --shapefile trees.shp
"""

import json
import sys
import argparse
import requests
from datetime import datetime
from pathlib import Path

# Import park boundaries for validation
try:
    from park_boundaries import is_point_in_park, PARK_BOUNDARIES
except ImportError:
    print("Warning: park_boundaries.py not found. Coordinate validation disabled.")
    PARK_BOUNDARIES = {}
    def is_point_in_park(lat, lon, park_name):
        return (True, 0)


# Field mapping: ArcGIS field names → our field names
# Customize these based on your ArcGIS layer's field names
FIELD_MAPPING = {
    # Required fields
    'tree_id': ['OBJECTID', 'TreeID', 'ID', 'tree_id', 'FID'],
    'organization': ['Organization', 'Org', 'Agency', 'organization', 'ORGANIZATION'],
    'health_status': ['Health', 'HealthStatus', 'health_status', 'HEALTH', 'Condition'],

    # Location fields
    'latitude': ['Latitude', 'LAT', 'Y', 'latitude', 'LATITUDE'],
    'longitude': ['Longitude', 'LON', 'LONG', 'X', 'longitude', 'LONGITUDE'],

    # Optional fields
    'planted_date': ['PlantedDate', 'DatePlanted', 'planted_date', 'PLANTED', 'InstallDate'],
    'last_updated': ['LastUpdate', 'UpdateDate', 'last_updated', 'LAST_UPDATE', 'ModifiedDate'],
    'notes': ['Notes', 'Comments', 'Description', 'notes', 'NOTES'],
    'location_description': ['Location', 'LocationDesc', 'location_description', 'LOCATION', 'SiteName'],
    'contact': ['Contact', 'Email', 'ContactEmail', 'contact', 'CONTACT'],

    # Growth data fields (if available)
    'height_2021': ['Height2021', 'Height_2021', 'HT2021'],
    'dbh_2021': ['DBH2021', 'DBH_2021', 'Diameter2021'],
    'height_2022': ['Height2022', 'Height_2022', 'HT2022'],
    'dbh_2022': ['DBH2022', 'DBH_2022', 'Diameter2022'],
    'height_2023': ['Height2023', 'Height_2023', 'HT2023'],
    'dbh_2023': ['DBH2023', 'DBH_2023', 'Diameter2023'],
    'height_2024': ['Height2024', 'Height_2024', 'HT2024'],
    'dbh_2024': ['DBH2024', 'DBH_2024', 'Diameter2024'],

    # Park/Area identifiers
    'park': ['Park', 'ParkName', 'park', 'PARK'],
    'area': ['Area', 'AreaName', 'area', 'AREA', 'Zone'],
    'tree_number': ['TreeNumber', 'TreeNum', 'tree_number', 'Number']
}

# Health status mapping: ArcGIS values → our standardized values
HEALTH_MAPPING = {
    'healthy': ['healthy', 'good', 'excellent', 'very good', 'thriving', '1', 'H'],
    'fair': ['fair', 'ok', 'okay', 'moderate', 'declining', '2', 'F'],
    'poor': ['poor', 'bad', 'critical', 'dying', 'dead', '3', 'P'],
    'unknown': ['unknown', 'not assessed', 'n/a', 'null', None, '', '0', 'U']
}

# Organization mapping (if ArcGIS uses different names)
ORGANIZATION_MAPPING = {
    'PPA': 'Prospect Park Alliance',
    'BBG': 'Brooklyn Botanic Garden',
    'NYCPARKS': 'NYC Parks',
    'NYC PARKS': 'NYC Parks',
    'GWC': 'Green-Wood Cemetery'
}


def find_field_value(feature_attributes, possible_fields):
    """
    Find the first matching field from a list of possible field names.

    Args:
        feature_attributes: Dict of ArcGIS feature attributes
        possible_fields: List of possible field names to search for

    Returns:
        Value of first matching field, or None
    """
    for field in possible_fields:
        if field in feature_attributes:
            value = feature_attributes[field]
            # Return value if not None/empty
            if value not in [None, '', 'null', 'NULL']:
                return value
    return None


def standardize_health_status(health_value):
    """
    Convert various health status values to standardized format.

    Args:
        health_value: Raw health value from ArcGIS

    Returns:
        Standardized health status: 'healthy', 'fair', 'poor', or 'unknown'
    """
    if health_value is None or health_value == '':
        return 'unknown'

    health_str = str(health_value).lower().strip()

    # Check each category
    for standard_status, variations in HEALTH_MAPPING.items():
        if health_str in [str(v).lower() if v else '' for v in variations]:
            return standard_status

    # Default to unknown if no match
    return 'unknown'


def standardize_organization(org_value):
    """
    Convert organization codes/abbreviations to full names.

    Args:
        org_value: Raw organization value from ArcGIS

    Returns:
        Standardized organization name
    """
    if org_value is None or org_value == '':
        return 'Unknown Organization'

    org_str = str(org_value).strip()

    # Check if it's a known abbreviation
    if org_str.upper() in ORGANIZATION_MAPPING:
        return ORGANIZATION_MAPPING[org_str.upper()]

    # Return as-is if not a known abbreviation
    return org_str


def parse_date(date_value):
    """
    Parse various date formats to YYYY-MM-DD.

    Args:
        date_value: Date string or timestamp

    Returns:
        Formatted date string or None
    """
    if date_value is None or date_value == '':
        return None

    # Handle ArcGIS timestamp (milliseconds since epoch)
    if isinstance(date_value, (int, float)):
        try:
            dt = datetime.fromtimestamp(date_value / 1000.0)
            return dt.strftime('%Y-%m-%d')
        except:
            return None

    # Handle string dates
    date_str = str(date_value).strip()

    # Try common formats
    formats = [
        '%Y-%m-%d',           # 2024-12-06
        '%m/%d/%Y',           # 12/06/2024
        '%d/%m/%Y',           # 06/12/2024
        '%Y/%m/%d',           # 2024/12/06
        '%Y-%m-%dT%H:%M:%S',  # 2024-12-06T15:30:00
        '%Y-%m-%d %H:%M:%S'   # 2024-12-06 15:30:00
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue

    return None


def extract_growth_data(attributes):
    """
    Extract multi-year growth data if available.

    Args:
        attributes: Feature attributes dict

    Returns:
        Dict of growth data by year, or None
    """
    growth_data = {}
    years = ['2021', '2022', '2023', '2024']

    for year in years:
        height_field = f'height_{year}'
        dbh_field = f'dbh_{year}'

        height = find_field_value(attributes, FIELD_MAPPING.get(height_field, []))
        dbh = find_field_value(attributes, FIELD_MAPPING.get(dbh_field, []))

        if height is not None or dbh is not None:
            growth_data[year] = {}
            if height is not None:
                try:
                    growth_data[year]['height'] = float(height)
                except:
                    pass
            if dbh is not None:
                try:
                    growth_data[year]['dbh'] = float(dbh)
                except:
                    pass

    return growth_data if growth_data else None


def fetch_from_feature_service(url, where_clause='1=1', max_records=5000):
    """
    Fetch features from ArcGIS Feature Service REST API.

    Args:
        url: Feature Service URL (e.g., https://services.arcgis.com/.../FeatureServer/0)
        where_clause: SQL where clause for filtering (default: all records)
        max_records: Maximum number of records to fetch

    Returns:
        List of features
    """
    # Add query endpoint if not present
    if not url.endswith('/query'):
        url = url.rstrip('/') + '/query'

    params = {
        'where': where_clause,
        'outFields': '*',
        'returnGeometry': 'true',
        'f': 'geojson',
        'resultRecordCount': max_records
    }

    print(f"Fetching data from: {url}")
    print(f"Where clause: {where_clause}")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if 'features' in data:
            print(f"✓ Retrieved {len(data['features'])} features")
            return data['features']
        else:
            print(f"✗ No features found in response")
            return []

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data: {e}")
        sys.exit(1)


def load_from_geojson(filepath):
    """
    Load features from a GeoJSON file.

    Args:
        filepath: Path to GeoJSON file

    Returns:
        List of features
    """
    print(f"Loading GeoJSON from: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'features' in data:
            print(f"✓ Loaded {len(data['features'])} features")
            return data['features']
        else:
            print(f"✗ Invalid GeoJSON format")
            sys.exit(1)

    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        sys.exit(1)


def load_from_shapefile(filepath):
    """
    Load features from a Shapefile (requires geopandas).

    Args:
        filepath: Path to .shp file

    Returns:
        List of features in GeoJSON format
    """
    try:
        import geopandas as gpd
    except ImportError:
        print("✗ geopandas is required for Shapefile support")
        print("  Install with: pip install geopandas")
        sys.exit(1)

    print(f"Loading Shapefile from: {filepath}")

    try:
        gdf = gpd.read_file(filepath)

        # Convert to GeoJSON format
        geojson = json.loads(gdf.to_json())

        if 'features' in geojson:
            print(f"✓ Loaded {len(geojson['features'])} features")
            return geojson['features']
        else:
            print(f"✗ No features found")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Error reading Shapefile: {e}")
        sys.exit(1)


def convert_feature_to_tree(feature, tree_counter):
    """
    Convert an ArcGIS feature to our tree format.

    Args:
        feature: GeoJSON feature from ArcGIS
        tree_counter: Sequential counter for tree ID

    Returns:
        Dict in our tree format
    """
    attrs = feature.get('properties', {})
    geometry = feature.get('geometry', {})

    # Extract coordinates
    if geometry.get('type') == 'Point':
        coordinates = geometry.get('coordinates', [])
        if len(coordinates) >= 2:
            lon, lat = coordinates[0], coordinates[1]
        else:
            print(f"  Warning: Feature has invalid coordinates, skipping")
            return None
    else:
        print(f"  Warning: Feature is not a Point geometry, skipping")
        return None

    # Generate tree ID
    tree_id_value = find_field_value(attrs, FIELD_MAPPING['tree_id'])
    if tree_id_value:
        tree_id = f"NYC-AC-{str(tree_id_value).zfill(3)}"
    else:
        tree_id = f"NYC-AC-{str(tree_counter).zfill(3)}"

    # Extract required fields
    organization = standardize_organization(
        find_field_value(attrs, FIELD_MAPPING['organization'])
    )

    health_status = standardize_health_status(
        find_field_value(attrs, FIELD_MAPPING['health_status'])
    )

    # Extract optional fields
    planted_date = parse_date(find_field_value(attrs, FIELD_MAPPING['planted_date']))
    last_updated = parse_date(find_field_value(attrs, FIELD_MAPPING['last_updated']))
    notes = find_field_value(attrs, FIELD_MAPPING['notes'])
    location_desc = find_field_value(attrs, FIELD_MAPPING['location_description'])
    contact = find_field_value(attrs, FIELD_MAPPING['contact'])

    # Extract park/area for validation
    park = find_field_value(attrs, FIELD_MAPPING['park'])
    area = find_field_value(attrs, FIELD_MAPPING['area'])
    tree_number = find_field_value(attrs, FIELD_MAPPING['tree_number'])

    # Extract growth data
    growth_data = extract_growth_data(attrs)

    # Validate coordinates against park boundaries
    accuracy_level = 'estimated'
    accuracy_description = 'Imported from ArcGIS'

    if park and park.upper() in PARK_BOUNDARIES:
        is_valid, distance = is_point_in_park(lat, lon, park.upper())
        if is_valid:
            accuracy_level = 'confirmed'
            accuracy_description = f'Confirmed location from ArcGIS (within {park})'
        else:
            print(f"  Warning: Tree {tree_id} coordinates outside {park} boundary (distance: {distance:.0f}m)")
            accuracy_level = 'estimated'
            accuracy_description = f'Coordinates may need verification (outside {park} by {distance:.0f}m)'

    # Build tree object
    tree = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [lon, lat]
        },
        'properties': {
            'tree_id': tree_id,
            'organization': organization,
            'health_status': health_status,
            'planted_date': planted_date or 'Unknown',
            'last_updated': last_updated or datetime.now().strftime('%Y-%m-%d'),
            'notes': notes or '',
            'location_description': location_desc or '',
            'contact': contact or 'conservation@nyc.gov',
            'location_accuracy': {
                'level': accuracy_level,
                'description': accuracy_description,
                'source': 'arcgis',
                'confidence': 90 if accuracy_level == 'confirmed' else 60
            }
        }
    }

    # Add optional fields
    if growth_data:
        tree['properties']['growth_data'] = growth_data

    if park:
        tree['properties']['park'] = park

    if area:
        tree['properties']['area'] = area

    if tree_number:
        tree['properties']['tree_number'] = tree_number

    # Add health detail if available (original value)
    original_health = find_field_value(attrs, FIELD_MAPPING['health_status'])
    if original_health and str(original_health).lower() != health_status:
        tree['properties']['health_detail'] = str(original_health)

    return tree


def import_arcgis_data(source, source_type='url', where_clause='1=1', output_file='data/trees.json'):
    """
    Main import function.

    Args:
        source: URL, file path, or shapefile path
        source_type: 'url', 'geojson', or 'shapefile'
        where_clause: SQL where clause for filtering (for URLs only)
        output_file: Output file path
    """
    print("\n=== ArcGIS Feature Service Importer ===\n")

    # Load features based on source type
    if source_type == 'url':
        features = fetch_from_feature_service(source, where_clause)
    elif source_type == 'geojson':
        features = load_from_geojson(source)
    elif source_type == 'shapefile':
        features = load_from_shapefile(source)
    else:
        print(f"✗ Unknown source type: {source_type}")
        sys.exit(1)

    if not features:
        print("✗ No features to process")
        sys.exit(1)

    print(f"\nProcessing {len(features)} features...")

    # Convert features to our format
    trees = []
    skipped = 0

    for i, feature in enumerate(features, 1):
        tree = convert_feature_to_tree(feature, i)
        if tree:
            trees.append(tree)
        else:
            skipped += 1

    print(f"\n✓ Converted {len(trees)} trees")
    if skipped > 0:
        print(f"  Skipped {skipped} features (invalid geometry or missing data)")

    # Create GeoJSON FeatureCollection
    geojson = {
        'type': 'FeatureCollection',
        'metadata': {
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'arcgis',
            'source_url': source if source_type == 'url' else 'file',
            'total_features': len(trees),
            'version': '4.0'
        },
        'features': trees
    }

    # Write to output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully created {output_file}")
    print(f"  Total trees: {len(trees)}")

    # Print summary statistics
    print("\nSummary:")
    print(f"  Organizations: {len(set(t['properties']['organization'] for t in trees))}")

    health_counts = {}
    for tree in trees:
        status = tree['properties']['health_status']
        health_counts[status] = health_counts.get(status, 0) + 1

    print("  Health status:")
    for status, count in sorted(health_counts.items()):
        print(f"    {status}: {count}")

    accuracy_counts = {}
    for tree in trees:
        level = tree['properties']['location_accuracy']['level']
        accuracy_counts[level] = accuracy_counts.get(level, 0) + 1

    print("  Location accuracy:")
    for level, count in sorted(accuracy_counts.items()):
        print(f"    {level}: {count}")

    print("\n=== Import Complete ===\n")


def main():
    parser = argparse.ArgumentParser(
        description='Import tree data from ArcGIS Feature Service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # From Feature Service URL
  python3 scripts/import_from_arcgis.py --url "https://services.arcgis.com/.../FeatureServer/0"

  # From Feature Service with filter
  python3 scripts/import_from_arcgis.py --url "https://..." --where "Park = 'Prospect Park'"

  # From GeoJSON file
  python3 scripts/import_from_arcgis.py --file arcgis_export.geojson

  # From Shapefile
  python3 scripts/import_from_arcgis.py --shapefile trees.shp

  # Custom output file
  python3 scripts/import_from_arcgis.py --file data.geojson --output data/trees_new.json
        '''
    )

    # Input source (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--url', help='ArcGIS Feature Service URL')
    source_group.add_argument('--file', help='GeoJSON file path')
    source_group.add_argument('--shapefile', help='Shapefile (.shp) path')

    # Optional arguments
    parser.add_argument('--where', default='1=1',
                       help='SQL where clause for filtering (default: "1=1" for all records)')
    parser.add_argument('--output', default='data/trees.json',
                       help='Output file path (default: data/trees.json)')
    parser.add_argument('--max-records', type=int, default=5000,
                       help='Maximum number of records to fetch (default: 5000)')

    args = parser.parse_args()

    # Determine source type and source
    if args.url:
        import_arcgis_data(args.url, 'url', args.where, args.output)
    elif args.file:
        import_arcgis_data(args.file, 'geojson', output_file=args.output)
    elif args.shapefile:
        import_arcgis_data(args.shapefile, 'shapefile', output_file=args.output)


if __name__ == '__main__':
    main()
