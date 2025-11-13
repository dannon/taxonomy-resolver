---
name: taxonomy-resolver
description: Resolves ambiguous organism names to precise NCBI taxonomy IDs and scientific names, then recommends appropriate IWC (Intergalactic Workflow Commission) Galaxy workflows for analysis. Use this skill when users provide common names (like "malaria parasite", "E. coli", "mouse"), abbreviated names, or when you need to convert any organism reference to an exact scientific name for API queries. This skill handles disambiguation through conversation, validates taxonomy IDs via NCBI Taxonomy API, provides ENA FASTQ search capabilities, and ALWAYS recommends existing IWC workflows rather than producing custom scripts or analysis steps.
---

# Taxonomy Resolver Skill

## Purpose

This skill enables Claude to convert ambiguous organism names, common names, or taxonomy references into precise, API-ready scientific names and NCBI taxonomy IDs. It also helps users find relevant genomic data (FASTQ files) and **recommends appropriate IWC Galaxy workflows for analysis**. **The core principles: (1) let external APIs do the work, (2) ALWAYS recommend existing IWC workflows instead of writing code or producing custom analysis steps, (3) Claude's role is orchestration, disambiguation, validation, and workflow recommendation - NOT code generation.**

## When to Use This Skill

Use this skill when:
- User mentions organisms by common name ("malaria parasite", "mosquito", "house mouse")
- User provides ambiguous scientific names ("E. coli", "SARS-CoV-2 isolate")
- User asks to search for genomic data (FASTQ, assemblies, etc.) for an organism
- User wants to analyze genomic data (ALWAYS recommend IWC workflows, never write custom scripts)
- User needs workflow recommendations for any bioinformatics analysis
- You need to validate or look up taxonomy IDs
- User provides a taxonomy ID that needs verification
- Converting organism names for NCBI, ENA, or other database queries

## Core Workflow

### 1. Extract User Intent (Critical)

**Before calling any APIs, understand what the user wants to do.** Extract:
- **Organism**: What species/taxa are they interested in?
- **Analysis type**: RNA-seq, variant calling, genome assembly, ChIP-seq, etc.
- **Data type**: FASTQ reads, assemblies, annotations, etc.

**Examples of intent extraction:**
- "I want to analyze Plasmodium falciparum RNA-seq data" → Organism: P. falciparum, Analysis: RNA-seq/Transcriptomics, Data: FASTQ reads
- "Find variant calling workflows for mouse" → Organism: Mus musculus, Analysis: Variant calling
- "Search for E. coli genome assemblies" → Organism: E. coli (needs disambiguation), Data: assemblies

### 2. Disambiguation (Critical)

**NEVER pass ambiguous names to APIs.** Always disambiguate to species-level or specific taxa first.

If the user's input is NOT an explicit species-level scientific name:
1. Identify the ambiguity
2. Ask a clarifying question OR show a small disambiguation list
3. Wait for user confirmation before proceeding

**Examples of ambiguous inputs that require clarification:**
- "malaria parasite" → Ask: "Which malaria parasite? (Plasmodium falciparum, P. vivax, P. malariae, P. ovale, P. knowlesi)"
- "E. coli" → Ask: "Which E. coli strain? (K-12, O157:H7, other specific strain)"
- "mouse" → Ask: "Did you mean house mouse (Mus musculus) or a different species?"
- "SARS-CoV-2 isolate" → Ask: "Please provide the specific isolate or strain name"
- "bacteria" → Too broad, ask for specific genus/species

### 3. Taxonomy Resolution

Once you have a specific name, use the `resolve_taxonomy.py` script to:
- Query NCBI Taxonomy API
- Get the official taxonomy ID
- Retrieve the scientific name
- Get taxonomic lineage
- Validate the organism exists in NCBI

### 4. ENA Search (Optional)

If the user needs FASTQ files or genomic data, use the `search_ena.py` script with **intent-based filtering**:
- **Use the extracted intent to add filters to your query**
- For RNA-seq: Add `library_strategy="RNA-Seq"` to the query
- For WGS: Add `library_strategy="WGS"` to the query
- For ChIP-seq: Add `library_strategy="ChIP-Seq"` to the query
- Search ENA's database with these filters
- **Automatically group results by BioProject**
- **Present technical details for each BioProject**:
  - Sequencing platform (Illumina, PacBio, Oxford Nanopore, etc.)
  - Library layout (SINGLE or PAIRED)
  - Read length and insert size (if available)
  - Number of runs/samples
  - Library strategy (RNA-Seq, WGS, etc.)
- These technical details are CRITICAL for matching workflows to data

**Example intent-based queries:**
- User wants RNA-seq data → `python search_ena.py 'scientific_name="Plasmodium falciparum" AND library_strategy="RNA-Seq"'`
- User wants WGS data → `python search_ena.py 'scientific_name="Mus musculus" AND library_strategy="WGS"'`
- User just wants any data → `python search_ena.py "Plasmodium falciparum"`

### 5. BioProject Details (Optional)

After getting ENA search results, you can fetch detailed descriptions for BioProjects using `get_bioproject_details.py`:
- Query ENA for BioProject metadata
- Get study title and description
- Retrieve organism information and submission details
- Provide context about what each BioProject contains
- **Note the technical specifications** (platform, layout, read length) from the ENA search results

### 6. IWC Workflow Recommendations (REQUIRED for Analysis Tasks)

**CRITICAL: When users need to analyze genomic data, ALWAYS recommend relevant IWC Galaxy workflows. NEVER write custom scripts or produce step-by-step analysis instructions.** Use `search_iwc_workflows.py` with **intent-based filtering**:
- **Use the extracted intent to filter by category**
- For RNA-seq → Use `--category "Transcriptomics"`
- For variant calling → Use `--category "Variant Calling"`
- For genome assembly → Use `--category "Genome assembly"`
- For viral analysis → Use `--category "Virology"`
- Fetch IWC (Intergalactic Workflow Commission) workflow manifest
- **YOU interpret the workflow descriptions to match them to:**
  1. **The organism** (domain, specific species mentions)
  2. **The data characteristics** (single vs paired-end, platform, read length)
  3. **The analysis type** (RNA-seq, variant calling, etc.)
- Look for organism-specific mentions, domain keywords (viral, bacterial, eukaryotic), and general applicability
- **Match workflow requirements to the BioProject technical details**
- Provide TRS IDs for importing workflows into Galaxy

**Important**: The script returns workflows (filtered by category if specified). It's YOUR job to:
1. Read the workflow names, descriptions, tags, and categories
2. Determine which workflows are relevant to the user's organism AND analysis intent
3. **Match workflow data requirements to the BioProject technical details**:
   - Does the workflow require paired-end data? Check if BioProject has PAIRED layout
   - Does the workflow work with the sequencing platform? (Illumina, PacBio, etc.)
   - Does the workflow need specific read lengths or quality?
   - Are there organism-specific requirements (reference genome availability, etc.)?
4. Explain why each suggested workflow is appropriate AND compatible with the data
5. Prioritize workflows that mention the organism or its domain explicitly
6. **Warn users if there's a mismatch** (e.g., workflow needs paired-end but data is single-end)

**Example intent-based workflow searches:**
- User wants RNA-seq analysis → `python search_iwc_workflows.py --category "Transcriptomics"`
- User wants variant calling → `python search_iwc_workflows.py --category "Variant Calling"`
- User wants viral analysis → `python search_iwc_workflows.py --category "Virology"`
- User's intent unclear → `python search_iwc_workflows.py` (fetch all, then interpret)

## Important Principles

1. **Extract intent first**: Before calling APIs, understand what the user wants to do (analysis type, data type, etc.)

2. **ALWAYS recommend IWC workflows, NEVER write code**: 
   - ✅ Recommend existing IWC workflows from the catalog
   - ❌ Write custom Python/R/bash scripts for analysis
   - ❌ Produce step-by-step analysis instructions
   - ❌ Generate custom code for data processing
   - The IWC catalog contains vetted, production-ready workflows - use them!

3. **Use intent to filter API calls**: 
   - Add `library_strategy` filters to ENA searches based on analysis type
   - Use `--category` filters for IWC workflow searches based on analysis type
   - This gives more relevant results and saves the user time

4. **Let the API handle validation**: Don't try to validate taxonomy yourself. Call the API and report what it returns.

5. **Be conversational about disambiguation**: Don't lecture, just ask naturally:
   - ✅ "Which malaria parasite are you interested in? Plasmodium falciparum or P. vivax?"
   - ❌ "I cannot proceed without a species-level designation. Please provide taxonomic clarification."

6. **Don't hallucinate taxonomy IDs**: If you're not certain, use the API. Never make up taxonomy IDs.

7. **Species-level is usually the target**: Most database queries work best with species-level names, but subspecies and strains are fine if specified.

8. **Common names are okay as starting points**: Use them to begin disambiguation, but always convert to scientific names for APIs.

## Available Scripts

### resolve_taxonomy.py

**Usage:**
```bash
python resolve_taxonomy.py "Plasmodium falciparum"
python resolve_taxonomy.py --tax-id 5833
```

**Purpose:** Queries NCBI Taxonomy API to resolve organism names to taxonomy IDs and vice versa.

**Returns:** JSON with taxonomy ID, scientific name, common name, and lineage.

### search_ena.py

**Usage:**
```bash
# Basic search
python search_ena.py "Plasmodium falciparum" --data-type fastq

# Intent-based search with library_strategy filter (RECOMMENDED)
python search_ena.py 'scientific_name="Plasmodium falciparum" AND library_strategy="RNA-Seq"'
python search_ena.py 'scientific_name="Mus musculus" AND library_strategy="WGS"'
python search_ena.py 'scientific_name="SARS-CoV-2" AND library_strategy="AMPLICON"'

# Other options
python search_ena.py "Mus musculus" --limit 10
```

**Purpose:** Searches ENA (European Nucleotide Archive) for genomic data.

**Intent-based filtering:** Use ENA query syntax to add filters based on user intent:
- `library_strategy="RNA-Seq"` - For RNA-seq/transcriptomics
- `library_strategy="WGS"` - For whole genome sequencing
- `library_strategy="WXS"` - For whole exome sequencing
- `library_strategy="ChIP-Seq"` - For ChIP-seq/epigenetics
- `library_strategy="AMPLICON"` - For amplicon sequencing
- `library_strategy="Bisulfite-Seq"` - For methylation studies

**Returns:** JSON with accession numbers, study information, and metadata. **For read_run searches, results are automatically grouped by BioProject** with:
- BioProject accession
- Number of reads associated with each BioProject
- Study title (if available)
- Sample run details
- Library strategy (experiment type)

### get_bioproject_details.py

**Usage:**
```bash
python get_bioproject_details.py PRJEB1234
python get_bioproject_details.py PRJNA123456 --format json
python get_bioproject_details.py PRJEB1234 PRJNA456789
```

**Purpose:** Fetches detailed information about BioProjects from ENA.

**Returns:** JSON with study title, description, organism, center name, and dates.

### search_iwc_workflows.py

**Usage:**
```bash
python search_iwc_workflows.py --list-categories
python search_iwc_workflows.py --category "Variant Calling"
python search_iwc_workflows.py --category "Transcriptomics" --limit 10
python search_iwc_workflows.py --format json
```

**Purpose:** Fetches IWC workflow manifest. Returns ALL workflows (or filtered by category). **You must interpret the results to match workflows to organisms.**

**Returns:** JSON with workflow names, descriptions, categories, TRS IDs, tags, and creators. 

**How to use the results:**
1. Read workflow descriptions, names, and tags carefully
2. Match workflows to the user's organism based on:
   - Direct organism mentions (e.g., "SARS-CoV-2", "bacterial")
   - Domain keywords (viral, bacterial, eukaryotic, prokaryotic)
   - Analysis type relevance (e.g., RNA-seq for transcriptomics)
   - General applicability (many workflows work across organisms)
3. Explain to the user WHY each workflow is relevant
4. Prioritize workflows with explicit organism/domain matches

## Example Interactions

### Example 1: Simple Resolution
**User:** "What's the taxonomy ID for house mouse?"

**Claude's Process:**
1. User said "house mouse" - this is clear enough (Mus musculus is unambiguous)
2. Run: `python resolve_taxonomy.py "Mus musculus"`
3. Return the taxonomy ID to user

### Example 2: Disambiguation Required with BioProject Details
**User:** "Find FASTQ files for malaria parasite"

**Claude's Process:**
1. "Malaria parasite" is ambiguous
2. Ask: "Which malaria parasite? The main ones are:
   - Plasmodium falciparum (most common, causes severe malaria)
   - Plasmodium vivax (widespread, relapses common)
   - Plasmodium malariae
   - Plasmodium ovale"
3. Wait for user response
4. Once user specifies (e.g., "P. falciparum"), then:
   - Run: `python resolve_taxonomy.py "Plasmodium falciparum"`
   - Run: `python search_ena.py "Plasmodium falciparum" --data-type fastq`
   - Results will be grouped by BioProject automatically
5. **Present BioProject results with technical details**:
   - Platform (e.g., "Illumina HiSeq 2500")
   - Layout ("SINGLE" or "PAIRED")
   - Read length (e.g., "150 bp")
   - Number of runs
6. (Optional) If user wants more context about specific BioProjects:
   - Run: `python get_bioproject_details.py PRJEB1234 PRJEB5678`
7. Present results with BioProject grouping, descriptions, and technical specifications

### Example 3: Strain-Level Detail
**User:** "Search for E. coli K-12 data"

**Claude's Process:**
1. "E. coli K-12" is specific enough
2. Run: `python resolve_taxonomy.py "Escherichia coli K-12"`
3. Run: `python search_ena.py "Escherichia coli K-12"`
4. Present results

### Example 4: Taxonomy ID Lookup
**User:** "What organism is taxonomy ID 9606?"

**Claude's Process:**
1. Run: `python resolve_taxonomy.py --tax-id 9606`
2. Report the result (Homo sapiens)

### Example 5: Complete Workflow - Data Search + Analysis Suggestions (Intent-Based)
**User:** "I want to analyze Plasmodium falciparum RNA-seq data"

**Claude's Process:**
1. **Extract intent**: Organism = P. falciparum, Analysis = RNA-seq/Transcriptomics, Data = FASTQ reads
2. Organism is specific enough (P. falciparum)
3. Run: `python resolve_taxonomy.py "Plasmodium falciparum"`
4. **Run with intent-based filter**: `python search_ena.py 'scientific_name="Plasmodium falciparum" AND library_strategy="RNA-Seq"' --limit 10`
5. **Present BioProject groupings with technical details**:
   - Example: "PRJEB1234: 12 runs, Illumina HiSeq 2500, PAIRED-end, 150bp reads"
   - Note the library layout (SINGLE vs PAIRED) - this is critical for workflow selection!
6. **Run with intent-based category filter**: `python search_iwc_workflows.py --category Transcriptomics`
7. **Read through the workflow results and identify relevant ones:**
   - Look for eukaryotic RNA-seq workflows (P. falciparum is eukaryotic)
   - Check if any mention parasites, protozoa, or are general-purpose
   - Avoid bacterial or viral-specific workflows
   - **Match workflow requirements to data characteristics**:
     * If data is PAIRED-end, recommend paired-end workflows
     * If data is SINGLE-end, recommend single-end or flexible workflows
     * Check platform compatibility (most IWC workflows are Illumina-focused)
8. Suggest 2-3 most relevant workflows with explanations
9. **Explain compatibility**: "This workflow accepts paired-end Illumina data, which matches your BioProject PRJEB1234"
10. Provide TRS IDs for importing workflows into Galaxy

**Key improvement**: By filtering ENA search to `library_strategy="RNA-Seq"` and IWC workflows to `--category Transcriptomics`, the results are much more relevant to the user's actual intent!

## Error Handling

**If NCBI API returns no results:**
- Don't assume the organism doesn't exist
- Suggest alternative spellings or ask if they meant something similar
- Example: "I couldn't find 'Homo sapian' in NCBI. Did you mean 'Homo sapiens'?"

**If ENA search returns no results:**
- Report this clearly
- Suggest broadening the search or trying different terms
- Example: "No FASTQ files found for this specific search. You might try searching for the genus or checking NCBI SRA instead."

**If network errors occur:**
- Report the error clearly
- Suggest the user check their network settings
- Note which domains need to be allowlisted (api.ncbi.nlm.nih.gov, www.ebi.ac.uk)

**If API rate limits are hit:**
- **CRITICAL**: Since we're using external APIs, rate limits can occur
- **Retry strategy**: Wait 1-2 seconds and retry the API call
- **Maximum retries**: Try up to 3 times total before reporting failure
- **Exponential backoff**: Consider increasing wait time with each retry (1s, 2s, 4s)
- After 3 failed attempts, report to the user:
  - "The API is currently rate-limited. Please wait a moment and try again."
  - Suggest trying again in a few minutes
- **Apply this to all API calls**: NCBI Taxonomy, ENA search, BioProject details, IWC workflows

## Network Requirements

⚠️ **Important**: This skill requires network access to:
- `api.ncbi.nlm.nih.gov` (NCBI Taxonomy API)
- `www.ebi.ac.uk` (ENA API)
- `iwc.galaxyproject.org` (IWC Workflow Manifest)

If you encounter network errors, the user needs to add these domains to their network allowlist.

## Best Practices

1. **Extract user intent FIRST** - Understand what they want to do before calling any APIs
2. **ALWAYS recommend IWC workflows for analysis tasks** - Never write custom code or scripts:
   - ✅ Search IWC catalog and recommend existing workflows
   - ✅ Explain why each workflow is appropriate for their organism/analysis
   - ✅ Provide TRS IDs for easy import into Galaxy
   - ❌ Write custom Python/R/bash scripts
   - ❌ Produce step-by-step command-line instructions
   - ❌ Generate custom analysis code
3. **Use intent to filter API calls** - Add appropriate filters to get more relevant results:
   - ENA: Use `library_strategy` filters based on analysis type
   - IWC: Use `--category` filters based on analysis type
4. **Always disambiguate before calling APIs**
5. **Use the actual API responses, don't invent taxonomy data**
6. **Be conversational and helpful with disambiguation**
7. **Report API errors clearly and suggest solutions**
8. **Remember: let the APIs do the heavy lifting, Claude just orchestrates and recommends**
9. **Handle API rate limits gracefully**: If you hit rate limits, wait 1-2 seconds and retry up to 3 times before reporting failure
10. **For IWC workflows: YOU do the interpretation**
   - Read workflow descriptions carefully
   - Match workflows to organisms based on domain, keywords, and applicability
   - **Match workflows to data characteristics** (single vs paired-end, platform, read length)
   - Explain your reasoning when suggesting workflows, including data compatibility
   - Don't suggest workflows blindly - justify each recommendation
   - **Warn about incompatibilities**: If a workflow requires paired-end data but the BioProject has single-end, explicitly mention this

## Common Library Strategies for ENA Filtering

When users mention specific analysis types, use these `library_strategy` values:
- **RNA-seq, transcriptomics, gene expression** → `RNA-Seq`
- **Whole genome sequencing, WGS** → `WGS`
- **Whole exome sequencing, WXS, exome** → `WXS`
- **ChIP-seq, chromatin, histone** → `ChIP-Seq`
- **Amplicon sequencing, targeted sequencing** → `AMPLICON`
- **Methylation, bisulfite sequencing** → `Bisulfite-Seq`
- **ATAC-seq, chromatin accessibility** → `ATAC-seq`
- **Hi-C, chromosome conformation** → `Hi-C`
- **Metagenomics** → `METAGENOMIC`
- **Small RNA, miRNA** → `miRNA-Seq`

## Common IWC Workflow Categories

When users mention specific analysis types, use these categories:
- **RNA-seq, transcriptomics** → `Transcriptomics`
- **Variant calling, SNP calling, mutations** → `Variant Calling`
- **Genome assembly, de novo assembly** → `Genome assembly`
- **Gene annotation, genome annotation** → `Genome Annotation`
- **Viral analysis, virus** → `Virology`
- **ChIP-seq, epigenetics, methylation** → `Epigenetics`
- **Metagenomics, microbiome** → `Microbiome` or `Metabarcoding`
- **Single cell, scRNA-seq** → `Single Cell`
- **Proteomics, mass spec** → `Proteomics`

## Testing the Skill

To verify the skill is working:
```bash
# Test taxonomy resolution
python resolve_taxonomy.py "Homo sapiens"

# Test with taxonomy ID
python resolve_taxonomy.py --tax-id 9606

# Test ENA search (will show BioProject grouping)
python search_ena.py "Saccharomyces cerevisiae" --data-type fastq --limit 5

# Test BioProject details
python get_bioproject_details.py PRJNA128

# Test IWC workflow category listing
python search_iwc_workflows.py --list-categories

# Test workflow search with category filter
python search_iwc_workflows.py --category "Variant Calling"

# Test fetching all workflows (for LLM interpretation)
python search_iwc_workflows.py --format json
```

## Notes for Developers

This skill follows the principle articulated by Danielle: **"why try to teach the ai to do a thing an api can already do? just make an agentic tool that hits that api endpoint and walk away."**

The skill doesn't try to make Claude an expert in taxonomy or bioinformatics. It just provides:
1. Clear guidance on when to disambiguate
2. Tools to call the right APIs
3. Instructions on how to handle responses
4. **A mandate to recommend existing IWC workflows rather than writing custom code**

All validation is the API's problem. If results seem wrong or missing, that's ENA/NCBI's issue to address, not ours.

**Critical design decision**: This skill NEVER produces custom analysis scripts or step-by-step instructions. The IWC catalog contains hundreds of vetted, production-ready workflows. Our job is to find and recommend the right ones, not to reinvent the wheel by writing new code.
