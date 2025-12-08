# Yearly Data Processing Workflow

**⭐ START HERE when processing next year's survey data (2025, 2026, etc.)**

This guide walks you through the complete process of updating the map with new annual survey data.

## 📅 When to Use This Guide

- Received new "YYYY year end chestnut results.xlsx" file
- Annual tree health survey completed
- Need to update the public map with latest data

## 🎯 Overview

The workflow takes you from raw Excel survey data to a live, updated map:

```
Excel Survey → Extract → Geocode → Validate → Build → Deploy
    ↓           ↓         ↓          ↓         ↓        ↓
  2025.xlsx  Locations  Coords   Boundaries trees.json GitHub
```

**Estimated Time**: 30-60 minutes (first time), 15-30 minutes (subsequent years)

## ✅ Prerequisites

### 1. Set Up Environment (One-Time)

```bash
cd nyc-american-chestnut-map-2025

# Create virtual environment if not exists
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install pandas openpyxl geopy requests shapely
```

### 2. Files You Need

- **New survey Excel file**: e.g., "2025 year end chestnut results.xlsx"
- **Previous year's archive** (for reference): `archive/2024 year end chestnut results.xlsx`

## 📊 Step-by-Step Process

### Step 1: Prepare New Survey File

```bash
# Place the new Excel file in project root
# Example: "2025 year end chestnut results.xlsx"

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Extract Survey Locations

This identifies all unique park/area combinations:

```bash
python3 scripts/extract_survey_locations.py
```

**What it does**:
- Reads the Excel file
- Extracts unique park names and area names
- Creates `survey_locations_to_geocode.csv`

**Check output**:
```csv
park,area,location_description
PROSPECT PARK,Sugar Bowl,PROSPECT PARK - Sugar Bowl
PROSPECT PARK,Peninsula,PROSPECT PARK - Peninsula
...
```

### Step 3: Geocode Locations (Optional if areas are same)

If you have **new areas** not in last year's data:

```bash
# This script automatically geocodes using OpenStreetMap
python3 scripts/geocode_locations.py  # (if needed - check if new areas exist)
```

**OR manually update** `archive/survey_locations_geocoded.csv` if areas are unchanged.

### Step 4: Update Park Boundaries (If Needed)

Check if any new parks or areas were added. If yes, update `scripts/park_boundaries.py`:

```python
PARK_BOUNDARIES = {
    "NEW PARK NAME": {
        "center": {"lat": 40.XXXX, "lon": -73.XXXX},
        "bbox": {
            "north": 40.XXXX,
            "south": 40.XXXX,
            "east": -73.XXXX,
            "west": -73.XXXX
        },
        "areas": {
            "New Area Name": {"lat": 40.XXXX, "lon": -73.XXXX}
        }
    }
}
```

**How to find coordinates**:
1. Google Maps: Right-click location → "What's here?"
2. OpenStreetMap: Click location, copy coordinates
3. Use GPS collector tool in the field

### Step 5: Build Trees Data

**Standard build** (recommended):

```bash
python3 scripts/build_trees_with_accuracy.py
```

**What it does**:
- Reads Excel survey file
- Extracts health status and growth data (2021-2025)
- Validates coordinates against park boundaries
- Generates dispersed coordinates using spiral pattern
- Creates `data/trees.json`

**With landuse validation** (optional, slower):

```bash
python3 scripts/build_with_landuse_validation.py
# Answer "yes" when prompted
# Takes ~45 seconds for 85 trees (checks against buildings/water/sports)
```

**Expected output**:
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

### Step 6: Verify Generated Data

```bash
# Check file was created
ls -lh data/trees.json

# View first tree entry
head -100 data/trees.json

# Count trees
grep -c "NYC-AC-" data/trees.json
```

**Quick validation checklist**:
- [ ] File size reasonable (~100KB for 85 trees)
- [ ] All trees have `location_accuracy` field
- [ ] Health status distribution makes sense
- [ ] Tree count matches survey

### Step 7: Test Locally

```bash
# Start local server
python3 -m http.server 8000

# Open in browser: http://localhost:8000
```

**Visual checks**:
1. All trees appear on map (check tree count in info panel)
2. Click markers - popups show correctly
3. Hover over location badge - coordinates appear
4. Click "View Growth Chart" - chart shows new year's data
5. Health status badges show correct colors

**Hard refresh** if changes don't appear: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

### Step 8: Archive Old Data

```bash
# Move last year's files to archive
mv "2024 year end chestnut results.xlsx" archive/
mv survey_locations_geocoded.csv archive/2024_locations_geocoded.csv

# Copy new survey to archive
cp "2025 year end chestnut results.xlsx" archive/
```

### Step 9: Update Documentation

Update these files with new year:

**README.md**:
```markdown
**Last Updated**: 2025-12-05
**Tree Count**: 92 (update with actual count)
**Organizations**: 5 (update if changed)
```

**data/trees.json metadata** (automatically updated by build script):
```json
{
  "metadata": {
    "last_updated": "2025-12-05",
    "survey_date": "2025-12-20",
    "version": "4.0"
  }
}
```

### Step 10: Deploy to GitHub Pages

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "$(cat <<EOF
Update map with 2025 survey data

- Processed 2025 year end chestnut results
- Updated tree count: 85 → 92
- Added 7 new trees (locations listed in survey)
- Updated health status and growth data
- All coordinates validated within park boundaries

🤖 Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push to GitHub
git push origin main
```

**Verify deployment**:
1. Go to GitHub repository → Actions tab
2. Wait for deployment workflow to complete (~2-3 minutes)
3. Visit: https://bondlegend4.github.io/nyc-american-chestnut-map-2025/
4. Hard refresh browser
5. Verify new tree count and data

## 🔄 Quick Reference for Next Year

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Place new Excel file in project root

# 3. Build data
python3 scripts/build_trees_with_accuracy.py

# 4. Test locally
python3 -m http.server 8000
# Visit http://localhost:8000, hard refresh

# 5. Deploy
git add .
git commit -m "Update with 2026 survey data"
git push origin main
```

## 📝 Year-Over-Year Changes to Watch For

### Survey Format Changes

If Excel column layout changes:
1. Open `scripts/build_trees_with_accuracy.py`
2. Update `YEAR_COLUMNS` mapping:
   ```python
   YEAR_COLUMNS = {
       '2021': {'height': 2, 'dbh': 3},
       '2022': {'height': 5, 'dbh': 6},
       '2023': {'height': 8, 'dbh': 9},
       '2024': {'height': 12, 'dbh': 13, 'health': 16},
       '2025': {'height': XX, 'dbh': XX, 'health': XX}  # Add new year
   }
   ```

### New Parks or Areas

If survey includes new locations:
1. Update `scripts/park_boundaries.py`
2. Add coordinates for new areas
3. Re-run build script

### New Organizations

If new partners join:
1. Update contact map in `scripts/build_trees_with_accuracy.py`:
   ```python
   contact_map = {
       'Prospect Park Alliance': 'info@prospectpark.org',
       'Brooklyn Botanic Garden': 'conservation@bbg.org',
       'New Organization Name': 'contact@neworg.org'  # Add this
   }
   ```

### Tree Removals

If trees died or were removed:
- The build script automatically excludes them if they're not in the new survey
- No manual action needed

## 🆘 Troubleshooting

### "No module named 'pandas'"
```bash
source venv/bin/activate
pip install pandas openpyxl geopy requests shapely
```

### "File not found: 2025 year end chestnut results.xlsx"
```bash
# Make sure file is in project root
ls *.xlsx

# Update filename in script if different
# Or rename file to match expected name
```

### Coordinates outside park boundaries
```bash
# Check build output for warnings:
# "WARNING: Coordinates outside park boundary"

# Update park_boundaries.py with correct area centers
# Re-run build script
```

### Map shows old data after rebuild
```bash
# Stop server
kill $(lsof -ti:8000)

# Restart
python3 -m http.server 8000

# Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

### Growth chart missing new year
1. Check `YEAR_COLUMNS` in build script includes new year
2. Verify Excel file has data in expected columns
3. Re-run build script

## 📊 Data Quality Checks

After each build, verify:

- [ ] **Tree count** matches survey row count
- [ ] **All trees within park bounds** (check build output)
- [ ] **Health distribution** looks reasonable (not all "unknown")
- [ ] **Growth data** includes new year (check chart in browser)
- [ ] **No duplicate tree IDs** (NYC-AC-001, NYC-AC-002, etc.)
- [ ] **Coordinates dispersed** (not all at same point)

## 🔮 Future Year Considerations

### 2026 and Beyond

The system is designed to handle:
- Unlimited years of growth data
- Dynamic health status updates
- New parks and areas
- Organization changes

**No code changes needed** unless:
- Excel format changes significantly
- New data fields added (e.g., photos, soil data)
- Different coordinate system required

### Archival Strategy

Keep in `archive/` directory:
- All previous year Excel files
- Geocoded location files
- Processing notes/documentation
- Git commits preserve all historical versions

## 📞 Need Help?

1. Check [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
2. Review [DATA_PROCESSING_SCRIPTS.md](DATA_PROCESSING_SCRIPTS.md)
3. Open GitHub issue with:
   - Year being processed
   - Error message (if any)
   - Build script output
   - Steps already tried

---

**Next Update Due**: December 2025
**Current Data**: December 2024 (85 trees)
**System Version**: 3.1
