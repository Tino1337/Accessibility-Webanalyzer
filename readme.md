# 🔍 Accessibility Web Analyzer

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![WCAG](https://img.shields.io/badge/WCAG-2.1%20AA-green.svg)](https://www.w3.org/WAI/WCAG21/quickref/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Professional WCAG 2.1 AA compliance checker with stunning PDF reports**

*Automated accessibility analysis for modern websites with comprehensive reporting and actionable insights.*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples) • [Contributing](#-contributing)

</div>

---

## 🚀 Features

### 🎯 **Comprehensive Analysis**
- **WCAG 2.1 AA Compliance** - Full standard coverage
- **Multi-page scanning** - Analyze entire websites
- **Smart page discovery** - Automatic sitemap detection
- **SPA support** - React, Vue, Nuxt.js, Next.js compatible
- **Language filtering** - Avoid duplicate analysis of translated pages

### 📱 **Advanced Testing**
- **Mobile responsiveness** - Real browser testing with Selenium
- **Touch target validation** - 44px minimum size checking  
- **Viewport analysis** - Proper mobile scaling detection
- **Screen reader compatibility** - ARIA labels and semantic structure

### 📊 **Professional Reporting**
- **Stunning PDF reports** - Client-ready documentation
- **Risk assessment** - Legal compliance evaluation  
- **Time estimates** - Realistic hour calculations for fixes
- **Priority categorization** - MANDATORY → SHOULD DO → NICE TO HAVE
- **Code examples** - Actionable implementation guidance

### 🔧 **Technical Detection**
- **Technology stack identification** - WordPress, React, Vue, etc.
- **Framework analysis** - Bootstrap, Tailwind, Foundation
- **Performance insights** - Page structure analysis

---

## 📦 Installation

### Prerequisites
- **Python 3.7+**
- **Chrome/Chromium browser** (for mobile testing)
- **Git**

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/Tino1337/Accessibility-Webanalyzer.git
cd Accessibility-Webanalyzer

# Install dependencies
pip install -r requirements.txt

# Run your first analysis
python main.py https://example.com
```

### Docker Setup (Alternative)

```bash
# Build the image
docker build -t accessibility-analyzer .

# Run analysis
docker run -v $(pwd)/output:/app/output accessibility-analyzer https://example.com
```

---

## 💻 Usage

### Basic Analysis
```bash
# Analyze a website (default: 10 pages)
python main.py https://yourwebsite.com

# Custom page limit
python main.py https://yourwebsite.com --max-pages 20

# Analyze all discoverable pages
python main.py https://yourwebsite.com --analyze-all

# Custom output filename
python main.py https://yourwebsite.com --output custom_report.pdf
```

### Advanced Options
```bash
# Show all available options
python main.py --help

# Examples with different configurations
python main.py https://example.com --max-pages 50 --output detailed_audit.pdf
python main.py https://mysite.com --analyze-all  # Discovers all pages automatically
```

### Example Output
```
🔍 Accessibility Web Analyzer
==================================================
Target URL: https://example.com
Max Pages: 10

🚀 Initializing analyzer...
Detecting website technologies...
🔍 SPA detected - trying common route patterns...
  ✓ Found SPA route: /about
  ✓ Found SPA route: /contact
🗺️ Found sitemap.xml - extracting URLs...
  ✓ Added from sitemap.xml: /services
  📄 Found 15 URLs in sitemap.xml

Found 10 pages to analyze (language pages filtered):
  ✓ /
  ✓ /about
  ✓ /contact
  ✓ /services

🔬 Running accessibility analysis...
Analyzing page 1/10: Homepage
Analyzing page 2/10: /about
...

📄 Generating PDF report...

🎉 Analysis complete!
📊 Report saved as: output/reports/accessibility_report_example.com_20250630_143022.pdf

📊 Analysis Summary:
   Pages analyzed: 10
   Technologies: WordPress, Bootstrap
   Total issues: 12
   Estimated fix time: 8.5 hours
   🔴 CRITICAL: 3 issues (4.2h)
   🟡 IMPORTANT: 7 issues (3.8h)
   🟢 NICE TO HAVE: 2 issues (0.5h)
   Legal compliance: ⚠️  MEDIUM RISK

💡 Next steps:
   1. Open the PDF report: output/reports/accessibility_report_example.com_20250630_143022.pdf
   2. Review MANDATORY issues first
   3. Implement fixes according to priority
   4. Re-run analysis to track progress
```

---

## 📋 Examples

### Sample Report Structure

#### 🔴 **MANDATORY Issues (Legal Risk)**
- Missing alt texts for images
- Form elements without labels
- Missing ARIA landmarks
- Invalid HTML structure

#### 🟡 **SHOULD DO Issues (Compliance)**  
- Heading hierarchy problems
- Color-only information
- Missing skip links
- Table accessibility

#### 🟢 **NICE TO HAVE (Optimization)**
- Enhanced navigation
- Improved mobile experience
- Performance optimizations

### Real-World Scenarios

```bash
# E-commerce site analysis
python main.py https://shop.example.com --max-pages 25

# Corporate website audit  
python main.py https://company.com --analyze-all

# Blog/content site
python main.py https://blog.example.com --max-pages 15 --output blog_audit.pdf

# Quick small site check
python main.py https://startup.com --max-pages 5
```

---

## 🛠️ Project Structure

```
accessibility-web-analyzer/
├── main.py                    # 🚀 Main entry point
├── requirements.txt           # 📦 Dependencies
├── README.md                 # 📖 This file
├── LICENSE                   # ⚖️ MIT License
├── .gitignore               # 🚫 Git ignore rules
├── components/              # 🧩 Modular code components
│   ├── __init__.py         # Package initialization
│   ├── analyzer.py         # Main analyzer orchestrator
│   ├── page_discovery.py   # Smart page finding logic
│   ├── accessibility_checks.py # All WCAG compliance checks
│   ├── report_generator.py # Professional PDF generation
│   └── utils.py            # Helper functions & tech detection
├── output/                 # 📄 Generated files (auto-created)
│   ├── reports/           # PDF reports
│   ├── logs/             # Analysis logs
│   └── temp/             # Temporary files
└── docs/                  # 📚 Documentation
    ├── installation.md   # Detailed setup guide
    ├── usage.md         # Advanced usage examples
    └── examples.md      # Real-world scenarios
```

### Modular Architecture Benefits
- **🔧 Easy to extend** - Add new checks by creating new modules
- **🧪 Testable** - Each component can be tested independently  
- **📚 Maintainable** - Clear separation of concerns
- **🤝 Contributor-friendly** - Simple to understand and modify

---

## 🛠️ Configuration

### Customizing Analysis

The analyzer automatically detects and adapts to:
- **Content Management Systems** (WordPress, Drupal, Joomla)
- **JavaScript Frameworks** (React, Vue, Angular, Svelte)
- **CSS Frameworks** (Bootstrap, Tailwind, Foundation)
- **Hosting Platforms** (Netlify, Vercel, GitHub Pages)

### Language Support
Automatically filters translated pages to avoid duplicate analysis:
- Supports 30+ language codes (en, de, fr, es, it, etc.)
- Smart detection of language-specific URLs (`/en/about`, `/de/kontakt`)

---

## 📊 Report Features

### Executive Summary
- **Compliance status** with color-coded risk levels
- **Technology stack** identification  
- **Legal risk assessment** (HIGH/MEDIUM/LOW)
- **Time investment** calculations

### Detailed Analysis
- **Issue consolidation** across multiple pages
- **WCAG criterion mapping** for each problem
- **Code examples** with before/after solutions
- **Implementation roadmap** with phases

### Business Intelligence
- **ROI insights** for accessibility investment
- **Competitive advantages** of compliance
- **Risk mitigation** strategies

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/Accessibility-Webanalyzer.git
cd Accessibility-Webanalyzer

# Create feature branch  
git checkout -b feature/amazing-new-feature

# Install development dependencies
pip install -r requirements.txt

# Test your changes
python main.py https://example.com --max-pages 3

# Make your changes and commit
git commit -m "Add amazing new feature"

# Push and create PR
git push origin feature/amazing-new-feature
```

### Areas for Contribution
- 🐛 **Bug fixes** - Report and fix issues
- ✨ **New accessibility checks** - Expand WCAG criterion coverage  
- 📚 **Documentation** - Improve guides and examples
- 🧪 **Testing** - Add test coverage for components
- 🌍 **Internationalization** - Multi-language support
- 🎨 **Report design** - Enhanced PDF styling and layout

### Adding New Accessibility Checks
```python
# Example: Add a new check in components/accessibility_checks.py
def check_custom_accessibility(self, url, soup):
    """Your custom accessibility check"""
    issues = []
    
    # Your check logic here
    if problem_detected:
        issues.append({
            'category': 'MANDATORY',  # or 'SHOULD DO', 'NICE TO HAVE'
            'type': 'Your Check Name',
            'description': 'Brief description of the issue',
            'count': 1,
            'effort_hours': 0.5,
            'details': ['Specific details about the problem'],
            'wcag_criterion': '1.1.1 Your WCAG Criterion',
            'impact': 'Description of impact on users'
        })
    
    return issues

# Then add it to the analyze_page method
def analyze_page(self, url):
    # ... existing checks ...
    issues.extend(self.check_custom_accessibility(url, soup))
```

---

## 🔧 Technical Details

### Component Architecture
```
main.py (Entry Point)
├── components/analyzer.py (Orchestrator)
│   ├── components/page_discovery.py
│   │   ├── Sitemap parsing
│   │   ├── SPA route detection
│   │   └── Link crawling
│   ├── components/accessibility_checks.py
│   │   ├── Alt text validation
│   │   ├── ARIA compliance
│   │   ├── Form accessibility  
│   │   ├── Navigation structure
│   │   ├── Mobile responsiveness
│   │   └── HTML validity
│   ├── components/report_generator.py
│   │   ├── Professional PDF styling
│   │   ├── Executive summaries
│   │   └── Implementation roadmaps
│   └── components/utils.py
│       ├── Technology detection
│       └── Helper functions
```

### Supported Accessibility Checks
- **Images**: Alt text validation, decorative image detection
- **Forms**: Label association, error handling, field validation
- **Navigation**: Heading hierarchy, landmark structure, skip links  
- **Interactivity**: ARIA labels, keyboard accessibility, focus management
- **Mobile**: Responsive design, touch targets, viewport configuration
- **Structure**: HTML validity, semantic markup, language attributes

### Technology Detection Capabilities
- **CMS Detection**: WordPress, Drupal, Joomla, TYPO3, Shopify
- **JS Frameworks**: React, Vue, Angular, Svelte, Next.js, Nuxt.js
- **CSS Frameworks**: Bootstrap, Tailwind, Foundation, Bulma
- **Libraries**: jQuery, Lodash, Moment.js
- **Analytics**: Google Analytics, Google Tag Manager
- **Hosting**: Cloudflare, AWS, Netlify, Vercel

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **WCAG Guidelines** by W3C Web Accessibility Initiative
- **ReportLab** for PDF generation capabilities
- **Selenium** for browser automation and mobile testing
- **BeautifulSoup** for HTML parsing excellence

---

## 📞 Support

- 🐛 **Bug Reports**: [Create an issue](https://github.com/Tino1337/Accessibility-Webanalyzer/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/Tino1337/Accessibility-Webanalyzer/discussions)
- 📧 **Contact**: [Your email or website]

---

<div align="center">

**Made with ❤️ for a more accessible web**

[![GitHub stars](https://img.shields.io/github/stars/Tino1337/Accessibility-Webanalyzer.svg?style=social&label=Star)](https://github.com/Tino1337/Accessibility-Webanalyzer)
[![GitHub forks](https://img.shields.io/github/forks/Tino1337/Accessibility-Webanalyzer.svg?style=social&label=Fork)](https://github.com/Tino1337/Accessibility-Webanalyzer)

</div>