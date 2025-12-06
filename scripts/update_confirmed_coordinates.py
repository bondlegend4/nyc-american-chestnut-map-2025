#!/usr/bin/env python3
"""
update_confirmed_coordinates.py

Updates trees.json with confirmed GPS coordinates from field collection.
"""

import json
import pandas as pd
import sys
from park_boundaries import calculate_accuracy_level

def update_coordinates_from_csv(csv_file, trees_json='data/trees.json'):
    """
    Update trees.json with confirmed coordinates from CSV.

    CSV format:
    tree_id,park,area,latitude,longitude,accuracy_meters,collector,notes,timestamp
    """
    # Read confirmed coordinates
    print(f"Reading confirmed coordinates from {csv_file}...")
    df_confirmed = pd.read_csv(csv_file)

    print(f"  Found {len(df_confirmed)} confirmed coordinates")

    # Read current trees.json
    print(f"\nReading {trees_json}...")
    with open(trees_json, 'r') as f:
        geojson = json.load(f)

    # Create lookup by tree_id and tree_number
    updates = {}
    for _, row in df_confirmed.iterrows():
        tree_id = str(row['tree_id']).strip()

        # Handle both "NYC-AC-001" and "Tree #7" formats
        if tree_id.startswith('NYC-AC-'):
            key = tree_id
        elif tree_id.startswith('Tree #') or tree_id.startswith('#'):
            # Extract number and match against tree_number
            num = int(tree_id.replace('Tree #', '').replace('#', '').strip())
            key = f"tree_number_{num}"
        else:
            print(f"  Warning: Unrecognized tree_id format: {tree_id}")
            continue

        updates[key] = {
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'accuracy_meters': float(row['accuracy_meters']),
            'collector': row.get('collector', ''),
            'notes': row.get('notes', ''),
            'timestamp': row.get('timestamp', ''),
            'park': row.get('park', ''),
            'area': row.get('area', '')
        }

    print(f"\nProcessed {len(updates)} coordinate updates")

    # Update trees
    updated_count = 0
    for feature in geojson['features']:
        props = feature['properties']
        tree_id = props['tree_id']
        tree_num = props.get('tree_number')

        # Try to match by tree_id first
        update_data = None
        if tree_id in updates:
            update_data = updates[tree_id]
        elif tree_num and f"tree_number_{tree_num}" in updates:
            update_data = updates[f"tree_number_{tree_num}"]

        if update_data:
            # Update coordinates
            old_coords = feature['geometry']['coordinates']
            new_lat = update_data['latitude']
            new_lon = update_data['longitude']

            feature['geometry']['coordinates'] = [new_lon, new_lat]  # GeoJSON: [lon, lat]

            # Update accuracy to "confirmed"
            park = update_data['park'] or props.get('location_description', '').split(' - ')[0]
            area = update_data['area'] or props.get('location_description', '').split(' - ')[1] if ' - ' in props.get('location_description', '') else None

            props['location_accuracy'] = {
                'level': 'confirmed',
                'description': f"GPS-verified location (±{update_data['accuracy_meters']:.1f}m)",
                'radius_meters': update_data['accuracy_meters'],
                'confidence': 100,
                'collector': update_data['collector'],
                'timestamp': update_data['timestamp']
            }

            # Add note about GPS collection
            if update_data['notes']:
                if props.get('notes'):
                    props['notes'] += f" | GPS: {update_data['notes']}"
                else:
                    props['notes'] = f"GPS: {update_data['notes']}"

            print(f"  ✓ Updated {tree_id}: ({old_coords[1]:.6f}, {old_coords[0]:.6f}) → ({new_lat:.6f}, {new_lon:.6f})")
            updated_count += 1

    # Update metadata
    geojson['metadata']['last_updated'] = pd.Timestamp.now().strftime('%Y-%m-%d')
    geojson['metadata']['confirmed_coordinates'] = updated_count

    # Save updated file
    with open(trees_json, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully updated {trees_json}")
    print(f"  Updated coordinates: {updated_count}/{len(geojson['features'])}")

    # Print accuracy summary
    accuracy_counts = {}
    for feature in geojson['features']:
        level = feature['properties']['location_accuracy']['level']
        accuracy_counts[level] = accuracy_counts.get(level, 0) + 1

    print("\nAccuracy distribution:")
    for level, count in sorted(accuracy_counts.items()):
        print(f"  {level}: {count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_confirmed_coordinates.py <coordinates.csv>")
        print("\nExample:")
        print("  python update_confirmed_coordinates.py tree_coordinates_2024-12-05.csv")
        sys.exit(1)

    csv_file = sys.argv[1]
    update_coordinates_from_csv(csv_file)
