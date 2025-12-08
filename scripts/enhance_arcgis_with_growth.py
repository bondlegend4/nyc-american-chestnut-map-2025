#!/usr/bin/env python3
"""
Enhance ArcGIS data with historical growth data from Excel surveys.

This script treats ArcGIS as the PRIMARY data source (coordinates, current status)
and COMPLEMENTS it with historical growth measurements from Excel.

Data Flow:
1. ArcGIS Feature Service → Primary source (coordinates, current health from Notes)
2. Excel Survey Data → Supplement with year-over-year growth measurements

Usage:
    python3 scripts/enhance_arcgis_with_growth.py \
        --arcgis data/trees_arcgis_fresh.json \
        --excel "archive/2024 year end chestnut results.xlsx" \
        --output data/trees.json
"""

import json
import argparse
import openpyxl
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


def parse_health_from_notes(notes: Optional[str]) -> Dict[str, Any]:
    """
    Parse health status from ArcGIS Notes field (PRIMARY source for health).

    Examples:
        "11/25 very good" → {status: "healthy", date: "11/25", detail: "very good"}
        "excellent" → {status: "healthy", date: None, detail: "excellent"}
        "11/25 some blight, coppising" → {status: "declining", date: "11/25", detail: "some blight, coppising"}
        "11/25 dead twig" → {status: "dead", date: "11/25", detail: "dead twig"}

    Returns:
        Dict with 'status', 'date', 'detail'
    """
    if not notes or notes.strip() == "":
        return {'status': 'unknown', 'date': None, 'detail': None}

    # Skip notes that are just planting info
    if 'planted' in notes.lower() and 'replacement' in notes.lower():
        return {'status': 'unknown', 'date': None, 'detail': None}

    # Look for date patterns (MM/DD, MM/DD/YY)
    date_match = re.search(r'(\d{1,2}/\d{1,2}(?:/\d{2,4})?)', notes)
    date_str = date_match.group(1) if date_match else None

    # Convert date to full format
    if date_str and '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 2:  # MM/DD
            # Use 2024 as default year, or 2025 if month is 11-12
            year = "2025" if int(parts[0]) >= 11 else "2024"
            date_str = f"{year}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        elif len(parts) == 3:  # MM/DD/YY or MM/DD/YYYY
            year = parts[2]
            if len(year) == 2:
                year = f"20{year}"
            date_str = f"{year}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    notes_lower = notes.lower()

    # Health status mapping (in priority order)
    # Check for dead/gone first
    if any(keyword in notes_lower for keyword in ['dead', 'gone', 'cannot find', 'may be dead', 'might be dead', 'looks dead']):
        health_status = 'dead'
    # Check for declining/blight
    elif any(keyword in notes_lower for keyword in ['blight', 'coppising', 'coppice', 'declining', 'significant blight', 'multi stem']):
        health_status = 'declining'
    # Check for poor
    elif any(keyword in notes_lower for keyword in ['poor', 'bad', 'critical']):
        health_status = 'poor'
    # Check for excellent/very good (healthy)
    elif any(keyword in notes_lower for keyword in ['excellent', 'very good', 'thriving']):
        health_status = 'healthy'
    # Check for good
    elif 'good' in notes_lower and 'very good' not in notes_lower:
        health_status = 'good'
    # Check for fair/ok
    elif any(keyword in notes_lower for keyword in ['fair', 'ok', 'okay', 'maybe ok']):
        health_status = 'fair'
    else:
        # If we have notes but no health keyword, it's unknown
        health_status = 'unknown'

    return {
        'status': health_status,
        'date': date_str,
        'detail': notes.strip()
    }


# Location name to abbreviation mapping (Excel → ArcGIS)
# These map Excel location names to ArcGIS abbreviations found in the "Name" field
LOCATION_ABBREV = {
    # Prospect Park locations
    'Sugar Bowl': 'SB',
    'Upper': 'SB',  # "Upper" in Excel = Sugar Bowl
    'Peninsula': 'PN',
    'Lookout Hill': 'LOH',  # ArcGIS uses LOH for Lookout Hill
    'West Drive': 'WD',
    'Litchfield Villa': 'LV',
    'Bartel-Pritchard': 'BP',
    'Bartell Pritchard': 'BP',
    'Bartell-Pritchard': 'BP',
    'Vale of Cashmere': 'VC',
    'Vale': 'VC',
    'Ravine': 'RV',
    'Lefferts House': 'LH',  # LH for Lefferts House
    'Breeze Hill': 'BH',
    'Fallkill': 'FK',
    'Midmeadow': 'MM',
    'Maintenance Yard': 'MY',
    'Ball fields': 'BF',
    'Flatbush Ave': 'FLB',
    'Dog Beach': 'DB',

    # Green-Wood Cemetery
    'Chestnut Hill': 'GW',
    'Chestnut Hill Greenwood': 'GW',
    'Quaker Cemetery': 'QC',

    # Brooklyn locations
    'Brooklyn Botanic Garden': 'BBG',
}


def parse_excel_growth_history(excel_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse Excel file to extract historical growth data for each tree.

    Returns:
        Dictionary mapping tree_key (location_abbrev + number) → growth history
        E.g., "LV-05" → {location, area, growth_data, excel_name}
    """
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    tree_growth = {}
    current_location = None
    current_area = None

    print(f"\nParsing Excel growth history: {excel_path}")

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

            # Extract location abbreviation
            location_name = current_location or current_area
            location_abbrev = LOCATION_ABBREV.get(location_name, 'UNK')

            # Create tree key (e.g., "LV-05", "BP-01")
            tree_key = f"{location_abbrev}-{str(tree_num).zfill(2)}"

            # Extract growth data for multiple years
            # Column indices: 2=A, 5=E, 6=F, 7=G, etc.
            growth_history = {}

            def extract_number(value):
                """Extract numeric value from strings like '14.7', \"8'\", '1\"', etc."""
                if value is None:
                    return None
                val_str = str(value).strip().replace("'", "").replace('"', "").replace("'", "")
                try:
                    return float(val_str)
                except:
                    return None

            # 2021 data (columns E=4, F=5 in 0-indexed)
            if len(row) > 5:
                height_2021 = extract_number(row[4]) if row[4] else None
                dbh_2021 = extract_number(row[5]) if row[5] else None
                if height_2021 or dbh_2021:
                    growth_history['2021'] = {}
                    if height_2021:
                        growth_history['2021']['height'] = height_2021
                    if dbh_2021:
                        growth_history['2021']['dbh'] = dbh_2021

            # 2022 data (columns G=6, H=7)
            if len(row) > 7:
                height_2022 = extract_number(row[5]) if row[5] else None
                dbh_2022 = extract_number(row[6]) if row[6] else None
                if height_2022 or dbh_2022:
                    growth_history['2022'] = {}
                    if height_2022:
                        growth_history['2022']['height'] = height_2022
                    if dbh_2022:
                        growth_history['2022']['dbh'] = dbh_2022

            # 2023 data (columns I=8, J=9)
            if len(row) > 9:
                height_2023 = extract_number(row[8]) if row[8] else None
                dbh_2023 = extract_number(row[9]) if row[9] else None
                if height_2023 or dbh_2023:
                    growth_history['2023'] = {}
                    if height_2023:
                        growth_history['2023']['height'] = height_2023
                    if dbh_2023:
                        growth_history['2023']['dbh'] = dbh_2023

            # 2024 data (columns M=12, N=13)
            if len(row) > 13:
                height_2024 = extract_number(row[12]) if row[12] else None
                dbh_2024 = extract_number(row[13]) if row[13] else None
                if height_2024 or dbh_2024:
                    growth_history['2024'] = {}
                    if height_2024:
                        growth_history['2024']['height'] = height_2024
                    if dbh_2024:
                        growth_history['2024']['dbh'] = dbh_2024

            # Extract 2024 health status from Excel (column Q=16)
            excel_health_2024 = None
            if len(row) > 16 and row[16]:
                excel_health_2024 = str(row[16]).strip()

            # Store with tree key for matching
            tree_growth[tree_key] = {
                'location': current_location or current_area,
                'area': current_area,
                'tree_number': tree_num,
                'excel_name': f"{location_name} #{tree_num}",
                'growth_data': growth_history if growth_history else None,
                'excel_health_2024': excel_health_2024
            }

    print(f"  Found growth data for {len(tree_growth)} trees")
    return tree_growth


def standardize_health_text(health_text: str) -> str:
    """
    Convert health descriptions to standardized categories.
    Used for both ArcGIS Notes and Excel health columns.
    """
    if not health_text:
        return 'unknown'

    health_lower = health_text.lower()

    # Health status mapping (same logic as parse_health_from_notes)
    if any(keyword in health_lower for keyword in ['dead', 'gone', 'cannot find', 'may be dead', 'might be dead', 'looks dead']):
        return 'dead'
    elif any(keyword in health_lower for keyword in ['blight', 'coppising', 'coppice', 'declining', 'significant blight', 'multi stem']):
        return 'declining'
    elif any(keyword in health_lower for keyword in ['poor', 'bad', 'critical']):
        return 'poor'
    elif any(keyword in health_lower for keyword in ['excellent', 'very good', 'thriving']):
        return 'healthy'
    elif 'good' in health_lower and 'very good' not in health_lower:
        return 'good'
    elif any(keyword in health_lower for keyword in ['fair', 'ok', 'okay', 'maybe ok']):
        return 'fair'
    else:
        return 'unknown'


def extract_tree_key_from_name(name: str) -> Optional[str]:
    """
    Extract tree key from ArcGIS Name field for matching with Excel.
    Examples:
        "LV 05" → "LV-05"
        "BBG 01" → "BBG-01"
        "LOH #7" → "LOH-07"
        "BP03" → "BP-03"

    Returns:
        Tree key in format "XX-NN" for matching, or None
    """
    if not name:
        return None

    name = str(name).strip()

    # Try to extract abbreviation and number (with optional # symbol)
    # Pattern: "XX NN", "XXX NN", "XX #NN"
    match = re.match(r'([A-Z]+)\s*#?\s*(\d+)', name)
    if match:
        abbrev, num = match.groups()
        return f"{abbrev}-{num.zfill(2)}"

    # Alternative patterns like "BP03" without space
    match = re.match(r'([A-Z]+)(\d+)', name)
    if match:
        abbrev, num = match.groups()
        return f"{abbrev}-{num.zfill(2)}"

    return None


def enhance_arcgis_with_growth(arcgis_path: str, excel_path: str, output_path: str):
    """
    Enhance ArcGIS data (primary) with Excel growth history (supplement).

    Args:
        arcgis_path: Path to ArcGIS JSON file (PRIMARY data source)
        excel_path: Path to Excel file (growth history supplement)
        output_path: Path for enhanced output
    """
    print("\n=== ArcGIS Data Enhancement with Growth History ===\n")

    # Load PRIMARY data source: ArcGIS
    print(f"Loading PRIMARY data from ArcGIS: {arcgis_path}")
    with open(arcgis_path, 'r') as f:
        arcgis_data = json.load(f)
    print(f"  ✓ Loaded {len(arcgis_data['features'])} trees from ArcGIS")

    # Load SUPPLEMENTAL data: Excel growth history
    excel_growth = parse_excel_growth_history(excel_path)

    # Enhance each tree with growth data
    print("\nEnhancing trees with historical growth data...")
    health_parsed = 0
    growth_added = 0
    matched_trees = []
    unmatched_arcgis = []
    unmatched_excel = list(excel_growth.keys())

    for feature in arcgis_data['features']:
        props = feature['properties']

        # Initialize health_history for tracking changes over time
        health_history = {}

        # STEP 1: Parse health from ArcGIS Notes
        notes = props.get('notes', '')
        health_info = parse_health_from_notes(notes)

        # Get ArcGIS EditDate to use as fallback date
        arcgis_edit_date = props.get('last_updated')

        if health_info['status'] != 'unknown':
            # Use parsed date from notes, or fall back to EditDate
            health_date = health_info['date'] if health_info['date'] else arcgis_edit_date

            if health_date:
                # Add to health history
                health_history[health_date] = {
                    'status': health_info['status'],
                    'detail': health_info['detail'],
                    'source': 'arcgis'
                }
            health_parsed += 1

        # STEP 2: Extract tree key for matching with Excel (e.g., "LV-05")
        tree_key = extract_tree_key_from_name(props.get('name'))

        if tree_key:
            # STEP 3: Add growth history AND health from Excel if available
            if tree_key in excel_growth:
                excel_tree = excel_growth[tree_key]

                # Store Excel name for transparency
                props['excel_match'] = excel_tree['excel_name']
                props['tree_number'] = excel_tree['tree_number']

                # Add growth data
                if excel_tree['growth_data']:
                    props['growth_data'] = excel_tree['growth_data']
                    growth_added += 1

                # Add Excel 2024 health to health_history
                if excel_tree.get('excel_health_2024'):
                    excel_health_status = standardize_health_text(excel_tree['excel_health_2024'])
                    if excel_health_status != 'unknown':
                        # Use 2024-12-31 as the Excel survey date (end of year survey)
                        health_history['2024-12-31'] = {
                            'status': excel_health_status,
                            'detail': excel_tree['excel_health_2024'],
                            'source': 'excel'
                        }

                # Enhance location description if Excel has more detail
                if excel_tree['location'] and excel_tree['location'] != excel_tree['area']:
                    if not props.get('location_description') or props['location_description'] == props.get('area'):
                        props['location_description'] = f"{excel_tree['area']}: {excel_tree['location']}"

                matched_trees.append(tree_key)
                if tree_key in unmatched_excel:
                    unmatched_excel.remove(tree_key)
            else:
                # ArcGIS tree not found in Excel
                unmatched_arcgis.append(f"{props.get('name')} (key: {tree_key})")
        else:
            # Couldn't extract tree key from name
            unmatched_arcgis.append(f"{props.get('name')} (no key extracted)")

        # STEP 4: Store health_history and determine current health status
        if health_history:
            props['health_history'] = health_history

            # Use the most recent health status as current
            most_recent_date = max(health_history.keys())
            most_recent = health_history[most_recent_date]

            props['health_status'] = most_recent['status']
            props['health_detail'] = most_recent['detail']
            props['last_survey_date'] = most_recent_date
            props['last_updated'] = most_recent_date

        # STEP 4: Set organization from Origin field (already mapped by import script)
        # Keep as TACF or whatever was imported

        # STEP 5: Preserve Variant and Seed from ArcGIS
        # Already in props from import

        # Set borough based on coordinates (simplified)
        lat, lon = feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]
        if lat > 40.7 and lat < 40.9:
            if lon < -73.95:
                props['borough'] = 'Manhattan'
            else:
                props['borough'] = 'Bronx'
        elif lat >= 40.63 and lat <= 40.7:
            if lon < -74.0:
                props['borough'] = 'Staten Island'
            else:
                props['borough'] = 'Brooklyn'
        else:
            props['borough'] = 'Queens'

    # Update metadata
    arcgis_data['metadata']['enhanced_date'] = datetime.now().strftime('%Y-%m-%d')
    arcgis_data['metadata']['primary_source'] = 'ArcGIS Feature Service'
    arcgis_data['metadata']['supplements'] = [
        {
            'type': 'excel',
            'description': 'Historical growth measurements (year-over-year)',
            'file': excel_path,
            'trees_with_growth': growth_added
        }
    ]
    arcgis_data['metadata']['enhancement_stats'] = {
        'total_trees': len(arcgis_data['features']),
        'health_from_arcgis_notes': health_parsed,
        'growth_history_added': growth_added
    }

    # Save enhanced data
    print(f"\nWriting enhanced data to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(arcgis_data, f, indent=2)

    # Print summary
    print("\n=== Enhancement Summary ===")
    print(f"PRIMARY Source: ArcGIS Feature Service")
    print(f"  Total trees: {len(arcgis_data['features'])}")
    print(f"  Health status parsed from Notes: {health_parsed}")
    print(f"\nSUPPLEMENTAL Source: Excel Survey Data")
    print(f"  Trees in Excel: {len(excel_growth)}")
    print(f"  Successfully matched: {len(matched_trees)}")
    print(f"  Growth history added: {growth_added} trees")
    print(f"  Years tracked: 2021, 2022, 2023, 2024")

    # Matching statistics
    print(f"\nMatching Statistics:")
    print(f"  Matched trees: {len(matched_trees)}")
    print(f"  Unmatched ArcGIS trees: {len(unmatched_arcgis)}")
    print(f"  Unmatched Excel trees: {len(unmatched_excel)}")

    # Show some unmatched trees for debugging
    if unmatched_arcgis:
        print(f"\n  Sample unmatched ArcGIS trees (first 10):")
        for name in unmatched_arcgis[:10]:
            print(f"    - {name}")

    if unmatched_excel:
        print(f"\n  Sample unmatched Excel trees (first 10):")
        for key in list(unmatched_excel)[:10]:
            excel_tree = excel_growth[key]
            print(f"    - {key} ({excel_tree['excel_name']})")

    # Health status breakdown
    health_counts = {}
    for feature in arcgis_data['features']:
        status = feature['properties']['health_status']
        health_counts[status] = health_counts.get(status, 0) + 1

    print("\nHealth Status Distribution:")
    for status, count in sorted(health_counts.items()):
        print(f"  {status}: {count}")

    print(f"\n✓ Enhanced data saved to: {output_path}")
    print("\nData Flow:")
    print("  ArcGIS → Coordinates, Names, Variants, Current Health (from Notes)")
    print("  Excel  → Historical Growth Data (2021-2024)")
    print("\nNote: 'excel_match' field shows Excel naming for transparency")


def main():
    parser = argparse.ArgumentParser(
        description='Enhance ArcGIS data with Excel growth history',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  python3 scripts/enhance_arcgis_with_growth.py \\
      --arcgis data/trees_arcgis_fresh.json \\
      --excel "archive/2024 year end chestnut results.xlsx" \\
      --output data/trees.json

Data Flow:
  PRIMARY:      ArcGIS Feature Service (coordinates, current health)
  SUPPLEMENT:   Excel Survey Data (historical growth measurements)
        '''
    )

    parser.add_argument(
        '--arcgis',
        required=True,
        help='Path to ArcGIS JSON file (PRIMARY source)'
    )
    parser.add_argument(
        '--excel',
        required=True,
        help='Path to Excel file with growth history (SUPPLEMENT)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path for enhanced output JSON file'
    )

    args = parser.parse_args()
    enhance_arcgis_with_growth(args.arcgis, args.excel, args.output)


if __name__ == '__main__':
    main()
