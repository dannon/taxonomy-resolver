#!/usr/bin/env python3
"""
IWC (Intergalactic Workflow Commission) Workflow Search Tool

Fetches and searches the IWC workflow manifest for Galaxy workflows.
The LLM will interpret workflow descriptions to match them to organisms.

Usage:
    python search_iwc_workflows.py --list-categories
    python search_iwc_workflows.py --category "Variant Calling"
    python search_iwc_workflows.py --category "Transcriptomics" --format json
    python search_iwc_workflows.py --limit 10
"""

import sys
import json
import argparse
from urllib import request, error
from typing import Dict, List, Optional


class IWCWorkflowSearcher:
    """Handler for IWC workflow manifest queries."""
    
    MANIFEST_URL = "https://iwc.galaxyproject.org/workflow_manifest.json"
    
    # Category mappings
    CATEGORIES = [
        "Variant Calling",
        "Transcriptomics",
        "Epigenetics",
        "Genome assembly",
        "Virology",
        "Genome Annotation",
        "Metagenomics",
        "Proteomics",
    ]
    
    def __init__(self):
        self.session_headers = {
            'User-Agent': 'Claude-IWCWorkflowSearcher/1.0',
            'Accept': 'application/json'
        }
        self._manifest_cache = None
    
    def _fetch_manifest(self) -> List[Dict]:
        """
        Fetch the IWC workflow manifest.
        
        Returns:
            List of workflow repositories with their workflows
        """
        if self._manifest_cache is not None:
            return self._manifest_cache
        
        try:
            req = request.Request(self.MANIFEST_URL, headers=self.session_headers)
            with request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                self._manifest_cache = data
                return data
        except error.HTTPError as e:
            raise Exception(f'HTTP error {e.code}: {e.reason}')
        except error.URLError as e:
            raise Exception(f'Network error: {str(e)}. Ensure iwc.galaxyproject.org is accessible.')
        except Exception as e:
            raise Exception(f'Unexpected error fetching manifest: {str(e)}')
    
    def _extract_workflows(self, manifest: List[Dict]) -> List[Dict]:
        """
        Extract all workflows from the manifest.
        
        Args:
            manifest: Raw manifest data
            
        Returns:
            List of workflow dictionaries with metadata
        """
        workflows = []
        
        for repo in manifest:
            for workflow in repo.get('workflows', []):
                # Skip workflows without tests (incomplete)
                if 'tests' not in workflow:
                    continue
                
                definition = workflow.get('definition', {})
                
                workflows.append({
                    'name': definition.get('name', 'Unknown'),
                    'description': definition.get('annotation', ''),
                    'trs_id': workflow.get('trsID', ''),
                    'iwc_id': workflow.get('iwcID', ''),
                    'release': definition.get('release', ''),
                    'categories': workflow.get('collections', []),
                    'license': definition.get('license', ''),
                    'creators': definition.get('creator', []),
                    'tags': definition.get('tags', []),
                })
        
        return workflows
    
    def _filter_by_category(self, workflows: List[Dict], category: str) -> List[Dict]:
        """
        Filter workflows by category.
        
        Args:
            workflows: List of workflow dictionaries
            category: Category to filter by
            
        Returns:
            Filtered list of workflows
        """
        if not category:
            return workflows
        
        return [
            w for w in workflows 
            if any(category.lower() in cat.lower() for cat in w.get('categories', []))
        ]
    
    
    def search(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict:
        """
        Search IWC workflows.
        
        Args:
            category: Workflow category to filter by (optional)
            limit: Maximum number of results to return (optional, no limit if None)
            
        Returns:
            Dictionary with search results
        """
        try:
            manifest = self._fetch_manifest()
            workflows = self._extract_workflows(manifest)
            
            # Apply category filter if specified
            if category:
                workflows = self._filter_by_category(workflows, category)
            
            # Apply limit if specified
            if limit is not None:
                workflows = workflows[:limit]
            
            return {
                'success': True,
                'category': category,
                'count': len(workflows),
                'workflows': workflows
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'suggestion': 'Check network settings and ensure iwc.galaxyproject.org is accessible'
            }
    
    def list_categories(self) -> Dict:
        """
        List all available workflow categories.
        
        Returns:
            Dictionary with category information
        """
        try:
            manifest = self._fetch_manifest()
            workflows = self._extract_workflows(manifest)
            
            # Collect all unique categories
            categories = set()
            for workflow in workflows:
                categories.update(workflow.get('categories', []))
            
            return {
                'success': True,
                'categories': sorted(list(categories)),
                'count': len(categories)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def format_output(data: Dict, format_type: str = 'human') -> str:
    """
    Format the search results for output.
    
    Args:
        data: Search results dictionary
        format_type: 'json' or 'human'
        
    Returns:
        Formatted string
    """
    if format_type == 'json':
        return json.dumps(data, indent=2)
    
    if not data.get('success'):
        error_msg = data.get('error', 'Unknown error')
        suggestion = data.get('suggestion', '')
        return f"Error: {error_msg}\n{suggestion}"
    
    # Handle category listing
    if 'categories' in data:
        output = []
        output.append(f"Available Workflow Categories ({data.get('count', 0)}):")
        output.append("="*60)
        for category in data['categories']:
            output.append(f"  - {category}")
        return '\n'.join(output)
    
    # Human-readable format for workflow search
    output = []
    if data.get('category'):
        output.append(f"Category Filter: {data['category']}")
    output.append(f"Workflows Found: {data.get('count', 0)}")
    
    if data.get('workflows'):
        output.append("\n" + "="*60)
        output.append("WORKFLOWS")
        output.append("="*60)
        
        for i, workflow in enumerate(data['workflows'], 1):
            output.append(f"\nWorkflow {i}:")
            output.append(f"  Name: {workflow.get('name', 'N/A')}")
            
            if workflow.get('description'):
                desc = workflow['description']
                if len(desc) > 150:
                    desc = desc[:147] + '...'
                output.append(f"  Description: {desc}")
            
            if workflow.get('categories'):
                output.append(f"  Categories: {', '.join(workflow['categories'])}")
            
            output.append(f"  TRS ID: {workflow.get('trs_id', 'N/A')}")
            
            if workflow.get('iwc_id'):
                output.append(f"  IWC ID: {workflow['iwc_id']}")
            
            if workflow.get('release'):
                output.append(f"  Release: v{workflow['release']}")
            
            if workflow.get('tags'):
                output.append(f"  Tags: {', '.join(workflow['tags'][:5])}")
            
            output.append("-"*60)
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch IWC (Intergalactic Workflow Commission) workflows. The LLM will interpret workflow descriptions to match them to organisms.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_iwc_workflows.py --list-categories
  python search_iwc_workflows.py --category "Variant Calling"
  python search_iwc_workflows.py --category "Transcriptomics" --limit 10
  python search_iwc_workflows.py --format json
        """
    )
    
    parser.add_argument('--category', help='Filter by workflow category (optional)')
    parser.add_argument('--limit', type=int,
                       help='Maximum number of results to return (optional, returns all if not specified)')
    parser.add_argument('--format', choices=['human', 'json'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--list-categories', action='store_true',
                       help='List all available workflow categories')
    
    args = parser.parse_args()
    
    searcher = IWCWorkflowSearcher()
    
    # Handle category listing
    if args.list_categories:
        result = searcher.list_categories()
        print(format_output(result, args.format))
        sys.exit(0 if result.get('success') else 1)
    
    # Fetch workflows (optionally filtered by category)
    result = searcher.search(
        category=args.category,
        limit=args.limit
    )
    
    print(format_output(result, args.format))
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
