# Taxonomy Resolver Skill - Deployment Package

## What You Have

This is a complete, production-ready Claude skill that resolves organism taxonomy and searches genomic databases.

### Package Contents

```
taxonomy-resolver/
├── SKILL.md              # Main skill file (Claude reads this)
├── resolve_taxonomy.py   # NCBI Taxonomy API client
├── search_ena.py        # ENA search API client
├── README.md            # Complete documentation
├── QUICKSTART.md        # 5-minute deployment guide
├── EXAMPLES.md          # Usage examples and patterns
├── CHANGELOG.md         # Version history
├── VERSION              # Current version (1.0.0)
├── test_skill.sh        # Automated test suite
└── .gitignore           # Git ignore patterns

Also included:
- taxonomy-resolver.zip  # Ready-to-upload package for Claude.ai
```

## What This Skill Does

Based on Dave Rogers and Danielle Callan's requirements, this skill:

1. **Resolves ambiguous organism names** → Asks clarifying questions conversationally
2. **Converts to NCBI taxonomy IDs** → Uses NCBI Taxonomy API (not AI guesses)
3. **Searches ENA for genomic data** → Finds FASTQ files, assemblies, etc.
4. **Handles all the edge cases** → Spelling variations, common names, strains

### Key Philosophy

> "Why try to teach the AI to do a thing an API can already do? Just make an agentic tool that hits that API endpoint and walk away."
> — Danielle Callan

This skill follows that principle:
- **Claude's role:** Orchestration and disambiguation
- **API's role:** Validation and data retrieval
- **Result:** Simple, maintainable, accurate

## Quick Start

### 1. Deploy to Claude.ai (Easiest)

```bash
# The zip file is ready to upload
# Go to: Settings → Features → Skills → Upload Skill
# Select: taxonomy-resolver.zip
```

### 2. Deploy to Claude Code

```bash
# Copy to your skills directory
cp -r taxonomy-resolver ~/.claude/skills/

# Claude Code will auto-discover it
```

### 3. Deploy via API

```python
import anthropic

client = anthropic.Anthropic()

with open('taxonomy-resolver.zip', 'rb') as f:
    skill = client.skills.create(
        name='taxonomy-resolver',
        description='Resolve taxonomy and search genomic databases',
        file=f
    )

print(f"Skill ID: {skill.id}")
```

## Critical: Network Configuration

⚠️ **This skill requires network access to:**
- `api.ncbi.nlm.nih.gov` (NCBI Taxonomy API)
- `www.ebi.ac.uk` (ENA API)

**Without this, the skill will fail with network errors.**

Add these domains to your Claude environment's network allowlist.

## Testing

After deployment, test with:

```bash
# Run the test suite
cd taxonomy-resolver
bash test_skill.sh

# Or test manually
python resolve_taxonomy.py "Homo sapiens"
python search_ena.py "Saccharomyces cerevisiae" --limit 5
```

In Claude, try:
- "What's the taxonomy ID for house mouse?"
- "Find FASTQ files for malaria parasite" (should trigger disambiguation)
- "Search ENA for yeast genome assemblies"

## Example Conversation

**You:** Find FASTQ files for malaria parasite

**Claude:** Which malaria parasite are you interested in?
- Plasmodium falciparum (most common, severe malaria)
- Plasmodium vivax (widespread, relapses)
- Plasmodium malariae
- Plasmodium ovale

**You:** P. falciparum

**Claude:** [Uses resolve_taxonomy.py and search_ena.py]
Found 1,247 FASTQ datasets for Plasmodium falciparum (taxonomy ID: 5833).

[Shows top results with accession numbers]

## Key Features

### 1. Smart Disambiguation
- Recognizes ambiguous terms (e.g., "E. coli", "mouse", "bacteria")
- Asks conversational clarifying questions
- Never proceeds without specific organism names

### 2. API-Driven Validation
- Never invents taxonomy IDs
- Always defers to NCBI for authoritative data
- Reports API responses accurately

### 3. Multi-Database Search
- NCBI Taxonomy (for ID resolution)
- ENA (for FASTQ, assemblies, samples, studies)
- Extensible to other databases

### 4. Error Handling
- Clear error messages
- Actionable solutions
- Graceful degradation

### 5. Production Ready
- Comprehensive documentation
- Automated testing
- Version control
- Clean code structure

## Addressing Dave's Concerns

> "How well will the long tail of our taxonomy IDs perform?"

**Answer:** The skill doesn't try to know taxonomy IDs itself. It always queries NCBI's API, so it handles the full taxonomy database—not just common organisms.

> "How well will the manual keyword → attribute mapping scale?"

**Answer:** There's no manual mapping. The skill uses free-text search in NCBI/ENA, letting their APIs handle the complexity.

> "It might be worth setting some expectations for ENA query accuracy."

**Answer:** The skill reports ENA results as-is. Accuracy is ENA's responsibility. If results are poor, that's a signal to improve the query or consider other databases.

## Codeathon Application

This skill is perfect for the BRC codeathon because:

1. **Reusable across the BRC community** ✓
2. **Solves a real workflow problem** ✓
3. **Built with extensibility in mind** ✓
4. **Well-documented and testable** ✓
5. **Measures accuracy via API responses** ✓

## Extending the Skill

Want to add more features? Easy:

### Add another database:
1. Create `search_sra.py` (following the same pattern)
2. Add instructions in SKILL.md
3. Test and document

### Add batch processing:
1. Create `batch_resolve.py`
2. Update SKILL.md with batch usage examples
3. Test with multiple organisms

### Add caching:
1. Add a simple JSON cache in resolve_taxonomy.py
2. Update SKILL.md to mention caching behavior

### Measure accuracy:
1. Create `evaluation/` directory
2. Add test cases and expected results
3. Run automated comparisons

## File Structure Explained

### SKILL.md (Most Important)
This is what Claude reads. It contains:
- When to use the skill (description in YAML frontmatter)
- How to disambiguate (critical workflow section)
- How to use the scripts
- Error handling guidance
- Best practices

### Python Scripts
- `resolve_taxonomy.py`: NCBI Taxonomy API client
- `search_ena.py`: ENA search API client

Both are:
- Self-contained (no external dependencies)
- Well-documented
- Command-line friendly
- JSON and human-readable output

### Documentation
- `README.md`: Complete documentation
- `QUICKSTART.md`: 5-minute deployment guide
- `EXAMPLES.md`: Real usage patterns
- `CHANGELOG.md`: Version history

### Testing
- `test_skill.sh`: Automated test suite
- Tests all major functions
- Provides clear pass/fail output

## Support & Maintenance

### Reporting Issues
If you find bugs or have suggestions:
1. Document the issue (what happened vs. what expected)
2. Include example queries that trigger the issue
3. Check if it's an API issue (NCBI/ENA) or skill issue
4. Update the skill or report to the appropriate API team

### Updating the Skill
1. Make changes to the files
2. Update VERSION and CHANGELOG.md
3. Test thoroughly with test_skill.sh
4. Re-zip and redeploy

### API Changes
If NCBI or ENA change their APIs:
1. Update the Python scripts (resolve_taxonomy.py or search_ena.py)
2. Test with real queries
3. Update version and changelog
4. Redeploy

## Next Steps

1. **Read QUICKSTART.md** for detailed deployment instructions
2. **Review EXAMPLES.md** to see expected behavior
3. **Run test_skill.sh** to verify everything works
4. **Deploy to your environment** using your preferred method
5. **Test with real queries** in Claude
6. **Iterate and improve** as needed

## Success Criteria

You'll know the skill is working when:
- ✓ Claude asks disambiguation questions for ambiguous terms
- ✓ Claude returns correct taxonomy IDs from NCBI
- ✓ Claude finds FASTQ/assembly data from ENA
- ✓ Claude handles errors gracefully with clear messages
- ✓ Claude uses the skill automatically (without prompting)

## Credits

- **Concept:** Dave Rogers & Danielle Callan
- **Project:** BRC Codeathon Taxonomy Resolver
- **Framework:** Anthropic Skills
- **APIs:** NCBI Taxonomy, ENA (EBI)

## License

Apache 2.0 (following Anthropic skills repository convention)

---

**You're all set!** The skill is ready to deploy. Start with QUICKSTART.md for step-by-step instructions.
