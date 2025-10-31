---
name: taxonomy-resolver
description: Resolves ambiguous organism names to precise NCBI taxonomy IDs and scientific names. Use this skill when users provide common names (like "malaria parasite", "E. coli", "mouse"), abbreviated names, or when you need to convert any organism reference to an exact scientific name for API queries. This skill handles disambiguation through conversation and validates taxonomy IDs via NCBI Taxonomy API. Also provides ENA FASTQ search capabilities.
---

# Taxonomy Resolver Skill

## Purpose

This skill enables Claude to convert ambiguous organism names, common names, or taxonomy references into precise, API-ready scientific names and NCBI taxonomy IDs. **The core principle: let external APIs do the work. Claude's role is orchestration, disambiguation, and validation.**

## When to Use This Skill

Use this skill when:
- User mentions organisms by common name ("malaria parasite", "mosquito", "house mouse")
- User provides ambiguous scientific names ("E. coli", "SARS-CoV-2 isolate")
- User asks to search for genomic data (FASTQ, assemblies, etc.) for an organism
- You need to validate or look up taxonomy IDs
- User provides a taxonomy ID that needs verification
- Converting organism names for NCBI, ENA, or other database queries

## Core Workflow

### 1. Disambiguation First (Critical)

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

### 2. Taxonomy Resolution

Once you have a specific name, use the `resolve_taxonomy.py` script to:
- Query NCBI Taxonomy API
- Get the official taxonomy ID
- Retrieve the scientific name
- Get taxonomic lineage
- Validate the organism exists in NCBI

### 3. ENA Search (Optional)

If the user needs FASTQ files or genomic data, use the `search_ena.py` script to:
- Search ENA's free text search
- Find relevant datasets
- Return accession numbers and metadata

## Important Principles

1. **Let the API handle validation**: Don't try to validate taxonomy yourself. Call the API and report what it returns.

2. **Be conversational about disambiguation**: Don't lecture, just ask naturally:
   - ✅ "Which malaria parasite are you interested in? Plasmodium falciparum or P. vivax?"
   - ❌ "I cannot proceed without a species-level designation. Please provide taxonomic clarification."

3. **Don't hallucinate taxonomy IDs**: If you're not certain, use the API. Never make up taxonomy IDs.

4. **Species-level is usually the target**: Most database queries work best with species-level names, but subspecies and strains are fine if specified.

5. **Common names are okay as starting points**: Use them to begin disambiguation, but always convert to scientific names for APIs.

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
python search_ena.py "Plasmodium falciparum" --data-type fastq
python search_ena.py "Mus musculus" --limit 10
```

**Purpose:** Searches ENA (European Nucleotide Archive) for genomic data.

**Returns:** JSON with accession numbers, study information, and metadata.

## Example Interactions

### Example 1: Simple Resolution
**User:** "What's the taxonomy ID for house mouse?"

**Claude's Process:**
1. User said "house mouse" - this is clear enough (Mus musculus is unambiguous)
2. Run: `python resolve_taxonomy.py "Mus musculus"`
3. Return the taxonomy ID to user

### Example 2: Disambiguation Required
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
5. Present results

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

## Network Requirements

⚠️ **Important**: This skill requires network access to:
- `api.ncbi.nlm.nih.gov` (NCBI Taxonomy API)
- `www.ebi.ac.uk` (ENA API)

If you encounter network errors, the user needs to add these domains to their network allowlist.

## Best Practices

1. **Always disambiguate before calling APIs**
2. **Use the actual API responses, don't invent taxonomy data**
3. **Be conversational and helpful with disambiguation**
4. **Report API errors clearly and suggest solutions**
5. **Remember: let the APIs do the heavy lifting, Claude just orchestrates**

## Testing the Skill

To verify the skill is working:
```bash
# Test taxonomy resolution
python resolve_taxonomy.py "Homo sapiens"

# Test with taxonomy ID
python resolve_taxonomy.py --tax-id 9606

# Test ENA search
python search_ena.py "Saccharomyces cerevisiae" --data-type fastq --limit 5
```

## Notes for Developers

This skill follows the principle articulated by Danielle: **"why try to teach the ai to do a thing an api can already do? just make an agentic tool that hits that api endpoint and walk away."**

The skill doesn't try to make Claude an expert in taxonomy. It just provides:
1. Clear guidance on when to disambiguate
2. Tools to call the right APIs
3. Instructions on how to handle responses

All validation is the API's problem. If results seem wrong or missing, that's ENA/NCBI's issue to address, not ours.
