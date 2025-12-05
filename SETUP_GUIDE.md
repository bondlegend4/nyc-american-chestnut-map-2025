# Quick Setup Guide

## Testing Locally (5 minutes)

1. **Open the map in your browser**:
   ```bash
   cd /Users/jose_d_sandoval/Desktop/Send_to_Diana/Highway_folder/lpr-/nyc-american-chestnut-map-2025
   python3 -m http.server 8000
   ```

2. **Visit**: http://localhost:8000

3. You should see 15 sample trees on the map across NYC

## Deploying to GitHub Pages (10 minutes)

### Step 1: Push to GitHub

```bash
cd /Users/jose_d_sandoval/Desktop/Send_to_Diana/Highway_folder/lpr-/nyc-american-chestnut-map-2025

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: NYC American Chestnut Map"

# Create GitHub repo and push
# (Replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/nyc-american-chestnut-map-2025.git
git branch -M main
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to: https://github.com/YOUR-USERNAME/nyc-american-chestnut-map-2025/settings/pages
2. Under **Source**, select `main` branch
3. Click **Save**
4. Wait 1-2 minutes for deployment
5. Your site will be live at: `https://YOUR-USERNAME.github.io/nyc-american-chestnut-map-2025/`

### Step 3: Enable GitHub Actions (Auto-deploy)

The workflow file is already created at `.github/workflows/deploy.yml`. It will automatically deploy changes whenever you push to main.

If it doesn't run automatically:
1. Go to: https://github.com/YOUR-USERNAME/nyc-american-chestnut-map-2025/settings/pages
2. Under **Build and deployment**, select **GitHub Actions**
3. Push a small change to trigger deployment

## Adding Real Tree Data

### Option 1: Edit JSON Directly

Edit `data/trees.json` and add your trees following this format:

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-73.9712, 40.7831]
  },
  "properties": {
    "tree_id": "NYC-AC-016",
    "organization": "Your Organization",
    "planted_date": "2024-05-20",
    "health_status": "healthy",
    "contact": "your-email@organization.org",
    "last_updated": "2024-12-05",
    "notes": "Description of the tree",
    "borough": "Manhattan",
    "location_description": "Park name or street"
  }
}
```

### Option 2: Convert from CSV/Excel

1. **Create a CSV file** with your tree data:

```csv
tree_id,organization,latitude,longitude,planted_date,health_status,contact,notes,borough,location_description
NYC-AC-016,Your Org,40.7831,-73.9712,2024-05-20,healthy,email@org.org,Notes here,Manhattan,Central Park
```

2. **Install dependencies**:
```bash
pip install pandas openpyxl geopy
```

3. **Convert to GeoJSON**:
```bash
python generate_map.py your_trees.csv
```

This will update `data/trees.json` automatically.

### Option 3: Use Geocoding (if you only have addresses)

```csv
tree_id,organization,address,planted_date,health_status,contact,notes
NYC-AC-016,Your Org,"123 Main St, Brooklyn, NY",2024-05-20,healthy,email@org.org,Notes
```

```bash
python generate_map.py your_trees.csv --geocode
```

## Customization Tips

### Change Map Center/Zoom

Edit [index.html](index.html) line 137:
```javascript
const map = L.map('map').setView([40.7128, -74.0060], 11);
//                                  ↑ latitude  ↑ longitude ↑ zoom
```

### Change Color Scheme

Edit the health icon colors in [index.html](index.html) lines 142-147:
```javascript
const colors = {
    'healthy': '#28a745',  // Change to your preferred green
    'fair': '#ffc107',     // Change to your preferred yellow
    'poor': '#dc3545',     // Change to your preferred red
    'unknown': '#6c757d'   // Change to your preferred gray
};
```

### Add Your Logo/Branding

Edit the info panel in [index.html](index.html) lines 118-126.

## Troubleshooting

### Map doesn't load locally
- Make sure you're running from the project root directory
- Check browser console for errors (F12)
- Ensure `data/trees.json` exists and is valid JSON

### Trees don't appear
- Verify coordinates are in `[longitude, latitude]` format (not reversed)
- Check that `health_status` is one of: `healthy`, `fair`, `poor`, `unknown`
- Validate JSON at https://jsonlint.com/

### GitHub Pages shows 404
- Wait 2-3 minutes after enabling Pages
- Check that `index.html` is in the root directory
- Verify the repository is public

## Next Steps

1. Replace sample data with real tree locations
2. Update contact information in README.md
3. Add photos to an `assets/photos/` folder
4. Invite conservation organizations to contribute
5. Share the map URL with the community

## Need Help?

- Create an issue: https://github.com/YOUR-USERNAME/nyc-american-chestnut-map-2025/issues
- Check README.md for detailed documentation
