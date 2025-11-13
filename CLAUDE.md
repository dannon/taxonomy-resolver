# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A Claude skill that resolves ambiguous organism names to precise NCBI taxonomy IDs and searches for genomic data in ENA (European Nucleotide Archive). The skill follows the principle: **"Let the APIs do the work, Claude just orchestrates."**

## Architecture

### Core Components

**resolve_taxonomy.py** - NCBI Taxonomy API client
- `NCBITaxonomyResolver` class handles all NCBI Taxonomy API interactions
- `search_by_name(organism_name)` - Searches NCBI for taxonomy by organism name
- `get_by_tax_id(tax_id)` - Retrieves taxonomy information by ID
- `_extract_lineage(lineage_data)` - Extracts simplified taxonomic lineage
- Returns structured data with taxonomy ID, scientific name, common name, rank, and lineage
- Base URL: `https://api.ncbi.nlm.nih.gov/datasets/v2/`

**search_ena.py** - ENA search API client
- `ENASearcher` class handles ENA (European Nucleotide Archive) queries
- `search(query, result_type, limit, offset, fields)` - Searches ENA for genomic data
- `get_fastq_urls(run_accession)` - Gets direct FASTQ download URLs for a run
- Supports multiple result types: read_run (FASTQ), assembly, wgs, sequence, study, sample, analysis
- Automatically groups read_run results by BioProject
- Base URL: `https://www.ebi.ac.uk/ena/portal/api`

**get_bioproject_details.py** - ENA BioProject metadata client
- `BioprojectDetailsFetcher` class handles BioProject (study) queries
- `get_details(bioproject_accession)` - Gets detailed information about a BioProject
- `get_multiple_details(accessions)` - Gets details for multiple BioProjects
- Returns study title, description, organism, center name, and dates
- Accepts both PRJEB (ENA) and PRJNA (NCBI) accessions
- Base URL: `https://www.ebi.ac.uk/ena/portal/api`

**search_iwc_workflows.py** - IWC workflow catalog search
- `IWCWorkflowSearcher` class handles IWC (Intergalactic Workflow Commission) workflow manifest queries
- `search(category, limit)` - Searches IWC workflows with optional category filter
- `list_categories()` - Lists all available workflow categories
- Returns workflow names, descriptions, TRS IDs, categories, tags, and creators
- Manifest URL: `https://iwc.galaxyproject.org/workflow_manifest.json`

**SKILL.md** - Main skill instructions (read by Claude)
- Defines when to use the skill and core workflows
- Critical disambiguation-first approach before calling APIs
- Example interactions and error handling patterns

### Design Philosophy

1. **API-Driven Validation**: Never try to validate or invent taxonomy data. Always defer to external APIs (NCBI, ENA) for authoritative information.

2. **Disambiguation First**: Never pass ambiguous names to APIs. Always disambiguate to species-level or specific taxa first through conversational clarification.

3. **No External Dependencies**: Both Python scripts use only the standard library (urllib, json, argparse) to maximize portability.

4. **Dual Output Formats**: All scripts support both human-readable and JSON output via `--format` flag.

## Common Commands

### Testing the Skill

```bash
# Run complete test suite
bash test_skill.sh

# Test individual components
python3 resolve_taxonomy.py "Homo sapiens"
python3 resolve_taxonomy.py --tax-id 9606
python3 resolve_taxonomy.py "Mus musculus" --detailed
python3 search_ena.py "Saccharomyces cerevisiae" --data-type fastq --limit 5
python3 get_bioproject_details.py PRJDB7788
python3 search_iwc_workflows.py --list-categories
python3 search_iwc_workflows.py --category "Variant Calling" --limit 3
```

### Script Usage Patterns

```bash
# Taxonomy resolution by name
python3 resolve_taxonomy.py "Plasmodium falciparum"
python3 resolve_taxonomy.py "Escherichia coli" --format json

# Taxonomy resolution by ID
python3 resolve_taxonomy.py --tax-id 5833

# Detailed lineage output
python3 resolve_taxonomy.py "Drosophila melanogaster" --detailed

# ENA searches
python3 search_ena.py "Mus musculus" --data-type fastq --limit 10
python3 search_ena.py "Arabidopsis thaliana" --data-type assembly
python3 search_ena.py "Homo sapiens" --format json --show-urls

# BioProject details
python3 get_bioproject_details.py PRJDB7788
python3 get_bioproject_details.py PRJNA123456 --format json
python3 get_bioproject_details.py PRJEB1234 PRJNA456789

# IWC workflow searches
python3 search_iwc_workflows.py --list-categories
python3 search_iwc_workflows.py --category "Variant Calling"
python3 search_iwc_workflows.py --category "Transcriptomics" --limit 10
python3 search_iwc_workflows.py --format json
```

### Deployment

```bash
# Rebuild the skill zip package (after making changes)
./build.sh

# Install for Claude Code (personal)
cp -r taxonomy-resolver ~/.claude/skills/

# Install for Claude Code (project-specific)
cp -r taxonomy-resolver ./.claude/skills/

# Make scripts executable (if needed)
chmod +x resolve_taxonomy.py search_ena.py test_skill.sh
```

## Network Requirements

⚠️ **Critical**: This skill requires network access to:
- `api.ncbi.nlm.nih.gov` (NCBI Taxonomy API)
- `www.ebi.ac.uk` (ENA API)
- `iwc.galaxyproject.org` (IWC Workflow Manifest)

These domains must be allowlisted in your Claude environment. Network errors indicate missing network permissions.

## Error Handling Patterns

All scripts follow consistent error handling:
- Network errors return `{'error': 'Network error: ...', 'suggestion': 'Check network settings...'}`
- API errors are caught and reported with actionable suggestions
- "No results found" indicates the query didn't match anything in the database
- All scripts exit with code 0 on success, 1 on error

## Key Implementation Details

### Taxonomy Resolution Flow
1. `search_by_name()` queries NCBI's taxon_suggest endpoint with the organism name
2. Takes the first (most relevant) result from `sci_name_and_ids`
3. Calls `get_by_tax_id()` with the returned taxonomy ID for detailed information
4. Returns structured data including scientific name, common name, rank, and full lineage

### ENA Search Flow
1. Constructs query URL with search parameters (query, result type, limit, offset, fields)
2. Default fields vary by result type (read_run, assembly, study, sample)
3. HTTP 204 responses indicate "no results found" (not an error condition)
4. FTP paths are converted to HTTPS URLs when `--show-urls` is used
5. For read_run searches, results are automatically grouped by BioProject (study_accession)

### BioProject Details Flow
1. Queries ENA's study endpoint with BioProject accession
2. Retrieves metadata including title, description, organism, center, and dates
3. Supports batch queries for multiple accessions
4. Accepts both PRJEB (ENA) and PRJNA (NCBI) accessions

### IWC Workflow Search Flow
1. Fetches the complete workflow manifest from iwc.galaxyproject.org
2. Extracts workflow metadata (name, description, TRS ID, categories, tags, creators)
3. Filters workflows without tests (considered incomplete)
4. Applies optional category filtering
5. Returns JSON with all workflow details for LLM interpretation

### Output Formatting
- `format_output()` functions in both scripts handle human-readable and JSON formats
- Human format shows key fields with clear labels
- JSON format returns complete API response data
- Long values are truncated in human format (>100 chars)
