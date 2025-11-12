#!/usr/bin/env python3
"""
ENA BioProject Details Fetcher

Queries ENA for detailed information about a bioproject (study), including
description, title, and other metadata.

Usage:
    python get_bioproject_details.py PRJEB1234
    python get_bioproject_details.py PRJNA123456 --format json
    python get_bioproject_details.py PRJEB1234 PRJNA456789
"""

import sys
import json
import argparse
from urllib import request, parse, error
from typing import Dict, List


class BioprojectDetailsFetcher:
    """Handler for fetching bioproject details from ENA."""
    
    BASE_URL = "https://www.ebi.ac.uk/ena/portal/api"
    
    def __init__(self):
        self.session_headers = {
            'User-Agent': 'Claude-BioprojectFetcher/1.0',
            'Accept': 'application/json'
        }
    
    def get_details(self, bioproject_accession: str) -> Dict:
        """
        Get detailed information about a bioproject.
        
        Args:
            bioproject_accession: BioProject accession (e.g., PRJEB1234, PRJNA123456)
            
        Returns:
            Dictionary with bioproject details
        """
        # Fields to retrieve for study details
        fields = [
            'study_accession',
            'study_title',
            'study_description',
            'study_alias',
            'center_name',
            'first_public',
            'last_updated',
            'scientific_name',
            'tax_id'
        ]
        
        # Build query URL
        params = {
            'result': 'study',
            'query': f'study_accession={bioproject_accession}',
            'format': 'json',
            'fields': ','.join(fields)
        }
        
        search_url = f"{self.BASE_URL}/search?{parse.urlencode(params)}"
        
        try:
            req = request.Request(search_url, headers=self.session_headers)
            with request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if isinstance(data, list) and len(data) > 0:
                    return {
                        'success': True,
                        'accession': bioproject_accession,
                        'details': data[0]
                    }
                else:
                    return {
                        'success': False,
                        'accession': bioproject_accession,
                        'error': 'BioProject not found',
                        'suggestion': 'Check that the accession is correct'
                    }
                    
        except error.HTTPError as e:
            if e.code == 204:
                return {
                    'success': False,
                    'accession': bioproject_accession,
                    'error': 'BioProject not found',
                    'suggestion': 'Check that the accession is correct'
                }
            return {
                'success': False,
                'accession': bioproject_accession,
                'error': f'HTTP error {e.code}: {e.reason}',
                'suggestion': 'Try again or check the accession'
            }
        except error.URLError as e:
            return {
                'success': False,
                'accession': bioproject_accession,
                'error': f'Network error: {str(e)}',
                'suggestion': 'Check network settings and ensure www.ebi.ac.uk is allowlisted'
            }
        except Exception as e:
            return {
                'success': False,
                'accession': bioproject_accession,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def get_multiple_details(self, accessions: List[str]) -> Dict:
        """
        Get details for multiple bioprojects.
        
        Args:
            accessions: List of bioproject accessions
            
        Returns:
            Dictionary with results for each accession
        """
        results = []
        for accession in accessions:
            result = self.get_details(accession)
            results.append(result)
        
        return {
            'success': True,
            'count': len(results),
            'results': results
        }


def format_output(data: Dict, format_type: str = 'human') -> str:
    """
    Format the bioproject details for output.
    
    Args:
        data: Bioproject details dictionary
        format_type: 'json' or 'human'
        
    Returns:
        Formatted string
    """
    if format_type == 'json':
        return json.dumps(data, indent=2)
    
    # Handle multiple results
    if 'results' in data:
        output = []
        output.append(f"Retrieved details for {data['count']} BioProject(s)")
        output.append("="*60)
        
        for result in data['results']:
            if result['success']:
                details = result['details']
                output.append(f"\nBioProject: {result['accession']}")
                output.append(f"Title: {details.get('study_title', 'N/A')}")
                
                description = details.get('study_description', 'N/A')
                if description and len(description) > 200:
                    description = description[:197] + '...'
                output.append(f"Description: {description}")
                
                output.append(f"Organism: {details.get('scientific_name', 'N/A')} (Tax ID: {details.get('tax_id', 'N/A')})")
                output.append(f"Center: {details.get('center_name', 'N/A')}")
                output.append(f"First Public: {details.get('first_public', 'N/A')}")
                output.append(f"Last Updated: {details.get('last_updated', 'N/A')}")
            else:
                output.append(f"\nBioProject: {result['accession']}")
                output.append(f"Error: {result.get('error', 'Unknown error')}")
                if result.get('suggestion'):
                    output.append(f"Suggestion: {result['suggestion']}")
            
            output.append("-"*60)
        
        return '\n'.join(output)
    
    # Handle single result
    if not data.get('success'):
        error_msg = data.get('error', 'Unknown error')
        suggestion = data.get('suggestion', '')
        return f"Error: {error_msg}\n{suggestion}"
    
    details = data['details']
    output = []
    output.append(f"BioProject: {data['accession']}")
    output.append("="*60)
    output.append(f"Title: {details.get('study_title', 'N/A')}")
    
    description = details.get('study_description', 'N/A')
    output.append("\nDescription:")
    output.append(description)
    
    output.append(f"\nOrganism: {details.get('scientific_name', 'N/A')} (Tax ID: {details.get('tax_id', 'N/A')})")
    output.append(f"Center: {details.get('center_name', 'N/A')}")
    output.append(f"Alias: {details.get('study_alias', 'N/A')}")
    output.append(f"First Public: {details.get('first_public', 'N/A')}")
    output.append(f"Last Updated: {details.get('last_updated', 'N/A')}")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Get detailed information about BioProjects from ENA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_bioproject_details.py PRJEB1234
  python get_bioproject_details.py PRJNA123456 --format json
  python get_bioproject_details.py PRJEB1234 PRJNA456789
  
Note: Accepts both PRJEB (ENA) and PRJNA (NCBI) accessions.
        """
    )
    
    parser.add_argument('accessions', nargs='+',
                       help='BioProject accession(s) to look up')
    parser.add_argument('--format', choices=['human', 'json'], default='human',
                       help='Output format (default: human)')
    
    args = parser.parse_args()
    
    fetcher = BioprojectDetailsFetcher()
    
    if len(args.accessions) == 1:
        result = fetcher.get_details(args.accessions[0])
    else:
        result = fetcher.get_multiple_details(args.accessions)
    
    print(format_output(result, args.format))
    
    # Exit with error code if any lookups failed
    if 'results' in result:
        success = all(r['success'] for r in result['results'])
    else:
        success = result.get('success', False)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
