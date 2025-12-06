#!/usr/bin/env python3
"""
landuse_validator.py

Validates coordinates against real-world features to avoid placing trees
in inappropriate locations like buildings, sports fields, or water bodies.

Uses OpenStreetMap Overpass API to check land use at coordinates.
"""

import requests
import time
from functools import lru_cache

# OpenStreetMap Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Features that should NOT have trees
INVALID_LANDUSE_TYPES = {
    # Buildings
    'building',
    'roof',

    # Sports facilities
    'pitch',
    'track',
    'sports_centre',
    'stadium',
    'tennis',
    'basketball',
    'baseball',
    'soccer',

    # Water bodies
    'water',
    'reservoir',
    'basin',
    'pond',
    'lake',
    'river',
    'stream',
    'wetland',

    # Paved areas
    'parking',
    'parking_space',
    'road',
    'highway',
    'path',
    'footway',
    'cycleway',

    # Other inappropriate areas
    'playground',  # Usually rubberized surface
    'swimming_pool',
    'fountain'
}

@lru_cache(maxsize=1000)
def check_coordinate_landuse(lat, lon, radius_meters=10):
    """
    Check if coordinate is in an invalid location for trees.

    Args:
        lat: Latitude
        lon: Longitude
        radius_meters: Search radius around point

    Returns:
        (is_valid, reason) tuple
        - is_valid: True if coordinate is suitable for trees
        - reason: Description of why it's invalid (or None if valid)
    """

    # Build Overpass QL query
    # Search for features within radius_meters of the coordinate
    query = f"""
    [out:json][timeout:25];
    (
      way(around:{radius_meters},{lat},{lon})["building"];
      way(around:{radius_meters},{lat},{lon})["leisure"="pitch"];
      way(around:{radius_meters},{lat},{lon})["leisure"="track"];
      way(around:{radius_meters},{lat},{lon})["leisure"="sports_centre"];
      way(around:{radius_meters},{lat},{lon})["leisure"="stadium"];
      way(around:{radius_meters},{lat},{lon})["leisure"="playground"];
      way(around:{radius_meters},{lat},{lon})["leisure"="swimming_pool"];
      way(around:{radius_meters},{lat},{lon})["natural"="water"];
      way(around:{radius_meters},{lat},{lon})["amenity"="parking"];
      way(around:{radius_meters},{lat},{lon})["highway"];
      relation(around:{radius_meters},{lat},{lon})["building"];
      relation(around:{radius_meters},{lat},{lon})["natural"="water"];
    );
    out body;
    >;
    out skel qt;
    """

    try:
        response = requests.post(
            OVERPASS_URL,
            data=query,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Check if any features were found
        if data.get('elements'):
            # Found some feature - check what it is
            for element in data['elements']:
                tags = element.get('tags', {})

                # Check building
                if 'building' in tags:
                    return False, f"Building ({tags.get('building', 'yes')})"

                # Check leisure facilities
                if 'leisure' in tags:
                    leisure = tags['leisure']
                    if leisure in ['pitch', 'track', 'sports_centre', 'stadium']:
                        return False, f"Sports facility ({leisure})"
                    if leisure == 'playground':
                        return False, "Playground (paved surface)"
                    if leisure == 'swimming_pool':
                        return False, "Swimming pool"

                # Check water
                if tags.get('natural') == 'water':
                    water_type = tags.get('water', 'water body')
                    return False, f"Water body ({water_type})"

                # Check parking
                if 'amenity' in tags and tags['amenity'] == 'parking':
                    return False, "Parking lot"

                # Check roads/paths
                if 'highway' in tags:
                    highway_type = tags['highway']
                    if highway_type in ['primary', 'secondary', 'tertiary', 'residential', 'service']:
                        return False, f"Road ({highway_type})"
                    if highway_type in ['footway', 'path', 'cycleway']:
                        return False, f"Paved path ({highway_type})"

        # No problematic features found
        return True, None

    except requests.exceptions.Timeout:
        # API timeout - assume valid to avoid blocking
        print(f"  ⚠️  Overpass API timeout for ({lat:.6f}, {lon:.6f}) - assuming valid")
        return True, None

    except Exception as e:
        # Other error - log and assume valid
        print(f"  ⚠️  Overpass API error for ({lat:.6f}, {lon:.6f}): {e} - assuming valid")
        return True, None


def validate_coordinate_with_retries(lat, lon, max_retries=3):
    """
    Validate coordinate with retries for API failures.

    Returns:
        (is_valid, reason) tuple
    """
    for attempt in range(max_retries):
        is_valid, reason = check_coordinate_landuse(lat, lon)

        if is_valid or reason:  # Got a definitive answer
            return is_valid, reason

        # Retry with exponential backoff
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)

    # All retries failed - assume valid
    return True, None


def batch_validate_coordinates(coords_list, delay_seconds=1):
    """
    Validate a batch of coordinates with rate limiting.

    Args:
        coords_list: List of (lat, lon) tuples
        delay_seconds: Delay between API calls

    Returns:
        List of (lat, lon, is_valid, reason) tuples
    """
    results = []

    for i, (lat, lon) in enumerate(coords_list):
        print(f"  Validating {i+1}/{len(coords_list)}: ({lat:.6f}, {lon:.6f})...", end='')

        is_valid, reason = validate_coordinate_with_retries(lat, lon)

        if is_valid:
            print(" ✓")
        else:
            print(f" ✗ ({reason})")

        results.append((lat, lon, is_valid, reason))

        # Rate limiting
        if i < len(coords_list) - 1:
            time.sleep(delay_seconds)

    return results


if __name__ == "__main__":
    # Test with some known coordinates
    print("Testing landuse validation:\n")

    test_coords = [
        # (lat, lon, expected_description)
        (40.6618, -73.9711, "Prospect Park - Sugar Bowl (should be valid)"),
        (40.6602, -73.9690, "Prospect Park center (should be valid)"),
        (40.6724, -73.9726, "Barclays Center building (should be invalid)"),
    ]

    for lat, lon, description in test_coords:
        print(f"{description}")
        is_valid, reason = check_coordinate_landuse(lat, lon)

        if is_valid:
            print(f"  ✓ Valid for trees")
        else:
            print(f"  ✗ Invalid: {reason}")
        print()

        time.sleep(1)  # Rate limiting
