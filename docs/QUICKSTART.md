# Quick Start Guide

## Running the Data Pipeline

### Simple Update (Recommended)

```bash
# Update map data from ArcGIS + Excel
./scripts/update_data_pipeline.sh
```

This single command will:
1. ✓ Fetch fresh data from ArcGIS Feature Service (PRIMARY)
2. ✓ Add historical growth data from Excel (SUPPLEMENT)
3. ✓ Generate `data/trees.json` for the map

### Manual Steps

If you prefer to run each step separately:

```bash
# Step 1: Fetch from ArcGIS
source venv/bin/activate
python3 scripts/import_from_arcgis.py \
  --url "https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0" \
  --output data/trees_arcgis_fresh.json

# Step 2: Enhance with Excel growth history
python3 scripts/enhance_arcgis_with_growth.py \
  --arcgis data/trees_arcgis_fresh.json \
  --excel "archive/2024 year end chestnut results.xlsx" \
  --output data/trees.json
```

## Data Sources

| Source | Role | Contains |
|--------|------|----------|
| **ArcGIS** | PRIMARY | GPS coordinates, current health (Notes field), tree IDs, variants, seeds |
| **Excel** | SUPPLEMENT | Historical growth data (2021-2024 measurements) |

## Key Principle

**ArcGIS is the source of truth for:**
- Locations (GPS coordinates)
- Current tree health (from Notes field)
- Tree identification (Name field: "LV 05", "BP 03")
- Metadata (variants, seeds, origins)

**Excel complements with:**
- Year-over-year growth history
- Detailed measurements (height, DBH)

## Viewing the Map

Simply open `index.html` in any web browser. The map displays:

- 🗺️ Tree locations (from ArcGIS coordinates)
- 🌳 Health status (from ArcGIS Notes: "11/25 very good")
- 📊 Growth charts (from Excel, if data available)
- 📋 All metadata (variants, seeds, plant years)

## Understanding the Data

### ArcGIS Fields Displayed

- **Name**: Tree identifier (e.g., "LV 05" = Litchfield Villa tree #5)
- **Area**: Location name ("Litchfield Villa", "Bartel-Pritchard")
- **Plant Yr**: Year planted
- **Origin**: Organization (TACF, GW, etc.)
- **Variant**: PBR (Pure American Blight Resistant), Native, or Hybrid
- **Seed**: Breeding program tracking number
- **Notes**: Latest health observation (e.g., "11/25 very good")

### Health Status (parsed from Notes)

The Notes field contains dated health observations:
- "11/25 excellent" → Health: Healthy
- "11/25 some blight" → Health: Declining
- "11/25 may be dead" → Health: Dead

### Growth Data (from Excel)

Trees matched with Excel surveys show:
- Multi-year measurements (2021-2024)
- Height (feet) and DBH (inches)
- Growth chart visualization

## File Structure

```
.
├── index.html                          # Interactive map (open this!)
├── data/
│   ├── trees.json                      # Final enhanced data
│   └── trees_arcgis_fresh.json         # Raw ArcGIS data
├── scripts/
│   ├── update_data_pipeline.sh         # Run this to update data
│   ├── import_from_arcgis.py           # Step 1: Fetch ArcGIS
│   └── enhance_arcgis_with_growth.py   # Step 2: Add Excel growth
├── archive/
│   └── 2024 year end chestnut results.xlsx  # Excel survey
├── DATA_ARCHITECTURE.md                # Detailed documentation
└── QUICKSTART.md                       # This file
```

## Troubleshooting

### "No module named 'requests'"

Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests openpyxl
```

### Trees not matching between ArcGIS and Excel

1. Check the matching statistics in the script output
2. Verify location abbreviations match (see [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md))
3. The `excel_match` field in output shows which Excel entry matched

### Map not loading

1. Ensure `data/trees.json` exists
2. Check browser console for errors
3. Verify JSON is valid: `python3 -m json.tool data/trees.json > /dev/null`

## Need Help?

- **Full Documentation**: See [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md)
- **ArcGIS Service**: https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer
- **Legacy Scripts**: Archived in `scripts/` (no longer needed, kept for reference)
