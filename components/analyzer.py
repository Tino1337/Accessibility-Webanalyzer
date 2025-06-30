"""
Main accessibility analyzer class - simplified version.
"""

import time
from urllib.parse import urlparse
from .page_discovery import PageDiscovery
from .accessibility_checks import AccessibilityChecker
from .report_generator import ReportGenerator
from .utils import detect_technologies


class AccessibilityAnalyzer:
    def __init__(self, url, max_pages=10):
        self.base_url = url
        self.max_pages = max_pages
        self.analyzed_pages = []
        self.issues = {
            'MANDATORY': [],
            'SHOULD DO': [],
            'NICE TO HAVE': []
        }
        self.detailed_findings = []
        self.page_stats = {}
        self.technologies = {}
        
        # Initialize components
        self.page_discovery = PageDiscovery()
        self.checker = AccessibilityChecker()
        self.report_generator = ReportGenerator()
        
    def run_analysis(self):
        """Run complete accessibility analysis"""
        print(f"Starting accessibility analysis for: {self.base_url}")
        
        # Detect technologies
        print("Detecting website technologies...")
        self.technologies = detect_technologies(self.base_url)
        
        # Discover pages
        pages = self.page_discovery.get_pages_to_analyze(self.base_url, self.max_pages)
        print(f"Found {len(pages)} pages to analyze:")
        for page in pages[:10]:
            page_path = urlparse(page).path or '/'
            print(f"  ✓ {page_path}")
        if len(pages) > 10:
            print(f"  ... and {len(pages) - 10} more pages")
        
        # Analyze each page
        for i, page in enumerate(pages):
            try:
                print(f"Analyzing page {i+1}/{len(pages)}: {urlparse(page).path or 'Homepage'}")
                page_issues = self.checker.analyze_page(page)
                
                # Add page context to issues
                for issue in page_issues:
                    issue['page'] = page
                    issue['page_title'] = urlparse(page).path or 'Homepage'
                
                self.detailed_findings.extend(page_issues)
                self.analyzed_pages.append(page)
                time.sleep(0.5)  # Be nice to the server
                
            except Exception as e:
                print(f"Error analyzing {page}: {e}")
                continue
        
        print("Consolidating issues...")
        self._consolidate_issues()
        
        print(f"Found issues:")
        for category, issues in self.issues.items():
            print(f"  {category}: {len(issues)} issues")
    
    def _consolidate_issues(self):
        """Consolidate redundant issues across pages"""
        consolidated = {
            'MANDATORY': {},
            'SHOULD DO': {},
            'NICE TO HAVE': {}
        }
        
        # Group issues by type and category
        for issue in self.detailed_findings:
            category = issue['category']
            issue_type = issue['type']
            
            if issue_type not in consolidated[category]:
                consolidated[category][issue_type] = {
                    'type': issue_type,
                    'category': category,
                    'pages': [],
                    'total_count': 0,
                    'total_hours': 0,
                    'details': [],
                    'wcag_criterion': issue.get('wcag_criterion', ''),
                    'impact': issue.get('impact', ''),
                    'descriptions': []
                }
            
            # Add page info
            page_name = urlparse(issue['page']).path or 'Homepage'
            consolidated[category][issue_type]['pages'].append(page_name)
            consolidated[category][issue_type]['total_count'] += issue['count']
            consolidated[category][issue_type]['total_hours'] += issue['effort_hours']
            consolidated[category][issue_type]['descriptions'].append(issue['description'])
            
            # Add unique details
            for detail in issue.get('details', []):
                if detail not in consolidated[category][issue_type]['details']:
                    consolidated[category][issue_type]['details'].append(detail)
        
        # Convert back to list format
        self.issues = {'MANDATORY': [], 'SHOULD DO': [], 'NICE TO HAVE': []}
        
        for category in consolidated:
            for issue_type, issue_data in consolidated[category].items():
                unique_pages = list(set(issue_data['pages']))
                page_count = len(unique_pages)
                
                # Create consolidated description
                if page_count > 1:
                    description = f"Auf {page_count} Seiten: {issue_data['descriptions'][0]}"
                    page_info = f"Betroffen: {', '.join(unique_pages[:3])}"
                    if len(unique_pages) > 3:
                        page_info += "..."
                else:
                    description = issue_data['descriptions'][0]
                    page_info = f"Seite: {unique_pages[0]}"
                
                consolidated_issue = {
                    'type': issue_data['type'],
                    'category': issue_data['category'],
                    'description': description,
                    'count': issue_data['total_count'],
                    'effort_hours': issue_data['total_hours'],
                    'details': [page_info] + issue_data['details'][:4],
                    'wcag_criterion': issue_data['wcag_criterion'],
                    'impact': issue_data['impact'],
                    'page_count': page_count
                }
                
                self.issues[category].append(consolidated_issue)
    
    def generate_pdf_report(self, filename=None):
        """Generate PDF report"""
        return self.report_generator.generate_pdf_report(
            base_url=self.base_url,
            analyzed_pages=self.analyzed_pages,
            issues=self.issues,
            technologies=self.technologies,
            filename=filename
        )