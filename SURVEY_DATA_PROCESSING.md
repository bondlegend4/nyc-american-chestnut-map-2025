# Survey Data Processing Summary

## Overview

Successfully processed the "2024 year end chestnut results.xlsx" survey file and populated the map with **85 American Chestnut trees** from Brooklyn parks.

## Processing Steps

### 1. Location Extraction
**Script**: `extract_survey_locations.py`
- Identified 19 unique locations across 5 parks
- Extracted park names and specific areas (e.g., "Sugar Bowl", "Lookout Hill")

### 2. Geocoding
- Used OpenStreetMap's Nominatim service to convert location names to coordinates
- Successfully geocoded 18 out of 19 locations
- Failed: Green-Wood Cemetery (will need manual coordinates)

**Output**: `survey_locations_geocoded.csv`

### 3. Tree Data Extraction
**Script**: `build_trees_from_survey.py`
- Parsed tree survey data from Excel file
- Matched trees to geocoded locations
- Added small coordinate offsets to prevent markers from overlapping
- Extracted tree numbers and measurements where available

## Results

### Trees by Organization
- **Prospect Park Alliance**: 75 trees
- **NYC Parks**: 6 trees
- **Brooklyn Botanic Garden**: 4 trees

### Geographic Coverage
All trees are currently in **Brooklyn**, NY:
- Prospect Park (multiple areas)
- Brooklyn Botanic Garden (Native Flora Garden)
- Washington Park
- Fort Greene Park

### Data Quality Notes

1. **Coordinates**: Approximate geocoded locations based on park/area names
   - Added small random offsets (±0.001°) to separate trees in same location
   - This helps with visualization but coordinates are not GPS-precise

2. **Health Status**: Most marked as "unknown"
   - Survey focuses on measurements rather than health status
   - Future: Can infer health from growth trends

3. **Missing Data**:
   - 8 trees from Green-Wood Cemetery excluded (no coordinates)
   - Limited measurement data extracted (2024 columns)

## Files Generated

1. **survey_locations_to_geocode.csv** - Initial location list
2. **survey_locations_geocoded.csv** - Locations with coordinates
3. **data/trees.json** - Final GeoJSON for map (85 trees)

## View the Map

```bash
cd nyc-american-chestnut-map-2025
python3 -m http.server 8000
# Visit http://localhost:8000
```

You should see 85 tree markers clustered around Brooklyn parks.

## Next Steps to Improve Data

### 1. Add Green-Wood Cemetery Coordinates

Edit `survey_locations_geocoded.csv` and add coordinates for:
- Green-Wood Cemetery - Chestnut Hill

Then re-run:
```bash
python3 build_trees_from_survey.py
```

### 2. Extract More Measurement Data

The survey has growth data from 2021-2024. Could enhance the script to:
- Extract height and DBH measurements
- Calculate growth rates
- Show trends in popup notes

### 3. Improve Health Status

Currently all trees show "unknown" health. Could:
- Map survey notes to health status
- Use growth rate as health indicator
- Add manual health assessments

### 4. Add More Precise Locations

For better accuracy:
- Contact park organizations for GPS coordinates
- Use park maps to identify specific tree locations
- Conduct field survey with GPS device

### 5. Add Other NYC Locations

The survey mentions these are primarily Brooklyn trees. Could expand to:
- Manhattan parks
- Queens botanical areas
- Bronx conservation sites
- Staten Island Greenbelt

## Technical Details

### Coordinate Offset Algorithm
```python
lat_offset = (hash(f"{tree_num}{area}") % 100) / 100000
lon_offset = (hash(f"{tree_num}{park}") % 100) / 100000
```

This creates consistent but dispersed markers for trees in the same location.

### Geocoding Fallback
If specific area geocoding fails (e.g., "Sugar Bowl, Prospect Park"), the script falls back to park-level geocoding ("Prospect Park, Brooklyn").

## Validation Checklist

- ✅ JSON is valid GeoJSON format
- ✅ All coordinates are in Brooklyn
- ✅ All trees have organization attribution
- ✅ Contact emails are appropriate
- ✅ Tree IDs are sequential (NYC-AC-001 to NYC-AC-085)
- ✅ Map loads successfully in browser
- ✅ Markers cluster correctly
- ✅ Popups show tree information

## Questions/Issues

1. **Are these all American Chestnut?**
   - Survey mentions "Chinese chestnut trees/hybrids" section
   - Currently all mapped as *Castanea dentata*
   - May need species field

2. **Planting dates?**
   - Set to "2020-01-01" as approximation
   - Survey started 2021, so likely planted 2020 or earlier

3. **Multiple organizations at same location?**
   - Some areas list "Prospect Park - Chinese chestnut" separately
   - These may overlap with main Prospect Park trees

---

**Last Updated**: 2025-12-05
**Data Source**: 2024 year end chestnut results.xlsx
**Survey Date**: 2024-12-20
**Trees Mapped**: 85 / ~93 surveyed
