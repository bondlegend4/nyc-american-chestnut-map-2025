## ArcGIS Integration Guide

**Purpose**: Import tree data from ArcGIS Feature Services, GeoJSON exports, or Shapefiles

---

## 🎯 Overview

This guide shows you how to import data from your organization's ArcGIS map into the NYC American Chestnut Map format.

**Supports**:
- ArcGIS Online Feature Services (REST API)
- ArcGIS Enterprise servers
- GeoJSON exports from ArcGIS
- Shapefile (.shp) exports from ArcGIS

**Script**: [scripts/import_from_arcgis.py](../scripts/import_from_arcgis.py)

---

## 📋 Prerequisites

### Required
```bash
pip install requests
```

### Optional (for Shapefile support)
```bash
pip install geopandas
```

---

## 🚀 Quick Start

### Method 1: From ArcGIS Feature Service URL

```bash
# Activate virtual environment
source venv/bin/activate

# Import all features
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/YOUR_ORG/arcgis/rest/services/Trees/FeatureServer/0"

# This creates data/trees.json
```

### Method 2: From GeoJSON Export

```bash
# Export from ArcGIS Online:
# 1. Open your web map
# 2. Click layer → Export → GeoJSON
# 3. Save as arcgis_export.geojson

# Import the file
python3 scripts/import_from_arcgis.py \
  --file arcgis_export.geojson
```

### Method 3: From Shapefile

```bash
# Export from ArcGIS Pro/Desktop:
# 1. Right-click layer → Data → Export Features
# 2. Save as trees.shp (includes .dbf, .shx, .prj files)

# Install geopandas if not already installed
pip install geopandas

# Import the shapefile
python3 scripts/import_from_arcgis.py \
  --shapefile trees.shp
```

---

## 🔧 Configuration

### Field Mapping

The script automatically maps ArcGIS field names to our standard fields. Edit `scripts/import_from_arcgis.py` if your fields have different names:

```python
FIELD_MAPPING = {
    # Required fields
    'tree_id': ['OBJECTID', 'TreeID', 'ID', 'tree_id', 'FID'],
    'organization': ['Organization', 'Org', 'Agency', 'ORGANIZATION'],
    'health_status': ['Health', 'HealthStatus', 'Condition'],

    # Location fields
    'latitude': ['Latitude', 'LAT', 'Y'],
    'longitude': ['Longitude', 'LON', 'X'],

    # Optional fields
    'planted_date': ['PlantedDate', 'DatePlanted', 'InstallDate'],
    'last_updated': ['LastUpdate', 'UpdateDate', 'ModifiedDate'],
    'notes': ['Notes', 'Comments', 'Description'],

    # Add your custom field names here
}
```

**Example customization**:
```python
# If your ArcGIS layer uses "TreeHealth" instead of "Health"
'health_status': ['TreeHealth', 'Health', 'HealthStatus', 'Condition'],

# If your layer uses "Sponsor" instead of "Organization"
'organization': ['Sponsor', 'Organization', 'Org', 'Agency'],
```

### Health Status Mapping

The script standardizes various health values to our 4 categories:

```python
HEALTH_MAPPING = {
    'healthy': ['healthy', 'good', 'excellent', 'very good', '1'],
    'fair': ['fair', 'ok', 'moderate', 'declining', '2'],
    'poor': ['poor', 'bad', 'critical', 'dying', 'dead', '3'],
    'unknown': ['unknown', 'not assessed', 'n/a', '0']
}
```

**Add custom health values**:
```python
# If your ArcGIS uses "Thriving" for healthy trees
'healthy': ['healthy', 'good', 'excellent', 'Thriving', '1'],
```

### Organization Mapping

Map abbreviations to full organization names:

```python
ORGANIZATION_MAPPING = {
    'PPA': 'Prospect Park Alliance',
    'BBG': 'Brooklyn Botanic Garden',
    'NYCPARKS': 'NYC Parks',
    # Add your organization codes here
    'YourOrgCode': 'Your Organization Full Name'
}
```

---

## 📊 Usage Examples

### Basic Import (All Features)

```bash
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/.../FeatureServer/0"
```

**Output**:
```
=== ArcGIS Feature Service Importer ===

Fetching data from: https://services.arcgis.com/.../query
Where clause: 1=1
✓ Retrieved 85 features

Processing 85 features...

✓ Converted 85 trees

✓ Successfully created data/trees.json
  Total trees: 85

Summary:
  Organizations: 4
  Health status:
    fair: 18
    healthy: 50
    poor: 13
    unknown: 4
  Location accuracy:
    confirmed: 85

=== Import Complete ===
```

### Filtered Import (Specific Park)

```bash
# Only import trees from Prospect Park
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/.../FeatureServer/0" \
  --where "Park = 'Prospect Park'"
```

### Filtered Import (Date Range)

```bash
# Only import trees planted after 2020
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/.../FeatureServer/0" \
  --where "PlantedDate >= date '2020-01-01'"
```

### Filtered Import (Organization)

```bash
# Only import trees from specific organization
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/.../FeatureServer/0" \
  --where "Organization = 'Prospect Park Alliance'"
```

### Custom Output File

```bash
# Save to different file (don't overwrite data/trees.json)
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/.../FeatureServer/0" \
  --output data/trees_arcgis_backup.json
```

### Large Datasets

```bash
# Fetch more than default 5000 records
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/.../FeatureServer/0" \
  --max-records 10000
```

---

## 🔗 Finding Your ArcGIS Feature Service URL

### ArcGIS Online

1. **Open your web map** at https://arcgis.com
2. **Click on your layer** in the Contents pane
3. **Click "More Options" (...)** → **View in ArcGIS REST Services Directory**
4. **Copy the URL** - it should look like:
   ```
   https://services.arcgis.com/YOUR_ORG_ID/arcgis/rest/services/YOUR_SERVICE/FeatureServer/0
   ```
5. Use this URL with the script

### ArcGIS Enterprise

1. **Navigate to your REST services endpoint**:
   ```
   https://your-server.com/arcgis/rest/services
   ```
2. **Find your service** → Click on it
3. **Find the layer number** (usually `/0` for first layer)
4. **Copy the full URL**

### Alternative: Export GeoJSON

If you can't access the REST API:

1. **In ArcGIS Online**: Open layer → Export → GeoJSON
2. **In ArcGIS Pro**: Right-click layer → Data → Export Features → Set format to GeoJSON
3. Use `--file` option with the script

---

## 🎨 Data Flow

```
ArcGIS Feature Service
        ↓
  [Fetch via REST API]
        ↓
  [Map field names]
        ↓
[Standardize health status]
        ↓
[Validate coordinates against park boundaries]
        ↓
  [Extract growth data if available]
        ↓
   [Generate GeoJSON]
        ↓
  data/trees.json
        ↓
  [Display on map]
```

---

## 📁 Output Format

The script creates `data/trees.json` in the standard format:

```json
{
  "type": "FeatureCollection",
  "metadata": {
    "last_updated": "2024-12-06",
    "source": "arcgis",
    "source_url": "https://services.arcgis.com/.../FeatureServer/0",
    "total_features": 85,
    "version": "4.0"
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.9712, 40.6618]
      },
      "properties": {
        "tree_id": "NYC-AC-001",
        "organization": "Prospect Park Alliance",
        "health_status": "healthy",
        "planted_date": "2023-04-15",
        "last_updated": "2024-12-06",
        "notes": "Planted as part of restoration project",
        "location_description": "Prospect Park - Sugar Bowl",
        "contact": "info@prospectpark.org",
        "location_accuracy": {
          "level": "confirmed",
          "description": "Confirmed location from ArcGIS (within PROSPECT PARK)",
          "source": "arcgis",
          "confidence": 90
        },
        "growth_data": {
          "2021": {"height": 8.5, "dbh": 2.1},
          "2022": {"height": 10.2, "dbh": 2.8},
          "2023": {"height": 12.5, "dbh": 3.5},
          "2024": {"height": 14.8, "dbh": 4.2}
        },
        "park": "PROSPECT PARK",
        "area": "Sugar Bowl",
        "tree_number": 1
      }
    }
  ]
}
```

---

## ✅ Validation

### Coordinate Validation

The script validates all coordinates against park boundaries defined in `scripts/park_boundaries.py`:

**Within bounds**:
```
✓ Tree NYC-AC-001: coordinates validated within PROSPECT PARK
  Accuracy: confirmed (90% confidence)
```

**Outside bounds**:
```
Warning: Tree NYC-AC-042 coordinates outside PROSPECT PARK boundary (distance: 150m)
  Accuracy: estimated (60% confidence)
```

### Health Status Validation

All health values are standardized to: `healthy`, `fair`, `poor`, or `unknown`

**Original value preserved**:
```json
{
  "health_status": "healthy",
  "health_detail": "Very Good (original ArcGIS value)"
}
```

---

## 🔄 Workflow Integration

### Initial Setup

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Import from ArcGIS
python3 scripts/import_from_arcgis.py \
  --url "YOUR_FEATURE_SERVICE_URL"

# 3. Verify output
cat data/trees.json | head -50

# 4. Test locally
python3 -m http.server 8000
# Visit http://localhost:8000

# 5. Deploy
git add data/trees.json
git commit -m "Import tree data from ArcGIS"
git push origin main
```

### Regular Updates

```bash
# Option 1: Replace all data
python3 scripts/import_from_arcgis.py --url "YOUR_URL"

# Option 2: Import to separate file, then merge manually
python3 scripts/import_from_arcgis.py \
  --url "YOUR_URL" \
  --output data/trees_arcgis_new.json

# Compare and merge
# ... manual review ...
```

### Scheduled Updates

**Using cron (Linux/Mac)**:
```bash
# Edit crontab
crontab -e

# Add line to run weekly on Sunday at 2 AM
0 2 * * 0 cd /path/to/project && source venv/bin/activate && python3 scripts/import_from_arcgis.py --url "YOUR_URL" && git add data/trees.json && git commit -m "Weekly ArcGIS sync" && git push
```

**Using GitHub Actions** (automated):
See [GitHub Actions Workflow](#github-actions-workflow) below

---

## 🔧 Advanced Usage

### Multi-Layer Import

If you have trees in multiple ArcGIS layers:

```bash
# Import from layer 0
python3 scripts/import_from_arcgis.py \
  --url "https://.../FeatureServer/0" \
  --output data/trees_layer0.json

# Import from layer 1
python3 scripts/import_from_arcgis.py \
  --url "https://.../FeatureServer/1" \
  --output data/trees_layer1.json

# Merge manually (Python script):
import json

with open('data/trees_layer0.json') as f:
    data0 = json.load(f)

with open('data/trees_layer1.json') as f:
    data1 = json.load(f)

merged = {
    'type': 'FeatureCollection',
    'metadata': data0['metadata'],
    'features': data0['features'] + data1['features']
}

with open('data/trees.json', 'w') as f:
    json.dump(merged, f, indent=2)
```

### Custom Field Extraction

Extract additional fields not in the standard mapping:

```python
# Edit scripts/import_from_arcgis.py, in convert_feature_to_tree()

# Add custom field extraction
soil_type = find_field_value(attrs, ['SoilType', 'Soil'])
tree['properties']['soil_type'] = soil_type

canopy_width = find_field_value(attrs, ['CanopyWidth', 'Width'])
tree['properties']['canopy_width'] = canopy_width
```

### Filtering by Date

```bash
# Only trees planted in 2024
python3 scripts/import_from_arcgis.py \
  --url "YOUR_URL" \
  --where "PlantedDate >= date '2024-01-01' AND PlantedDate < date '2025-01-01'"

# Trees updated in last 30 days
python3 scripts/import_from_arcgis.py \
  --url "YOUR_URL" \
  --where "UpdateDate >= CURRENT_DATE - INTERVAL '30' DAY"
```

---

## 🆘 Troubleshooting

### "No features found in response"

**Cause**: Feature Service returned 0 results

**Solutions**:
1. Check URL is correct (ends with `/FeatureServer/0` or similar)
2. Try without `--where` clause to get all records
3. Verify layer contains data in ArcGIS Online
4. Check if layer requires authentication (see Authentication section below)

### "Invalid JSON" Error

**Cause**: ArcGIS returned HTML error page instead of JSON

**Solutions**:
1. Verify URL in browser - should show JSON data
2. Check if service requires authentication
3. Verify service is publicly accessible

### Field Not Found

**Cause**: Script can't find expected field names

**Solution**: Update `FIELD_MAPPING` in script:
```python
# Add your field name to the list
'tree_id': ['OBJECTID', 'TreeID', 'YourCustomID'],
```

### Coordinates Outside Park

**Warning**: Tree coordinates don't fall within park boundaries

**Solutions**:
1. Verify coordinates in ArcGIS are correct
2. Update park boundaries in `scripts/park_boundaries.py`
3. Ignore warning if coordinates are intentionally outside parks

### Import Successful But Map Shows Nothing

**Checklist**:
- [ ] Check `data/trees.json` exists and is valid JSON
- [ ] Verify coordinates are in correct format (longitude, latitude)
- [ ] Check browser console for errors
- [ ] Hard refresh browser (Cmd+Shift+R)
- [ ] Verify trees have valid health_status values

---

## 🔐 Authentication

### Public Feature Services

No authentication needed - works out of the box

### Secured Feature Services

For services requiring authentication:

**Option 1: Token-based (ArcGIS Online)**:
```python
# Edit import_from_arcgis.py, add token to params
params['token'] = 'YOUR_ARCGIS_TOKEN'
```

**Option 2: OAuth (Enterprise)**:
```python
# Add authentication headers
headers = {'Authorization': 'Bearer YOUR_TOKEN'}
response = requests.get(url, params=params, headers=headers)
```

**Option 3: Export to file**:
- Log in to ArcGIS Online
- Export layer to GeoJSON
- Use `--file` option (no authentication needed)

---

## 📊 GitHub Actions Workflow

Automate ArcGIS imports with GitHub Actions:

Create `.github/workflows/arcgis-sync.yml`:
```yaml
name: Sync from ArcGIS

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install requests

      - name: Import from ArcGIS
        run: |
          python3 scripts/import_from_arcgis.py \
            --url "${{ secrets.ARCGIS_FEATURE_SERVICE_URL }}"

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/trees.json
          git commit -m "Automated ArcGIS sync $(date +'%Y-%m-%d')" || exit 0
          git push
```

**Setup**:
1. Add your Feature Service URL to GitHub Secrets:
   - Repository → Settings → Secrets → New repository secret
   - Name: `ARCGIS_FEATURE_SERVICE_URL`
   - Value: Your full Feature Service URL

2. Enable GitHub Actions in repository settings

3. Workflow runs automatically every Sunday, or trigger manually

---

## 📞 Support

**For ArcGIS issues**:
- Check REST Services Directory: https://services.arcgis.com
- ArcGIS REST API docs: https://developers.arcgis.com/rest/

**For script issues**:
- Review output messages for specific errors
- Check `FIELD_MAPPING` matches your field names
- Verify park boundaries are configured

**For data issues**:
- Validate GeoJSON: https://geojsonlint.com
- Check coordinates format (longitude first, then latitude)
- Verify health status values are standardized

---

## 🎯 Next Steps

1. **Configure field mapping** for your ArcGIS layer
2. **Test import** with small dataset first
3. **Verify output** in browser
4. **Set up automated sync** (optional)
5. **Document your specific workflow** for team

---

**Last Updated**: December 6, 2024
**Version**: 1.0
**Feature Branch**: feature/arcgis-integration
