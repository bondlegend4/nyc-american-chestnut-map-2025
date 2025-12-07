# Tree Photo Storage

This directory contains metadata for tree photos. Photos are stored externally on **Supabase** (open-source S3-compatible storage).

## 📁 Contents

- **metadata.json** - Complete index of all tree photos with URLs and descriptions

## 🔗 Storage

Photos are NOT stored in this repository (to avoid Git size limits). Instead:

- **Storage Provider**: Supabase
- **Bucket**: `tree-photos`
- **Access**: Public CDN URLs
- **Cost**: Free tier (1 GB) or $25/month Pro (100 GB)

## 📸 Uploading Photos

**Mobile Upload Tool**: [../tools/photo_upload.html](../tools/photo_upload.html)

**Full Guide**: [../docs/PHOTO_UPLOAD_WORKFLOW.md](../docs/PHOTO_UPLOAD_WORKFLOW.md)

**Quick Start**:
1. Set up Supabase (see [docs/SUPABASE_SETUP.md](../docs/SUPABASE_SETUP.md))
2. Configure credentials in `config/supabase-config.js`
3. Use upload tool to upload photos
4. Manually add entries to `metadata.json`
5. Commit and push to deploy

## 📋 metadata.json Format

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2024-12-06",
    "total_photos": 0,
    "trees_with_photos": 0,
    "storage_provider": "supabase",
    "storage_url": "https://xxxxx.supabase.co/storage/v1/object/public/tree-photos/"
  },
  "photos": [
    {
      "photo_id": "NYC-AC-001_2024-12-06_a3b2c1",
      "tree_id": "NYC-AC-001",
      "filename": "2024-12-06_a3b2c1.jpg",
      "url": "https://xxxxx.supabase.co/.../NYC-AC-001/2024-12-06_a3b2c1.jpg",
      "thumbnail_url": "...",
      "uploaded_date": "2024-12-06T15:30:00Z",
      "uploaded_by": "Jane Smith",
      "description": "Healthy growth, 15' tall",
      "season": "winter",
      "tags": ["full-tree", "healthy"]
    }
  ]
}
```

## 🖼️ Viewing Photos

Photos appear on the map:
- **Thumbnails** in tree marker popups (max 3 shown)
- **Full gallery** modal with navigation
- **"Upload Photo"** button if tree has no photos yet

## 🔐 Security

- Photos are **publicly accessible** (matching public map)
- No authentication required for viewing
- Upload requires Supabase API key (configured in config)
- EXIF data (GPS, camera info) should be stripped before upload

## 💾 Backup

**Important**: Photos are only stored in Supabase. Create backups:

```bash
# Manual backup (via Supabase dashboard)
1. Go to Storage → tree-photos
2. Select all files
3. Download as ZIP
4. Store in archive/photos-backup-YYYY-MM-DD/

# Or use Supabase CLI
supabase storage download --bucket tree-photos --all
```

## 📊 Current Stats

- **Total Photos**: 0
- **Trees with Photos**: 0
- **Storage Used**: 0 MB / 1000 MB (free tier)

Update these after adding photos!

## 🆘 Troubleshooting

**Photos not appearing on map?**
1. Check `metadata.json` has entry for photo
2. Verify tree_id matches exactly
3. Test photo URL in browser (should load)
4. Check you committed and pushed changes
5. Wait 2-3 minutes for GitHub Pages deployment
6. Hard refresh browser (Cmd+Shift+R)

**Upload tool not working?**
1. Check `config/supabase-config.js` is configured
2. Verify Supabase bucket is public
3. Test connection (see SUPABASE_SETUP.md)

---

**See Also**:
- [Photo Upload Workflow](../docs/PHOTO_UPLOAD_WORKFLOW.md)
- [Supabase Setup Guide](../docs/SUPABASE_SETUP.md)
- [Upload Tool](../tools/photo_upload.html)
