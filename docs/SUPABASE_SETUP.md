# Supabase Photo Storage Setup Guide

**Purpose**: Instructions for setting up Supabase storage for tree photos

## 🎯 Why Supabase?

- **Open Source**: Fully open-source, can self-host
- **Free Tier**: 1GB storage, 2GB bandwidth/month (1-2 years of photos)
- **S3-Compatible**: No vendor lock-in, can migrate anytime
- **Cost-Effective**: $25/month Pro tier = 100GB (5+ years)
- **Built-in Features**: Authentication, direct upload API, CDN

## 📋 Initial Setup (One-Time)

### Step 1: Create Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub account (free)
4. Create new project:
   - **Name**: nyc-american-chestnut-photos
   - **Database Password**: (save this securely)
   - **Region**: Choose closest to NYC (us-east-1)
   - **Pricing Plan**: Free

### Step 2: Create Storage Bucket

1. In Supabase dashboard, go to **Storage** (left sidebar)
2. Click **New bucket**
3. Configure bucket:
   - **Name**: `tree-photos`
   - **Public bucket**: ✅ Yes (photos will be publicly viewable)
   - **File size limit**: 5 MB (mobile photos)
   - **Allowed MIME types**: `image/jpeg,image/png,image/webp`
4. Click **Create bucket**

### Step 3: Set Up Storage Policies

Enable public read access (anyone can view photos):

1. Go to **Storage** → **Policies**
2. Click **New policy** on `tree-photos` bucket
3. **Policy name**: "Public read access"
4. **Policy definition**:
   ```sql
   -- Allow anyone to read photos
   CREATE POLICY "Public read access"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'tree-photos');
   ```
5. Click **Review** → **Save policy**

Enable authenticated upload (optional - for now we'll use API key):

```sql
-- Allow authenticated users to upload
CREATE POLICY "Authenticated upload"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'tree-photos'
  AND auth.role() = 'authenticated'
);
```

### Step 4: Get API Credentials

1. Go to **Settings** → **API** (left sidebar)
2. Copy these values (you'll need them):
   - **Project URL**: `https://xxxxx.supabase.co`
   - **API Key (anon/public)**: `eyJhbG...` (safe to expose in client-side code)
   - **Service Role Key**: `eyJhbG...` (keep secret, for server-side only)

### Step 5: Configure Project

Create configuration file with your credentials:

**config/supabase-config.js** (client-side, safe to commit):
```javascript
// Supabase configuration for tree photo storage
const SUPABASE_CONFIG = {
  url: 'https://YOUR-PROJECT.supabase.co',
  anonKey: 'YOUR-ANON-KEY-HERE',
  bucketName: 'tree-photos'
};
```

**IMPORTANT**: Replace `YOUR-PROJECT` and `YOUR-ANON-KEY-HERE` with your actual values.

## 📁 Storage Structure

Photos will be organized in Supabase storage:

```
tree-photos/  (bucket)
├── NYC-AC-001/
│   ├── 2024-12-20_001.jpg
│   ├── 2024-12-20_002.jpg
│   └── thumbs/
│       ├── 2024-12-20_001.jpg  (400x400)
│       └── 2024-12-20_002.jpg
├── NYC-AC-002/
│   └── ...
└── metadata/
    └── photos.json  (master metadata file)
```

## 🔐 Security Configuration

### Public Bucket (Recommended for Public Map)

Since the map is public anyway, photos can be public:

```sql
-- Read: Anyone
-- Upload: Authenticated users only
-- Delete: Admin only
```

### Private Bucket (If Needed Later)

```sql
-- Read: Authenticated users only
-- Upload: Authenticated users only
-- Delete: Admin only
```

## 💰 Cost Estimation

### Free Tier Limits
- **Storage**: 1 GB
- **Bandwidth**: 2 GB/month
- **Database**: 500 MB

### Usage Estimates
- **Year 1**: 85 trees × 4 photos × 3 MB = ~1 GB (fits in free tier!)
- **Year 2**: Another 1 GB = 2 GB total (need Pro: $25/month)
- **Year 5**: ~5 GB total (still well within Pro tier 100 GB)

### When to Upgrade
- **Stay Free**: If you keep photos under 1 GB total
- **Upgrade to Pro ($25/month)**: When you exceed 1 GB or 2 GB bandwidth/month

### Cost Optimization
- Resize photos before upload (compress to 1-2 MB)
- Use WebP format (50% smaller than JPEG)
- Delete duplicate/poor-quality photos
- Generate thumbnails (100 KB vs 3 MB)

## 🔧 Testing Connection

Test Supabase connection before implementing upload:

**test-supabase.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Supabase Connection</title>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
</head>
<body>
    <h1>Supabase Connection Test</h1>
    <button onclick="testConnection()">Test Connection</button>
    <pre id="result"></pre>

    <script>
        const { createClient } = supabase;
        const supabaseClient = createClient(
            'https://YOUR-PROJECT.supabase.co',
            'YOUR-ANON-KEY'
        );

        async function testConnection() {
            try {
                // List buckets
                const { data, error } = await supabaseClient.storage.listBuckets();

                if (error) throw error;

                document.getElementById('result').textContent =
                    'Success! Buckets: ' + JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').textContent =
                    'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
```

## 📚 Supabase JavaScript API Reference

### Upload Photo
```javascript
const file = event.target.files[0];
const filePath = `${treeId}/${timestamp}_${file.name}`;

const { data, error } = await supabaseClient.storage
  .from('tree-photos')
  .upload(filePath, file, {
    cacheControl: '3600',
    upsert: false
  });
```

### Get Public URL
```javascript
const { data } = supabaseClient.storage
  .from('tree-photos')
  .getPublicUrl(filePath);

const url = data.publicUrl;
```

### List Photos for Tree
```javascript
const { data, error } = await supabaseClient.storage
  .from('tree-photos')
  .list(`${treeId}/`, {
    limit: 100,
    offset: 0,
    sortBy: { column: 'created_at', order: 'desc' }
  });
```

### Delete Photo
```javascript
const { error } = await supabaseClient.storage
  .from('tree-photos')
  .remove([filePath]);
```

## 🚀 Deployment Workflow

### Development
1. Use test Supabase project
2. Test uploads/downloads locally
3. Verify public URLs work

### Production
1. Create production Supabase project
2. Update `config/supabase-config.js` with prod credentials
3. Migrate test photos (if any)
4. Deploy to GitHub Pages

## 🆘 Troubleshooting

### "Invalid API key" error
- Double-check you copied the full anon key
- Verify project URL is correct
- Try regenerating API key in dashboard

### "Storage bucket not found"
- Verify bucket name is exactly `tree-photos`
- Check bucket was created successfully
- Ensure bucket is public

### Upload fails with 413 error
- File too large (limit: 5 MB)
- Compress photo before upload
- Check bucket file size limit settings

### Photos not displaying
- Verify public URL is correct
- Check bucket is public
- Inspect browser console for CORS errors
- Ensure storage policy allows public read

### Bandwidth exceeded (free tier)
- Optimize images (WebP, compression)
- Use thumbnails for gallery view
- Upgrade to Pro tier ($25/month)

## 📊 Monitoring Usage

Check usage in Supabase dashboard:

1. Go to **Settings** → **Usage**
2. Monitor:
   - **Storage**: Should stay under 1 GB for free tier
   - **Bandwidth**: Should stay under 2 GB/month
   - **Database**: Not heavily used for photos

Set up alerts:
1. Go to **Settings** → **Billing**
2. Enable usage alerts at 80% of limits

## 🔄 Migration Plan (If Needed)

If you ever need to migrate from Supabase:

1. **Download all photos**:
   ```javascript
   // List all files
   const { data } = await supabaseClient.storage
     .from('tree-photos')
     .list('', { limit: 1000 });

   // Download each file
   for (const file of data) {
     const { data: blob } = await supabaseClient.storage
       .from('tree-photos')
       .download(file.name);
   }
   ```

2. **Export metadata**:
   - Download `photos/metadata.json`
   - Includes all photo URLs and descriptions

3. **Upload to new provider**:
   - Backblaze B2, Cloudflare R2, or self-hosted MinIO
   - Update URLs in metadata.json
   - Deploy updated metadata

## 📞 Support

- **Supabase Docs**: https://supabase.com/docs/guides/storage
- **Community**: https://github.com/supabase/supabase/discussions
- **Status**: https://status.supabase.com

---

**Next Steps**:
1. Create Supabase account
2. Set up `tree-photos` bucket
3. Copy API credentials to `config/supabase-config.js`
4. Test connection with test-supabase.html
5. Proceed to upload tool implementation
