# Quick Reference Card

**NYC American Chestnut Map - Command Cheat Sheet**

---

## 🌳 Git Branches

```bash
# List all branches
git branch --list

# Switch branches
git checkout main                      # Production
git checkout develop                   # Integration/testing
git checkout feature/photo-gallery     # Photo features
git checkout feature/arcgis-integration # ArcGIS import

# Create new feature
git checkout -b feature/new-feature

# Merge feature to production
git checkout develop
git merge feature/your-feature
git checkout main
git merge develop
git push origin main
```

---

## 🗺️ Import from ArcGIS

```bash
# Activate environment
source venv/bin/activate

# Import from Feature Service
python3 scripts/import_from_arcgis.py \
  --url "https://services.arcgis.com/YOUR_ORG/.../FeatureServer/0"

# Import from GeoJSON file
python3 scripts/import_from_arcgis.py \
  --file arcgis_export.geojson

# Import from Shapefile
python3 scripts/import_from_arcgis.py \
  --shapefile trees.shp

# Filter by park
python3 scripts/import_from_arcgis.py \
  --url "YOUR_URL" \
  --where "Park = 'Prospect Park'"
```

---

## 📊 Build from Excel Survey

```bash
# Standard build
python3 scripts/build_trees_with_accuracy.py

# With landuse validation (slower)
python3 scripts/build_with_landuse_validation.py
```

---

## 📍 GPS Coordinates

```bash
# Merge GPS data
python3 scripts/update_confirmed_coordinates.py tree_coordinates_2024-12-06.csv
```

---

## 🖥️ Local Server

```bash
# Start server
python3 -m http.server 8000

# Visit: http://localhost:8000

# Stop server
kill $(lsof -ti:8000)
# OR press Ctrl+C

# Hard refresh browser
# Mac: Cmd+Shift+R
# Windows/Linux: Ctrl+Shift+R
```

---

## 🚀 Deploy to GitHub Pages

```bash
# Stage changes
git add .

# Commit
git commit -m "Your commit message"

# Push to main (auto-deploys)
git push origin main

# Live site: https://bondlegend4.github.io/nyc-american-chestnut-map-2025/
# Wait 2-3 minutes for deployment
```

---

## 📸 Photo Features

```bash
# Setup Supabase (one-time)
# See: docs/SUPABASE_SETUP.md

# Upload photos
# Visit: tools/photo_upload.html on mobile

# Update metadata
# Edit: photos/metadata.json
# Add photo entry, commit and push
```

---

## 📁 Key Files

```bash
# Data
data/trees.json                    # Tree data (generated, don't edit manually)
photos/metadata.json               # Photo metadata

# Scripts
scripts/build_trees_with_accuracy.py     # Excel → GeoJSON
scripts/import_from_arcgis.py            # ArcGIS → GeoJSON
scripts/update_confirmed_coordinates.py  # Merge GPS data

# Tools
tools/photo_upload.html            # Upload photos
tools/coordinate_collector.html    # Collect GPS

# Config
config/supabase-config.js          # Supabase credentials

# Docs (start here!)
docs/DOCUMENTATION_INDEX.md        # Master index
docs/YEARLY_DATA_WORKFLOW.md       # Annual updates
docs/ARCGIS_INTEGRATION.md         # ArcGIS import
docs/GIT_BRANCHING_STRATEGY.md     # Feature branches
```

---

## 🆘 Troubleshooting

```bash
# Python module not found
pip install requests pandas openpyxl geopy

# Git conflicts
git status                         # See conflicted files
# Edit files, resolve conflicts
git add resolved-file.html
git commit -m "Resolve merge conflict"

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# View commit history
git log --oneline --graph --all

# See what changed
git diff
git diff HEAD~1
```

---

## 📚 Documentation

- **[ARCGIS_AND_BRANCHING_SUMMARY.md](ARCGIS_AND_BRANCHING_SUMMARY.md)** - ArcGIS integration & branching guide
- **[PHOTO_FEATURES_SUMMARY.md](PHOTO_FEATURES_SUMMARY.md)** - Photo system overview
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current project status
- **[docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)** - Complete doc index

---

## 🎯 Common Workflows

### Yearly Data Update (Excel)
```bash
source venv/bin/activate
# Place new: "2025 year end chestnut results.xlsx"
python3 scripts/build_trees_with_accuracy.py
python3 -m http.server 8000  # Test
git add . && git commit -m "2025 survey data" && git push
```

### Yearly Data Update (ArcGIS)
```bash
source venv/bin/activate
git checkout feature/arcgis-integration
python3 scripts/import_from_arcgis.py --url "YOUR_URL"
python3 -m http.server 8000  # Test
git checkout develop && git merge feature/arcgis-integration
git checkout main && git merge develop && git push
```

### Add New Feature
```bash
git checkout -b feature/new-feature
# ... develop feature ...
git add . && git commit -m "Add new feature"
git checkout develop && git merge feature/new-feature
# ... test ...
git checkout main && git merge develop && git push
```

### Rollback Feature
```bash
# If feature not merged to main yet
git checkout main  # Already doesn't have the feature

# If already merged
git revert HEAD

# If need to remove completely
git reset --hard HEAD~1
```

---

**Version**: 4.1
**Last Updated**: December 6, 2024
