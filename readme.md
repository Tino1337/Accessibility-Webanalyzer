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
python accessibility_analyzer.py https://example.com
```

### Docker Setup (Alternative)

```bash
# Build the image
docker build -t accessibility-analyzer .

# Run analysis
docker run -v $(pwd)/reports:/app/reports accessibility-analyzer https://example.com
```

---

## 💻 Usage

### Basic Analysis
```bash
# Analyze a website (default: 10 pages)
python accessibility_analyzer.py https://yourwebsite.com

# Custom page limit
python accessibility_analyzer.py https://yourwebsite.com --max-pages 20

# Analyze all discoverable pages
python accessibility_analyzer.py https://yourwebsite.com --analyze-all

# Custom output filename
python accessibility_analyzer.py https://yourwebsite.com --output custom_report.pdf
```

### Advanced Options
```bash
# Full help
python accessibility_analyzer.py --help
```

### Example Output
```
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

Analyzing page 1/10: Homepage
Analyzing page 2/10: /about
...

Analysis complete! Consolidating issues...
Found issues:
  MANDATORY: 2 issues
  SHOULD DO: 5 issues  
  NICE TO HAVE: 3 issues

🎉 Analysis complete! Report saved as: accessibility_report_example.com_20250630_143022.pdf
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
python accessibility_analyzer.py https://shop.example.com --max-pages 15

# Corporate website audit  
python accessibility_analyzer.py https://company.com --analyze-all

# Blog/content site
python accessibility_analyzer.py https://blog.example.com --max-pages 25
```

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

# Create feature branch  
git checkout -b feature/amazing-new-feature

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Make your changes and commit
git commit -m "Add amazing new feature"

# Push and create PR
git push origin feature/amazing-new-feature
```

### Areas for Contribution
- 🐛 **Bug fixes** - Report and fix issues
- ✨ **New features** - WCAG criterion coverage expansion  
- 📚 **Documentation** - Improve guides and examples
- 🧪 **Testing** - Add test coverage
- 🌍 **Internationalization** - Multi-language support
- 🎨 **UI/UX** - Report design improvements

---

## 🔧 Technical Details

### Architecture
```
accessibility_analyzer.py
├── Page Discovery (Sitemap, SPA routes, Links)
├── Content Analysis (WCAG checks, Mobile testing)  
├── Issue Consolidation (Cross-page deduplication)
├── Technology Detection (CMS, Framework identification)
└── PDF Generation (Professional reporting)
```

### Supported Checks
- **Images**: Alt text validation, decorative image detection
- **Forms**: Label association, error handling
- **Navigation**: Heading hierarchy, landmark structure  
- **Interactivity**: ARIA labels, keyboard accessibility
- **Mobile**: Responsive design, touch targets
- **Structure**: HTML validity, semantic markup

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