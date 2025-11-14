#!/bin/bash
# Build script for taxonomy-resolver skill
# Creates a deployment-ready zip package

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_NAME="taxonomy-resolver"
ZIP_FILE="$SCRIPT_DIR/${SKILL_NAME}.zip"

echo "======================================"
echo "Building Taxonomy Resolver Skill"
echo "======================================"
echo ""

# Remove old zip if it exists
if [ -f "$ZIP_FILE" ]; then
    echo "Removing old zip file..."
    rm "$ZIP_FILE"
fi

# Create zip from parent directory
echo "Creating new zip file..."
cd "$PARENT_DIR"

zip -r "${SKILL_NAME}/${SKILL_NAME}.zip" "${SKILL_NAME}/" \
    -x "${SKILL_NAME}/.git/*" \
    -x "${SKILL_NAME}/.git" \
    -x "${SKILL_NAME}/.claude/*" \
    -x "${SKILL_NAME}/.claude" \
    -x "${SKILL_NAME}/__pycache__/*" \
    -x "${SKILL_NAME}/__pycache__" \
    -x "${SKILL_NAME}/DEPLOYMENT_GUIDE.md" \
    -x "${SKILL_NAME}/CLAUDE.md" \
    -x "${SKILL_NAME}/${SKILL_NAME}.zip" \
    -x "${SKILL_NAME}/build.sh" \
    -x "*.pyc" \
    -x ".DS_Store"

cd "$SCRIPT_DIR"

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
