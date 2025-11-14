# Changelog

All notable changes to the taxonomy-resolver skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-22

### Added
- Initial release of taxonomy-resolver skill
- NCBI Taxonomy API integration via `resolve_taxonomy.py`
  - Resolve organism names to taxonomy IDs
  - Lookup taxonomy IDs to get organism information
  - Retrieve taxonomic lineage
  - Support for both scientific and common names
- ENA (European Nucleotide Archive) search via `search_ena.py`
  - Search for FASTQ/read run data
  - Search for genome assemblies
  - Search for WGS sequences
  - Search for studies and samples
  - Customizable result limits and pagination
- Disambiguation workflow
  - Conversational clarification prompts
  - Species-level resolution guidance
  - Common name handling
- Comprehensive documentation
  - SKILL.md with detailed instructions for Claude
  - README.md with full documentation
  - QUICKSTART.md for rapid deployment
  - EXAMPLES.md with usage patterns
  - CHANGELOG.md (this file)
- Testing infrastructure
  - test_skill.sh for automated testing
  - Example commands and expected outputs
- Error handling
  - Network error detection and guidance
  - Graceful handling of API failures
  - Helpful suggestions for common issues

### Design Principles
- API-first validation (let NCBI/ENA do the heavy lifting)
- Conversational disambiguation (friendly, not pedantic)
- Progressive disclosure (load only what's needed)
- Clear error reporting with actionable solutions

### Requirements
- Python 3.6 or higher
- Network access to:
  - api.ncbi.nlm.nih.gov (NCBI Taxonomy API)
  - www.ebi.ac.uk (ENA API)

### Acknowledgments
- Developed based on requirements from Dave Rogers and Danielle Callan
- Follows Anthropic Skills best practices
- Inspired by the BRC codeathon taxonomy resolver project

## [Unreleased]

### Planned Features
- Additional database integrations (NCBI SRA, GenBank)
- Batch processing for multiple organisms
- Caching to reduce API calls
- Support for taxonomy ID validation across queries
- Enhanced lineage visualization
- Integration with additional genomic databases
- Performance metrics and accuracy tracking

### Known Issues
- Network access must be manually configured (not auto-detected)
- No offline mode or caching yet
- Limited to read-only operations (no write/update capabilities)

### Future Considerations
- Integration with other BRC tools
- Support for custom taxonomy mappings
- Real-time taxonomy ID monitoring
- Automated testing with mock APIs
- Docker container for isolated testing
