# Git Branching Strategy

**Purpose**: Manage features independently, enable quick rollbacks, and maintain stable production

---

## 🌳 Branch Structure

```
main (production)
  ├── develop (integration/staging)
  │   ├── feature/photo-gallery
  │   ├── feature/growth-charts
  │   ├── feature/coordinate-accuracy
  │   ├── feature/gps-collection
  │   ├── feature/landuse-validation
  │   └── feature/arcgis-integration
  └── hotfix/* (emergency fixes)
```

---

## 📋 Branch Descriptions

### main
- **Purpose**: Production-ready code
- **Deploys to**: GitHub Pages (live site)
- **Protection**: Only merge from `develop` or `hotfix/*`
- **Rule**: Always stable, always deployable

### develop
- **Purpose**: Integration branch for testing features together
- **Merges from**: Feature branches
- **Merges to**: `main` (after testing)
- **Use**: Test multiple features together before production

### feature/* (Feature Branches)

#### feature/photo-gallery
- **Contains**: Photo upload, gallery modal, Supabase integration
- **Files**:
  - `tools/photo_upload.html`
  - `photos/metadata.json`
  - `config/supabase-config.js`
  - Photo-related code in `index.html`
  - `docs/SUPABASE_SETUP.md`
  - `docs/PHOTO_UPLOAD_WORKFLOW.md`

#### feature/growth-charts
- **Contains**: Interactive Chart.js growth visualizations
- **Files**:
  - Growth chart code in `index.html`
  - `docs/GROWTH_CHARTS_ADDED.md`

#### feature/coordinate-accuracy
- **Contains**: 4-tier accuracy system, park boundary validation
- **Files**:
  - `scripts/park_boundaries.py`
  - `scripts/build_trees_with_accuracy.py`
  - Accuracy badge code in `index.html`
  - `docs/COORDINATE_ACCURACY_SYSTEM.md`

#### feature/gps-collection
- **Contains**: Mobile GPS collector tool
- **Files**:
  - `tools/coordinate_collector.html`
  - `scripts/update_confirmed_coordinates.py`
  - `docs/GPS_COLLECTION_GUIDE.md`

#### feature/landuse-validation
- **Contains**: OpenStreetMap landuse validation
- **Files**:
  - `scripts/build_with_landuse_validation.py`
  - `tools/landuse_validator.py`
  - `docs/LANDUSE_VALIDATION.md`

#### feature/arcgis-integration
- **Contains**: ArcGIS data import and sync (NEW)
- **Files**: (To be created)
  - `scripts/import_from_arcgis.py`
  - `docs/ARCGIS_INTEGRATION.md`

### hotfix/*
- **Purpose**: Emergency production fixes
- **Naming**: `hotfix/issue-description`
- **Merges to**: Both `main` AND `develop`
- **Example**: `hotfix/fix-missing-trees`

---

## 🔄 Workflows

### Adding a New Feature

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/new-feature-name

# 2. Develop the feature
# ... make changes ...

# 3. Commit regularly
git add .
git commit -m "Add feature: description"

# 4. Push to remote
git push origin feature/new-feature-name

# 5. Test locally
python3 -m http.server 8000

# 6. When ready, merge to develop for integration testing
git checkout develop
git merge feature/new-feature-name

# 7. Test in develop
# ... verify works with other features ...

# 8. When stable, merge to main
git checkout main
git merge develop
git push origin main
```

### Updating an Existing Feature

```bash
# 1. Switch to feature branch
git checkout feature/photo-gallery

# 2. Make changes
# ... edit files ...

# 3. Commit
git add .
git commit -m "Update photo gallery: add time-lapse view"

# 4. Push
git push origin feature/photo-gallery

# 5. Merge to develop for testing
git checkout develop
git merge feature/photo-gallery

# 6. Deploy to main when ready
git checkout main
git merge develop
git push origin main
```

### Temporarily Removing a Feature

```bash
# Option A: Revert to main without feature
git checkout main
git checkout -b main-without-photos
# ... deploy this branch instead ...

# Option B: Cherry-pick other features to new branch
git checkout -b production-hotfix main
git cherry-pick <commit-hash-of-other-features>
```

### Emergency Hotfix

```bash
# 1. Create hotfix from main
git checkout main
git checkout -b hotfix/fix-map-crash

# 2. Fix the issue
# ... make minimal changes ...

# 3. Commit
git add .
git commit -m "Hotfix: fix map crash on marker click"

# 4. Merge to main
git checkout main
git merge hotfix/fix-map-crash
git push origin main

# 5. ALSO merge to develop (important!)
git checkout develop
git merge hotfix/fix-map-crash

# 6. Delete hotfix branch
git branch -d hotfix/fix-map-crash
```

---

## 🎯 Best Practices

### Do's ✅
- **Commit often** with descriptive messages
- **Test locally** before merging to develop
- **Merge to develop** before merging to main
- **Keep features isolated** in their branches
- **Document changes** in feature branch commits
- **Push feature branches** to remote for backup

### Don'ts ❌
- **Don't work directly on main** (except hotfixes)
- **Don't merge untested code** to main
- **Don't mix features** in one branch
- **Don't delete feature branches** (keep them for future updates)
- **Don't force push** to main or develop
- **Don't skip the develop** integration step

---

## 📊 Deployment Strategy

### Development Testing
```bash
# Test on feature branch
git checkout feature/photo-gallery
python3 -m http.server 8000
# Visit http://localhost:8000
```

### Integration Testing
```bash
# Test multiple features together
git checkout develop
python3 -m http.server 8000
# Visit http://localhost:8000
```

### Production Deployment
```bash
# Deploy to GitHub Pages
git checkout main
git merge develop
git push origin main
# Wait 2-3 minutes for GitHub Actions
# Visit https://bondlegend4.github.io/nyc-american-chestnut-map-2025/
```

---

## 🔧 Managing Feature Toggles

If you need to disable a feature without removing the branch:

### Method 1: Feature Flag in Code

Add to `index.html`:
```javascript
const FEATURE_FLAGS = {
  photoGallery: true,      // Toggle photo features
  growthCharts: true,      // Toggle growth charts
  landUseValidation: false // Temporarily disable
};

// Use throughout code
if (FEATURE_FLAGS.photoGallery) {
  // Show photo gallery
}
```

### Method 2: Conditional Loading

```javascript
// Load photo features only if enabled
if (FEATURE_FLAGS.photoGallery) {
  document.write('<script src="config/supabase-config.js"></script>');
}
```

### Method 3: Separate Deployment Branches

```bash
# Create production branch without specific feature
git checkout -b production-stable main
git revert <photo-feature-commit>
git push origin production-stable

# Deploy production-stable instead of main
```

---

## 🚀 Quick Reference

### Common Commands

```bash
# List all branches
git branch --list

# Switch branches
git checkout branch-name

# Create and switch to new branch
git checkout -b feature/new-feature

# See which branch you're on
git branch

# Merge feature to develop
git checkout develop
git merge feature/feature-name

# Push branch to remote
git push origin branch-name

# Pull latest changes
git pull origin branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name
```

---

## 📁 Current Feature Mapping

### Photo Gallery (feature/photo-gallery)
**Status**: ✅ Complete, ready to isolate
**Key Files**:
- `tools/photo_upload.html`
- `photos/metadata.json`, `photos/README.md`
- `config/supabase-config.js`
- Photo code in `index.html` (lines 291-460, 548-687, 733-756)
- `docs/SUPABASE_SETUP.md`, `docs/PHOTO_UPLOAD_WORKFLOW.md`

**To isolate** (if needed):
```bash
git checkout feature/photo-gallery
# Remove photo-related code from index.html
# Remove tools/photo_upload.html
# Push to feature branch only, don't merge to main
```

### Growth Charts (feature/growth-charts)
**Status**: ✅ Complete
**Key Files**:
- Growth chart code in `index.html` (lines 388-526)
- Chart.js library reference
- `docs/GROWTH_CHARTS_ADDED.md`

### Coordinate Accuracy (feature/coordinate-accuracy)
**Status**: ✅ Complete
**Key Files**:
- `scripts/park_boundaries.py`
- `scripts/build_trees_with_accuracy.py`
- Accuracy badge code in `index.html`
- `docs/COORDINATE_ACCURACY_SYSTEM.md`

---

## 🆘 Troubleshooting

### "Merge conflict" Error

```bash
# 1. Open conflicted files
# Look for <<<<<<< HEAD markers

# 2. Resolve conflicts manually
# Edit files to keep desired changes

# 3. Stage resolved files
git add resolved-file.html

# 4. Complete merge
git commit -m "Resolve merge conflict"
```

### Accidentally Committed to Wrong Branch

```bash
# 1. Copy commit hash
git log  # Find the commit hash

# 2. Switch to correct branch
git checkout correct-branch

# 3. Cherry-pick the commit
git cherry-pick <commit-hash>

# 4. Remove from wrong branch
git checkout wrong-branch
git reset --hard HEAD~1
```

### Need to Undo Last Commit

```bash
# Undo commit but keep changes
git reset --soft HEAD~1

# Undo commit and discard changes
git reset --hard HEAD~1
```

---

## 📅 Branch Lifecycle

### Feature Branch Lifecycle
1. **Create** from `main`
2. **Develop** feature in isolation
3. **Test** locally
4. **Merge** to `develop` for integration testing
5. **Deploy** to `main` when stable
6. **Keep** branch for future updates (don't delete)

### When to Delete Branches
- Hotfix branches (after merging to both main and develop)
- Experimental branches that won't be used
- Duplicate branches

### When to Keep Branches
- All feature branches (for future updates)
- `develop` (always keep)
- `main` (always keep)

---

## 🎓 Learning Resources

- **Git Branching**: https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
- **Feature Branch Workflow**: https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow
- **Git Flow**: https://nvie.com/posts/a-successful-git-branching-model/

---

**Last Updated**: December 6, 2024
**Version**: 1.0
