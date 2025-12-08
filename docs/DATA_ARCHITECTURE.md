# NYC American Chestnut Map - Data Architecture

## Overview

This project uses **ArcGIS as the PRIMARY data source** and complements it with historical growth data from Excel surveys.

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA PIPELINE                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  ArcGIS Feature  │         │  Excel Survey    │
│     Service      │         │    Data (2024)   │
│   (PRIMARY)      │         │  (SUPPLEMENT)    │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ Coordinates                │ Growth History
         │ Current Health (Notes)     │ (2021-2024)
         │ Names (LV 05, BP 03, etc)  │ Year-over-year
         │ Variants (PBR/Native)      │ measurements
         │ Seed numbers               │
         │ Plant years                │
         │                            │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  enhance_arcgis_       │
         │  with_growth.py        │
         │  (Merger Script)       │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   data/trees.json      │
         │   (Combined Output)    │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │     index.html         │
         │  (Interactive Map)     │
         └────────────────────────┘
```

## Data Sources

### 1. PRIMARY Source: ArcGIS Feature Service

**URL:** `https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0`

**Provides:**
- **Accurate GPS coordinates** (verified locations)
- **Current health status** (from Notes field, e.g., "11/25 very good")
- **Tree identifiers** (Name field: "LV 05", "BP 03", "BBG 01")
- **Location details** (Area field: "Litchfield Villa", "Bartel-Pritchard")
- **Variant information** (PBR, Native, Hybrid)
- **Seed numbers** (for breeding program tracking)
- **Plant years** (when trees were planted)
- **Origin** (TACF, GW, etc.)

**Key Fields:**
```javascript
{
  "FID": 1,                    // Feature ID
  "Name": "LV 05",             // Tree identifier
  "Plant Yr": 2015,            // Year planted
  "Area": "Litchfield Villa",  // Location name
  "Origin": "TACF",            // Organization
  "Variant": "PBR",            // Pure American Blight Resistant
  "Seed": "40",                // Seed number for tracking
  "Notes": "11/25 very good",  // Latest health observation
  "CreationDate": "2024-01-15",
  "EditDate": "2024-11-25"
}
```

### 2. SUPPLEMENTAL Source: Excel Survey Data

**File:** `archive/2024 year end chestnut results.xlsx`

**Provides:**
- **Historical growth measurements** (2021, 2022, 2023, 2024)
- **Year-over-year tracking** (height and DBH)
- **Detailed location context** (sub-areas within parks)

**Structure:**
```
Location Headers (ALL CAPS):  PROSPECT PARK
Sub-locations (with colon):   Litchfield Villa:
Tree rows:                     Tree# | 2021 | 2022 | 2023 | 2024 | Health
                              H  DBH   H  DBH   H  DBH   H  DBH
```

## Matching Logic

Trees are matched between ArcGIS and Excel using:

**Tree Key Format:** `ABBREVIATION-NUMBER`

Examples:
- `LV-05` = Litchfield Villa tree #5
- `BP-03` = Bartel-Pritchard tree #3
- `LOH-07` = Lookout Hill tree #7

### Location Abbreviation Mapping

| Excel Location | ArcGIS Abbrev | Example |
|----------------|---------------|---------|
| Sugar Bowl | SB | SB-24 |
| Litchfield Villa | LV | LV-05 |
| Lookout Hill | LOH | LOH-10 |
| Lefferts House | LH | LH-01 |
| West Drive | WD | WD-02 |
| Bartel-Pritchard | BP | BP-03 |
| Peninsula | PN | PN-05 |
| Vale of Cashmere | VC | VC-04 |
| Breeze Hill | BH | BH-02 |
| Fallkill | FK | FK-09 |
| Brooklyn Botanic Garden | BBG | BBG-01 |
| Green-Wood Cemetery | GW | GW-04 |
| Quaker Cemetery | QC | QC-05 |

## Output Data Structure

### Enhanced Trees JSON

```javascript
{
  "type": "FeatureCollection",
  "metadata": {
    "last_updated": "2025-12-08",
    "primary_source": "ArcGIS Feature Service",
    "supplements": [{
      "type": "excel",
      "description": "Historical growth measurements",
      "trees_with_growth": 60
    }]
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.9665, 40.6695]  // From ArcGIS
      },
      "properties": {
        // PRIMARY data from ArcGIS
        "tree_id": "NYC-AC-005",
        "name": "LV 05",                    // ArcGIS identifier
        "organization": "TACF",
        "area": "Litchfield Villa",
        "variant": "Native",
        "seed": "25",
        "planted_date": "2015-04-15",

        // Health from ArcGIS Notes field
        "health_status": "healthy",         // Parsed from notes
        "health_detail": "11/25 very good", // Original notes
        "last_survey_date": "2024-11-25",

        // SUPPLEMENTAL growth data from Excel
        "excel_match": "Litchfield Villa #5",  // For transparency
        "tree_number": 5,
        "growth_data": {
          "2021": { "height": 6.5, "dbh": 0.4 },
          "2022": { "height": 7.2, "dbh": 0.45 },
          "2023": { "height": 8.3, "dbh": 0.5 },
          "2024": { "height": 8.0, "dbh": 0.5 }
        },

        // Location accuracy
        "location_accuracy": {
          "level": "verified",
          "description": "Verified coordinates from ArcGIS",
          "confidence": 95
        }
      }
    }
  ]
}
```

## Usage

### Step 1: Fetch Fresh ArcGIS Data

```bash
source venv/bin/activate
python3 scripts/import_from_arcgis.py \
  --url "https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0" \
  --output data/trees_arcgis_fresh.json
```

### Step 2: Enhance with Excel Growth History

```bash
python3 scripts/enhance_arcgis_with_growth.py \
  --arcgis data/trees_arcgis_fresh.json \
  --excel "archive/2024 year end chestnut results.xlsx" \
  --output data/trees.json
```

### Step 3: View the Map

Open `index.html` in a browser. The map will display:
- Tree locations from ArcGIS (accurate GPS coordinates)
- Current health status (from ArcGIS Notes)
- Historical growth charts (from Excel, if available)
- All ArcGIS metadata (variants, seeds, origins)

## Benefits of This Architecture

### ✅ Advantages

1. **ArcGIS as Source of Truth**
   - Professional GIS coordinates (not estimated)
   - Maintained by field surveyors
   - Up-to-date health observations in Notes field
   - Proper tree identification (Name field)

2. **Excel as Historical Complement**
   - Year-over-year growth tracking
   - Detailed measurements (height, DBH)
   - Doesn't override ArcGIS coordinates

3. **Transparency**
   - `excel_match` field shows which Excel entry matched
   - Unmatched trees are reported
   - Easy to identify discrepancies

4. **Modular Design**
   - Each script has a single responsibility
   - Can update ArcGIS data without re-processing Excel
   - Can add new data sources easily

### 🎯 Data Quality

**Current Status (as of 2025-12-08):**
- Total trees in ArcGIS: **161**
- Health status from Notes: **31** trees
- Growth history matched: **60** trees
- Trees with multi-year data: **60** trees

**Unmatched Trees:**
- ArcGIS trees not in Excel: **101** (newer plantings, or different survey scope)
- Excel trees not in ArcGIS: **28** (may have been removed, or naming discrepancy)

## Script Reference

### 1. `import_from_arcgis.py`

**Purpose:** Fetch fresh data from ArcGIS Feature Service

**Input:**  ArcGIS Feature Service URL
**Output:** `data/trees_arcgis_fresh.json`

**Features:**
- Fetches all features from ArcGIS REST API
- Maps ArcGIS fields to our schema
- Validates coordinates
- Preserves all ArcGIS metadata

### 2. `enhance_arcgis_with_growth.py`

**Purpose:** Add Excel growth history to ArcGIS data

**Inputs:**
- `data/trees_arcgis_fresh.json` (PRIMARY)
- `archive/2024 year end chestnut results.xlsx` (SUPPLEMENT)

**Output:** `data/trees.json`

**Features:**
- Parses health status from ArcGIS Notes field
- Matches trees by location abbreviation + number
- Adds historical growth data (2021-2024)
- Reports matching statistics
- Preserves Excel naming for transparency

### 3. Supporting Module

**park_boundaries.py** - Optional coordinate validation module
- Used by import_from_arcgis.py for boundary checking
- Can be omitted if not needed

## Maintenance

### Updating Data (Monthly or After Surveys)

1. **Fetch latest ArcGIS data:**
   ```bash
   python3 scripts/import_from_arcgis.py \
     --url "https://services6.arcgis.com/.../ FeatureServer/0" \
     --output data/trees_arcgis_fresh.json
   ```

2. **If new Excel survey available, enhance:**
   ```bash
   python3 scripts/enhance_arcgis_with_growth.py \
     --arcgis data/trees_arcgis_fresh.json \
     --excel "archive/2025_survey.xlsx" \
     --output data/trees.json
   ```

3. **Commit and deploy:**
   ```bash
   git add data/trees.json
   git commit -m "Update tree data from ArcGIS (2025-01-15)"
   git push
   ```

### Adding New Locations

If Excel includes a new location not in the abbreviation mapping:

1. Check ArcGIS for the abbreviation used in tree names
2. Add to `LOCATION_ABBREV` dict in `enhance_arcgis_with_growth.py`
3. Rerun the enhancement script

Example:
```python
LOCATION_ABBREV = {
    # ... existing ...
    'New Location Name': 'NL',  # Use ArcGIS abbreviation
}
```

## Field Display in UI

The `index.html` map displays all ArcGIS fields:

- **Name**: Tree identifier (e.g., "LV 05")
- **Plant Year**: When planted
- **Area**: Location name
- **Origin**: Organization (TACF, GW, etc.)
- **Variant**: PBR, Native, Hybrid
- **Seed**: Breeding program tracking number
- **Notes**: Latest health observations (primary health source)
- **Growth Chart**: Multi-year data (if available from Excel)
- **Coordinates**: GPS location with accuracy level

## Questions?

Contact the project maintainer or refer to:
- [ArcGIS Feature Service](https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer)
- Excel survey documentation: `archive/SURVEY_DATA_PROCESSING.md`
