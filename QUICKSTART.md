# Taxonomy Resolver - Quick Start

Get up and running with the taxonomy-resolver skill in 5 minutes.

## Prerequisites

- [ ] Python 3.6 or higher installed
- [ ] Access to Claude (via claude.ai, Claude Code, or API)
- [ ] Network access enabled (see below)

## Critical: Enable Network Access

⚠️ **This skill will not work without network access to these domains:**

1. `api.ncbi.nlm.nih.gov`
2. `www.ebi.ac.uk`

### How to Enable Network Access

#### For Claude.ai
Contact your administrator or check your workspace settings to allowlist these domains.

#### For Claude Code
Check your network configuration file (typically in your environment settings).

#### For Claude API
Ensure your runtime environment can access these domains. Check firewalls, VPNs, and proxy settings.

## Installation (Choose One)

### Option A: Claude.ai (Web/Desktop)

1. **Create a zip file:**
   ```bash
   cd taxonomy-resolver/..
   zip -r taxonomy-resolver.zip taxonomy-resolver/
   ```

2. **Upload to Claude:**
   - Go to Settings → Features → Skills
   - Click "Upload Skill"
   - Select `taxonomy-resolver.zip`
   - Enable the skill

3. **Test it:**
   - Open a new conversation
   - Ask: "What's the taxonomy ID for Homo sapiens?"
   - Claude should use the skill automatically

### Option B: Claude Code (Terminal)

1. **Copy to skills directory:**
   ```bash
   # For personal use
   cp -r taxonomy-resolver ~/.claude/skills/
   
   # For project-specific use
   cp -r taxonomy-resolver ./.claude/skills/
   ```

2. **Verify installation:**
   ```bash
   # Claude Code will auto-discover the skill
   # No additional steps needed
   ```

3. **Test it:**
   - In Claude Code, ask: "Use the taxonomy resolver to find data for yeast"
   - Claude should discover and use the skill

### Option C: Claude API

1. **Create a Python script:**
   ```python
   import anthropic
   import zipfile
   from pathlib import Path
   
   # Zip the skill
   with zipfile.ZipFile('taxonomy-resolver.zip', 'w') as zf:
       for file in Path('taxonomy-resolver').rglob('*'):
           if file.is_file():
               zf.write(file, file.relative_to('taxonomy-resolver'))
   
   # Upload to API
   client = anthropic.Anthropic()
   with open('taxonomy-resolver.zip', 'rb') as f:
       skill = client.skills.create(
           name='taxonomy-resolver',
           description='Resolve taxonomy and search genomic databases',
           file=f
       )
   
   print(f"Skill uploaded with ID: {skill.id}")
   ```

2. **Use in API calls:**
   ```python
   message = client.messages.create(
       model="claude-sonnet-4-20250514",
       max_tokens=1024,
       messages=[
           {"role": "user", "content": "What's the taxonomy ID for Plasmodium falciparum?"}
       ],
       betas=["skills-2025-10-02"],
       container={
           "type": "code_execution",
           "skill_ids": [skill.id]
       }
   )
   ```

## Quick Test

After installation, test the skill with these queries:

### Test 1: Simple Lookup
**Ask Claude:**
> What's the taxonomy ID for Escherichia coli?

**Expected:** Claude uses resolve_taxonomy.py and returns the taxonomy ID (562).

### Test 2: Disambiguation
**Ask Claude:**
> Find FASTQ files for malaria parasite

**Expected:** Claude asks which malaria parasite species you mean.

### Test 3: Search
**Ask Claude:**
> Search ENA for Saccharomyces cerevisiae FASTQ files, limit to 5 results

**Expected:** Claude uses both scripts and returns search results.

## Troubleshooting

### Problem: "Network error" messages

**Cause:** Network access not enabled for required domains.

**Solution:**
1. Add `api.ncbi.nlm.nih.gov` to allowlist
2. Add `www.ebi.ac.uk` to allowlist
3. Restart Claude or start a new conversation

### Problem: Skill not being used

**Cause:** Claude doesn't recognize when to use the skill.

**Solution:** Be explicit in your query:
- ❌ "Tell me about yeast" (too vague)
- ✅ "What's the taxonomy ID for yeast?" (clear task)
- ✅ "Search for FASTQ files for Saccharomyces cerevisiae" (clear task)

### Problem: Scripts have permission errors

**Cause:** Scripts not executable.

**Solution:**
```bash
cd taxonomy-resolver
chmod +x *.py *.sh
```

### Problem: "No results found" for valid organism

**Possible causes:**
1. Spelling error (check scientific name spelling)
2. Organism not in NCBI Taxonomy database
3. Need to be more or less specific

**Solution:** Try variations or ask Claude to suggest alternatives.

## Advanced: Run Scripts Manually

You can also run the scripts directly (useful for testing):

```bash
# Resolve taxonomy by name
python resolve_taxonomy.py "Drosophila melanogaster"

# Resolve taxonomy by ID
python resolve_taxonomy.py --tax-id 7227

# Get detailed lineage
python resolve_taxonomy.py "Mus musculus" --detailed

# Search ENA for FASTQ
python search_ena.py "Arabidopsis thaliana" --data-type fastq

# Search for assemblies
python search_ena.py "Caenorhabditis elegans" --data-type assembly --limit 10

# Get JSON output
python resolve_taxonomy.py "Homo sapiens" --format json
python search_ena.py "Danio rerio" --format json --show-urls
```

## Example Conversations

### Example 1: Research Workflow
```
You: I'm working on a comparative genomics project. Can you find FASTQ data for 
     the model organisms: yeast, fruit fly, and C. elegans?

Claude: [Recognizes three common names]
        Just to clarify:
        - Yeast → Saccharomyces cerevisiae (baker's yeast)?
        - Fruit fly → Drosophila melanogaster?
        - C. elegans → Caenorhabditis elegans?

You: Yes, exactly.

Claude: [Uses resolve_taxonomy.py three times]
        [Uses search_ena.py three times]
        [Presents comprehensive results with accession numbers]
```

### Example 2: Quick Lookup
```
You: Taxonomy ID for zebra finch?

Claude: [Uses resolve_taxonomy.py]
        The taxonomy ID for zebra finch (Taeniopygia guttata) is 59729.
```

### Example 3: Validation
```
You: Is taxonomy ID 9031 chicken?

Claude: [Uses resolve_taxonomy.py --tax-id 9031]
        Yes, taxonomy ID 9031 is Gallus gallus (chicken).
```

## Next Steps

1. **Read the examples:** Check `EXAMPLES.md` for more usage patterns
2. **Review the README:** See `README.md` for detailed documentation
3. **Check the skill instructions:** Look at `SKILL.md` to understand how Claude uses it
4. **Run the test suite:** Execute `./test_skill.sh` to verify everything works

## Support

If you encounter issues:

1. Check the README.md troubleshooting section
2. Verify network access is properly configured
3. Test scripts manually to isolate the problem
4. Check API status:
   - NCBI: https://www.ncbi.nlm.nih.gov/
   - ENA: https://www.ebi.ac.uk/ena/

## Configuration Checklist

Before using the skill, ensure:

- [ ] Python 3.6+ is installed
- [ ] Network access to api.ncbi.nlm.nih.gov is enabled
- [ ] Network access to www.ebi.ac.uk is enabled
- [ ] Scripts are executable (chmod +x *.py *.sh)
- [ ] Skill is properly installed in Claude
- [ ] Test queries work as expected

---

**You're ready!** Start asking Claude about organisms, taxonomy IDs, and genomic data.
