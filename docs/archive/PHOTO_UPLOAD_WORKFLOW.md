# Photo Upload and Management Workflow

**Complete guide for uploading, managing, and displaying tree photos**

## 🎯 Overview

This system allows users to upload photos of trees using their mobile devices and displays them in an interactive photo gallery on the map.

**Architecture**:
- **Storage**: Supabase (open-source, S3-compatible)
- **Upload Tool**: [tools/photo_upload.html](../tools/photo_upload.html)
- **Gallery**: Built into main map (index.html)
- **Metadata**: JSON file tracking all photos

## 📋 Prerequisites

Before uploading photos, you must:

1. **Set up Supabase** (one-time):
   - Follow [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
   - Create account and bucket
   - Copy API credentials

2. **Configure credentials**:
   - Edit `config/supabase-config.js`
   - Replace `YOUR-SUPABASE-PROJECT-URL` with your project URL
   - Replace `YOUR-SUPABASE-ANON-KEY` with your anon key

3. **Test connection**:
   ```bash
   # Start local server
   python3 -m http.server 8000

   # Visit http://localhost:8000/tools/photo_upload.html
   # Verify "Supabase not configured" warning is gone
   ```

## 🚀 Upload Workflow

### Option A: From Mobile Device (Field Collection)

1. **Navigate to tree on map**:
   - Visit: https://bondlegend4.github.io/nyc-american-chestnut-map-2025/
   - Find and click the tree marker
   - Note the **Tree ID** (e.g., NYC-AC-001)

2. **Open upload tool**:
   - Click **"📤 Upload Photo"** button in popup
   - Opens upload form in new tab

3. **Fill out form**:
   - **Tree ID**: Pre-filled from link
   - **Photo**: Tap to take photo or choose from gallery
   - **Description**: Add observations (optional)
   - **Your Name**: Required
   - **Email**: Optional (for follow-up)
   - **Season**: Auto-detected or manual selection
   - ✅ Confirm correct tree

4. **Submit**:
   - Click **"📤 Upload Photo"**
   - Wait for upload (may take 10-30 seconds on mobile data)
   - Photo is uploaded to Supabase!

5. **Important - Manual Step**:
   After upload succeeds, you'll see metadata like:
   ```json
   {
     "photo_id": "NYC-AC-001_2024-12-06_a3b2c1",
     "tree_id": "NYC-AC-001",
     "url": "https://xxxxx.supabase.co/storage/v1/object/public/tree-photos/NYC-AC-001/2024-12-06_a3b2c1.jpg",
     ...
   }
   ```

   **Copy this metadata** - you'll need it for the next step.

### Option B: From Desktop (Batch Upload)

1. **Prepare photos**:
   - Rename files with tree IDs (e.g., `NYC-AC-001_spring_2024.jpg`)
   - Resize/compress if over 5 MB
   - Organize by tree

2. **Use upload tool**:
   - Visit: http://localhost:8000/tools/photo_upload.html
   - Fill form for each photo
   - Upload one by one

3. **Or use Supabase dashboard**:
   - Go to https://supabase.com/dashboard
   - Navigate to Storage → tree-photos
   - Click "Upload file"
   - Manually organize into tree folders

## 📝 Updating Metadata

After photos are uploaded to Supabase, you must update `photos/metadata.json` to make them appear on the map.

### Method 1: Manual Edit (Recommended)

1. **Open metadata file**:
   ```bash
   code photos/metadata.json  # Or any text editor
   ```

2. **Add photo entry** to the `photos` array:
   ```json
   {
     "metadata": {
       "version": "1.0",
       "last_updated": "2024-12-06",
       "total_photos": 1,
       "trees_with_photos": 1,
       "storage_provider": "supabase"
     },
     "photos": [
       {
         "photo_id": "NYC-AC-001_2024-12-06_a3b2c1",
         "tree_id": "NYC-AC-001",
         "filename": "2024-12-06_a3b2c1.jpg",
         "url": "https://xxxxx.supabase.co/storage/v1/object/public/tree-photos/NYC-AC-001/2024-12-06_a3b2c1.jpg",
         "thumbnail_url": "https://xxxxx.supabase.co/storage/v1/object/public/tree-photos/NYC-AC-001/2024-12-06_a3b2c1.jpg",
         "uploaded_date": "2024-12-06T15:30:00Z",
         "uploaded_by": "Jane Smith",
         "uploader_email": "jane@example.com",
         "description": "Healthy growth, approximately 15' tall",
         "season": "winter",
         "tags": ["full-tree", "healthy"],
         "file_size": 2458931
       }
     ]
   }
   ```

3. **Update metadata counts**:
   ```json
   "metadata": {
     "last_updated": "2024-12-06",
     "total_photos": 1,  // Increment
     "trees_with_photos": 1  // Increment if new tree
   }
   ```

4. **Save and validate**:
   ```bash
   # Check JSON is valid
   python3 -c "import json; json.load(open('photos/metadata.json'))"
   # No output = valid JSON
   ```

### Method 2: Automated Script (Future)

```bash
# TODO: Create Python script to automate metadata updates
python3 scripts/update_photo_metadata.py
```

## 🚀 Deploy Updates

After updating metadata.json:

```bash
# 1. Stage changes
git add photos/metadata.json

# 2. Commit
git commit -m "Add photo for NYC-AC-001"

# 3. Push to GitHub
git push origin main

# 4. Wait 2-3 minutes for GitHub Pages deployment

# 5. Verify on live site
# Visit: https://bondlegend4.github.io/nyc-american-chestnut-map-2025/
# Click tree marker → Should show photo thumbnail
```

## 🖼️ Photo Gallery Features

### Viewing Photos

**In Map Popup**:
- Click any tree marker
- If tree has photos, see:
  - **Thumbnails**: Up to 3 photos shown
  - **Count badge**: "+X more" if > 3 photos
  - **Gallery button**: "📷 View Gallery (5)"

**In Full Gallery**:
- Click "View Gallery" button or any thumbnail
- Opens fullscreen gallery modal
- Features:
  - Large main image
  - Photo info (date, uploader, description)
  - Navigation (← Previous / Next →)
  - Thumbnail strip at bottom
  - Click any thumbnail to jump to that photo

### Upload Button

If tree has NO photos yet:
- Shows **"📤 Upload Photo"** button instead
- Links directly to upload tool with tree ID pre-filled

## 📊 Photo Metadata Schema

```json
{
  "photo_id": "string",           // Unique: {tree_id}_{date}_{random}
  "tree_id": "string",            // REQUIRED: NYC-AC-001
  "filename": "string",           // Original filename
  "url": "string",                // REQUIRED: Full Supabase URL
  "thumbnail_url": "string",      // Thumbnail URL (same as url for now)
  "uploaded_date": "ISO 8601",    // REQUIRED: 2024-12-06T15:30:00Z
  "uploaded_by": "string",        // REQUIRED: Uploader name
  "uploader_email": "string",     // Optional: Contact email
  "description": "string",        // Optional: Photo description
  "season": "string",             // spring/summer/fall/winter
  "tags": ["string"],             // Optional: ["flowering", "healthy"]
  "gps_coords": [lat, lon],       // Optional: [40.6618, -73.9710]
  "gps_accuracy": number,         // Optional: Meters
  "file_size": number             // Bytes
}
```

## 🔧 Managing Photos

### View All Photos

```bash
# List photos in Supabase
# Go to: https://supabase.com/dashboard
# Navigate to: Storage → tree-photos
# Browse folders by tree ID
```

### Download Photos

**Individual photo**:
- Right-click photo in gallery → "Save image as"

**Bulk download**:
- Use Supabase dashboard
- Storage → tree-photos → Select files → Download

### Delete Photos

1. **Remove from Supabase**:
   - Dashboard → Storage → tree-photos
   - Find file → Delete

2. **Remove from metadata.json**:
   - Edit `photos/metadata.json`
   - Remove photo entry from array
   - Update counts in metadata section
   - Commit and push

## 📱 Mobile Upload Tips

### Best Practices

1. **Photo Quality**:
   - Use phone camera (not downloads)
   - Take in good lighting
   - Get full tree in frame
   - Include surroundings for context

2. **File Size**:
   - Modern phones: 2-5 MB per photo
   - Max allowed: 5 MB
   - If too large, use "save as smaller size" before upload

3. **Descriptions**:
   - Note tree height estimate
   - Mention flowering, fruiting, damage
   - Record weather conditions
   - Date observations

4. **Seasonal Coverage**:
   - Try to get 1 photo per season
   - Spring: new leaves, flowers
   - Summer: full canopy
   - Fall: fall colors, fruits
   - Winter: bare branches, structure

### Troubleshooting Mobile Upload

**"Upload failed" error**:
- Check internet connection
- Try WiFi instead of cellular
- Compress photo if > 5 MB
- Check Supabase credentials configured

**Photo uploads but doesn't appear on map**:
- Check you updated photos/metadata.json
- Verify you committed and pushed changes
- Wait 2-3 minutes for deployment
- Hard refresh browser (Cmd+Shift+R)

**"Supabase not configured" warning**:
- Edit config/supabase-config.js
- Add your project URL and anon key
- See SUPABASE_SETUP.md

## 🎨 Organizing Photos

### Folder Structure in Supabase

```
tree-photos/ (bucket)
├── NYC-AC-001/
│   ├── 2024-12-06_a3b2c1.jpg
│   ├── 2024-05-15_x8y2z4.jpg
│   └── 2024-09-20_m5n8p1.jpg
├── NYC-AC-002/
│   └── 2024-11-01_q4r7s2.jpg
└── ...
```

### Naming Convention

Auto-generated by upload tool:
```
{date}_{random-id}.{ext}
2024-12-06_a3b2c1.jpg
```

**Date**: Upload date (YYYY-MM-DD)
**Random ID**: 6-character alphanumeric
**Extension**: .jpg, .png, or .webp

## 📈 Usage Statistics

Check Supabase dashboard:
1. Go to Settings → Usage
2. Monitor:
   - **Storage used**: Stay under 1 GB (free tier)
   - **Bandwidth**: Stay under 2 GB/month
   - **File count**: No limit

**Estimates**:
- 85 trees × 4 photos/year = 340 photos
- Average 3 MB/photo = ~1 GB/year
- Free tier: 1 year of photos
- Pro tier ($25/mo): 5+ years (100 GB)

## 🔄 Yearly Workflow

**During field survey season**:

1. **Collect photos**:
   - Visit each tree with mobile device
   - Open upload tool
   - Take + upload photos in field
   - OR collect photos and upload later

2. **Update metadata** (weekly):
   ```bash
   # Edit photos/metadata.json with new entries
   git add photos/metadata.json
   git commit -m "Add photos from week of Dec 6"
   git push
   ```

3. **Review gallery**:
   - Check photos appear correctly on map
   - Verify descriptions are helpful
   - Delete duplicates or poor quality

4. **Archive** (end of year):
   - Export all photos from Supabase (backup)
   - Store in archive/photos-2024/
   - Keep Supabase as live source

## 🆘 Common Issues

### Photo doesn't appear in gallery

**Checklist**:
- [ ] Photo uploaded to Supabase? (check dashboard)
- [ ] Entry added to photos/metadata.json?
- [ ] Tree ID matches exactly? (case-sensitive)
- [ ] URL is correct and accessible?
- [ ] metadata.json is valid JSON?
- [ ] Changes committed and pushed to GitHub?
- [ ] Waited 2-3 minutes for deployment?
- [ ] Hard refreshed browser?

### Upload button missing

**Cause**: Upload tool path incorrect
**Fix**: Verify `tools/photo_upload.html` exists
**Workaround**: Navigate directly to upload tool

### Thumbnails not loading

**Cause**: Supabase bucket not public
**Fix**: Check storage policies allow public read
**See**: SUPABASE_SETUP.md → "Set Up Storage Policies"

### Gallery navigation broken

**Cause**: Multiple photos with same photo_id
**Fix**: Ensure photo_id is unique for each photo
**Check**: `photos/metadata.json` for duplicates

## 📞 Support

**For upload issues**:
1. Check browser console for errors (F12)
2. Verify Supabase credentials
3. Test with sample photo first

**For gallery issues**:
1. Validate metadata.json format
2. Check photo URLs are accessible
3. Review browser console errors

**For Supabase issues**:
- Docs: https://supabase.com/docs/guides/storage
- Status: https://status.supabase.com

---

**Next Steps**:
1. Set up Supabase (SUPABASE_SETUP.md)
2. Configure credentials (config/supabase-config.js)
3. Test upload with one photo
4. Update metadata.json
5. Deploy and verify on map
6. Roll out to field teams

---

**Last Updated**: December 6, 2024
**Version**: 1.0
