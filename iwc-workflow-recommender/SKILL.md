---
name: iwc-workflow-recommender
description: Recommends appropriate IWC (Intergalactic Workflow Commission) Galaxy workflows for genomic analysis. Use this skill when users need to analyze genomic data - the skill searches the IWC workflow catalog and matches workflows to organisms, data characteristics, and analysis types. ALWAYS recommends existing IWC workflows rather than producing custom scripts or analysis steps.
---

# IWC Workflow Recommender Skill

## Purpose

This skill enables Claude to search the IWC (Intergalactic Workflow Commission) Galaxy workflow catalog and recommend appropriate workflows for genomic data analysis. **The core principle: ALWAYS recommend existing IWC workflows instead of writing code or producing custom analysis steps.** Claude's role is to search, interpret, and match workflows - NOT code generation.

## When to Use This Skill

Use this skill when:
- User wants to analyze genomic data (RNA-seq, variant calling, assembly, etc.)
- User asks "how do I analyze..." or "what workflow should I use for..."
- User needs workflow recommendations for any bioinformatics analysis
- User mentions specific analysis types (transcriptomics, variant calling, ChIP-seq, etc.)
- User has FASTQ files, assemblies, or other genomic data and wants to process them

## Core Workflow

### 1. Extract Analysis Intent (Critical)

**Before calling the API, understand what analysis the user wants.** Extract:
- **Analysis type**: RNA-seq, variant calling, genome assembly, ChIP-seq, metagenomics, etc.
- **Organism type** (if mentioned): bacterial, viral, eukaryotic, specific species
- **Data characteristics** (if known): single vs paired-end, sequencing platform, read length

**Examples of intent extraction:**
- "I want to analyze RNA-seq data" → Analysis: Transcriptomics
- "Find variant calling workflows for mouse" → Analysis: Variant calling, Organism: Mus musculus (eukaryotic)
- "How do I assemble a bacterial genome?" → Analysis: Genome assembly, Organism: bacterial

### 2. Search IWC Workflows

Use `search_iwc_workflows.py` with intent-based category filtering:
- For RNA-seq → Use `--category "Transcriptomics"`
- For variant calling → Use `--category "Variant Calling"`
- For genome assembly → Use `--category "Genome assembly"`
- For viral analysis → Use `--category "Virology"`
- For ChIP-seq/epigenetics → Use `--category "Epigenetics"`
- For metagenomics → Use `--category "Microbiome"` or `--category "Metabarcoding"`

The script returns workflows filtered by category. **It's YOUR job to:**
1. Read workflow names, descriptions, tags, and categories
2. Match workflows to the user's organism AND analysis intent
3. Match workflow requirements to data characteristics (if provided)
4. Explain why each suggested workflow is appropriate

### 3. Match Workflows to Requirements

**Critical: Match workflow data requirements to user's data:**
- Does the workflow require paired-end data? Check if user has PAIRED layout
- Does the workflow work with the sequencing platform? (Illumina, PacBio, Nanopore)
- Does the workflow need specific read lengths or quality?
- Are there organism-specific requirements? (reference genome availability, etc.)
- Does the workflow mention the organism's domain? (viral, bacterial, eukaryotic)

**Warn users about mismatches:**
- "This workflow requires paired-end data, but your dataset is single-end"
- "This workflow is optimized for bacterial genomes, but your organism is eukaryotic"

### 4. Present Recommendations

For each recommended workflow, provide:
- Workflow name and description
- TRS ID (for importing into Galaxy)
- Why it's appropriate for their organism/analysis
- Data compatibility notes
- Any caveats or requirements

## Important Principles

1. **ALWAYS recommend IWC workflows, NEVER write code**:
   - ✅ Recommend existing IWC workflows from the catalog
   - ✅ Explain why each workflow is appropriate
   - ✅ Provide TRS IDs for easy import into Galaxy
   - ❌ Write custom Python/R/bash scripts
   - ❌ Produce step-by-step command-line instructions
   - ❌ Generate custom analysis code
   - The IWC catalog contains vetted, production-ready workflows - use them!

2. **Use intent to filter searches**:
   - Add `--category` filters based on analysis type
   - This gives more relevant results and saves time

3. **YOU interpret the workflow descriptions**:
   - Read descriptions carefully to understand what each workflow does
   - Match to organisms based on domain keywords (viral, bacterial, eukaryotic)
   - Look for organism-specific mentions
   - Consider general applicability

4. **Match data characteristics**:
   - Check single vs paired-end requirements
   - Verify platform compatibility
   - Note read length requirements
   - Warn about incompatibilities

5. **Don't suggest workflows blindly**:
   - Justify each recommendation
   - Explain compatibility
   - Be honest about limitations

## Available Script

### search_iwc_workflows.py

**Usage:**
```bash
python search_iwc_workflows.py --list-categories
python search_iwc_workflows.py --category "Variant Calling"
python search_iwc_workflows.py --category "Transcriptomics" --limit 10
python search_iwc_workflows.py --format json
```

**Purpose:** Fetches IWC workflow manifest and returns workflows (optionally filtered by category).

**Returns:** JSON with workflow names, descriptions, categories, TRS IDs, tags, and creators.

**Category-based filtering:**
- Use `--category` to filter by analysis type
- Use `--list-categories` to see all available categories
- Categories include: Variant Calling, Transcriptomics, Genome assembly, Virology, Epigenetics, Microbiome, Proteomics, etc.

## Common IWC Workflow Categories

When users mention specific analysis types, use these categories:
- **RNA-seq, transcriptomics, gene expression** → `Transcriptomics`
- **Variant calling, SNP calling, mutations** → `Variant Calling`
- **Genome assembly, de novo assembly** → `Genome assembly`
- **Gene annotation, genome annotation** → `Genome Annotation`
- **Viral analysis, virus** → `Virology`
- **ChIP-seq, epigenetics, methylation** → `Epigenetics`
- **Metagenomics, microbiome** → `Microbiome` or `Metabarcoding`
- **Single cell, scRNA-seq** → `Single Cell`
- **Proteomics, mass spec** → `Proteomics`

## Example Interactions

### Example 1: RNA-seq Analysis Request
**User:** "I want to analyze Plasmodium falciparum RNA-seq data"

**Claude's Process:**
1. Extract intent: Analysis = RNA-seq/Transcriptomics, Organism = P. falciparum (eukaryotic parasite)
2. Run: `python search_iwc_workflows.py --category Transcriptomics`
3. Read through results looking for:
   - Eukaryotic RNA-seq workflows
   - General-purpose transcriptomics workflows
   - Avoid bacterial/viral-specific ones
4. Check data compatibility (if data characteristics were provided)
5. Recommend 2-3 most relevant workflows with TRS IDs
6. Explain why each is appropriate for P. falciparum

### Example 2: Viral Variant Calling
**User:** "How do I call variants in SARS-CoV-2 amplicon data?"

**Claude's Process:**
1. Extract intent: Analysis = Variant calling, Organism = SARS-CoV-2 (viral), Data = amplicon sequencing
2. Run: `python search_iwc_workflows.py --category "Variant Calling"`
3. Look specifically for:
   - SARS-CoV-2 workflows
   - Amplicon-based workflows
   - Viral variant calling workflows
4. Recommend workflows designed for SARS-CoV-2 amplicons (likely ARTIC protocol)
5. Provide TRS IDs and explain why they're appropriate

### Example 3: General Inquiry
**User:** "What workflows are available for metagenomics?"

**Claude's Process:**
1. Extract intent: Analysis = Metagenomics
2. Run: `python search_iwc_workflows.py --category Microbiome`
3. Present overview of available metagenomics workflows
4. Group by specific purposes (taxonomic classification, functional analysis, etc.)
5. Explain what each workflow does

## Error Handling

**If no workflows match:**
- Be honest that IWC may not have a workflow for this specific use case
- Suggest checking the IWC catalog directly at iwc.galaxyproject.org
- Suggest looking at related categories
- DO NOT fall back to writing custom code

**If network errors occur:**
- Report clearly that iwc.galaxyproject.org needs to be accessible
- Suggest checking network allowlist
- DO NOT try to generate code as a fallback

## Network Requirements

⚠️ **Important**: This skill requires network access to:
- `iwc.galaxyproject.org` (IWC Workflow Manifest)

If you encounter network errors, the user needs to add this domain to their network allowlist.

## Testing the Skill

To verify the skill is working:
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

## Notes for Developers

**This skill follows a strict no-code-generation policy:**
- The IWC catalog contains hundreds of vetted, production-ready workflows
- Our job is to find and recommend the right ones
- We never write custom scripts as an alternative
- If IWC doesn't have a workflow for a specific use case, we acknowledge that limitation rather than generating code

**Workflow interpretation is key:**
- Claude must read and understand workflow descriptions
- Match them to organisms, domains, and data types
- Provide thoughtful, justified recommendations
- Be honest about limitations and compatibility
