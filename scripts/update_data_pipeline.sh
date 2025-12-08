#!/bin/bash
# NYC American Chestnut Map - Data Update Pipeline
#
# This script updates the map data by:
# 1. Fetching fresh data from ArcGIS (PRIMARY source)
# 2. Enhancing with Excel growth history (SUPPLEMENT)
#
# Usage:
#   ./scripts/update_data_pipeline.sh
#   ./scripts/update_data_pipeline.sh --excel "archive/2025_survey.xlsx"

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ARCGIS_URL="https://services6.arcgis.com/3g7BMIrmSPKyPLSM/arcgis/rest/services/AmericanChestnuts/FeatureServer/0"
EXCEL_FILE="${1:-archive/2024 year end chestnut results.xlsx}"
ARCGIS_OUTPUT="data/trees_arcgis_fresh.json"
FINAL_OUTPUT="data/trees.json"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  NYC American Chestnut Map - Data Update Pipeline${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q requests openpyxl
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    source venv/bin/activate
fi

echo ""
echo -e "${BLUE}STEP 1: Fetching fresh data from ArcGIS (PRIMARY)${NC}"
echo "  Source: ArcGIS Feature Service"
echo "  URL: $ARCGIS_URL"
echo ""

python3 scripts/import_from_arcgis.py \
    --url "$ARCGIS_URL" \
    --output "$ARCGIS_OUTPUT"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}✗ Failed to fetch ArcGIS data${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}STEP 2: Enhancing with Excel growth history (SUPPLEMENT)${NC}"
echo "  Excel file: $EXCEL_FILE"
echo ""

python3 scripts/enhance_arcgis_with_growth.py \
    --arcgis "$ARCGIS_OUTPUT" \
    --excel "$EXCEL_FILE" \
    --output "$FINAL_OUTPUT"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}✗ Failed to enhance data${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Data pipeline complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Output files:"
echo "  - $ARCGIS_OUTPUT (ArcGIS raw data)"
echo "  - $FINAL_OUTPUT (Enhanced data with growth history)"
echo ""
echo "Next steps:"
echo "  1. Open index.html in a browser to view the map"
echo "  2. Commit changes: git add $FINAL_OUTPUT && git commit -m 'Update tree data'"
echo ""
