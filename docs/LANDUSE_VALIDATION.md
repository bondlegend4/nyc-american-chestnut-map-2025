# Landuse Validation System

## Overview

Added capability to validate generated coordinates against real-world features to avoid placing trees in inappropriate locations like buildings, sports fields, or water bodies.

## Problem Statement

Even with park boundary validation, artificial coordinates might land on:
- **Buildings** (houses, community centers, bathrooms)
- **Sports facilities** (baseball diamonds, tennis courts, running tracks)
- **Water bodies** (ponds, lakes, streams)
- **Paved areas** (parking lots, roads, paths)
- **Playgrounds** (rubberized surfaces where trees can't grow)

## Solution

### 1. OpenStreetMap Integration

**File**: [landuse_validator.py](landuse_validator.py)

Uses the Overpass API to query OpenStreetMap for features within a radius of each coordinate.

**Features Checked**:
```python
INVALID_LANDUSE_TYPES = {
    # Buildings
    'building', 'roof',

    # Sports facilities
    'pitch', 'track', 'sports_centre', 'stadium',
    'tennis', 'basketball', 'baseball', 'soccer',

    # Water bodies
    'water', 'reservoir', 'basin', 'pond', 'lake',
    'river', 'stream', 'wetland',

    # Paved areas
    'parking', 'parking_space', 'road', 'highway',
    'path', 'footway', 'cycleway',

    # Other
    'playground', 'swimming_pool', 'fountain'
}
```

### 2. Validation Function

```python
def check_coordinate_landuse(lat, lon, radius_meters=10):
    """
    Check if coordinate is in an invalid location for trees.

    Returns:
        (is_valid, reason) tuple
        - is_valid: True if suitable for trees
        - reason: Why it's invalid (or None if valid)
    """
```

**Example Queries**:
- Searches within 10m radius
- Checks for buildings, sports fields, water
- Returns reason if invalid: "Building (residential)", "Water body (pond)", etc.

### 3. Enhanced Coordinate Generation

**File**: [park_boundaries.py](park_boundaries.py:129-215)

Added `validate_landuse` parameter to `generate_dispersed_coordinates()`:

```python
def generate_dispersed_coordinates(
    center_lat, center_lon, num_points,
    radius_meters=50,
    park_name=None,
    validate_landuse=False  # NEW PARAMETER
):
```

**Two-Level Validation**:
1. **Park boundary check** (fast, local)
2. **Landuse check** (slow, requires API call)

### 4. Optional Build Script

**File**: [build_with_landuse_validation.py](build_with_landuse_validation.py)

Separate build script that enables landuse validation:

```bash
python3 build_with_landuse_validation.py
```

**Performance**:
- ~0.5 seconds per tree (API rate limiting)
- 85 trees ≈ 45 seconds total
- Caches results with `@lru_cache`

## Usage

### Standard Build (Fast)

```bash
# Without landuse validation
python3 build_trees_with_accuracy.py

# Takes ~2 seconds
# Validates park boundaries only
```

### Validated Build (Slow, Maximum Accuracy)

```bash
# With landuse validation
python3 build_with_landuse_validation.py

# Takes ~45 seconds
# Validates park boundaries AND real-world features
```

**When to Use Landuse Validation**:
- Initial data generation
- After major park boundary changes
- When precision is critical
- For production deployment

**When to Skip Landuse Validation**:
- Development/testing
- Iterative rebuilds
- When you know coordinates are generally good

## Example Output

```
Generating dispersed coordinates with landuse validation...

  PROSPECT PARK > Sugar Bowl: 15 trees
    Validating 1/15: (40.661800, -73.971100)... ✓
    Validating 2/15: (40.661714, -73.970996)... ✓
    Validating 3/15: (40.661845, -73.971245)... ✗ (Sports facility (pitch))
    ⚠️  Skipping coordinate in Sports facility (pitch)
    Validating 3/15: (40.661823, -73.971189)... ✓
    ...
  ✓ Generated: 15/15 within park bounds
```

## Washington Park Issue

### Current Status

The geocoding service returned the same coordinates for all Washington Park areas:
- Old School House: 40.6732161, -73.9850305
- Vanderbilt Playground: 40.6732161, -73.9850305
- Lefferts Homestead: 40.6732161, -73.9850305
- PPW/7th St.: 40.6732161, -73.9850305

All were geocoded to the park center, not specific area locations.

### Investigation Needed

"WASHINGTON PARK" in Brooklyn could refer to:
1. **Fort Greene Park** (sometimes called Washington Park historically)
2. **J.J. Byrne Playground** (in Washington Park neighborhood)
3. **A different park** entirely

### Recommended Fix

1. **Manual coordinate lookup** for each Washington Park area
2. **Update park_boundaries.py** with correct area centers
3. **Re-run build script**

Example fix:
```python
"WASHINGTON PARK": {
    "areas": {
        "Old School House": {"lat": 40.XXXX, "lon": -73.XXXX},  # Need actual coords
        "Vanderbilt Playground": {"lat": 40.XXXX, "lon": -73.XXXX},
        "Lefferts Homestead": {"lat": 40.XXXX, "lon": -73.XXXX},
        "PPW/7th St.": {"lat": 40.XXXX, "lon": -73.XXXX}
    }
}
```

### Verification Steps

1. **Check survey Excel** for any location details
2. **Contact NYC Parks** for Washington Park tree locations
3. **Use Google Maps** to find "Washington Park" + area names
4. **GPS collection** for these 6 trees specifically

## API Rate Limiting

### Overpass API Limits

- Max 2 requests per second
- Built-in 0.5s delay between requests
- Automatic retry with exponential backoff
- Caches results to avoid duplicate queries

### Error Handling

```python
try:
    response = requests.post(OVERPASS_URL, data=query, timeout=30)
    response.raise_for_status()
    # Process data...
except requests.exceptions.Timeout:
    # Assume valid to avoid blocking
    return True, None
except Exception as e:
    # Log error and assume valid
    print(f"⚠️  API error: {e} - assuming valid")
    return True, None
```

**Graceful Degradation**:
- If API fails, assume coordinate is valid
- Prevents build from failing due to network issues
- Logs warnings for manual review

## Testing

### Test Script

```bash
python3 landuse_validator.py
```

**Test Coordinates**:
1. Prospect Park - Sugar Bowl (should pass)
2. Prospect Park center (should pass)
3. Barclays Center building (should fail - building)

### Example Output

```
Testing landuse validation:

Prospect Park - Sugar Bowl (should be valid)
  ✓ Valid for trees

Prospect Park center (should be valid)
  ✓ Valid for trees

Barclays Center building (should be invalid)
  ✗ Invalid: Building (arena)
```

## Future Enhancements

### 1. Offline Mode

Download park OSM data once, validate locally:
```python
import osmium
# Parse park OSM data
# Validate against local database
```

### 2. Green Space Detection

Prefer coordinates in green/vegetated areas:
```python
if tags.get('landuse') == 'grass':
    preference_score += 10
if tags.get('natural') in ['wood', 'tree_row']:
    preference_score += 20
```

### 3. Batch Validation

Validate all coordinates in single API call:
```python
# Query all features in park at once
# Check each coordinate against cached feature list
```

### 4. Visual Validation Tool

Web interface to review and adjust coordinates:
- Show satellite imagery
- Overlay generated coordinates
- Allow manual adjustment
- Export corrections

## Dependencies

```bash
pip install requests
```

No additional dependencies - uses only standard library + requests.

## Summary

**Two-tier validation system**:
1. **Fast** (2s): Park boundaries only
2. **Slow** (45s): Park boundaries + real-world features

**Washington Park issue**:
- Currently using park center for all 6 trees
- Need to verify actual park name and area locations
- May require manual coordinate lookup or GPS collection

**Landuse validation**:
- Optional, controlled by `validate_landuse` parameter
- Checks 15+ inappropriate landuse types
- Regenerates coordinates if invalid
- Rate-limited to respect OSM API

---

**Status**: ✅ Landuse validation system complete
**Usage**: Optional, for maximum accuracy
**Washington Park**: ⚠️  Needs manual verification
