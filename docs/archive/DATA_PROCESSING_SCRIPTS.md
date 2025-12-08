# Data Processing Scripts Reference

Complete reference for all Python scripts used in the NYC American Chestnut Map project.

## 📁 Script Organization

```
scripts/
├── build_trees_with_accuracy.py       ⭐ PRIMARY - Use this for yearly updates
├── build_with_landuse_validation.py   🐌 OPTIONAL - Slower, validates against OSM
├── update_confirmed_coordinates.py    📍 GPS - Merge field-collected coordinates
├── park_boundaries.py                 🗺️  LIBRARY - Park definitions & validation
├── extract_survey_locations.py        🔍 UTILITY - Parse Excel for locations
├── build_trees_from_survey.py         📦 ARCHIVE - Superseded by accuracy version
└── build_trees_with_growth_data.py    📦 ARCHIVE - Superseded by accuracy version
```

## ⭐ PRIMARY SCRIPT

### build_trees_with_accuracy.py

**Purpose**: Main data processing script - converts Excel survey to validated GeoJSON

**When to use**:
- Annual data updates
- Testing new survey data
- Regenerating map after park boundary changes

**Input Files**:
- `2024 year end chestnut results.xlsx` (or current year)
- `archive/survey_locations_geocoded.csv`
- `scripts/park_boundaries.py`

**Output Files**:
- `data/trees.json`

**Usage**:
```bash
source venv/bin/activate
python3 scripts/build_trees_with_accuracy.py
```

**What it does**:
1. Reads Excel survey (health status, measurements from 2021-2024)
2. Loads geocoded park area centers
3. Validates coordinates against park boundaries
4. Generates dispersed coordinates using spiral pattern (50m radius)
5. Categorizes health status (healthy/fair/poor/unknown)
6. Extracts multi-year growth data
7. Calculates location accuracy level
8. Creates GeoJSON with all metadata

**Output Example**:
```
Generating dispersed coordinates...
  PROSPECT PARK > Sugar Bowl: 15 trees, 15/15 within bounds
  PROSPECT PARK > Peninsula: 1 trees, 1/1 within bounds
  ...

✓ Successfully created data/trees.json
  Total trees: 85

Location accuracy distribution:
  area: 85

Health status distribution:
  fair: 18
  healthy: 50
  poor: 13
  unknown: 4
```

**Configuration**:
Edit these sections to customize:

```python
# Contact emails (line 33-38)
contact_map = {
    'Prospect Park Alliance': 'info@prospectpark.org',
    'Brooklyn Botanic Garden': 'conservation@bbg.org',
    'Green-Wood Cemetery': 'info@green-wood.com',
    'NYC Parks': 'forestry@parks.nyc.gov'
}

# Survey column mapping (line 79-84)
YEAR_COLUMNS = {
    '2021': {'height': 2, 'dbh': 3},
    '2022': {'height': 5, 'dbh': 6},
    '2023': {'height': 8, 'dbh': 9},
    '2024': {'height': 12, 'dbh': 13, 'health': 16}
}

# Dispersion radius (line 163)
radius_meters=50  # Adjust if needed
```

**Dependencies**:
```bash
pip install pandas openpyxl geopy
```

---

## 🐌 OPTIONAL SCRIPT

### build_with_landuse_validation.py

**Purpose**: Enhanced builder that validates coordinates against real-world features (buildings, sports fields, water)

**When to use**:
- Initial map creation
- Major park boundary changes
- When maximum coordinate accuracy is critical
- NOT for routine yearly updates (too slow)

**Input Files**: Same as build_trees_with_accuracy.py

**Output Files**: Same as build_trees_with_accuracy.py

**Usage**:
```bash
source venv/bin/activate
python3 scripts/build_with_landuse_validation.py
# Answer "yes" when prompted
# Wait ~45 seconds (0.5s per tree × 85 trees)
```

**What it does**:
Everything build_trees_with_accuracy.py does, PLUS:
- Queries OpenStreetMap Overpass API for each coordinate
- Checks for buildings, sports facilities, water bodies, paved areas
- Regenerates coordinates if landing on inappropriate features
- Rate-limited to respect OSM API terms (0.5s delay)

**Output Example**:
```
PROSPECT PARK > Peninsula: 1 trees
  Validating 1/1: (40.655000, -73.962500)... ✗ (Paved path (footway))
  ⚠️  Skipping coordinate in Paved path (footway)
  [Regenerates with different angle/distance]
  Validating 1/1: (40.654987, -73.962534)... ✓
```

**Performance**:
- Standard build: ~2 seconds
- Landuse validation: ~45 seconds for 85 trees
- Scales linearly with tree count

**Dependencies**:
```bash
pip install pandas openpyxl geopy requests
```

**See**: [LANDUSE_VALIDATION.md](LANDUSE_VALIDATION.md) for details

---

## 📍 GPS INTEGRATION SCRIPT

### update_confirmed_coordinates.py

**Purpose**: Merge GPS-collected coordinates from field work into trees.json

**When to use**:
- After field GPS collection campaign
- Upgrading "area" accuracy to "confirmed" accuracy
- Correcting misplaced coordinates

**Input Files**:
- `tree_coordinates_YYYY-MM-DD.csv` (from GPS collector)
- `data/trees.json` (current)

**Output Files**:
- `data/trees.json` (updated)

**Usage**:
```bash
python3 scripts/update_confirmed_coordinates.py tree_coordinates_2024-12-06.csv
```

**CSV Format**:
```csv
tree_id,park,area,latitude,longitude,accuracy_meters,collector,notes,timestamp
NYC-AC-001,PROSPECT PARK,Sugar Bowl,40.661845,-73.971023,3.2,Jane Smith,At base of tree,2024-12-06T15:23:45
```

**What it does**:
1. Reads confirmed coordinates from CSV
2. Loads current trees.json
3. Matches trees by tree_id or tree_number
4. Updates coordinates to GPS location
5. Changes accuracy level to "confirmed"
6. Adds collector name and timestamp
7. Appends GPS notes to existing notes

**Output Example**:
```
Reading confirmed coordinates from tree_coordinates_2024-12-06.csv...
  Found 15 confirmed coordinates

  ✓ Updated NYC-AC-001: (40.661800, -73.971100) → (40.661845, -73.971023)
  ✓ Updated NYC-AC-002: (40.661714, -73.970996) → (40.661832, -73.971045)
  ...

✓ Successfully updated data/trees.json
  Updated coordinates: 15/85

Accuracy distribution:
  confirmed: 15
  area: 70
```

**ID Matching**:
Handles both formats:
- `NYC-AC-001` (tree_id)
- `7` or `Tree #7` (tree_number)

**Dependencies**:
```bash
pip install pandas
```

**See**: [GPS_COLLECTION_GUIDE.md](GPS_COLLECTION_GUIDE.md) for field workflow

---

## 🗺️ LIBRARY MODULE

### park_boundaries.py

**Purpose**: Park boundary definitions and coordinate validation functions

**When to use**:
- Imported by build scripts (not run directly)
- Edit to add new parks or areas
- Update area coordinates

**Structure**:
```python
PARK_BOUNDARIES = {
    "PARK_NAME": {
        "center": {"lat": XX.XXXX, "lon": -XX.XXXX},
        "bbox": {
            "north": XX.XXXX, "south": XX.XXXX,
            "east": -XX.XXXX, "west": -XX.XXXX
        },
        "areas": {
            "Area Name": {"lat": XX.XXXX, "lon": -XX.XXXX}
        }
    }
}
```

**Functions**:

```python
# Check if coordinate is within park
is_point_in_park(lat, lon, park_name)
→ (is_valid, distance_meters)

# Get coordinates for specific area
get_area_center(park_name, area_name)
→ (lat, lon) or None

# Generate dispersed coordinates
generate_dispersed_coordinates(center_lat, center_lon, num_points,
                               radius_meters=50, park_name=None,
                               validate_landuse=False)
→ [(lat, lon), ...]

# Calculate accuracy level
calculate_accuracy_level(park_name, area_name, lat, lon, is_confirmed=False)
→ {"level": "area", "description": "...", "radius_meters": 50, "confidence": 70}
```

**Adding a New Park**:

1. Find center coordinates (Google Maps)
2. Define bounding box (rough rectangle around park)
3. List area centers (specific locations within park)

```python
"NEW PARK": {
    "center": {"lat": 40.6602, "lon": -73.9690},
    "bbox": {
        "north": 40.6756,  # Northernmost point
        "south": 40.6449,  # Southernmost point
        "east": -73.9610,  # Easternmost point
        "west": -73.9800   # Westernmost point
    },
    "areas": {
        "North Meadow": {"lat": 40.6700, "lon": -73.9650},
        "South Woods": {"lat": 40.6500, "lon": -73.9750}
    }
}
```

**Testing**:
```bash
python3 scripts/park_boundaries.py
```

**Dependencies**:
```bash
pip install shapely geopy
```

---

## 🔍 UTILITY SCRIPT

### extract_survey_locations.py

**Purpose**: Parse Excel survey to extract unique park/area combinations

**When to use**:
- Processing new survey file
- Identifying locations to geocode
- Verifying survey structure

**Input Files**:
- `2024 year end chestnut results.xlsx`

**Output Files**:
- `survey_locations_to_geocode.csv`

**Usage**:
```bash
python3 scripts/extract_survey_locations.py
```

**Output**:
```csv
park,area,location_description
PROSPECT PARK,Sugar Bowl,PROSPECT PARK - Sugar Bowl
PROSPECT PARK,Peninsula,PROSPECT PARK - Peninsula
BROOKLYN BOTANIC GARDEN,Native Flora Garden,BROOKLYN BOTANIC GARDEN - Native Flora Garden
```

**What it does**:
1. Reads Excel file (header=None to handle custom format)
2. Identifies park headers (ALL CAPS lines)
3. Identifies area headers (lines ending with ":")
4. Extracts unique combinations
5. Creates geocoding template

**Dependencies**:
```bash
pip install pandas openpyxl
```

---

## 📦 ARCHIVED SCRIPTS

### build_trees_from_survey.py

**Status**: SUPERSEDED by build_trees_with_accuracy.py
**Reason**: Lacks boundary validation and accuracy system
**Keep for**: Historical reference only

### build_trees_with_growth_data.py

**Status**: SUPERSEDED by build_trees_with_accuracy.py
**Reason**: Missing coordinate validation
**Keep for**: Shows original growth data implementation

---

## 🔄 Typical Workflow

### Annual Update (Standard)

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Place new Excel file: "2025 year end chestnut results.xlsx"

# 3. Extract locations (if needed for new areas)
python3 scripts/extract_survey_locations.py

# 4. Build data with validation
python3 scripts/build_trees_with_accuracy.py

# 5. Test locally
python3 -m http.server 8000
# Visit http://localhost:8000

# 6. Deploy
git add data/trees.json
git commit -m "Update 2025 survey data"
git push origin main
```

### With GPS Collection

```bash
# 1-4. Same as above

# 5. Collect GPS coordinates in field using tools/coordinate_collector.html

# 6. Merge GPS data
python3 scripts/update_confirmed_coordinates.py tree_coordinates_2025-03-15.csv

# 7. Test and deploy
```

### First-Time Setup (New Park)

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Add park to park_boundaries.py

# 3. Test boundary validation
python3 scripts/park_boundaries.py

# 4. Build with landuse validation (one-time)
python3 scripts/build_with_landuse_validation.py

# 5. Future updates use standard build
python3 scripts/build_trees_with_accuracy.py
```

---

## 🛠️ Configuration Reference

### Health Status Categorization

Edit `build_trees_with_accuracy.py` line 53-76:

```python
def categorize_health_status(health_str):
    # HEALTHY: excellent/very good/good without blight
    if any(word in lower for word in ['excellent', 'very good']):
        return 'healthy', original

    # FAIR: some issues but surviving
    if any(word in lower for word in ['fair', 'ok', 'maybe ok']):
        return 'fair', original

    # POOR: severe issues or dead
    if any(word in lower for word in ['dead', 'died', 'gone']):
        return 'poor', original

    # UNKNOWN: uncertain
    return 'unknown', original
```

### Coordinate Dispersion

Edit `park_boundaries.py` line 162-174:

```python
# Spiral pattern parameters
angle = i * 137.5  # Golden angle (don't change)
angle_jitter = random.uniform(-5, 5)  # ±5 degrees variation

# Distance parameters
base_dist = math.sqrt(i / max(num_points, 1)) * radius_meters
dist_jitter = random.uniform(-5, 5)  # ±5 meters variation
```

### API Rate Limiting

Edit `tools/landuse_validator.py` line 200:

```python
time.sleep(0.5)  # Rate limiting for OSM API (adjust if needed)
```

---

## 📊 Output Files Comparison

| Script | Output | Size | Time | Use Case |
|--------|--------|------|------|----------|
| build_trees_with_accuracy.py | trees.json | ~100KB | 2s | Annual updates |
| build_with_landuse_validation.py | trees.json | ~100KB | 45s | Initial creation |
| update_confirmed_coordinates.py | trees.json | ~100KB | 1s | GPS merges |

All produce the same format, just with different accuracy levels.

---

## 🆘 Common Issues

### ImportError: No module named 'pandas'
```bash
source venv/bin/activate
pip install pandas openpyxl geopy requests shapely
```

### FileNotFoundError: Excel file not found
```bash
# Verify filename matches
ls *.xlsx

# Update script if different, or rename file
```

### ValueError: coordinates outside park
```bash
# Update park_boundaries.py with correct area centers
# Re-run build script
```

### RequestException: OSM API timeout
```bash
# Only affects landuse validation
# Increase timeout in landuse_validator.py line 95:
timeout=60  # Increase from 30
```

---

**See Also**:
- [YEARLY_DATA_WORKFLOW.md](YEARLY_DATA_WORKFLOW.md) - Step-by-step annual process
- [COORDINATE_ACCURACY_SYSTEM.md](COORDINATE_ACCURACY_SYSTEM.md) - Technical details
- [LANDUSE_VALIDATION.md](LANDUSE_VALIDATION.md) - OSM validation system
