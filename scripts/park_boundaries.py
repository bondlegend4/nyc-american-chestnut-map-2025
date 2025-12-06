#!/usr/bin/env python3
"""
park_boundaries.py

Defines approximate park boundaries for NYC parks to validate tree coordinates.
Uses bounding boxes and polygon boundaries where available.
"""

import json
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

# Park boundary definitions
# Each park has: center, bounding box, and optionally a detailed polygon
PARK_BOUNDARIES = {
    "PROSPECT PARK": {
        "center": {"lat": 40.6602, "lon": -73.9690},
        "bbox": {
            "north": 40.6756,
            "south": 40.6449,
            "east": -73.9610,
            "west": -73.9800  # Extended west to include Bartel-Pritchard entrance area
        },
        "areas": {
            "Sugar Bowl": {"lat": 40.6618, "lon": -73.9711},
            "Peninsula": {"lat": 40.6550, "lon": -73.9625},
            "Lookout Hill": {"lat": 40.6632, "lon": -73.9695},
            "West Drive": {"lat": 40.6620, "lon": -73.9750},
            "Litchfield Villa": {"lat": 40.6669, "lon": -73.9738},
            "Bartel-Pritchard": {"lat": 40.6605, "lon": -73.9775},  # Moved east into park boundary
            "Wellhouse": {"lat": 40.6648, "lon": -73.9685},
            "Vail": {"lat": 40.6590, "lon": -73.9650},
            "PPW/8th St.": {"lat": 40.6642, "lon": -73.9742},
            "Breeze Hill": {"lat": 40.6655, "lon": -73.9680},
            "Lefferts Homestead": {"lat": 40.6624, "lon": -73.9650},
            "Quaker Cemetery": {"lat": 40.6690, "lon": -73.9720},
            "GAP Berms": {"lat": 40.6580, "lon": -73.9700}
        }
    },
    "BROOKLYN BOTANIC GARDEN": {
        "center": {"lat": 40.6677, "lon": -73.9636},
        "bbox": {
            "north": 40.6700,
            "south": 40.6650,
            "east": -73.9600,
            "west": -73.9680
        },
        "areas": {
            "Native Flora Garden": {"lat": 40.6680, "lon": -73.9640}
        }
    },
    "FORT GREEN PARK": {
        "center": {"lat": 40.6920, "lon": -73.9745},
        "bbox": {
            "north": 40.6935,
            "south": 40.6890,
            "east": -73.9720,
            "west": -73.9770
        }
    },
    "WASHINGTON PARK": {
        "center": {"lat": 40.6732, "lon": -73.9850},
        "bbox": {
            "north": 40.6760,
            "south": 40.6700,
            "east": -73.9820,
            "west": -73.9880
        },
        "areas": {
            "Old School House": {"lat": 40.6735, "lon": -73.9845},
            "Vanderbilt Playground": {"lat": 40.6740, "lon": -73.9860},
            "Lefferts Homestead": {"lat": 40.6720, "lon": -73.9855},
            "PPW/7th St.": {"lat": 40.6745, "lon": -73.9835}
        }
    },
    "GREENWOOD CEMETERY": {
        "center": {"lat": 40.6565, "lon": -73.9935},
        "bbox": {
            "north": 40.6650,
            "south": 40.6480,
            "east": -73.9850,
            "west": -74.0020
        },
        "areas": {
            "Chestnut Hill": {"lat": 40.6580, "lon": -73.9950}
        }
    }
}

def is_point_in_park(lat, lon, park_name):
    """
    Check if a point is within park boundaries.

    Returns: (is_valid, distance_from_center_meters)
    """
    if park_name not in PARK_BOUNDARIES:
        return False, None

    park = PARK_BOUNDARIES[park_name]
    bbox = park["bbox"]

    # Check bounding box
    if not (bbox["south"] <= lat <= bbox["north"] and
            bbox["west"] <= lon <= bbox["east"]):
        # Calculate distance from center
        from geopy.distance import geodesic
        center = (park["center"]["lat"], park["center"]["lon"])
        point = (lat, lon)
        distance = geodesic(center, point).meters
        return False, distance

    return True, 0

def get_area_center(park_name, area_name):
    """Get the center coordinates for a specific park area."""
    if park_name not in PARK_BOUNDARIES:
        return None

    park = PARK_BOUNDARIES[park_name]

    # Check if specific area exists
    if "areas" in park and area_name in park["areas"]:
        area = park["areas"][area_name]
        return area["lat"], area["lon"]

    # Fall back to park center
    return park["center"]["lat"], park["center"]["lon"]

def generate_dispersed_coordinates(center_lat, center_lon, num_points, radius_meters=50, park_name=None, validate_landuse=False):
    """
    Generate dispersed coordinates around a center point.
    Uses spiral pattern to avoid overlap and validates against park boundaries.

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        num_points: Number of points to generate
        radius_meters: Maximum radius for dispersion
        park_name: Name of park for boundary validation (optional)
        validate_landuse: If True, check against buildings/water/sports fields (slower, uses OSM API)

    Returns:
        List of (lat, lon) tuples
    """
    import math
    import random

    # Import landuse validator if needed
    if validate_landuse:
        try:
            from landuse_validator import check_coordinate_landuse
            import time
        except ImportError:
            print("  ⚠️  landuse_validator not available, skipping landuse validation")
            validate_landuse = False

    coords = []

    for i in range(num_points):
        attempts = 0
        max_attempts = 100  # Increased for landuse validation

        while attempts < max_attempts:
            # Spiral pattern: angle increases with each point
            angle = i * 137.5  # Golden angle in degrees
            # Add small random variation to avoid perfectly regular patterns
            angle_jitter = random.uniform(-5, 5)
            actual_angle = angle + angle_jitter

            # Distance increases with square root for even distribution
            # Add small random variation to distance
            base_dist = math.sqrt(i / max(num_points, 1)) * radius_meters
            dist_jitter = random.uniform(-5, 5)  # ±5 meters
            dist = max(0, base_dist + dist_jitter)

            # Convert to lat/lon offset
            # 1 degree latitude ≈ 111km
            lat_offset = (dist * math.cos(math.radians(actual_angle))) / 111000
            # Longitude adjustment for latitude (gets smaller near poles)
            lon_offset = (dist * math.sin(math.radians(actual_angle))) / (111000 * math.cos(math.radians(center_lat)))

            new_lat = center_lat + lat_offset
            new_lon = center_lon + lon_offset

            # Validation checks
            is_valid = True

            # Check 1: Park boundary validation
            if park_name:
                is_in_park, _ = is_point_in_park(new_lat, new_lon, park_name)
                if not is_in_park:
                    is_valid = False

            # Check 2: Landuse validation (buildings, water, sports fields)
            if is_valid and validate_landuse:
                is_appropriate, reason = check_coordinate_landuse(new_lat, new_lon, radius_meters=5)
                if not is_appropriate:
                    print(f"    ⚠️  Skipping coordinate in {reason}")
                    is_valid = False
                time.sleep(0.5)  # Rate limiting for OSM API

            if is_valid:
                coords.append((new_lat, new_lon))
                break
            else:
                # Try with smaller radius and different angle
                radius_meters *= 0.95
                attempts += 1

        if attempts >= max_attempts:
            # Fallback: use center point if unable to find valid coordinate
            print(f"    ⚠️  Using center point after {max_attempts} attempts")
            coords.append((center_lat, center_lon))

    return coords

def calculate_accuracy_level(park_name, area_name, lat, lon, is_confirmed=False):
    """
    Calculate accuracy level for a coordinate.

    Returns: dict with accuracy info
    """
    if is_confirmed:
        return {
            "level": "confirmed",
            "description": "GPS-verified location",
            "radius_meters": 5,
            "confidence": 100
        }

    # Check if within park boundaries
    is_valid, distance = is_point_in_park(lat, lon, park_name)

    if not is_valid and distance:
        return {
            "level": "estimated",
            "description": f"Approximate location (geocoded park boundary, {int(distance)}m from park center)",
            "radius_meters": int(distance),
            "confidence": 30
        }

    # Has specific area
    if area_name and area_name in PARK_BOUNDARIES.get(park_name, {}).get("areas", {}):
        return {
            "level": "area",
            "description": f"Geocoded to '{area_name}' area within park",
            "radius_meters": 50,
            "confidence": 70
        }

    # Park-level geocoding only
    return {
        "level": "park",
        "description": "Geocoded to park center only",
        "radius_meters": 100,
        "confidence": 50
    }

if __name__ == "__main__":
    # Test the boundaries
    print("Testing park boundaries:\n")

    # Test Prospect Park
    test_coords = [
        (40.6618, -73.9711, "PROSPECT PARK", "Sugar Bowl"),
        (40.7000, -73.9711, "PROSPECT PARK", "Invalid"),  # Outside
    ]

    for lat, lon, park, area in test_coords:
        valid, dist = is_point_in_park(lat, lon, park)
        accuracy = calculate_accuracy_level(park, area, lat, lon)
        print(f"{park} - {area}:")
        print(f"  Valid: {valid}, Distance: {dist}m" if dist else f"  Valid: {valid}")
        print(f"  Accuracy: {accuracy['level']} - {accuracy['description']}")
        print()
