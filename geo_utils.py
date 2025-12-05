# -*- coding: utf-8 -*-
"""
geo_utils.py

Utility functions for geocoding addresses and calculating distances.
"""

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from constants import GEOCODER_USER_AGENT_BASE, NUMBER_OF_CAMERAS_TO_CHECK

def get_coords_from_address(address, app_suffix="generic"):
    """
    Converts an address string to (latitude, longitude) using Nominatim.

    Args:
        address (str): The address to geocode.
        app_suffix (str): A suffix to append to the base user agent for identification.

    Returns:
        tuple: (latitude, longitude) tuple, or None on failure.
    """
    print(f"Geocoding address: '{address}'...")
    # Construct a unique user agent
    user_agent = f"{GEOCODER_USER_AGENT_BASE}_{app_suffix}"
    geolocator = Nominatim(user_agent=user_agent)
    try:
        location = geolocator.geocode(address, timeout=10) # 10 second timeout
        if location:
            coords = (location.latitude, location.longitude)
            print(f"--- Geocoding successful: {coords}")
            return coords
        else:
            print(f"!!! ERROR: Could not find coordinates for address: '{address}'")
            return None
    except GeocoderTimedOut:
        print("!!! ERROR: Geocoding service timed out.")
        return None
    except GeocoderServiceError as e:
        print(f"!!! ERROR: Geocoding service error: {e}")
        return None
    except Exception as e:
        print(f"!!! ERROR: An unexpected error occurred during geocoding: {e}")
        return None

def calculate_distance(coords1, coords2):
    """
    Calculates the geodesic distance between two (lat, lon) points in miles.

    Args:
        coords1 (tuple): First (latitude, longitude) tuple.
        coords2 (tuple): Second (latitude, longitude) tuple.

    Returns:
        float: Distance in miles, or float('inf') if input is invalid.
    """
    if not (isinstance(coords1, tuple) and len(coords1) == 2 and
            isinstance(coords2, tuple) and len(coords2) == 2):
        return float('inf')
    try:
        # Ensure coordinates are numeric before calculation
        lat1, lon1 = float(coords1[0]), float(coords1[1])
        lat2, lon2 = float(coords2[0]), float(coords2[1])
        distance = geodesic((lat1, lon1), (lat2, lon2)).miles
        return distance
    except (ValueError, TypeError) as e:
        print(f"!!! Warning: Invalid coordinates for distance calculation ({coords1}, {coords2}): {e}")
        return float('inf')
    except Exception as e:
        print(f"!!! Warning: Error calculating geodesic distance: {e}")
        return float('inf')

def find_nearby_cameras(target_coords, all_cameras, num_cameras=NUMBER_OF_CAMERAS_TO_CHECK):
    """
    Finds the N closest cameras from a list to a target coordinate point.

    Args:
        target_coords (tuple): The target (latitude, longitude).
        all_cameras (list): A list of camera dictionaries, each must have a 'coords' tuple.
        num_cameras (int): The maximum number of nearby cameras to return.

    Returns:
        list: A list of the closest camera dictionaries, sorted by distance (ascending).
              Each dictionary will have an added 'distance_miles' key.
    """
    if not target_coords or not all_cameras:
        return []

    cameras_with_distance = []
    for cam in all_cameras:
        cam_coords = cam.get("coords")
        if cam_coords:
            distance = calculate_distance(target_coords, cam_coords)
            if distance != float('inf'):
                cam_copy = cam.copy() # Avoid modifying original list items
                cam_copy["distance_miles"] = distance
                cameras_with_distance.append(cam_copy)
        # else: print(f"Skipping camera {cam.get('id')} - missing 'coords'") # Debug

    # Sort by distance
    cameras_with_distance.sort(key=lambda x: x["distance_miles"])

    # Return the top N
    return cameras_with_distance[:num_cameras]