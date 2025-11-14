# Genomic Data Skills for Claude

This repository contains two complementary Claude skills for working with genomic data:

## Skills

### 🧬 [taxonomy-resolver](./taxonomy-resolver/)
**Purpose:** Find and identify genomic data

Resolves organism names to NCBI taxonomy IDs, searches ENA for genomic data (FASTQ, assemblies), and retrieves BioProject details.

**Key features:**
- Convert common names to scientific names with disambiguation
- Search NCBI Taxonomy API for validation
- Find FASTQ files, assemblies, and other data in ENA
- Group results by BioProject with technical details
- Intent-based filtering (RNA-Seq, WGS, ChIP-Seq, etc.)

**APIs used:** NCBI Taxonomy, ENA (European Nucleotide Archive)

### 🔬 [iwc-workflow-recommender](./iwc-workflow-recommender/)
**Purpose:** Recommend Galaxy workflows for analysis

Searches the IWC (Intergalactic Workflow Commission) workflow catalog and recommends appropriate workflows for genomic analysis.

**Key features:**
- Search IWC workflow catalog by category
- Match workflows to organisms and data types
- Check data compatibility (single/paired-end, platform, etc.)
- Provide TRS IDs for importing into Galaxy
- **ALWAYS recommends existing workflows** (never writes custom code)

**APIs used:** IWC Workflow Manifest

## Repository Structure

```
taxonomy-resolver/          (the repository)
├── taxonomy-resolver/      (skill: data discovery)
│   ├── resolve_taxonomy.py
│   ├── search_ena.py
│   ├── get_bioproject_details.py
│   ├── SKILL.md
│   ├── README.md
│   └── ...
├── iwc-workflow-recommender/  (skill: workflow recommendation)
│   ├── search_iwc_workflows.py
│   ├── SKILL.md
│   ├── README.md
│   └── ...
├── CLAUDE.md               (project-level guidance for Claude Code)
└── README.md               (this file)
```

## Installation

### For Claude Code
Copy both skill directories to your Claude skills folder:
```bash
cp -r taxonomy-resolver ~/.claude/skills/
cp -r iwc-workflow-recommender ~/.claude/skills/
```

### For Claude.ai
Build each skill separately:
```bash
cd taxonomy-resolver && ./build.sh
cd ../iwc-workflow-recommender && ./build.sh
```
Then upload the generated ZIP files to Claude.ai (Settings → Features → Skills).

## Testing

Each skill has its own test suite:
```bash
# Test taxonomy-resolver
cd taxonomy-resolver && bash test_skill.sh

# Test iwc-workflow-recommender
cd iwc-workflow-recommender && bash test_skill.sh
```

## Network Requirements

Both skills require network access. Add these domains to your Claude environment's allowlist:

**taxonomy-resolver:**
- `api.ncbi.nlm.nih.gov`
- `www.ebi.ac.uk`

**iwc-workflow-recommender:**
- `iwc.galaxyproject.org`

## Philosophy

Both skills follow the principle: **"Let the APIs do the work, Claude just orchestrates."**

- **No data invention:** Always defer to external APIs for authoritative information
- **No code generation:** The IWC workflow recommender strictly prohibits writing custom analysis scripts
- **Disambiguation first:** Never pass ambiguous inputs to APIs without clarification
- **Focused responsibilities:** Each skill has one clear purpose

## Workflow Example

A typical user interaction might use both skills:

1. **taxonomy-resolver**: "Find RNA-seq data for *Plasmodium falciparum*"
   - Resolves organism name to taxonomy ID
   - Searches ENA with RNA-Seq filter
   - Returns BioProjects grouped by study with technical details

2. **iwc-workflow-recommender**: "What workflows can I use for this data?"
   - Searches IWC catalog for Transcriptomics workflows
   - Matches workflows to eukaryotic parasites
   - Checks compatibility with paired-end Illumina data
   - Recommends appropriate workflows with TRS IDs

## License

Apache 2.0

## Related Resources

- [NCBI Taxonomy Database](https://www.ncbi.nlm.nih.gov/taxonomy)
- [ENA (European Nucleotide Archive)](https://www.ebi.ac.uk/ena)
- [IWC Workflow Catalog](https://iwc.galaxyproject.org)
- [Galaxy Project](https://galaxyproject.org)
- [Anthropic Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
