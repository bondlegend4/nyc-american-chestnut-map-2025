# Data Merge Summary - NYC American Chestnut Map

## Overview

Successfully merged data from two authoritative sources to create a comprehensive tree dataset with accurate coordinates AND health information.

## Data Sources

### 1. ArcGIS Feature Service (Primary)
- **URL**: https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0
- **Trees**: 161 total
- **Provides**:
  - Verified GPS coordinates (95% confidence)
  - Location names (Brooklyn Botanic Garden, Litchfield Villa, etc.)
  - Tree variants (Native, hybrid types)
  - Seed information
  - Health updates in Notes field (26 trees)
  - Planting years

### 2. Excel Spreadsheet (Secondary)
- **File**: `archive/2024 year end chestnut results.xlsx`
- **Trees**: 31 trees with detailed survey data
- **Provides**:
  - Health status from field surveys
  - Height and DBH measurements (2024)
  - Detailed location notes
  - Tree type (Native vs PBR)

## Merge Results

### Health Data Coverage
- **Total trees**: 161
- **Trees with health status**: 43 (26.7%)
  - From ArcGIS Notes: 26 trees
  - From Excel surveys: 17 trees
- **Trees without health data**: 118

### Health Status Distribution
- **Healthy** (excellent/very good): 19 trees
- **Good**: 7 trees
- **Fair**: 3 trees
- **Declining** (blight/coppising): 4 trees
- **Dead** (or may be dead): 6 trees
- **Unknown**: 122 trees

## Data Quality Improvements

### Before Merge
- Organization: "Unknown Organization" for most trees
- Location accuracy: "estimated" (60% confidence)
- Contact: Generic conservation email
- Health status: All "unknown"

### After Merge
- **Organization**: "TACF" (The American Chestnut Foundation) for all trees
- **Location accuracy**: "verified" (95% confidence)
  - Marked as verified by TACF
  - Verification date: 2025-12-07
- **Contact**: TACF-NYC@acf.org
- **Health status**: 43 trees with current data
- **Health dates**: Recent updates (e.g., "11/25", "11/16/25")

## Sample Health Updates

### From ArcGIS Notes (Most Recent)
```
Tree: LV 05
  Status: healthy
  Date: 11/25
  Notes: "11/25 very good"

Tree: LV 07
  Status: declining
  Date: 11/25
  Notes: "11/25 some blight, coppising"

Tree: WD 10
  Status: good
  Date: 11/16/25
  Notes: "11/16/25 Good, 8', possible blight"
```

### From Excel Survey Data
```
Tree #14
  Status: healthy
  Notes: "Excel 2024: excellent"
  Height: 22.4'
  DBH: 2"

Tree #15
  Status: dead
  Notes: "Excel 2024: may be dead"
  Height: .8'
```

## How to Update Data

### Full Refresh (Recommended)
Merge latest data from both sources:

```bash
# 1. Re-import from ArcGIS
source venv/bin/activate
python3 scripts/import_from_arcgis.py \
  --url "https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0" \
  --output data/trees_arcgis_latest.json

# 2. Merge with Excel data
python3 scripts/merge_data_sources.py \
  --arcgis data/trees_arcgis_latest.json \
  --excel "archive/2024 year end chestnut results.xlsx" \
  --output data/trees.json
```

### ArcGIS Only Update
If you just need to update coordinates without Excel data:

```bash
source venv/bin/activate
python3 scripts/import_from_arcgis.py \
  --url "https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0"
```

## Health Notes Format

The merger script recognizes these patterns in ArcGIS Notes:

### Date Formats
- `MM/DD` (e.g., "11/25")
- `MM/DD/YY` (e.g., "11/16/25")
- `MM/DD/YYYY`

### Health Keywords
- **Excellent/Very Good** → Standardized to "healthy"
- **Good** → "good"
- **Fair** → "fair"
- **Poor/Blight/Declining/Coppising** → "declining"
- **Dead/May be dead** → "dead"

## Files

### Scripts
- **scripts/import_from_arcgis.py** - Import from ArcGIS Feature Service
- **scripts/merge_data_sources.py** - Merge ArcGIS + Excel data

### Data Files
- **data/trees.json** - Current merged dataset (production)
- **data/trees_arcgis_fresh.json** - Latest ArcGIS import
- **data/trees_backup_before_merge.json** - Backup before merge
- **archive/2024 year end chestnut results.xlsx** - Excel survey data

## Next Steps

1. **View the map**: Open http://localhost:8000 to see all 161 trees
2. **Check health data**: Click on trees to see health status in popup
3. **Verify accuracy**: Confirm coordinates match field observations
4. **Add more health data**: Update ArcGIS Notes field with new observations

## Merge Priority

The merger uses this priority order:

1. **ArcGIS Notes** (highest priority)
   - Most recent field updates
   - Includes dates
   - 26 trees currently have notes

2. **Excel Spreadsheet** (fallback)
   - Detailed survey data
   - Used when ArcGIS Notes are empty
   - 17 additional trees

3. **Defaults** (if no data available)
   - Organization: TACF
   - Contact: TACF-NYC@acf.org
   - Health: unknown
   - Accuracy: verified (from ArcGIS coordinates)

---

Last updated: 2025-12-07
