# IWC Workflow Recommender Skill

A skill for recommending appropriate IWC (Intergalactic Workflow Commission) Galaxy workflows for genomic data analysis.

## Overview

This skill enables Claude to:
- Search the IWC Galaxy workflow catalog
- Match workflows to organisms and analysis types
- Recommend workflows based on data characteristics (single/paired-end, platform, etc.)
- Provide TRS IDs for easy workflow import into Galaxy
- **ALWAYS recommend existing workflows** rather than writing custom analysis code

## Philosophy

Following the principle: **"ALWAYS recommend existing IWC workflows instead of writing custom code."**

This skill doesn't generate analysis scripts or step-by-step instructions. Instead, it:
1. Searches the vetted IWC workflow catalog
2. Interprets workflow descriptions to match user needs
3. Recommends appropriate workflows with justification
4. Provides TRS IDs for importing into Galaxy

## Files

```
iwc-workflow-recommender/
├── SKILL.md                  # Main skill instructions (read by Claude)
├── search_iwc_workflows.py   # IWC workflow catalog search client
├── README.md                 # This file (documentation)
├── VERSION                   # Current version number
├── test_skill.sh             # Automated test suite
└── build.sh                  # Build script for packaging
```

## Requirements

### Network Access
This skill requires network access to:
- `iwc.galaxyproject.org` (IWC Workflow Manifest)

**Important**: Add this domain to your Claude environment's network allowlist. Without this, the skill will fail with network errors.

### Python
- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Installation

### For Claude Code
1. Copy the `iwc-workflow-recommender` folder to:
   - `~/.claude/skills/` (personal skills), or
   - `.claude/skills/` in your project (project-specific skills)
2. Claude will automatically discover it

### For Claude.ai
1. Run `./build.sh` to create the deployment package
2. Go to Settings → Features → Skills
3. Upload the generated `iwc-workflow-recommender.zip` file

## Usage Examples

Once installed, Claude will automatically use this skill when appropriate. You don't need to explicitly invoke it.

### Example 1: RNA-seq Analysis
**You:** "I need to analyze Plasmodium falciparum RNA-seq data"

**Claude:** [Uses search_iwc_workflows.py with --category Transcriptomics]
> I found 3 relevant RNA-seq workflows for eukaryotic organisms. The "RNA-seq analysis with preprocessing" workflow is well-suited for P. falciparum...
> [Provides TRS ID and import instructions]

### Example 2: Variant Calling
**You:** "What workflows are available for viral variant calling?"

**Claude:** [Uses search_iwc_workflows.py with --category "Variant Calling"]
> I found several variant calling workflows optimized for viral genomes, including SARS-CoV-2 specific workflows...

### Example 3: Browse Categories
**You:** "What types of workflows are available?"

**Claude:** [Uses search_iwc_workflows.py --list-categories]
> The IWC catalog includes workflows for: Variant Calling, Transcriptomics, Genome assembly, Virology, Epigenetics, Microbiome, Proteomics...

## Testing the Skill

Run the test script to verify everything works:

```bash
cd iwc-workflow-recommender
bash test_skill.sh
```

Or test components individually:

```bash
# List available categories
python search_iwc_workflows.py --list-categories

# Search specific category
python search_iwc_workflows.py --category "Variant Calling"

# Limit results
python search_iwc_workflows.py --category "Transcriptomics" --limit 5

# Get JSON output
python search_iwc_workflows.py --format json
```

## Key Design Decisions

### 1. No Code Generation
The skill strictly prohibits writing custom analysis code. The IWC catalog contains hundreds of vetted, production-ready workflows - our job is to find and recommend the right ones.

### 2. Interpretation Over Automation
The skill returns workflow metadata (descriptions, tags, categories) but **Claude must interpret** which workflows match the user's organism, analysis type, and data characteristics.

### 3. Data Compatibility Checking
Claude checks workflow requirements against user's data:
- Single vs paired-end reads
- Sequencing platform compatibility
- Organism domain (bacterial, viral, eukaryotic)
- Read length requirements

### 4. Honest Limitations
If IWC doesn't have a workflow for a specific use case, the skill acknowledges that rather than falling back to code generation.

## Troubleshooting

### Network Errors
**Error:** `Network error: <urlopen error...>`

**Solution:** Add `iwc.galaxyproject.org` to your network allowlist

### No Relevant Workflows Found
**Problem:** Search returns workflows but none match the user's needs

**Solution:**
- Try broader category searches
- Visit iwc.galaxyproject.org to browse the full catalog
- Check if a related analysis type has applicable workflows

### Script Permission Errors
**Error:** `Permission denied` when running scripts

**Solution:** Make scripts executable:
```bash
chmod +x search_iwc_workflows.py test_skill.sh
```

## API Documentation

### IWC Workflow Manifest
- Manifest URL: `https://iwc.galaxyproject.org/workflow_manifest.json`
- Contains metadata for all IWC workflows including names, descriptions, categories, tags, and TRS IDs
- Updated regularly as new workflows are added

## Contributing

This skill follows the pattern established in the Anthropic skills repository. To contribute:

1. Test your changes thoroughly
2. Update documentation
3. Follow the existing code style
4. Keep the skill focused on its core purpose

## License

Apache 2.0 (following the Anthropic skills repository convention)

## Related Resources

- [IWC Workflow Catalog](https://iwc.galaxyproject.org)
- [Galaxy Project](https://galaxyproject.org)
- [Anthropic Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
