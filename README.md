# Taxonomy Resolver Skill

A Claude skill for resolving organism names to NCBI taxonomy IDs and searching for genomic data in ENA (European Nucleotide Archive).

## Overview

This skill enables Claude to:
- Convert common names to scientific names (e.g., "malaria parasite" → "Plasmodium falciparum")
- Resolve scientific names to NCBI taxonomy IDs
- Validate taxonomy IDs and retrieve organism information
- Search ENA for FASTQ files and other genomic data
- Handle disambiguation through natural conversation

## Philosophy

Following the principle: **"Let the APIs do the work, Claude just orchestrates."**

This skill doesn't try to teach Claude everything about taxonomy. Instead, it provides:
1. Clear guidance on when to ask for clarification
2. Scripts that call external APIs
3. Instructions for handling API responses

All validation and data accuracy is handled by NCBI and ENA.

## Files

```
taxonomy-resolver/
├── SKILL.md              # Main skill instructions (read by Claude)
├── resolve_taxonomy.py   # NCBI Taxonomy API client
├── search_ena.py        # ENA search API client
├── README.md            # This file (documentation)
└── test_skill.sh        # Test script
```

## Requirements

### Network Access
This skill requires network access to:
- `api.ncbi.nlm.nih.gov` (NCBI Taxonomy API)
- `www.ebi.ac.uk` (ENA API)

**Important**: Add these domains to your Claude environment's network allowlist. Without this, the skill will fail with network errors.

### Python
- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Installation

### For Claude.ai
1. Zip the `taxonomy-resolver` folder
2. Go to Settings → Features → Skills
3. Upload the zip file

### For Claude Code
1. Copy the `taxonomy-resolver` folder to:
   - `~/.claude/skills/` (personal skills), or
   - `.claude/skills/` in your project (project-specific skills)
2. Claude will automatically discover it

### For Claude API
Use the Skills API to upload:
```python
import anthropic
from pathlib import Path

client = anthropic.Anthropic()

# Create a zip of the skill
import zipfile
with zipfile.ZipFile('taxonomy-resolver.zip', 'w') as zf:
    for file in Path('taxonomy-resolver').rglob('*'):
        if file.is_file():
            zf.write(file, file.relative_to('taxonomy-resolver'))

# Upload the skill
with open('taxonomy-resolver.zip', 'rb') as f:
    skill = client.skills.create(
        name='taxonomy-resolver',
        description='Resolve taxonomy names and search genomic databases',
        file=f
    )
```

## Usage Examples

Once installed, Claude will automatically use this skill when appropriate. You don't need to explicitly invoke it.

### Example 1: Simple Taxonomy Lookup
**You:** "What's the taxonomy ID for house mouse?"

**Claude:** [Uses resolve_taxonomy.py]
> The taxonomy ID for house mouse (Mus musculus) is 10090.

### Example 2: Disambiguation Flow
**You:** "Find FASTQ files for malaria parasite"

**Claude:** 
> Which malaria parasite are you interested in? The main ones are:
> - Plasmodium falciparum (most common, causes severe malaria)
> - Plasmodium vivax (widespread, relapses common)
> - Plasmodium malariae
> - Plasmodium ovale

**You:** "P. falciparum"

**Claude:** [Uses resolve_taxonomy.py, then search_ena.py]
> Found 1,247 FASTQ datasets for Plasmodium falciparum (taxonomy ID: 5833).
> [Shows top results with accession numbers and metadata]

### Example 3: Strain-Specific Search
**You:** "Search for E. coli K-12 genome assemblies"

**Claude:** [Uses resolve_taxonomy.py with "Escherichia coli K-12", then search_ena.py with --data-type assembly]
> [Returns assembly accessions and metadata]

## Testing the Skill

Run the test script to verify everything works:

```bash
cd taxonomy-resolver
bash test_skill.sh
```

Or test components individually:

```bash
# Test taxonomy resolution
python resolve_taxonomy.py "Homo sapiens"
python resolve_taxonomy.py --tax-id 9606

# Test with detailed lineage
python resolve_taxonomy.py "Plasmodium falciparum" --detailed

# Test ENA search
python search_ena.py "Saccharomyces cerevisiae" --data-type fastq --limit 5

# Test with JSON output
python resolve_taxonomy.py "Mus musculus" --format json
python search_ena.py "Escherichia coli" --format json
```

## Key Design Decisions

### 1. Disambiguation First
The skill emphasizes asking for clarification before making API calls. Common names like "malaria parasite" or "E. coli" are ambiguous and should trigger a disambiguation question.

### 2. API-Driven Validation
The skill never tries to validate taxonomy on its own. It always defers to NCBI's API for authoritative data.

### 3. Conversational Clarity
The skill instructs Claude to be conversational and helpful with disambiguation, not robotic or pedantic.

### 4. Error Transparency
When APIs fail, the skill reports errors clearly and suggests solutions (like enabling network domains).

## Troubleshooting

### Network Errors
**Error:** `Network error: <urlopen error [Errno -3] Temporary failure in name resolution>`

**Solution:** Add the required domains to your network allowlist:
- `api.ncbi.nlm.nih.gov`
- `www.ebi.ac.uk`

### No Results Found
**Problem:** Search returns zero results for a valid organism

**Possible causes:**
1. The name spelling is incorrect (try variations)
2. The organism is not in the database
3. The search query is too specific (try genus-level instead of strain)

**Solution:** Try broader searches or alternative spellings

### Script Permission Errors
**Error:** `Permission denied` when running scripts

**Solution:** Make scripts executable:
```bash
chmod +x resolve_taxonomy.py search_ena.py test_skill.sh
```

## API Documentation

### NCBI Taxonomy API
- Base URL: `https://api.ncbi.nlm.nih.gov/datasets/v2/`
- Docs: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/

### ENA API
- Base URL: `https://www.ebi.ac.uk/ena/portal/api/`
- Docs: https://www.ebi.ac.uk/ena/browser/api/

## Contributing

This skill follows the pattern established in the Anthropic skills repository. To contribute:

1. Test your changes thoroughly
2. Update documentation
3. Follow the existing code style
4. Keep the skill focused on its core purpose

## License

Apache 2.0 (following the Anthropic skills repository convention)

## Acknowledgments

Developed based on requirements from Dave Rogers and Danielle Callan for the BRC codeathon project, emphasizing:
- Letting APIs handle validation
- Keeping Claude's role focused on orchestration
- Making disambiguation conversational and user-friendly

## Related Resources

- [NCBI Taxonomy Database](https://www.ncbi.nlm.nih.gov/taxonomy)
- [ENA (European Nucleotide Archive)](https://www.ebi.ac.uk/ena)
- [Anthropic Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Skills GitHub Repository](https://github.com/anthropics/skills)
