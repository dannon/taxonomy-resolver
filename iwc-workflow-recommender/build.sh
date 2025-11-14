#!/bin/bash
# Build script for iwc-workflow-recommender skill
# Creates a deployment-ready zip package

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="iwc-workflow-recommender"
ZIP_FILE="$SCRIPT_DIR/${SKILL_NAME}.zip"

echo "======================================"
echo "Building IWC Workflow Recommender Skill"
echo "======================================"
echo ""

# Remove old zip if it exists
if [ -f "$ZIP_FILE" ]; then
    echo "Removing old zip file..."
    rm "$ZIP_FILE"
fi

# Create zip from current directory
echo "Creating new zip file..."
cd "$SCRIPT_DIR"

zip -r "${SKILL_NAME}.zip" . \
    -x ".git/*" \
    -x ".git" \
    -x "__pycache__/*" \
    -x "__pycache__" \
    -x "${SKILL_NAME}.zip" \
    -x "*.pyc" \
    -x ".DS_Store"

# Show what was included
echo ""
echo "Package contents:"
echo "--------------------------------------"
unzip -l "$ZIP_FILE"

echo ""
echo "======================================"
echo "Build complete!"
echo "======================================"
echo ""
echo "Output: $ZIP_FILE"
echo "Size: $(du -h "$ZIP_FILE" | cut -f1)"
echo ""
echo "Ready to upload to Claude.ai"
