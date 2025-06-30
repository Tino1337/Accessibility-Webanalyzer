#!/usr/bin/env python3
"""
Website Accessibility Analyzer - Main Entry Point
Simple, clean entry point for the modular accessibility analyzer.
"""

import argparse
import sys
import os
from components.analyzer import AccessibilityAnalyzer


def main():
    """Main function to run the accessibility analyzer"""
    parser = argparse.ArgumentParser(
        description='Website Accessibility Analyzer - WCAG 2.1 AA Compliance Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://example.com
  python main.py example.com --max-pages 20
  python main.py https://mysite.com --analyze-all --output my_report.pdf
  python main.py example.com --output custom_report.pdf
        """
    )
    
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument(
        '--max-pages', 
        type=int, 
        default=10,
        help='Maximum number of pages to analyze (default: 10)'
    )
    parser.add_argument(
        '--output', 
        help='Output PDF filename (auto-generated if not specified)'
    )
    parser.add_argument(
        '--analyze-all', 
        action='store_true',
        help='Analyze all found pages (overrides --max-pages)'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Accessibility Analyzer v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate and normalize URL
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"📍 Using URL: {url}")
    
    # Set max_pages to None if analyze-all flag is used
    max_pages = None if args.analyze_all else args.max_pages
    
    # Display configuration
    print("🔍 Accessibility Web Analyzer")
    print("=" * 50)
    print(f"Target URL: {url}")
    if max_pages:
        print(f"Max Pages: {max_pages}")
    else:
        print("Max Pages: All discoverable pages")
    
    if args.output:
        print(f"Output File: {args.output}")
    print()
    
    # Create output directories if they don't exist
    os.makedirs('output/reports', exist_ok=True)
    os.makedirs('output/logs', exist_ok=True)
    os.makedirs('output/temp', exist_ok=True)
    
    try:
        # Initialize and run analyzer
        print("🚀 Initializing analyzer...")
        analyzer = AccessibilityAnalyzer(url, max_pages=max_pages)
        
        print("🔬 Running accessibility analysis...")
        analyzer.run_analysis()
        
        print("\n📄 Generating PDF report...")
        pdf_file = analyzer.generate_pdf_report(args.output)
        
        if pdf_file:
            print(f"\n🎉 Analysis complete!")
            print(f"📊 Report saved as: {pdf_file}")
            
            # Display summary
            _display_summary(analyzer)
            
            print(f"\n💡 Next steps:")
            print(f"   1. Open the PDF report: {pdf_file}")
            print(f"   2. Review MANDATORY issues first")
            print(f"   3. Implement fixes according to priority")
            print(f"   4. Re-run analysis to track progress")
            
        else:
            print("❌ Error: Failed to generate PDF report")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user")
        print("💾 Partial results may be available in output/temp/")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   - Check if the URL is accessible")
        print("   - Verify your internet connection") 
        print("   - Try with a different website")
        print("   - Check if Chrome/Chromium is installed for mobile testing")
        sys.exit(1)


def _display_summary(analyzer):
    """Display analysis summary"""
    total_issues = sum(len(issues) for issues in analyzer.issues.values())
    total_hours = sum(
        sum(issue['effort_hours'] for issue in issues)
        for issues in analyzer.issues.values()
    )
    
    print(f"\n📊 Analysis Summary:")
    print(f"   Pages analyzed: {len(analyzer.analyzed_pages)}")
    
    # Technology summary
    tech_summary = []
    if analyzer.technologies.get('cms'):
        tech_summary.extend(analyzer.technologies['cms'])
    if analyzer.technologies.get('frameworks'):
        tech_summary.extend(analyzer.technologies['frameworks'][:2])
    
    tech_text = ', '.join(tech_summary) if tech_summary else 'Not detected'
    print(f"   Technologies: {tech_text}")
    
    print(f"   Total issues: {total_issues}")
    print(f"   Estimated fix time: {total_hours:.1f} hours")
    
    # Category breakdown
    for category, issues in analyzer.issues.items():
        if issues:
            count = len(issues)
            hours = sum(issue['effort_hours'] for issue in issues)
            
            # Color coding for terminal output
            if category == 'MANDATORY':
                status = "🔴 CRITICAL"
            elif category == 'SHOULD DO':
                status = "🟡 IMPORTANT"
            else:
                status = "🟢 NICE TO HAVE"
            
            print(f"   {status}: {count} issues ({hours:.1f}h)")
    
    # Risk assessment
    mandatory_count = len(analyzer.issues['MANDATORY'])
    if mandatory_count > 5:
        risk_level = "🚨 HIGH LEGAL RISK"
    elif mandatory_count > 0:
        risk_level = "⚠️  MEDIUM RISK"
    else:
        risk_level = "✅ LOW RISK"
    
    print(f"   Legal compliance: {risk_level}")


if __name__ == "__main__":
    main()