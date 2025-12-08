# Documentation Index

Complete guide to the NYC American Chestnut Conservation Map project.

## 📚 Main Documentation

### Getting Started
- **[README.md](README.md)** - Project overview, quick start, deployment
- **[SERVER_MANAGEMENT.md](SERVER_MANAGEMENT.md)** - Local server operations

### Data Processing
- **[YEARLY_DATA_WORKFLOW.md](YEARLY_DATA_WORKFLOW.md)** - Annual data update process ⭐ **START HERE FOR NEXT YEAR**
- **[DATA_PROCESSING_SCRIPTS.md](DATA_PROCESSING_SCRIPTS.md)** - Script reference guide
- **[ARCGIS_INTEGRATION.md](ARCGIS_INTEGRATION.md)** - Import data from ArcGIS Feature Services ✨ **NEW**
- **[GIT_BRANCHING_STRATEGY.md](GIT_BRANCHING_STRATEGY.md)** - Feature branch management ✨ **NEW**

### Features
- **[COORDINATE_ACCURACY_SYSTEM.md](COORDINATE_ACCURACY_SYSTEM.md)** - Boundary validation & accuracy badges
- **[LANDUSE_VALIDATION.md](LANDUSE_VALIDATION.md)** - Optional OSM validation (buildings/water/sports)
- **[GPS_COLLECTION_GUIDE.md](GPS_COLLECTION_GUIDE.md)** - Field GPS collection workflow
- **[PHOTO_UPLOAD_WORKFLOW.md](PHOTO_UPLOAD_WORKFLOW.md)** - Photo upload and gallery system ✨ **NEW**
- **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Supabase storage configuration

### Implementation Notes
- **[GROWTH_CHARTS_ADDED.md](GROWTH_CHARTS_ADDED.md)** - Multi-year growth chart feature
- **[HEALTH_STATUS_UPDATE.md](HEALTH_STATUS_UPDATE.md)** - Health categorization system
- **[FEATURE_DEMO.md](FEATURE_DEMO.md)** - Interactive feature walkthrough

## 🗂️ Project Structure

```
nyc-american-chestnut-map-2025/
├── README.md                              # Main project documentation
├── index.html                             # Interactive map (DO NOT EDIT manually)
│
├── data/
│   └── trees.json                        # Generated GeoJSON (DO NOT EDIT manually)
│
├── scripts/                               # Data processing scripts
│   ├── build_trees_with_accuracy.py      # Primary data builder ⭐
│   ├── build_with_landuse_validation.py  # Optional OSM validation
│   ├── update_confirmed_coordinates.py   # Merge GPS data
│   ├── extract_survey_locations.py       # Parse Excel for locations
│   └── park_boundaries.py                # Park definitions & validation
│
├── tools/                                 # Utility tools
│   ├── coordinate_collector.html         # Mobile GPS collection
│   ├── photo_upload.html                 # Mobile photo upload ✨ NEW
│   ├── landuse_validator.py             # OSM API validation
│   └── generate_map.py                   # Legacy CSV converter
│
├── photos/                                # Photo storage ✨ NEW
│   └── metadata.json                     # Photo metadata (URLs to Supabase)
│
├── config/                                # Configuration ✨ NEW
│   └── supabase-config.js                # Supabase credentials
│
├── docs/                                  # Documentation
│   ├── DOCUMENTATION_INDEX.md            # This file
│   ├── YEARLY_DATA_WORKFLOW.md           # Annual processing guide
│   ├── DATA_PROCESSING_SCRIPTS.md        # Script reference
│   ├── SERVER_MANAGEMENT.md              # Local server guide
│   ├── COORDINATE_ACCURACY_SYSTEM.md     # Accuracy implementation
│   ├── LANDUSE_VALIDATION.md             # OSM validation
│   ├── GPS_COLLECTION_GUIDE.md           # Field collection
│   ├── GROWTH_CHARTS_ADDED.md            # Growth chart feature
│   ├── HEALTH_STATUS_UPDATE.md           # Health categorization
│   └── FEATURE_DEMO.md                   # Feature walkthrough
│
├── archive/                               # Historical records
│   ├── 2024 year end chestnut results.xlsx
│   ├── survey_locations_geocoded.csv
│   └── SURVEY_DATA_PROCESSING.md
│
└── venv/                                  # Python virtual environment
    └── (dependencies)
```

## 🔄 Annual Workflow (2025 → 2026)

1. **Receive new survey data** (e.g., "2025 year end chestnut results.xlsx")
2. **Follow [YEARLY_DATA_WORKFLOW.md](YEARLY_DATA_WORKFLOW.md)**
3. **Generate updated map**
4. **Deploy to GitHub Pages**

## 🛠️ Quick Reference

### Build Data (Standard)
```bash
source venv/bin/activate
python3 scripts/build_trees_with_accuracy.py
```

### Build Data (With OSM Validation)
```bash
source venv/bin/activate
python3 scripts/build_with_landuse_validation.py
```

### Update GPS Coordinates
```bash
python3 scripts/update_confirmed_coordinates.py tree_coordinates_YYYY-MM-DD.csv
```

### Run Local Server
```bash
python3 -m http.server 8000
# Visit http://localhost:8000
```

## 📊 Data Flow

```
Excel Survey → extract_survey_locations.py → survey_locations_geocoded.csv
                                                      ↓
                         park_boundaries.py ← build_trees_with_accuracy.py
                                                      ↓
                                              data/trees.json
                                                      ↓
                                                 index.html
                                                      ↓
                                              GitHub Pages
```

## 🎯 Current Status (December 2024)

- ✅ 85 trees mapped from 2024 survey
- ✅ Boundary validation (100% within parks)
- ✅ Coordinate tooltips on hover
- ✅ Growth charts (2021-2024)
- ✅ Health status badges
- ✅ GPS collection system
- ✅ Mobile-responsive
- ⚠️ Washington Park needs manual coordinate verification
- 🔜 Image documentation (planned)

## 🔐 Important Files (DO NOT MODIFY MANUALLY)

These files are **generated** by scripts:

- `data/trees.json` - Generated by build scripts
- `index.html` - Hand-coded but carefully structured
- `survey_locations_geocoded.csv` - Generated by geocoding

**Always edit source data and re-run build scripts**

## 🆘 Troubleshooting

### Map not updating after rebuild?
1. Stop server: `kill $(lsof -ti:8000)`
2. Restart server: `python3 -m http.server 8000`
3. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

### Script errors?
1. Activate virtual environment: `source venv/bin/activate`
2. Install dependencies: `pip install pandas openpyxl geopy requests shapely`
3. Check file paths in script

### Coordinates outside park?
1. Update `scripts/park_boundaries.py` with correct area centers
2. Re-run build script
3. Verify with boundary validation output

## 📖 Reading Order for New Users

1. [README.md](README.md) - Project overview
2. [YEARLY_DATA_WORKFLOW.md](YEARLY_DATA_WORKFLOW.md) - How to process data
3. [SERVER_MANAGEMENT.md](SERVER_MANAGEMENT.md) - How to test locally
4. [GPS_COLLECTION_GUIDE.md](GPS_COLLECTION_GUIDE.md) - Field collection (if needed)

## 📖 Reading Order for Developers

1. [DATA_PROCESSING_SCRIPTS.md](DATA_PROCESSING_SCRIPTS.md) - Script reference
2. [COORDINATE_ACCURACY_SYSTEM.md](COORDINATE_ACCURACY_SYSTEM.md) - Technical implementation
3. [LANDUSE_VALIDATION.md](LANDUSE_VALIDATION.md) - OSM validation details
4. Source code in `scripts/` directory

## 🔮 Future Features

See **[IMAGE_DOCUMENTATION_PLAN.md](IMAGE_DOCUMENTATION_PLAN.md)** for:
- Tree photo uploads
- Progress photo galleries
- Image storage strategy
- Mobile photo collection

---

**Last Updated**: 2024-12-06
**Map Version**: 3.1
**Total Trees**: 85
**Organizations**: 4 (Prospect Park Alliance, NYC Parks, Brooklyn Botanic Garden)
