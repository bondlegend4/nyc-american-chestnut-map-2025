# Image Documentation Feature - Implementation Plan

**⚠️ PAUSED FOR USER REVIEW - DO NOT IMPLEMENT YET**

This document outlines the complete plan for adding tree photo documentation to the NYC American Chestnut Map.

## 🎯 Goals

Allow users to:
1. **View photos** of each tree (current appearance, seasonal changes, growth progress)
2. **Upload photos** from mobile devices in the field
3. **Compare photos** year-over-year to track growth
4. **Document health issues** visually (blight, damage, pests)
5. **Celebrate success** (flowering, fruiting, healthy growth)

## 📋 Requirements

### User Stories

**As a park manager**, I want to:
- Upload photos of trees during annual surveys
- See historical photos to track growth
- Document health issues with visual evidence
- Share success stories with stakeholders

**As a researcher**, I want to:
- Access time-series photos for analysis
- Download full-resolution images
- Filter photos by date, season, or tree
- Export photo metadata

**As a community member**, I want to:
- See what the trees look like
- Report observations with photos
- Watch trees grow over time
- Learn to identify American Chestnuts

## 🏗️ Architecture Options

### Option 1: GitHub-Based (Free, Simple) ⭐ RECOMMENDED FOR MVP

**Storage**: GitHub repository in `photos/` directory
**Upload**: Manual via GitHub web interface or git push
**Display**: Direct links to raw.githubusercontent.com

**Pros**:
- ✅ Free (GitHub has generous limits)
- ✅ Version controlled (all changes tracked)
- ✅ No backend needed
- ✅ Fast CDN delivery
- ✅ Works with current static site

**Cons**:
- ❌ No mobile upload (must use computer)
- ❌ Requires GitHub account
- ❌ Manual process for adding photos
- ❌ Not ideal for many frequent updates

**Cost**: $0/month

---

### Option 2: Cloudinary (Free Tier, Good UX)

**Storage**: Cloudinary CDN
**Upload**: API-based, works from mobile
**Display**: Cloudinary URLs with transformations

**Pros**:
- ✅ Free tier: 25GB storage, 25GB bandwidth/month
- ✅ Image transformations (thumbnails, optimization)
- ✅ Mobile upload support
- ✅ CDN delivery
- ✅ Direct URL access

**Cons**:
- ❌ Requires API key management
- ❌ Monthly limits (exceeded = cost or service stop)
- ❌ Vendor lock-in
- ❌ Need upload widget or backend

**Cost**: $0-89/month (free tier → paid when limits exceeded)

---

### Option 3: Supabase Storage (Free Tier, Most Features)

**Storage**: Supabase S3-compatible bucket
**Upload**: API + direct mobile upload
**Display**: Supabase CDN URLs

**Pros**:
- ✅ Free tier: 1GB storage, 2GB bandwidth/month
- ✅ PostgreSQL database included (for metadata)
- ✅ Authentication built-in
- ✅ Real-time subscriptions
- ✅ Mobile-friendly upload

**Cons**:
- ❌ Requires backend setup
- ❌ Learning curve
- ❌ Free tier limits tight for photos
- ❌ More complex than static site

**Cost**: $0-25/month (free tier → Pro)

---

### Option 4: Imgur API (Free for Non-Commercial)

**Storage**: Imgur
**Upload**: API-based
**Display**: Imgur CDN

**Pros**:
- ✅ Free for non-commercial
- ✅ Simple API
- ✅ Fast CDN
- ✅ No bandwidth limits

**Cons**:
- ❌ Not designed for archives
- ❌ Images may be public
- ❌ Terms of Service limitations
- ❌ Not professional

**Cost**: $0/month (if non-commercial use allowed)

---

## 🎨 User Interface Design

### Map Popup Enhancement

**Current popup**:
```
┌─────────────────────────────┐
│ Prospect Park Alliance      │
│ Tree ID: NYC-AC-001         │
│ Health: HEALTHY             │
│ Location: 🎯 AREA           │
│ [📊 View Growth Chart]      │
│ [📧 Report Update]          │
└─────────────────────────────┘
```

**Enhanced popup with photos**:
```
┌─────────────────────────────┐
│ Prospect Park Alliance      │
│ Tree ID: NYC-AC-001         │
│ Health: HEALTHY             │
│                             │
│ ┌───────────────────┐       │
│ │  [Latest Photo]   │       │  ← Thumbnail
│ │  Dec 2024         │       │
│ └───────────────────┘       │
│ [📷 View Gallery (12)]      │  ← New button
│                             │
│ [📊 View Growth Chart]      │
│ [📧 Report Update]          │
└─────────────────────────────┘
```

### Photo Gallery Modal

```
╔═══════════════════════════════════════════╗
║ Photo Gallery - NYC-AC-001             [X]║
╠═══════════════════════════════════════════╣
║                                           ║
║  ┌─────────────────────────────────┐     ║
║  │                                 │     ║
║  │      [Full-Size Photo]          │     ║
║  │      Dec 20, 2024               │     ║
║  │      Uploaded by: Jane Smith    │     ║
║  │                                 │     ║
║  └─────────────────────────────────┘     ║
║                                           ║
║  Description: "Healthy growth, 15' tall" ║
║                                           ║
║  [← Prev]  12/24  [Next →]               ║
║                                           ║
║  ┌──┬──┬──┬──┬──┬──┬──┬──┐              ║
║  │█ │  │  │  │  │  │  │  │  Thumbnails  ║
║  └──┴──┴──┴──┴──┴──┴──┴──┘              ║
║                                           ║
║  Filter: [All] [2024] [2023] [2022]      ║
║  Sort: [Newest] [Oldest] [Season]        ║
║                                           ║
║  [📤 Upload Photo]  [💾 Download All]    ║
╚═══════════════════════════════════════════╝
```

### Mobile Upload Interface

```
╔═══════════════════════════════════════════╗
║ Upload Tree Photo                      [X]║
╠═══════════════════════════════════════════╣
║                                           ║
║  Tree: NYC-AC-001                         ║
║  Location: Prospect Park - Sugar Bowl     ║
║                                           ║
║  ┌─────────────────────────────────┐     ║
║  │                                 │     ║
║  │    📷 Take Photo                │     ║
║  │    or                           │     ║
║  │    📁 Choose from Gallery       │     ║
║  │                                 │     ║
║  └─────────────────────────────────┘     ║
║                                           ║
║  Description: ________________           ║
║  [Optional notes about tree]             ║
║                                           ║
║  Your name: _______________              ║
║  Email: ____________________             ║
║                                           ║
║  [ ] I confirm this is the correct tree  ║
║                                           ║
║  [📤 Upload Photo]                       ║
╚═══════════════════════════════════════════╝
```

## 📐 Data Structure

### Photo Metadata

**If using GitHub** (`photos/metadata.json`):
```json
{
  "photos": [
    {
      "photo_id": "NYC-AC-001_2024-12-20_001",
      "tree_id": "NYC-AC-001",
      "filename": "NYC-AC-001_2024-12-20_001.jpg",
      "url": "https://raw.githubusercontent.com/.../photos/NYC-AC-001/2024-12-20_001.jpg",
      "thumbnail_url": "https://raw.githubusercontent.com/.../photos/NYC-AC-001/thumbs/2024-12-20_001.jpg",
      "uploaded_date": "2024-12-20T15:30:00Z",
      "uploaded_by": "Jane Smith",
      "description": "Healthy growth, approximately 15' tall",
      "season": "winter",
      "tags": ["full-tree", "healthy", "flowering"],
      "gps_coords": [40.661845, -73.971023],
      "gps_accuracy": 3.2
    }
  ]
}
```

**Directory structure**:
```
photos/
├── metadata.json
├── NYC-AC-001/
│   ├── 2024-12-20_001.jpg       # Full resolution
│   ├── 2024-12-20_002.jpg
│   ├── 2024-05-15_001.jpg
│   └── thumbs/
│       ├── 2024-12-20_001.jpg   # 400x400 thumbnails
│       ├── 2024-12-20_002.jpg
│       └── 2024-05-15_001.jpg
├── NYC-AC-002/
│   └── ...
└── by-date/
    ├── 2024-12/
    ├── 2024-05/
    └── ...
```

### Extended trees.json

```json
{
  "properties": {
    "tree_id": "NYC-AC-001",
    "organization": "Prospect Park Alliance",
    "health_status": "healthy",
    "growth_data": { ... },
    "location_accuracy": { ... },
    "photos": {
      "count": 12,
      "latest": {
        "url": "https://raw.githubusercontent.com/.../photos/NYC-AC-001/2024-12-20_001.jpg",
        "thumbnail": "https://raw.githubusercontent.com/.../photos/NYC-AC-001/thumbs/2024-12-20_001.jpg",
        "date": "2024-12-20",
        "description": "Healthy growth"
      },
      "metadata_url": "photos/metadata.json"  // For full gallery
    }
  }
}
```

## 🔨 Implementation Phases

### Phase 1: MVP - GitHub-Based (Week 1)

**Goal**: Basic photo viewing, manual upload

**Tasks**:
1. Create `photos/` directory in repository
2. Create `photos/metadata.json` template
3. Add photo gallery modal to index.html
4. Update popup to show latest photo thumbnail
5. Add "View Gallery" button
6. Document manual upload process

**Deliverables**:
- Photo gallery modal UI
- Thumbnail display in popups
- Manual upload guide for organizations
- 5-10 sample photos uploaded

**Effort**: 6-8 hours

---

### Phase 2: Mobile Upload Tool (Week 2)

**Goal**: Mobile-friendly photo upload

**Options**:

**A. GitHub API Upload (Simple)**:
- Create HTML form for photo upload
- Use GitHub API to create/update files
- Requires GitHub Personal Access Token
- Works from mobile browser

**B. Cloudinary Widget (Better UX)**:
- Embed Cloudinary upload widget
- Direct mobile upload
- Automatic thumbnail generation
- No GitHub account needed

**Tasks**:
1. Choose upload method
2. Create upload interface (HTML/JS)
3. Add photo validation (size, format)
4. Generate thumbnails
5. Update metadata.json automatically
6. Test on mobile devices

**Deliverables**:
- Mobile upload tool (`tools/photo_upload.html`)
- Automatic thumbnail generation
- Metadata update automation
- User guide for photo collection

**Effort**: 10-15 hours

---

### Phase 3: Enhanced Features (Week 3-4)

**Goal**: Professional photo management

**Features**:
- **Time-lapse view**: Animate photos chronologically
- **Seasonal comparison**: Side-by-side spring/summer/fall/winter
- **Before/After slider**: Compare years with interactive slider
- **Photo filtering**: By date, season, uploader, tags
- **Bulk download**: Download all photos for a tree
- **Photo moderation**: Approve/reject community uploads

**Tasks**:
1. Build time-lapse player
2. Create seasonal comparison view
3. Implement before/after slider
4. Add photo filtering UI
5. Create bulk download feature
6. (Optional) Add moderation workflow

**Deliverables**:
- Time-lapse visualization
- Seasonal comparison tool
- Advanced filtering
- Bulk operations

**Effort**: 15-20 hours

---

## 💾 Storage Estimates

### Photo Size Assumptions

- Full resolution: 2-5 MB (phone camera)
- Thumbnail: 50-200 KB
- Average: 3 MB full + 100 KB thumbnail = 3.1 MB per photo

### Yearly Estimates

- 85 trees × 4 photos/year = 340 photos
- 340 × 3.1 MB = 1,054 MB ≈ 1 GB/year

### 5-Year Projection

- 5 GB total (photos)
- GitHub free: 1 GB repository size limit
- **Conclusion**: GitHub suitable for 1-2 years, then need alternative

### Solutions for Scale

1. **Use Git LFS** (Large File Storage): $5/month for 50GB
2. **Switch to Cloudinary**: Free 25GB
3. **Use Supabase**: $25/month for 100GB
4. **Imgur**: Free but less professional

## 🔐 Security & Privacy

### Considerations

- Photos may include people (need consent)
- GPS coordinates in EXIF (should strip)
- Exact tree locations (already public)
- Vandalism risk (location data is public anyway)

### Mitigations

1. **Strip EXIF data**: Remove GPS/camera info from uploads
2. **Photo review**: Moderate before publishing
3. **Watermark**: Add subtle watermark to discourage misuse
4. **Terms**: Require uploader consent/agreement
5. **Backup**: Keep archive of all photos

## 📱 Mobile Upload Workflow

### Field Collection

1. **Navigate to tree** using main map
2. **Click "Upload Photo"** in popup
3. **Take photo** with camera or choose from gallery
4. **Add description** (optional)
5. **Enter name/email**
6. **Confirm tree ID** (auto-filled)
7. **Upload**
8. **Photo appears** in gallery within seconds

### Offline Support

- Use Service Worker to cache photos
- Upload when connection restored
- Show pending uploads queue

## 🧪 Testing Plan

### Browser Testing

- ✅ Chrome (desktop, mobile)
- ✅ Firefox (desktop, mobile)
- ✅ Safari (desktop, iOS)
- ✅ Edge (desktop)

### Device Testing

- ✅ iPhone (camera, gallery access)
- ✅ Android (camera, gallery access)
- ✅ iPad/Tablet
- ✅ Desktop

### Feature Testing

- ✅ Photo upload (various sizes, formats)
- ✅ Thumbnail generation
- ✅ Gallery navigation
- ✅ Modal interactions
- ✅ Mobile responsiveness
- ✅ Performance (100+ photos)

## 📊 Success Metrics

### MVP Goals (Phase 1)

- [ ] 10+ trees with photos
- [ ] Photo gallery functional
- [ ] Manual upload workflow documented
- [ ] 3+ organizations using feature

### Full Launch (Phase 3)

- [ ] 50+ trees with photos
- [ ] Average 3+ photos per tree
- [ ] Mobile upload working
- [ ] Time-lapse feature complete
- [ ] User feedback: 4+/5 stars

## 🚀 Go-Live Checklist

Before enabling photo features:

- [ ] Storage solution selected & configured
- [ ] Upload tool tested on mobile
- [ ] Photo gallery UI complete
- [ ] Documentation written
- [ ] User guide created
- [ ] Terms of use drafted
- [ ] Backup system in place
- [ ] Moderation process defined
- [ ] Test with 5 sample trees
- [ ] Organization training completed

---

## 🎬 Next Steps (When Approved)

1. **Review this plan** with stakeholders
2. **Choose storage solution** (recommend GitHub MVP)
3. **Create sample photo gallery** (10 trees)
4. **Test with one organization**
5. **Iterate based on feedback**
6. **Full rollout** to all trees

## 📞 Questions to Answer

Before implementation:

1. **Budget**: Any budget for paid services? ($0-25/month options)
2. **Timeline**: When do you need photos live? (MVP = 1 week, Full = 1 month)
3. **Upload**: Who should upload? (Orgs only, or public contributions?)
4. **Moderation**: Review photos before publishing?
5. **Storage**: Comfort with GitHub or prefer hosted service?

---

**⚠️ IMPLEMENTATION PAUSED**

**Status**: Plan complete, ready for review
**Next**: User approval to proceed
**Estimated Start**: After save/review
**Estimated MVP**: 1 week from start
