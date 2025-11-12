#!/usr/bin/env python3
"""
ENA (European Nucleotide Archive) Search Tool

Searches ENA for genomic data including FASTQ files, assemblies, and other datasets.

Usage:
    python search_ena.py "Plasmodium falciparum"
    python search_ena.py "Mus musculus" --data-type fastq
    python search_ena.py "Escherichia coli" --limit 20
    python search_ena.py "Homo sapiens" --format json
"""

import sys
import json
import argparse
from urllib import request, parse, error
from typing import Dict, List, Optional


class ENASearcher:
    """Handler for ENA (European Nucleotide Archive) API queries."""
    
    BASE_URL = "https://www.ebi.ac.uk/ena/portal/api"
    
    # ENA result types
    RESULT_TYPES = {
        'read': 'read_run',           # FASTQ/read data
        'fastq': 'read_run',          # Alias for read
        'assembly': 'assembly',       # Genome assemblies
        'wgs': 'wgs_set',            # Whole genome shotgun
        'sequence': 'sequence',       # Nucleotide sequences
        'study': 'study',            # Study metadata
        'sample': 'sample',          # Sample metadata
        'analysis': 'analysis',      # Analysis objects
        'taxon': 'taxon'            # Taxonomy information
    }
    
    def __init__(self):
        self.session_headers = {
            'User-Agent': 'Claude-ENASearcher/1.0',
            'Accept': 'application/json'
        }

    def _format_query(self, query: str) -> str:
        """
        Format query for ENA API.

        ENA requires specific query syntax:
        - tax_eq(taxid) for exact taxonomy match
        - tax_tree(taxid) for taxonomy and descendants
        - field="value" for text searches

        Args:
            query: User query (taxonomy ID, organism name, or ENA query syntax)

        Returns:
            Properly formatted ENA query
        """
        # If query already uses ENA syntax, return as-is
        if any(op in query for op in ['tax_eq', 'tax_tree', 'study_accession', 'sample_accession', 'run_accession', '=']):
            return query

        # If query is a number, treat as taxonomy ID
        if query.strip().isdigit():
            return f'tax_tree({query.strip()})'

        # Otherwise, search by scientific_name field
        # This works across all result types (read_run, assembly, etc.)
        return f'scientific_name="{query}"'

    def _group_by_bioproject(self, results: List[Dict]) -> List[Dict]:
        """
        Group read run results by bioproject (study_accession).
        
        Args:
            results: List of read run results
            
        Returns:
            List of bioproject groups with accession, read count, and runs
        """
        from collections import defaultdict
        
        bioprojects = defaultdict(lambda: {'runs': [], 'study_title': None})
        
        for result in results:
            study_acc = result.get('study_accession', 'Unknown')
            bioprojects[study_acc]['runs'].append(result)
            # Capture study title if available
            if result.get('study_title') and not bioprojects[study_acc]['study_title']:
                bioprojects[study_acc]['study_title'] = result.get('study_title')
        
        # Convert to list format
        grouped = []
        for study_acc, data in bioprojects.items():
            grouped.append({
                'bioproject_accession': study_acc,
                'read_count': len(data['runs']),
                'study_title': data['study_title'],
                'runs': data['runs']
            })
        
        # Sort by read count (descending)
        grouped.sort(key=lambda x: x['read_count'], reverse=True)
        
        return grouped
    
    def search(
        self,
        query: str,
        result_type: str = 'read_run',
        limit: int = 10,
        offset: int = 0,
        fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Search ENA for genomic data.
        
        Args:
            query: Search query (organism name, accession, etc.)
            result_type: Type of results to return (read_run, assembly, etc.)
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            fields: Specific fields to return (None = default fields)
            
        Returns:
            Dictionary with search results
        """
        # Default fields for different result types
        default_fields = {
            'read_run': [
                'run_accession', 'study_accession', 'sample_accession',
                'scientific_name', 'instrument_platform', 'library_layout',
                'fastq_ftp', 'fastq_bytes', 'library_strategy', 'study_title'
            ],
            'assembly': [
                'accession', 'scientific_name', 'assembly_level',
                'genome_representation', 'assembly_name', 'assembly_title'
            ],
            'study': [
                'study_accession', 'study_title', 'study_alias',
                'scientific_name', 'study_description'
            ],
            'sample': [
                'sample_accession', 'scientific_name', 'collection_date',
                'country', 'host', 'isolation_source'
            ]
        }
        
        if fields is None:
            fields = default_fields.get(result_type, ['accession', 'scientific_name'])

        # Format the query for ENA API
        formatted_query = self._format_query(query)

        # Build the query URL
        params = {
            'result': result_type,
            'query': formatted_query,
            'limit': limit,
            'offset': offset,
            'format': 'json',
            'fields': ','.join(fields)
        }
        
        search_url = f"{self.BASE_URL}/search?{parse.urlencode(params)}"
        
        try:
            req = request.Request(search_url, headers=self.session_headers)
            with request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                results = data if isinstance(data, list) else []
                
                # Group by bioproject if this is a read_run search
                if result_type == 'read_run' and results:
                    grouped = self._group_by_bioproject(results)
                    return {
                        'success': True,
                        'query': query,
                        'result_type': result_type,
                        'count': len(results),
                        'total_bioprojects': len(grouped),
                        'results': results,
                        'grouped_by_bioproject': grouped
                    }
                
                return {
                    'success': True,
                    'query': query,
                    'result_type': result_type,
                    'count': len(results),
                    'results': results
                }
                
        except error.HTTPError as e:
            if e.code == 204:
                return {
                    'success': True,
                    'query': query,
                    'result_type': result_type,
                    'count': 0,
                    'results': [],
                    'message': 'No results found'
                }
            return {
                'success': False,
                'error': f'HTTP error {e.code}: {e.reason}',
                'suggestion': 'Try a different search term or check the query syntax'
            }
        except error.URLError as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'suggestion': 'Check network settings and ensure www.ebi.ac.uk is allowlisted'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def get_fastq_urls(self, run_accession: str) -> Dict:
        """
        Get direct FASTQ download URLs for a specific run accession.
        
        Args:
            run_accession: ENA run accession (e.g., ERR123456, SRR123456)
            
        Returns:
            Dictionary with FASTQ URLs and metadata
        """
        fields = ['run_accession', 'fastq_ftp', 'fastq_md5', 'fastq_bytes']
        
        result = self.search(
            query=f'run_accession={run_accession}',
            result_type='read_run',
            limit=1,
            fields=fields
        )
        
        if not result['success'] or not result['results']:
            return {'success': False, 'error': f'Run accession {run_accession} not found'}
        
        run_data = result['results'][0]
        
        # Parse FASTQ FTP paths into downloadable URLs
        fastq_ftp = run_data.get('fastq_ftp', '')
        fastq_urls = []
        
        if fastq_ftp:
            ftp_paths = fastq_ftp.split(';')
            fastq_urls = [f'https://{path}' if not path.startswith('http') else path 
                         for path in ftp_paths]
        
        return {
            'success': True,
            'run_accession': run_data.get('run_accession'),
            'fastq_urls': fastq_urls,
            'file_sizes': run_data.get('fastq_bytes', '').split(';'),
            'md5_checksums': run_data.get('fastq_md5', '').split(';')
        }


def format_output(data: Dict, format_type: str = 'human', show_urls: bool = False) -> str:
    """
    Format the search results for output.
    
    Args:
        data: Search results dictionary
        format_type: 'json' or 'human'
        show_urls: Show download URLs (for FASTQ results)
        
    Returns:
        Formatted string
    """
    if format_type == 'json':
        return json.dumps(data, indent=2)
    
    if not data.get('success'):
        error_msg = data.get('error', 'Unknown error')
        suggestion = data.get('suggestion', '')
        return f"Error: {error_msg}\n{suggestion}"
    
    # Human-readable format
    output = []
    output.append(f"Query: {data.get('query', 'N/A')}")
    output.append(f"Result Type: {data.get('result_type', 'N/A')}")
    output.append(f"Results Found: {data.get('count', 0)}")
    
    # Show bioproject grouping summary if available
    if data.get('grouped_by_bioproject'):
        output.append(f"Total BioProjects: {data.get('total_bioprojects', 0)}")
    
    if data.get('message'):
        output.append(f"\n{data['message']}")
    
    # Display grouped by bioproject if available
    if data.get('grouped_by_bioproject'):
        output.append("\n" + "="*60)
        output.append("RESULTS GROUPED BY BIOPROJECT")
        output.append("="*60)
        
        for i, bioproject in enumerate(data['grouped_by_bioproject'], 1):
            output.append(f"\nBioProject {i}:")
            output.append(f"  Accession: {bioproject['bioproject_accession']}")
            output.append(f"  Number of Reads: {bioproject['read_count']}")
            if bioproject.get('study_title'):
                output.append(f"  Title: {bioproject['study_title']}")
            
            # Show first few runs as examples
            output.append("  Sample Runs:")
            for j, run in enumerate(bioproject['runs'][:3], 1):
                output.append(f"    {j}. {run.get('run_accession', 'N/A')} - {run.get('library_layout', 'N/A')}")
            
            if len(bioproject['runs']) > 3:
                output.append(f"    ... and {len(bioproject['runs']) - 3} more")
            
            output.append("-"*60)
        
        return '\n'.join(output)
    
    if data.get('results'):
        output.append("\n" + "="*60)
        
        for i, result in enumerate(data['results'], 1):
            output.append(f"\nResult {i}:")
            
            # Format each field nicely
            for key, value in result.items():
                if value:  # Only show non-empty fields
                    # Clean up the field name for display
                    display_key = key.replace('_', ' ').title()
                    
                    # Handle FTP paths specially
                    if 'ftp' in key.lower() and show_urls:
                        if ';' in str(value):
                            urls = value.split(';')
                            output.append(f"  {display_key}:")
                            for url in urls:
                                if not url.startswith('http'):
                                    url = f'https://{url}'
                                output.append(f"    - {url}")
                        else:
                            if not value.startswith('http'):
                                value = f'https://{value}'
                            output.append(f"  {display_key}: {value}")
                    else:
                        # Truncate long values
                        str_value = str(value)
                        if len(str_value) > 100:
                            str_value = str_value[:97] + '...'
                        output.append(f"  {display_key}: {str_value}")
            
            output.append("-"*60)
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Search ENA (European Nucleotide Archive) for genomic data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Data Types:
  read/fastq    FASTQ/read run data (default)
  assembly      Genome assemblies
  wgs           Whole genome shotgun sequences
  sequence      Nucleotide sequences
  study         Study metadata
  sample        Sample metadata
  analysis      Analysis objects

Examples:
  python search_ena.py "Plasmodium falciparum"
  python search_ena.py "Mus musculus" --data-type fastq --limit 20
  python search_ena.py "Escherichia coli" --format json
  python search_ena.py "Homo sapiens" --show-urls
  python search_ena.py "study_accession=PRJEB1234" --data-type read
        """
    )
    
    parser.add_argument('query', help='Search query (organism name, accession, etc.)')
    parser.add_argument('--data-type', '--type', 
                       choices=['read', 'fastq', 'assembly', 'wgs', 'sequence', 'study', 'sample', 'analysis'],
                       default='fastq',
                       help='Type of data to search for (default: fastq)')
    parser.add_argument('--limit', type=int, default=10,
                       help='Maximum number of results to return (default: 10)')
    parser.add_argument('--offset', type=int, default=0,
                       help='Number of results to skip (default: 0)')
    parser.add_argument('--format', choices=['human', 'json'], default='human',
                       help='Output format (default: human)')
    parser.add_argument('--show-urls', action='store_true',
                       help='Show full download URLs for FASTQ files')
    
    args = parser.parse_args()
    
    searcher = ENASearcher()
    
    # Map the data type argument to ENA result type
    result_type = searcher.RESULT_TYPES.get(args.data_type, 'read_run')
    
    result = searcher.search(
        query=args.query,
        result_type=result_type,
        limit=args.limit,
        offset=args.offset
    )
    
    print(format_output(result, args.format, args.show_urls))
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
