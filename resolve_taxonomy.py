#!/usr/bin/env python3
"""
NCBI Taxonomy Resolver

Resolves organism names to taxonomy IDs and retrieves taxonomic information
from the NCBI Taxonomy database.

Usage:
    python resolve_taxonomy.py "Plasmodium falciparum"
    python resolve_taxonomy.py --tax-id 5833
    python resolve_taxonomy.py "Homo sapiens" --format json
    python resolve_taxonomy.py "Mus musculus" --detailed
"""

import sys
import json
import argparse
from urllib import request, parse, error
from typing import Dict, List, Optional


class NCBITaxonomyResolver:
    """Handler for NCBI Taxonomy API queries."""
    
    BASE_URL = "https://api.ncbi.nlm.nih.gov"
    
    def __init__(self):
        self.session_headers = {
            'User-Agent': 'Claude-TaxonomyResolver/1.0',
            'Accept': 'application/json'
        }
    
    def search_by_name(self, organism_name: str) -> Optional[Dict]:
        """
        Search for an organism by name and return taxonomy information.
        
        Args:
            organism_name: Scientific or common name of the organism
            
        Returns:
            Dictionary with taxonomy information or None if not found
        """
        # First, search for the taxonomy ID
        search_url = f"{self.BASE_URL}/datasets/v2/taxonomy/taxon_suggest/{parse.quote(organism_name)}"
        
        try:
            req = request.Request(search_url, headers=self.session_headers)
            with request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if not data.get('sci_name_and_ids'):
                    return None
                
                # Get the first (most relevant) result
                results = data['sci_name_and_ids']
                if not results:
                    return None
                
                top_result = results[0]
                tax_id = top_result.get('tax_id')
                
                if not tax_id:
                    return None
                
                # Now get detailed information for this tax ID
                return self.get_by_tax_id(tax_id)
                
        except error.URLError as e:
            return {'error': f'Network error: {str(e)}', 'suggestion': 'Check network settings and ensure api.ncbi.nlm.nih.gov is allowlisted'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
    
    def get_by_tax_id(self, tax_id: int) -> Optional[Dict]:
        """
        Get detailed taxonomy information by taxonomy ID.
        
        Args:
            tax_id: NCBI taxonomy ID
            
        Returns:
            Dictionary with detailed taxonomy information
        """
        detail_url = f"{self.BASE_URL}/datasets/v2/taxonomy/taxon/{tax_id}"
        
        try:
            req = request.Request(detail_url, headers=self.session_headers)
            with request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'taxonomy_nodes' not in data or not data['taxonomy_nodes']:
                    return None
                
                node = data['taxonomy_nodes'][0]
                taxonomy = node.get('taxonomy', {})

                # Get common name from multiple possible fields
                common_name = None
                if taxonomy.get('common_names'):
                    common_name = taxonomy['common_names'][0]
                elif taxonomy.get('genbank_common_name'):
                    common_name = taxonomy['genbank_common_name']

                return {
                    'tax_id': taxonomy.get('tax_id'),
                    'scientific_name': taxonomy.get('organism_name'),
                    'common_name': common_name,
                    'rank': taxonomy.get('rank'),
                    'lineage': taxonomy.get('lineage', []),
                    'parent_tax_id': taxonomy.get('parent_tax_id')
                }
                
        except error.URLError as e:
            return {'error': f'Network error: {str(e)}', 'suggestion': 'Check network settings and ensure api.ncbi.nlm.nih.gov is allowlisted'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}


def format_output(data: Dict, format_type: str = 'human', detailed: bool = False) -> str:
    """
    Format the taxonomy data for output.
    
    Args:
        data: Taxonomy data dictionary
        format_type: 'json' or 'human'
        detailed: Include full lineage information
        
    Returns:
        Formatted string
    """
    if 'error' in data:
        if format_type == 'json':
            return json.dumps(data, indent=2)
        else:
            error_msg = data['error']
            suggestion = data.get('suggestion', '')
            return f"Error: {error_msg}\n{suggestion}"
    
    if format_type == 'json':
        return json.dumps(data, indent=2)
    
    # Human-readable format
    output = []
    output.append(f"Taxonomy ID: {data['tax_id']}")
    output.append(f"Scientific Name: {data['scientific_name']}")
    
    if data.get('common_name'):
        output.append(f"Common Name: {data['common_name']}")
    
    output.append(f"Rank: {data['rank']}")

    if detailed and data.get('lineage'):
        output.append(f"\nLineage (taxonomy IDs): {', '.join(map(str, data['lineage']))}")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Resolve organism names to NCBI taxonomy IDs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python resolve_taxonomy.py "Plasmodium falciparum"
  python resolve_taxonomy.py --tax-id 5833
  python resolve_taxonomy.py "Homo sapiens" --format json
  python resolve_taxonomy.py "Mus musculus" --detailed
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('organism_name', nargs='?', help='Organism name to resolve')
    group.add_argument('--tax-id', type=int, help='Taxonomy ID to look up')
    
    parser.add_argument('--format', choices=['human', 'json'], default='human',
                       help='Output format (default: human)')
    parser.add_argument('--detailed', action='store_true',
                       help='Include detailed lineage information')
    
    args = parser.parse_args()
    
    resolver = NCBITaxonomyResolver()
    
    if args.tax_id:
        result = resolver.get_by_tax_id(args.tax_id)
    else:
        result = resolver.search_by_name(args.organism_name)
    
    if result is None:
        if args.format == 'json':
            print(json.dumps({'error': 'No results found'}))
        else:
            print(f"No results found for '{args.organism_name if args.organism_name else args.tax_id}'")
        sys.exit(1)
    
    print(format_output(result, args.format, args.detailed))
    sys.exit(0 if 'error' not in result else 1)


if __name__ == '__main__':
    main()
