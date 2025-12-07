#!/usr/bin/env python3
"""
Merge data from multiple sources (ArcGIS + Excel) to create complete tree dataset.

This script combines:
- ArcGIS: Accurate coordinates, location descriptions, variants, planting info
- Excel: Health status, detailed observations from field surveys

Usage:
    python3 scripts/merge_data_sources.py \
        --arcgis data/trees_arcgis.json \
        --excel "archive/2024 year end chestnut results.xlsx" \
        --output data/trees.json
"""

import json
import argparse
import openpyxl
from datetime import datetime
from typing import Dict, List, Any, Optional


def parse_excel_health_data(excel_path: str) -> Dict[int, Dict[str, Any]]:
    """
    Parse Excel file to extract tree health data.

    Returns:
        Dictionary mapping tree_number -> {health, location, height, dbh, etc.}
    """
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    tree_data = {}
    current_location = None
    current_area = None

    print(f"\nParsing Excel file: {excel_path}")

    for row_num, row in enumerate(sheet.iter_rows(min_row=10, max_row=200, values_only=True), 10):
        # Check if this is a main location header (ALL CAPS)
        if row[0] and isinstance(row[0], str):
            text = str(row[0]).strip()
            if text.isupper() and len(text) > 3:
                current_area = text.strip(':').strip()
                current_location = None
                continue
            elif ':' in text:
                current_location = text.strip(':').strip()
                continue

        # Check if this row has a tree number (number in column B, index 1)
        if row[1] and isinstance(row[1], (int, float)):
            tree_num = int(row[1])

            # Extract 2024 data (columns 12-16)
            height_2024 = row[12] if len(row) > 12 else None
            dbh_2024 = row[13] if len(row) > 13 else None
            type_2024 = row[14] if len(row) > 14 else None  # Nat/PBR
            new_2024 = row[15] if len(row) > 15 else None
            health = row[16] if len(row) > 16 else None

            tree_data[tree_num] = {
                'location': current_location or current_area,
                'area': current_area,
                'health': str(health).strip() if health else None,
                'height': str(height_2024).strip() if height_2024 else None,
                'dbh': str(dbh_2024).strip() if dbh_2024 else None,
                'type': str(type_2024).strip() if type_2024 else None,
                'new_in_2024': bool(new_2024),
            }

    print(f"  Found {len(tree_data)} trees with health/survey data")
    return tree_data


def parse_health_from_notes(notes: Optional[str]) -> Dict[str, Any]:
    """
    Parse health status and date from ArcGIS Notes field.

    Examples:
        "11/25 very good" -> {status: "healthy", date: "11/25", original: "very good"}
        "11/16/25 2015/24/1 SB excellent" -> {status: "healthy", date: "11/16/25", original: "excellent"}

    Returns:
        Dict with 'status', 'date', 'original', and 'full_note'
    """
    if not notes:
        return {'status': 'unknown', 'date': None, 'original': None, 'full_note': None}

    import re

    # Look for date patterns (MM/DD, MM/DD/YY, MM/DD/YYYY)
    date_match = re.search(r'(\d{1,2}/\d{1,2}(?:/\d{2,4})?)', notes)
    date_str = date_match.group(1) if date_match else None

    # Extract health keywords
    notes_lower = notes.lower()
    health_status = 'unknown'
    health_original = None

    # Find health descriptors
    health_keywords = [
        ('excellent', 'healthy'),
        ('very good', 'healthy'),
        ('good', 'good'),
        ('fair', 'fair'),
        ('poor', 'declining'),
        ('blight', 'declining'),
        ('declining', 'declining'),
        ('dead', 'dead'),
        ('may be dead', 'dead'),
        ('coppising', 'declining'),  # resprouting after damage
    ]

    for keyword, status in health_keywords:
        if keyword in notes_lower:
            health_status = status
            health_original = keyword
            break

    return {
        'status': health_status,
        'date': date_str,
        'original': health_original,
        'full_note': notes
    }


def standardize_health_status(health_text: Optional[str]) -> str:
    """
    Convert Excel health descriptions to standardized categories.
    """
    if not health_text:
        return "unknown"

    health_lower = health_text.lower()

    # Map Excel descriptions to standard categories
    if "excellent" in health_lower or "very good" in health_lower:
        return "healthy"
    elif "good" in health_lower:
        return "good"
    elif "dead" in health_lower or "may be dead" in health_lower:
        return "dead"
    elif "blight" in health_lower or "declining" in health_lower or "coppising" in health_lower:
        return "declining"
    elif "fair" in health_lower or "ok" in health_lower:
        return "fair"
    else:
        return "unknown"


def extract_tree_number_from_name(name: str) -> Optional[int]:
    """
    Extract tree number from ArcGIS Name field.
    Examples: "7", "Tree 42", "AC-007" -> 7, 42, 7
    """
    if not name:
        return None

    import re
    # Look for numbers in the name
    numbers = re.findall(r'\d+', str(name))
    if numbers:
        return int(numbers[0])
    return None


def merge_data_sources(arcgis_path: str, excel_path: str, output_path: str):
    """
    Merge ArcGIS and Excel data sources.
    """
    print("\n=== Data Source Merger ===\n")

    # Load ArcGIS data (coordinates, locations, variants)
    print(f"Loading ArcGIS data from: {arcgis_path}")
    with open(arcgis_path, 'r') as f:
        arcgis_data = json.load(f)
    print(f"  Loaded {len(arcgis_data['features'])} trees from ArcGIS")

    # Parse Excel health data
    excel_health = parse_excel_health_data(excel_path)

    # Merge the data
    print("\nMerging data sources...")
    matched = 0
    health_updated = 0
    health_from_arcgis_notes = 0

    for feature in arcgis_data['features']:
        props = feature['properties']

        # First, check ArcGIS Notes for health updates
        arcgis_notes = props.get('notes', '')
        health_from_notes = parse_health_from_notes(arcgis_notes)

        # Try to extract tree number from the Name field in ArcGIS
        tree_number = None
        if 'name' in props:
            tree_number = extract_tree_number_from_name(props.get('name'))

        # Also check if the tree_id has a number we can extract
        if not tree_number and 'tree_id' in props:
            tree_number = extract_tree_number_from_name(props.get('tree_id'))

        # Store the tree number for reference if found
        if tree_number:
            props['tree_number'] = tree_number

        # Priority 1: Use ArcGIS Notes for health (most recent updates)
        if health_from_notes['status'] != 'unknown':
            props['health_status'] = health_from_notes['status']
            props['health_notes'] = health_from_notes['full_note']
            if health_from_notes['date']:
                props['health_date'] = health_from_notes['date']
            health_from_arcgis_notes += 1
            health_updated += 1

        # Priority 2: If no health in ArcGIS notes, try Excel data
        elif tree_number and tree_number in excel_health:
            matched += 1
            excel_tree = excel_health[tree_number]

            # Update health status from Excel
            if excel_tree['health']:
                props['health_status'] = standardize_health_status(excel_tree['health'])
                props['health_notes'] = f"Excel 2024: {excel_tree['health']}"
                health_updated += 1

            # Add survey measurements from Excel
            if excel_tree['height']:
                props['height_2024'] = excel_tree['height']
            if excel_tree['dbh']:
                props['dbh_2024'] = excel_tree['dbh']
            if excel_tree['type']:
                props['tree_type'] = excel_tree['type']  # Native vs PBR

            # Update location if Excel has more specific info
            if excel_tree['location'] and excel_tree['location'] != excel_tree['area']:
                props['location_detail'] = excel_tree['location']

        # Set default organization to TACF
        if props.get('organization') in ['Unknown Organization', '', None]:
            props['organization'] = 'TACF'

        # Update location accuracy to "verified" for ArcGIS data
        if 'location_accuracy' in props:
            props['location_accuracy']['level'] = 'verified'
            props['location_accuracy']['description'] = 'Verified coordinates from ArcGIS Feature Service'
            props['location_accuracy']['confidence'] = 95
            props['location_accuracy']['verified_by'] = 'TACF'
            props['location_accuracy']['verified_date'] = datetime.now().strftime('%Y-%m-%d')

        # Set default contact
        if not props.get('contact') or props.get('contact') == 'conservation@nyc.gov':
            props['contact'] = 'TACF-NYC@acf.org'

    # Update metadata
    arcgis_data['metadata']['sources'] = [
        {
            'type': 'arcgis',
            'description': 'Coordinates and location data',
            'url': arcgis_data['metadata'].get('source_url', ''),
            'trees': len(arcgis_data['features'])
        },
        {
            'type': 'excel',
            'description': 'Health status and field survey data',
            'file': excel_path,
            'trees': len(excel_health)
        }
    ]
    arcgis_data['metadata']['last_merged'] = datetime.now().strftime('%Y-%m-%d')
    arcgis_data['metadata']['merge_stats'] = {
        'total_trees': len(arcgis_data['features']),
        'matched_with_excel': matched,
        'health_updated': health_updated,
        'health_from_arcgis_notes': health_from_arcgis_notes,
        'excel_trees': len(excel_health)
    }

    # Save merged data
    print(f"\nWriting merged data to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(arcgis_data, f, indent=2)

    # Print summary
    print("\n=== Merge Summary ===")
    print(f"Total trees in ArcGIS: {len(arcgis_data['features'])}")
    print(f"Total trees in Excel: {len(excel_health)}")
    print(f"Matched and merged: {matched}")
    print(f"Health status updated: {health_updated}")
    print(f"  - From ArcGIS Notes: {health_from_arcgis_notes}")
    print(f"  - From Excel data: {health_updated - health_from_arcgis_notes}")
    print(f"Unmatched ArcGIS trees: {len(arcgis_data['features']) - matched - health_from_arcgis_notes}")
    print(f"Unmatched Excel trees: {len(excel_health) - matched}")

    print("\nUpdates applied to all trees:")
    print("  - Organization set to 'TACF' (where blank)")
    print("  - Location accuracy set to 'verified' (ArcGIS source)")
    print("  - Contact set to 'TACF-NYC@acf.org'")

    print(f"\n✓ Merged data saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Merge ArcGIS and Excel data sources for NYC American Chestnut map'
    )
    parser.add_argument(
        '--arcgis',
        required=True,
        help='Path to ArcGIS JSON file (input)'
    )
    parser.add_argument(
        '--excel',
        required=True,
        help='Path to Excel file with health data (input)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path for merged output JSON file'
    )

    args = parser.parse_args()

    merge_data_sources(args.arcgis, args.excel, args.output)


if __name__ == '__main__':
    main()
