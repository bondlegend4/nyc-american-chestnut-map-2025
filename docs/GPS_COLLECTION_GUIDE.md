# GPS Collection Guide for Park Organizations

## Overview

This guide explains how to collect confirmed GPS coordinates for American Chestnut trees using the mobile coordinate collector tool.

## Why Collect GPS Coordinates?

Currently, tree locations on the map are **estimated** based on park area names (accuracy: ±50-200 meters). GPS-confirmed coordinates will:

- Improve location accuracy to ±5 meters
- Help visitors find specific trees
- Enable precise monitoring over time
- Support research and conservation efforts
- Display green "CONFIRMED" badges on the map

## What You Need

### Equipment
- **Smartphone or tablet** with GPS capability
- **Internet browser** (Chrome, Safari, Firefox)
- **Pen and paper** (backup for notes)

### Information to Collect
For each tree:
- Tree ID (e.g., "NYC-AC-001") or Tree number (e.g., "Tree #7")
- GPS coordinates (automatic from phone)
- Accuracy reading (automatic from phone)
- Your name (as collector)
- Any observations or notes

## Step-by-Step Instructions

### Before You Go

1. **Download the GPS Collector**:
   - Visit: `https://bondlegend4.github.io/nyc-american-chestnut-map-2025/coordinate_collector.html`
   - Bookmark this page for easy access
   - Test that GPS works by clicking "Get Current Location"

2. **Plan Your Route**:
   - Review the map to see which trees need confirmation
   - Trees with red ⚠️ "ESTIMATED" badges are highest priority
   - Trees with blue 🎯 "AREA" badges could use improvement
   - Print or screenshot the tree list for your park

3. **Check Weather**:
   - GPS works best on clear days
   - Avoid heavy tree cover if possible (limits satellite visibility)
   - Rain won't hurt the phone, but make it harder to use

### In the Field

#### Step 1: Navigate to Tree
- Use the map to get near the tree's estimated location
- Look for the physical tree based on the area description
- Example: "Sugar Bowl area, near the baseball fields"

#### Step 2: Open GPS Collector
- Open the bookmark on your phone
- Click **"Get Current Location"**
- Wait for GPS to activate (usually 5-15 seconds)

#### Step 3: Wait for Good Accuracy
**GPS Accuracy Guidelines**:
- **Excellent**: < 5 meters (green light, proceed immediately)
- **Good**: 5-10 meters (yellow light, acceptable)
- **Poor**: > 10 meters (red light, wait longer or move to open area)

**Tips for Better Accuracy**:
- Stand in an open area with clear sky view
- Hold phone away from body (extend arm)
- Wait 30-60 seconds for GPS to stabilize
- Avoid standing under dense tree canopy
- Move away from tall buildings if possible

#### Step 4: Position at Tree
- Stand **at the base of the trunk**
- Do NOT stand several feet away
- For best results, stand on the side with clearest sky view
- Hold phone at chest height

#### Step 5: Record Measurement

Fill in the form:
1. **Park**: Select from dropdown (e.g., "PROSPECT PARK")
2. **Area**: Select from dropdown (e.g., "Sugar Bowl")
3. **Tree ID or Number**:
   - Enter "NYC-AC-001" if you know the official ID
   - OR enter "7" if you know it's Tree #7
   - Check the map or your tree list for this information
4. **Your Name**: Enter your name (e.g., "Jane Smith")
5. **Notes**: Add any observations:
   - Tree condition
   - Nearby landmarks
   - Access directions
   - Example: "Next to park bench, 20m from path"

6. Click **"Save Measurement"**

You'll see a success message and the measurement added to the list.

#### Step 6: Move to Next Tree
- Repeat for all trees in your area
- No need to export until you're done with all trees

### After Field Collection

#### Export Your Data
1. Review the list of saved measurements
2. Click **"Export All to CSV"**
3. A file named `tree_coordinates_YYYY-MM-DD.csv` will download

#### Submit Coordinates
**Option 1: Email**
- Email the CSV file to the map maintainer
- Subject: "GPS Coordinates - [Your Park Name] - [Date]"
- Include: Number of trees measured, any issues encountered

**Option 2: GitHub** (if you're tech-savvy)
- Create a Pull Request with the CSV file
- The maintainer will merge and update the map

## Data Format

Your exported CSV will look like this:

```csv
tree_id,park,area,latitude,longitude,accuracy_meters,collector,notes,timestamp
NYC-AC-001,PROSPECT PARK,Sugar Bowl,40.661845,-73.971023,3.2,Jane Smith,Next to bench,2024-12-06T15:23:45
7,PROSPECT PARK,Sugar Bowl,40.661912,-73.971156,4.5,Jane Smith,Near baseball field,2024-12-06T15:31:22
```

## Quality Control

### Before Submitting
Check your data:
- [ ] All trees have accuracy < 10 meters (preferably < 5m)
- [ ] Coordinates are in the correct park (check latitude/longitude make sense)
- [ ] Tree IDs match your park's tree list
- [ ] Notes explain how to find the tree
- [ ] Your name is consistent across all entries

### Validation
The maintainer will:
- Verify coordinates fall within park boundaries
- Check accuracy values are reasonable
- Confirm tree IDs match existing records
- May contact you with questions

## Troubleshooting

### GPS Not Working
**Problem**: "Get Current Location" doesn't work
**Solutions**:
- Enable Location Services in phone settings
- Allow browser to access location (click "Allow" when prompted)
- Try a different browser (Chrome usually works best)
- Restart your phone

### Poor Accuracy
**Problem**: Accuracy stuck at 20-30 meters
**Solutions**:
- Move to an open area with clear sky view
- Wait 1-2 minutes for GPS to stabilize
- Avoid thick tree canopy overhead
- Check that High Accuracy mode is enabled in phone settings
- Try turning phone GPS off and on again

### Wrong Location
**Problem**: Coordinates show you in wrong location
**Solutions**:
- GPS may be using WiFi/cell tower instead of satellites
- Disable WiFi temporarily to force GPS mode
- Move away from buildings
- Wait for "GPS Accuracy" to improve

### Can't Find Tree
**Problem**: Tree not at estimated location
**Solutions**:
- Expand search radius to 100 meters
- Ask park staff for help
- Check if tree has been removed (note in submission)
- Take photo of area for future reference

### Data Lost
**Problem**: Closed browser and lost measurements
**Solutions**:
- Data is saved in browser's localStorage
- Re-open coordinate_collector.html on same phone
- Your data should still be there
- Export immediately as backup

## Best Practices

### Recommended Workflow
1. **Batch Collection**: Collect 10-20 trees per session
2. **Export Often**: Export after each session as backup
3. **Clear After Export**: Option to clear saved data (keeps browser storage clean)
4. **Double-Check**: Review coordinates on map before final submission

### Safety
- Always collect with a partner for safety
- Stay on designated paths
- Watch for poison ivy, ticks, and wildlife
- Bring water, especially in summer
- Tell someone your planned route and return time

### Photo Documentation
Consider taking photos:
- Tree from multiple angles
- GPS screen showing accuracy
- Nearby landmarks for future reference
- Upload photos separately with tree ID in filename

## Example Collection Session

**Prospect Park - Sugar Bowl Area**
**Date**: December 6, 2024
**Collector**: Jane Smith
**Trees Collected**: 15

| Time | Tree | Accuracy | Notes |
|------|------|----------|-------|
| 2:15 PM | NYC-AC-001 | 3.2m | Near bench, good condition |
| 2:22 PM | #7 | 4.5m | Baseball field corner |
| 2:30 PM | #10 | 5.1m | On hill, clear sky |
| 2:38 PM | #12 | 8.2m | Under trees, waited 2 min |
| ... | ... | ... | ... |

**Average Accuracy**: 4.8 meters
**Time Per Tree**: ~7 minutes (including walking)
**Issues**: Trees #15 and #18 could not be located

## Impact of Your Work

Each confirmed coordinate you collect:
- Improves map accuracy by 90% (from ±50m to ±5m)
- Helps researchers track individual trees over time
- Enables precise growth monitoring
- Makes it easier for volunteers to find trees for care
- Contributes to scientific documentation
- Shows conservation success to stakeholders

**Thank you for your contribution to American Chestnut conservation!**

## Questions?

Contact the map maintainer:
- **GitHub**: [Open an issue](https://github.com/bondlegend4/nyc-american-chestnut-map-2025/issues)
- **Email**: conservation@[your-org].org

## Quick Reference

```
📱 Open coordinate_collector.html on phone
📍 Click "Get Current Location"
⏱️ Wait for accuracy < 10m (ideally < 5m)
🌳 Stand at base of tree trunk
📝 Fill in tree ID, your name, notes
💾 Click "Save Measurement"
🔄 Repeat for all trees
📤 Export All to CSV
📧 Email CSV to maintainer
```

---

**Version**: 1.0
**Last Updated**: 2024-12-06
**Tool**: coordinate_collector.html
