# 🌳 NYC American Chestnut Conservation Map

An interactive map tracking American Chestnut (*Castanea dentata*) trees planted and maintained by various organizations across New York City. This project helps coordinate conservation efforts and enables community participation in tracking tree health and growth.

## 🗺️ Live Map

**View the map**: Open `index.html` in your browser or deploy to GitHub Pages

## ⚡ Quick Start

### Update Map Data (Recommended)

```bash
# Run the complete data pipeline
./scripts/update_data_pipeline.sh
```

This fetches fresh data from ArcGIS and enhances it with Excel growth history.

### View the Map

Simply open `index.html` in any web browser to see the interactive map.

## 📊 Data Sources

| Source | Role | What It Provides |
|--------|------|------------------|
| **ArcGIS Feature Service** | PRIMARY | GPS coordinates, current health (Notes field), tree IDs, variants, seeds, plant years |
| **Excel Survey Data** | SUPPLEMENT | Historical growth measurements (2021-2024) |

**Key Principle**: ArcGIS is the source of truth. Excel complements with year-over-year growth history.

## 🎯 Features

### Map Display
- **Interactive Markers**: Click trees to view details
- **Health Status**: Color-coded markers (Green=Healthy, Yellow=Fair, Red=Declining, Gray=Unknown)
- **Organization Filtering**: Toggle layers by organization
- **Growth Charts**: Multi-year visualization for trees with historical data
- **Marker Clustering**: Automatic clustering for performance

### ArcGIS Fields Displayed
- **Name**: Tree identifier (e.g., "LV 05" = Litchfield Villa #5)
- **Area**: Location name
- **Plant Yr**: Year planted
- **Origin**: Organization (TACF, GW, etc.)
- **Variant**: PBR (Pure American Blight Resistant), Native, or Hybrid
- **Seed**: Breeding program tracking number
- **Notes**: Latest health observation (e.g., "11/25 very good")

### Growth Data (from Excel)
- Year-over-year measurements (2021-2024)
- Height (feet) and DBH (inches)
- Interactive charts showing growth trends

## 📁 Project Structure

```
.
├── index.html                    # Interactive map (open this!)
├── data/
│   ├── trees.json                # Enhanced data (ArcGIS + Excel)
│   └── trees_arcgis_fresh.json   # Raw ArcGIS data
├── scripts/
│   ├── update_data_pipeline.sh   # Run this to update data
│   ├── import_from_arcgis.py     # Fetch from ArcGIS
│   └── enhance_arcgis_with_growth.py  # Add Excel growth history
├── archive/
│   └── 2024 year end chestnut results.xlsx  # Excel survey data
├── docs/
│   ├── QUICKSTART.md             # Quick reference guide
│   ├── DATA_ARCHITECTURE.md      # Technical documentation
│   └── archive/                  # Historical documentation
└── README.md                      # This file
```

## 🔄 Data Pipeline

```
ArcGIS Feature Service (PRIMARY)
          ↓
  [Coordinates, Health, IDs]
          ↓
    import_from_arcgis.py
          ↓
  trees_arcgis_fresh.json
          ↓
enhance_arcgis_with_growth.py  ← Excel Survey Data (SUPPLEMENT)
          ↓                        [Growth History 2021-2024]
      trees.json
          ↓
     index.html (Map Display)
```

## 🛠️ Manual Update Steps

If you prefer to run each step separately:

```bash
# 1. Setup virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate
pip install requests openpyxl

# 2. Fetch fresh data from ArcGIS
source venv/bin/activate
python3 scripts/import_from_arcgis.py \
  --url "https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0" \
  --output data/trees_arcgis_fresh.json

# 3. Enhance with Excel growth history
python3 scripts/enhance_arcgis_with_growth.py \
  --arcgis data/trees_arcgis_fresh.json \
  --excel "archive/2024 year end chestnut results.xlsx" \
  --output data/trees.json

# 4. View the map
open index.html
```

## 📈 Current Data Status

- **Total trees in ArcGIS**: 161
- **Health from Notes field**: 31 trees
- **Trees with growth history**: 60 trees
- **Years tracked**: 2021, 2022, 2023, 2024

## 📚 Documentation

- **[QUICKSTART.md](docs/QUICKSTART.md)** - Fast reference for common tasks
- **[DATA_ARCHITECTURE.md](docs/DATA_ARCHITECTURE.md)** - Technical details, field mappings, data flow
- **[Archive](docs/archive/)** - Historical documentation and detailed guides

## 🤝 Contributing

1. Update ArcGIS Feature Service with new tree data
2. Run `./scripts/update_data_pipeline.sh` to refresh the map
3. Commit changes: `git add data/trees.json && git commit -m "Update tree data"`
4. Deploy: `git push origin main`

## 📊 Data Fields Reference

### Primary Fields (from ArcGIS)
```javascript
{
  "name": "LV 05",              // Tree identifier
  "area": "Litchfield Villa",   // Location
  "organization": "TACF",       // Origin/Organization
  "variant": "Native",          // PBR, Native, or Hybrid
  "seed": "25",                 // Breeding program tracking
  "planted_date": "2015-04-15", // When planted
  "notes": "11/25 very good",   // Latest health observation
  "health_status": "healthy",   // Parsed from notes
  "coordinates": [-73.97, 40.67] // GPS location
}
```

### Supplemental Fields (from Excel)
```javascript
{
  "excel_match": "Litchfield Villa #5",  // For transparency
  "tree_number": 5,
  "growth_data": {
    "2021": { "height": 6.5, "dbh": 0.4 },
    "2022": { "height": 7.2, "dbh": 0.45 },
    "2023": { "height": 8.3, "dbh": 0.5 },
    "2024": { "height": 8.0, "dbh": 0.5 }
  }
}
```

## 🔍 Health Status Parsing

The system parses health status from ArcGIS Notes field:
- "11/25 excellent" → Healthy
- "11/25 very good" → Healthy
- "11/25 good" → Good
- "11/25 fair" → Fair
- "11/25 some blight" → Declining
- "11/25 may be dead" → Dead

## 🚨 Troubleshooting

### Trees not loading
- Ensure `data/trees.json` exists
- Check browser console for errors
- Validate JSON: `python3 -m json.tool data/trees.json > /dev/null`

### Module errors
```bash
# Recreate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install requests openpyxl
```

### Trees not matching between sources
- Check matching statistics in script output
- Review location abbreviations in DATA_ARCHITECTURE.md
- Look for `excel_match` field in output to verify matches

## 📝 License

Open source - feel free to adapt for your own tree conservation projects.

## 🙏 Acknowledgments

- American Chestnut Foundation (TACF) for tree data
- NYC Parks, Brooklyn Botanic Garden, Green-Wood Cemetery, and other partner organizations
- Field surveyors who maintain the data

## 📧 Contact

For questions about the map or to report tree updates, contact the respective organization listed in each tree's details.

---

**Made with 🌳 for NYC American Chestnut conservation**
