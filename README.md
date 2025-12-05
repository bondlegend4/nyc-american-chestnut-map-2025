# 🌳 NYC American Chestnut Conservation Map

An interactive map tracking American Chestnut (*Castanea dentata*) trees planted and maintained by various organizations across New York City. This project helps coordinate conservation efforts and enables community participation in tracking tree health and growth.

## 🎯 Project Goals

- **Transparency**: Open-source, public repository showing all tree locations and data
- **Coordination**: Help organizations discover nearby conservation efforts
- **Community Engagement**: Enable citizens to report tree updates to maintaining organizations
- **Free Hosting**: Static site hosted on GitHub Pages (no backend costs)

## 🗺️ Live Map

**View the map**: [https://YOUR-USERNAME.github.io/nyc-american-chestnut-map-2025/](https://YOUR-USERNAME.github.io/nyc-american-chestnut-map-2025/)

_(Replace with your actual GitHub Pages URL after deployment)_

## 📊 Features

- **Interactive Markers**: Click any tree to view details including:
  - Organization responsible for planting/maintenance
  - Health status (healthy, fair, poor, unknown)
  - Planting date and last update
  - Contact email for reporting updates

- **Organization Filtering**: Toggle layers to view trees by organization

- **Health Status Legend**: Color-coded markers:
  - 🟢 Green = Healthy
  - 🟡 Yellow = Fair
  - 🔴 Red = Poor / Monitoring
  - ⚫ Gray = Unknown

- **Marker Clustering**: Trees automatically cluster at higher zoom levels for performance

## 🚀 Quick Start (GitHub Pages Deployment)

### 1. Fork/Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/nyc-american-chestnut-map-2025.git
cd nyc-american-chestnut-map-2025
```

### 2. Update Tree Data

Edit `data/trees.json` with your tree locations (see [Data Format](#data-format) below).

### 3. Enable GitHub Pages

1. Go to your repository Settings
2. Navigate to **Pages** (left sidebar)
3. Under **Source**, select `main` branch
4. Click **Save**
5. Your site will be live at `https://YOUR-USERNAME.github.io/nyc-american-chestnut-map-2025/`

### 4. Test Locally (Optional)

```bash
# Simple HTTP server (Python 3)
python3 -m http.server 8000

# Or using Node.js
npx http-server

# Visit http://localhost:8000
```

## 📁 Project Structure

```
nyc-american-chestnut-map-2025/
├── index.html              # Main map visualization
├── data/
│   └── trees.json         # GeoJSON tree data
├── generate_map.py        # CSV/Excel → GeoJSON converter
├── README.md              # This file
└── .github/
    └── workflows/
        └── deploy.yml     # Auto-deploy on push (optional)
```

## 📋 Data Format

### GeoJSON Structure (`data/trees.json`)

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.9712, 40.7831]
      },
      "properties": {
        "tree_id": "NYC-AC-001",
        "organization": "NYC Parks",
        "planted_date": "2023-04-15",
        "health_status": "healthy",
        "contact": "forestry@parks.nyc.gov",
        "last_updated": "2024-11-20",
        "notes": "Young sapling, showing strong growth",
        "borough": "Manhattan",
        "location_description": "Central Park, North Woods"
      }
    }
  ]
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `coordinates` | `[lon, lat]` | Longitude and latitude (GeoJSON format) |
| `tree_id` | `string` | Unique identifier for the tree |
| `organization` | `string` | Organization that planted/maintains tree |
| `health_status` | `string` | One of: `healthy`, `fair`, `poor`, `unknown` |
| `contact` | `string` | Email for reporting updates |

### Optional Fields

- `planted_date` (YYYY-MM-DD)
- `last_updated` (YYYY-MM-DD)
- `notes` (string)
- `borough` (string)
- `location_description` (string)

## 🔧 Converting CSV/Excel to GeoJSON

If you have tree data in CSV or Excel format, use the included converter:

### Install Dependencies

```bash
pip install pandas openpyxl geopy
```

### CSV Template

Create `trees.csv` with these columns:

```csv
tree_id,organization,latitude,longitude,planted_date,health_status,contact,notes,borough,location_description
NYC-AC-001,NYC Parks,40.7831,-73.9712,2023-04-15,healthy,forestry@parks.nyc.gov,Young sapling,Manhattan,Central Park
```

Or generate a sample template:

```bash
python generate_map.py --sample
```

### Convert to GeoJSON

```bash
# From CSV
python generate_map.py trees.csv

# From Excel
python generate_map.py trees.xlsx

# With geocoding (if you have addresses instead of coordinates)
python generate_map.py trees.csv --geocode

# Custom output path
python generate_map.py trees.csv -o data/trees.json
```

## 🤝 Contributing Tree Data

### For Conservation Organizations

1. **Fork this repository**
2. **Add your trees** to `data/trees.json` or submit a CSV file
3. **Submit a Pull Request** with:
   - Organization contact information
   - Tree locations and health status
   - Photos (optional, can add to `assets/` folder)

### For Community Members

To report tree updates:
1. Click any tree marker on the map
2. Click "📧 Report Growth/Update" in the popup
3. Email will pre-fill with tree details
4. Send observations to the maintaining organization

## 🔐 Security & Privacy

- **No Backend**: Static site with no server-side code
- **Public Data**: All tree locations are publicly viewable
- **Email Protection**: Contact emails are encoded to reduce scraping
- **No Tracking**: No analytics or user tracking by default
- **Open Source**: All code visible in repository

## 🛣️ Future Enhancements

When budget allows, consider:

### Phase 2: Dynamic Updates (Supabase - Free Tier)
- Real-time tree health updates
- Community submission forms
- Photo uploads
- Historical growth tracking

### Phase 3: Advanced Features
- Tree growth predictions (ML models)
- Organization dashboards
- Mobile app (React Native)
- API for researchers

## 📞 Contact

For questions about this map or to add your organization's trees:

- **GitHub Issues**: [Create an issue](https://github.com/YOUR-USERNAME/nyc-american-chestnut-map-2025/issues)
- **Email**: YOUR-EMAIL@example.com
- **Organization**: YOUR-ORGANIZATION

## 📜 License

This project is released into the public domain under the [Unlicense](https://unlicense.org/) or [CC0](https://creativecommons.org/publicdomain/zero/1.0/) (your choice).

Tree data contributions retain original organization attribution.

## 🙏 Acknowledgments

- **Organizations**: NYC Parks, Million Trees NYC, Brooklyn Botanic Garden, and all conservation partners
- **Technology**: Leaflet.js, OpenStreetMap, GitHub Pages
- **Community**: All citizens reporting tree health updates

## 🌱 Data Sources

Current data includes:
- NYC Parks Department plantings
- Million Trees NYC initiative
- Brooklyn Botanic Garden conservation collection
- Prospect Park Alliance restoration projects
- Queens Botanical Garden specimens
- New York Botanical Garden research trees
- American Chestnut Foundation - NY Chapter
- Bronx River Alliance riparian projects
- Staten Island Greenbelt Conservancy

---

**Last Updated**: 2025-12-05
**Tree Count**: 15 (sample data - update after adding real data)
**Organizations**: 9

*Help save the American Chestnut from extinction* 🌳
