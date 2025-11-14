# Taxonomy Resolver Skill - Usage Examples

This document shows how Claude will use the taxonomy-resolver skill in various scenarios.

## Example 1: Direct Species Name

**User Input:**
> What's the taxonomy ID for Homo sapiens?

**Claude's Process:**
1. Recognizes "Homo sapiens" is an unambiguous species name
2. Executes: `python resolve_taxonomy.py "Homo sapiens"`
3. Returns result directly

**Expected Output:**
```
Taxonomy ID: 9606
Scientific Name: Homo sapiens
Common Name: human
Rank: species
```

---

## Example 2: Common Name Disambiguation

**User Input:**
> Find FASTQ files for malaria parasite

**Claude's Process:**
1. Recognizes "malaria parasite" is ambiguous
2. **Does NOT call any APIs yet**
3. Asks disambiguation question

**Claude's Response:**
> Which malaria parasite are you interested in? The main ones are:
> - **Plasmodium falciparum** (most common, causes severe malaria)
> - **Plasmodium vivax** (widespread, relapses common)
> - **Plasmodium malariae** (chronic infection)
> - **Plasmodium ovale** (mild symptoms, rare)

**User Follow-up:**
> P. falciparum

**Claude's Next Steps:**
1. Executes: `python resolve_taxonomy.py "Plasmodium falciparum"`
2. Executes: `python search_ena.py "Plasmodium falciparum" --data-type fastq`
3. Returns results

---

## Example 3: Strain-Level Query

**User Input:**
> Search for E. coli K-12 genome data

**Claude's Process:**
1. Recognizes "E. coli K-12" is specific enough (strain level)
2. Executes: `python resolve_taxonomy.py "Escherichia coli K-12"`
3. Executes: `python search_ena.py "Escherichia coli K-12"`
4. Returns results

**No disambiguation needed** because K-12 is a specific strain.

---

## Example 4: Multiple Ambiguities

**User Input:**
> Compare mosquito and mouse genomes

**Claude's Process:**
1. Recognizes TWO ambiguous terms
2. Asks about the first ambiguity

**Claude's Response:**
> I'd be happy to help compare mosquito and mouse genomes. First, let me clarify:
> 
> **Which mosquito species?**
> - *Anopheles gambiae* (African malaria mosquito)
> - *Aedes aegypti* (yellow fever mosquito)
> - *Culex quinquefasciatus* (southern house mosquito)
> - Other?
>
> **Which mouse?**
> - *Mus musculus* (house mouse/laboratory mouse)
> - Other species?

**Waits for clarification before proceeding**

---

## Example 5: Taxonomy ID Lookup

**User Input:**
> What organism is taxonomy ID 5833?

**Claude's Process:**
1. Executes: `python resolve_taxonomy.py --tax-id 5833`
2. Returns result

**Expected Output:**
```
Taxonomy ID: 5833
Scientific Name: Plasmodium falciparum
Common Name: malaria parasite P. falciparum
Rank: species
```

---

## Example 6: Broad to Specific

**User Input:**
> Find data for bacteria

**Claude's Process:**
1. Recognizes "bacteria" is FAR too broad
2. Does NOT call any APIs

**Claude's Response:**
> "Bacteria" is a very broad category with millions of species. Could you specify which bacterium you're interested in? For example:
> - A specific genus (like *Escherichia*, *Salmonella*, *Staphylococcus*)?
> - A specific species (like *E. coli*, *S. aureus*)?
> - A particular application or context (gut bacteria, pathogenic bacteria, etc.)?

---

## Example 7: Spelling Variation

**User Input:**
> Search for Saccharomyces cerevisae

**Claude's Process:**
1. Executes: `python resolve_taxonomy.py "Saccharomyces cerevisae"`
2. Gets no results (misspelling: "cerevisae" vs "cerevisiae")
3. Suggests correction

**Claude's Response:**
> I couldn't find "Saccharomyces cerevisae" in NCBI. Did you mean **Saccharomyces cerevisiae** (baker's yeast)? That's a common spelling variation.

---

## Example 8: Assembly Search

**User Input:**
> Find genome assemblies for zebrafish

**Claude's Process:**
1. Recognizes "zebrafish" → *Danio rerio* (common, unambiguous)
2. Executes: `python resolve_taxonomy.py "Danio rerio"`
3. Executes: `python search_ena.py "Danio rerio" --data-type assembly`
4. Returns results with assembly accessions

---

## Example 9: Multiple Searches

**User Input:**
> Compare the number of FASTQ datasets available for human, mouse, and fruit fly

**Claude's Process:**
1. All three are unambiguous common names
2. Executes three searches:
   - `python search_ena.py "Homo sapiens" --data-type fastq`
   - `python search_ena.py "Mus musculus" --data-type fastq`
   - `python search_ena.py "Drosophila melanogaster" --data-type fastq`
3. Compares the counts and presents a summary

---

## Example 10: Network Error Handling

**User Input:**
> Get taxonomy for Arabidopsis thaliana

**If network access is not configured:**

**Claude's Process:**
1. Executes: `python resolve_taxonomy.py "Arabidopsis thaliana"`
2. Receives network error
3. Reports the issue with solution

**Claude's Response:**
> I encountered a network error while trying to query the NCBI Taxonomy database. This means the required domain `api.ncbi.nlm.nih.gov` needs to be added to the network allowlist.
>
> You can add this domain in your Claude environment's network settings. Once that's configured, I'll be able to retrieve the taxonomy information.

---

## Anti-Patterns (What Claude Should NOT Do)

### ❌ Don't Make Up Taxonomy IDs
```
User: What's the taxonomy ID for cloud bacteria?
Claude: The taxonomy ID for cloud bacteria is 12345. ❌ WRONG
```

**Correct Behavior:**
```
Claude: I don't know "cloud bacteria" off the top of my head. Let me check the NCBI database.
[Executes resolve_taxonomy.py]
[If not found:] I couldn't find "cloud bacteria" in NCBI. Could you provide more details?
```

### ❌ Don't Skip Disambiguation
```
User: Find E. coli data
Claude: [Immediately searches without asking which strain] ❌ WRONG
```

**Correct Behavior:**
```
Claude: E. coli is a species with many strains. Which one are you interested in?
- K-12 (lab strain)
- O157:H7 (pathogenic)
- Other specific strain?
```

### ❌ Don't Lecture About Taxonomy
```
User: What's the taxonomy for mouse?
Claude: Well, first you need to understand that 'mouse' is ambiguous because there are many species in the family Muridae, and without proper binomial nomenclature, I cannot... ❌ WRONG (too formal/pedantic)
```

**Correct Behavior:**
```
Claude: Do you mean house mouse (Mus musculus)? That's the most common one, often used in research.
```

---

## Key Principles Demonstrated

1. **Disambiguate conversationally** - Ask friendly questions, not lectures
2. **Use APIs for validation** - Never invent data
3. **Be helpful with errors** - Suggest solutions and alternatives
4. **Species-level is the target** - But accept more specific (strains) or broader (genus) when appropriate
5. **Let the user guide specificity** - Don't assume what they want

---

## Testing These Examples

You can test any of these patterns by:

1. Installing the skill
2. Asking Claude the example questions
3. Observing whether it follows the expected process

The skill should make Claude behave consistently with these examples.
