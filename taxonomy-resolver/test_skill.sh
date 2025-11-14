#!/bin/bash
# Test script for the taxonomy-resolver skill

set -e

echo "======================================"
echo "Taxonomy Resolver Skill - Test Suite"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Test 1: Taxonomy resolution by name
echo "Test 1: Resolve taxonomy by name (Homo sapiens)"
echo "--------------------------------------"
if python3 resolve_taxonomy.py "Homo sapiens" 2>/dev/null; then
    echo "✓ Test 1 passed"
else
    echo "❌ Test 1 failed (Network access may not be configured)"
fi
echo ""

# Test 2: Taxonomy resolution by ID
echo "Test 2: Resolve taxonomy by ID (9606 = Homo sapiens)"
echo "--------------------------------------"
if python3 resolve_taxonomy.py --tax-id 9606 2>/dev/null; then
    echo "✓ Test 2 passed"
else
    echo "❌ Test 2 failed (Network access may not be configured)"
fi
echo ""

# Test 3: Detailed taxonomy with lineage
echo "Test 3: Detailed taxonomy with lineage (Mus musculus)"
echo "--------------------------------------"
if python3 resolve_taxonomy.py "Mus musculus" --detailed 2>/dev/null; then
    echo "✓ Test 3 passed"
else
    echo "❌ Test 3 failed (Network access may not be configured)"
fi
echo ""

# Test 4: JSON output format
echo "Test 4: JSON output format (Escherichia coli)"
echo "--------------------------------------"
if python3 resolve_taxonomy.py "Escherichia coli" --format json 2>/dev/null; then
    echo "✓ Test 4 passed"
else
    echo "❌ Test 4 failed (Network access may not be configured)"
fi
echo ""

# Test 5: ENA search for FASTQ
echo "Test 5: ENA search for FASTQ files (Saccharomyces cerevisiae, limit 5)"
echo "--------------------------------------"
if python3 search_ena.py "Saccharomyces cerevisiae" --data-type fastq --limit 5 2>/dev/null; then
    echo "✓ Test 5 passed"
else
    echo "❌ Test 5 failed (Network access may not be configured)"
fi
echo ""

# Test 6: ENA search for assemblies
echo "Test 6: ENA search for assemblies (Drosophila melanogaster, limit 3)"
echo "--------------------------------------"
if python3 search_ena.py "Drosophila melanogaster" --data-type assembly --limit 3 2>/dev/null; then
    echo "✓ Test 6 passed"
else
    echo "❌ Test 6 failed (Network access may not be configured)"
fi
echo ""

# Test 7: BioProject details lookup
echo "Test 7: BioProject details lookup (PRJDB7788)"
echo "--------------------------------------"
if python3 get_bioproject_details.py PRJDB7788 2>/dev/null; then
    echo "✓ Test 7 passed"
else
    echo "❌ Test 7 failed (Network access may not be configured)"
fi
echo ""

# Test 8: Invalid taxonomy query (should fail gracefully)
echo "Test 8: Invalid taxonomy query (should fail gracefully)"
echo "--------------------------------------"
if python3 resolve_taxonomy.py "ThisOrganismDoesNotExist12345" 2>/dev/null; then
    echo "⚠ Test 8: Script should have failed but didn't"
else
    echo "✓ Test 8 passed (failed gracefully as expected)"
fi
echo ""

echo "======================================"
echo "Test Suite Complete"
echo "======================================"
echo ""
echo "Note: If tests failed with network errors, ensure these domains are allowlisted:"
echo "  - api.ncbi.nlm.nih.gov"
echo "  - www.ebi.ac.uk"
echo ""
echo "Add these to your Claude environment's network settings."
