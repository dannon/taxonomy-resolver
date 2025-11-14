#!/bin/bash
# Test script for the iwc-workflow-recommender skill

set -e

echo "======================================"
echo "IWC Workflow Recommender - Test Suite"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Test 1: List workflow categories
echo "Test 1: List workflow categories"
echo "--------------------------------------"
if python3 search_iwc_workflows.py --list-categories 2>/dev/null; then
    echo "✓ Test 1 passed"
else
    echo "❌ Test 1 failed (Network access may not be configured)"
fi
echo ""

# Test 2: Search workflows by category
echo "Test 2: Search by category (Variant Calling, limit 3)"
echo "--------------------------------------"
if python3 search_iwc_workflows.py --category "Variant Calling" --limit 3 2>/dev/null; then
    echo "✓ Test 2 passed"
else
    echo "❌ Test 2 failed (Network access may not be configured)"
fi
echo ""

# Test 3: Search workflows by different category
echo "Test 3: Search by category (Transcriptomics, limit 5)"
echo "--------------------------------------"
if python3 search_iwc_workflows.py --category "Transcriptomics" --limit 5 2>/dev/null; then
    echo "✓ Test 3 passed"
else
    echo "❌ Test 3 failed (Network access may not be configured)"
fi
echo ""

# Test 4: JSON output format
echo "Test 4: JSON output format (Virology category)"
echo "--------------------------------------"
if python3 search_iwc_workflows.py --category "Virology" --format json --limit 2 2>/dev/null; then
    echo "✓ Test 4 passed"
else
    echo "❌ Test 4 failed (Network access may not be configured)"
fi
echo ""

# Test 5: Fetch all workflows (no category filter)
echo "Test 5: Fetch all workflows (no category filter, limit 10)"
echo "--------------------------------------"
if python3 search_iwc_workflows.py --limit 10 2>/dev/null; then
    echo "✓ Test 5 passed"
else
    echo "❌ Test 5 failed (Network access may not be configured)"
fi
echo ""

echo "======================================"
echo "Test Suite Complete"
echo "======================================"
echo ""
echo "Note: If tests failed with network errors, ensure this domain is allowlisted:"
echo "  - iwc.galaxyproject.org"
echo ""
echo "Add this to your Claude environment's network settings."
