#!/usr/bin/env python3
"""
Website Accessibility Analyzer (Compact Version)
Automatisierte Barrierefreiheits-Analyse nach WCAG 2.1 AA Standards
Mit kompakter Darstellung und professionellem Report
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
from datetime import datetime
import re
import math

# Optional selenium imports for mobile testing
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from PIL import Image as PILImage
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class AccessibilityAnalyzer:
    def __init__(self, url, max_pages=10):
        self.base_url = url
        self.max_pages = max_pages  # Default to 10 pages for reasonable analysis time
        self.analyzed_pages = []
        self.issues = {
            'MANDATORY': [],
            'SHOULD DO': [],
            'NICE TO HAVE': []
        }
        self.detailed_findings = []
        self.page_stats = {}
        self.technologies = {}
        
        # Setup Chrome driver for mobile testing if available
        self.driver = None
        if SELENIUM_AVAILABLE:
            self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver for mobile testing"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Warning: Could not initialize Chrome driver: {e}")
            print("Mobile testing will be disabled")
            self.driver = None
    
    def detect_technologies(self, url):
        """Detect website technologies and frameworks"""
        technologies = {
            'cms': [],
            'frameworks': [],
            'libraries': [],
            'other': []
        }
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            content = response.content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for CMS indicators
            if 'wp-content' in content or 'wp-includes' in content:
                technologies['cms'].append('WordPress')
            elif '/sites/default/' in content or 'Drupal.settings' in content:
                technologies['cms'].append('Drupal')
            elif '/components/com_' in content or 'joomla' in content.lower():
                technologies['cms'].append('Joomla')
            elif 'typo3' in content.lower():
                technologies['cms'].append('TYPO3')
            elif 'shopify' in content.lower():
                technologies['cms'].append('Shopify')
            elif 'wix.com' in content or 'wixstatic.com' in content:
                technologies['cms'].append('Wix')
            elif 'squarespace' in content.lower():
                technologies['cms'].append('Squarespace')
            
            # Check for JavaScript frameworks
            if 'react' in content.lower() and ('react-dom' in content or 'ReactDOM' in content):
                technologies['frameworks'].append('React')
            elif 'vue' in content.lower() and ('vue.js' in content or 'Vue.js' in content):
                technologies['frameworks'].append('Vue.js')
            elif 'angular' in content.lower() and ('angular.js' in content or '@angular' in content):
                technologies['frameworks'].append('Angular')
            elif 'svelte' in content.lower():
                technologies['frameworks'].append('Svelte')
            elif 'next.js' in content.lower() or '_next' in content:
                technologies['frameworks'].append('Next.js')
            elif 'nuxt' in content.lower():
                technologies['frameworks'].append('Nuxt.js')
            
            # Check for CSS frameworks
            if 'bootstrap' in content.lower():
                technologies['frameworks'].append('Bootstrap')
            elif 'tailwind' in content.lower():
                technologies['frameworks'].append('Tailwind CSS')
            elif 'foundation' in content.lower() and 'css' in content.lower():
                technologies['frameworks'].append('Foundation')
            elif 'bulma' in content.lower():
                technologies['frameworks'].append('Bulma')
            
            # Check for JavaScript libraries
            if 'jquery' in content.lower():
                technologies['libraries'].append('jQuery')
            elif 'lodash' in content.lower():
                technologies['libraries'].append('Lodash')
            elif 'moment.js' in content.lower():
                technologies['libraries'].append('Moment.js')
            
            # Check meta tags for additional info
            generator_meta = soup.find('meta', attrs={'name': 'generator'})
            if generator_meta:
                generator_content = generator_meta.get('content', '').lower()
                if 'wordpress' in generator_content:
                    if 'WordPress' not in technologies['cms']:
                        technologies['cms'].append('WordPress')
                elif 'drupal' in generator_content:
                    if 'Drupal' not in technologies['cms']:
                        technologies['cms'].append('Drupal')
                elif 'joomla' in generator_content:
                    if 'Joomla' not in technologies['cms']:
                        technologies['cms'].append('Joomla')
            
            # Check for hosting/CDN
            if 'cloudflare' in content.lower():
                technologies['other'].append('Cloudflare')
            elif 'amazonaws' in content:
                technologies['other'].append('AWS')
            elif 'googletagmanager' in content:
                technologies['other'].append('Google Tag Manager')
            elif 'google-analytics' in content:
                technologies['other'].append('Google Analytics')
            
            # Clean up empty categories
            technologies = {k: v for k, v in technologies.items() if v}
            
        except Exception as e:
            print(f"Technology detection error: {e}")
        
        return technologies
        
    def get_pages_to_analyze(self):
        """Get list of pages to analyze - enhanced for SPAs like Nuxt and language filtering"""
        pages = []
        
        # Language codes to ignore (avoid analyzing translated pages)
        language_codes = [
            'en', 'de', 'fr', 'es', 'it', 'nl', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar',
            'pl', 'cz', 'cs', 'sk', 'hu', 'ro', 'bg', 'hr', 'sl', 'fi', 'sv', 
            'no', 'da', 'tr', 'el', 'he', 'th', 'vi', 'uk', 'lt', 'lv', 'et'
        ]
        
        def is_language_page(url_or_path):
            """Check if URL path starts with a language code"""
            # Extract path from full URL if needed
            if url_or_path.startswith('http'):
                parsed = urlparse(url_or_path)
                url_path = parsed.path
            else:
                url_path = url_or_path
                
            if not url_path or url_path == '/':
                return False
            
            # Remove leading slash and get first segment
            path_parts = url_path.lstrip('/').split('/')
            if not path_parts or not path_parts[0]:
                return False
                
            first_segment = path_parts[0].lower()
            is_lang = first_segment in language_codes
            
            if is_lang:
                print(f"  🚫 Skipped language page: {url_path}")
            
            return is_lang
        
        # Priority pages to look for
        priority_keywords = [
            'home', 'about', 'über', 'contact', 'kontakt', 'services', 'dienstleistungen',
            'impressum', 'datenschutz', 'privacy', 'team', 'portfolio', 'produkte', 'products',
            'blog', 'news', 'faq', 'support', 'help', 'pricing', 'preise'
        ]
        
        try:
            response = requests.get(self.base_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
            content = response.content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Add homepage
            pages.append(self.base_url)
            found_pages = []
            
            # Method 1: Traditional link discovery
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                full_url = urljoin(self.base_url, href)
                
                # Check if it's from same domain and not external
                parsed_base = urlparse(self.base_url)
                parsed_url = urlparse(full_url)
                
                if (parsed_url.netloc == parsed_base.netloc and 
                    not any(ext in full_url.lower() for ext in ['.pdf', '.doc', '.zip', '.jpg', '.png', 'mailto:', 'tel:']) and
                    not is_language_page(full_url)):  # Use full URL for language check
                    
                    link_text = link.get_text().lower().strip()
                    href_lower = href.lower()
                    
                    # Check for priority keywords
                    for keyword in priority_keywords:
                        if keyword in link_text or keyword in href_lower:
                            if full_url not in found_pages and full_url != self.base_url:
                                found_pages.append(full_url)
                                break
            
            # Method 2: Check for SPA frameworks and try common routes
            is_spa = any(framework in content.lower() for framework in ['nuxt', 'next.js', 'vue', 'react', 'angular'])
            
            if is_spa:
                print("🔍 SPA detected - trying common route patterns...")
                
                # Common SPA routes to try
                common_routes = [
                    '/about', '/über-uns', '/ueber-uns',
                    '/contact', '/kontakt', 
                    '/services', '/dienstleistungen',
                    '/products', '/produkte',
                    '/team', '/unternehmen',
                    '/blog', '/news',
                    '/impressum', '/imprint',
                    '/datenschutz', '/privacy',
                    '/faq', '/help', '/hilfe'
                ]
                
                for route in common_routes:
                    test_url = urljoin(self.base_url, route)
                    if (test_url not in found_pages and 
                        test_url != self.base_url and
                        not is_language_page(test_url)):  # Use full URL for language check
                        # Quick test if the route exists
                        try:
                            test_response = requests.head(test_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                            if test_response.status_code == 200:
                                found_pages.append(test_url)
                                print(f"  ✓ Found SPA route: {route}")
                        except:
                            pass
            
            # Method 3: Look for sitemap.xml and page-sitemap.xml
            sitemap_urls = [
                '/sitemap.xml',
                '/page-sitemap.xml',
                '/sitemap_index.xml',
                '/sitemap-pages.xml'
            ]
            
            for sitemap_path in sitemap_urls:
                try:
                    sitemap_url = urljoin(self.base_url, sitemap_path)
                    sitemap_response = requests.get(sitemap_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    if sitemap_response.status_code == 200:
                        print(f"🗺️ Found {sitemap_path} - extracting URLs...")
                        try:
                            sitemap_soup = BeautifulSoup(sitemap_response.content, 'xml')
                        except:
                            # Fallback to html parser if xml parser not available
                            sitemap_soup = BeautifulSoup(sitemap_response.content, 'html.parser')
                        
                        # Extract URLs from sitemap
                        loc_tags = sitemap_soup.find_all('loc')
                        sitemap_count = 0
                        max_per_sitemap = min(10, self.max_pages - len(found_pages))  # Don't exceed total limit
                        
                        for loc in loc_tags:
                            if sitemap_count >= max_per_sitemap:  # Respect page limits
                                break
                                
                            sitemap_url_text = loc.get_text().strip()
                            parsed_url = urlparse(sitemap_url_text)
                            parsed_base = urlparse(self.base_url)
                            
                            if (parsed_url.netloc == parsed_base.netloc and 
                                sitemap_url_text not in found_pages and 
                                sitemap_url_text != self.base_url and
                                not any(ext in sitemap_url_text.lower() for ext in ['.xml', '.pdf', '.jpg', '.png']) and
                                not is_language_page(sitemap_url_text)):  # Use full URL for language check
                                found_pages.append(sitemap_url_text)
                                print(f"  ✓ Added from {sitemap_path}: {parsed_url.path}")
                                sitemap_count += 1
                        
                        # If we found URLs in this sitemap, we can break or continue to next
                        if sitemap_count > 0:
                            print(f"  📄 Found {sitemap_count} URLs in {sitemap_path}")
                        
                        # Stop if we've reached our limit
                        if len(found_pages) >= self.max_pages - 1:  # -1 for homepage
                            break
                        
                except Exception as e:
                    # Silently continue to next sitemap - don't spam console
                    continue
            
            # Add found priority pages
            pages.extend(found_pages[:self.max_pages-1])
            
            # Method 4: If we still don't have enough pages, add more from regular links
            if len(pages) < self.max_pages:
                for link in links:
                    href = link['href']
                    full_url = urljoin(self.base_url, href)
                    parsed_url = urlparse(full_url)
                    
                    if (parsed_url.netloc == parsed_base.netloc 
                        and full_url not in pages 
                        and len(pages) < self.max_pages
                        and not any(ext in full_url.lower() for ext in ['.pdf', '.doc', '.zip', '.jpg', '.png', 'mailto:', 'tel:', '#'])
                        and not is_language_page(full_url)):  # Use full URL for language check
                        pages.append(full_url)
                        
        except Exception as e:
            print(f"Error getting pages: {e}")
            pages = [self.base_url]
            
        # Remove duplicates while preserving order
        seen = set()
        unique_pages = []
        for page in pages:
            if page not in seen:
                seen.add(page)
                unique_pages.append(page)
        
        return unique_pages[:self.max_pages]
    
    def analyze_page_performance(self, url, soup):
        """Analyze basic page performance metrics"""
        stats = {
            'total_images': len(soup.find_all('img')),
            'total_links': len(soup.find_all('a', href=True)),
            'total_headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'total_forms': len(soup.find_all('form')),
            'has_lang': bool(soup.find('html', lang=True)),
            'has_title': bool(soup.find('title') and soup.find('title').get_text().strip()),
            'page_length': len(soup.get_text())
        }
        
        self.page_stats[url] = stats
        return stats
    
    def check_alt_texts(self, url):
        """Enhanced alt text analysis"""
        issues = []
        details = []
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            images = soup.find_all('img')
            missing_alt = 0
            empty_alt = 0
            decorative_images = 0
            total_images = len(images)
            
            for i, img in enumerate(images):
                alt = img.get('alt')
                src = img.get('src', 'unknown')
                
                if alt is None:
                    missing_alt += 1
                    details.append(f"Bild ohne Alt-Text: {src[:50]}...")
                elif alt.strip() == '':
                    # Empty alt might be intentional for decorative images
                    if any(keyword in src.lower() for keyword in ['icon', 'decoration', 'spacer', 'bg']):
                        decorative_images += 1
                    else:
                        empty_alt += 1
                        details.append(f"Bild mit leerem Alt-Text: {src[:50]}...")
                elif len(alt) > 100:
                    details.append(f"Alt-Text zu lang ({len(alt)} Zeichen): {alt[:50]}...")
            
            total_issues = missing_alt + empty_alt
            
            if total_issues > 0:
                severity = 'MANDATORY' if total_issues > total_images * 0.3 else 'SHOULD DO'
                
                description = f"{total_issues} von {total_images} Bildern ohne korrekte Alt-Texte"
                if decorative_images > 0:
                    description += f" ({decorative_images} vermutlich dekorative Bilder)"
                
                issues.append({
                    'category': severity,
                    'type': 'Alt-Texte für Bilder',
                    'description': description,
                    'count': total_issues,
                    'effort_hours': max(0.25, total_issues * 0.15),  # 9 minutes per missing alt text
                    'details': details[:8],  # Show more examples
                    'wcag_criterion': '1.1.1 Nicht-Text-Inhalte',
                    'impact': 'KRITISCH - Screenreader-Nutzer können essenzielle Bildinformationen nicht erfassen'
                })
                
        except Exception as e:
            print(f"Alt text check error for {url}: {e}")
            
        return issues
    
    def check_responsive_design(self, url):
        """Check responsive design and mobile accessibility"""
        issues = []
        details = []
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            content = response.content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            responsive_issues = []
            
            # Check viewport meta tag
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport_meta:
                responsive_issues.append("Viewport Meta-Tag fehlt")
                details.append("Ohne Viewport-Tag wird die Seite auf mobilen Geräten nicht korrekt skaliert")
            else:
                viewport_content = viewport_meta.get('content', '').lower()
                if 'width=device-width' not in viewport_content:
                    responsive_issues.append("Viewport Meta-Tag ohne 'width=device-width'")
                if 'user-scalable=no' in viewport_content:
                    responsive_issues.append("Zoom deaktiviert (user-scalable=no)")
                    details.append("Benutzer können nicht zoomen - schlechte Barrierefreiheit")
            
            # Check for CSS media queries
            has_media_queries = False
            style_tags = soup.find_all('style')
            for style in style_tags:
                if style.string and '@media' in style.string:
                    has_media_queries = True
                    break
            
            # Check linked CSS for media queries
            if not has_media_queries:
                link_tags = soup.find_all('link', rel='stylesheet')
                if len(link_tags) > 0:
                    # Assume modern sites have responsive CSS
                    has_media_queries = True
            
            if not has_media_queries:
                responsive_issues.append("Keine CSS Media Queries erkannt")
                details.append("Website könnte nicht für verschiedene Bildschirmgrößen optimiert sein")
            
            # Test with mobile user agent if selenium available
            mobile_issues = []
            if self.driver:
                try:
                    # Test mobile viewport
                    self.driver.set_window_size(375, 667)  # iPhone size
                    self.driver.get(url)
                    time.sleep(2)
                    
                    # Check for horizontal scrollbar
                    body_width = self.driver.execute_script("return document.body.scrollWidth")
                    window_width = self.driver.execute_script("return window.innerWidth")
                    
                    if body_width > window_width + 10:  # 10px tolerance
                        mobile_issues.append("Horizontaler Scroll auf mobilen Geräten")
                        details.append(f"Seiteninhalt ({body_width}px) übersteigt Viewport ({window_width}px)")
                    
                    # Check for tiny text
                    small_text = self.driver.find_elements(By.CSS_SELECTOR, "*")
                    tiny_text_count = 0
                    for element in small_text[:20]:  # Check first 20 elements
                        try:
                            font_size = self.driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).fontSize", element
                            )
                            if font_size and 'px' in font_size:
                                size_px = float(font_size.replace('px', ''))
                                if size_px < 12:  # Text smaller than 12px
                                    tiny_text_count += 1
                        except:
                            continue
                    
                    if tiny_text_count > 3:
                        mobile_issues.append(f"{tiny_text_count} Elemente mit sehr kleiner Schrift (<12px)")
                        details.append("Kleine Schrift ist auf mobilen Geräten schwer lesbar")
                    
                    # Check touch target sizes
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, input[type='button'], input[type='submit'], a")
                    small_targets = 0
                    for button in buttons[:10]:  # Check first 10
                        try:
                            size = button.size
                            if size['width'] < 44 or size['height'] < 44:  # Apple's 44px recommendation
                                small_targets += 1
                        except:
                            continue
                    
                    if small_targets > 2:
                        mobile_issues.append(f"{small_targets} Touch-Targets unter 44px")
                        details.append("Kleine Buttons sind schwer zu treffen auf Touchscreens")
                    
                    # Reset window size
                    self.driver.set_window_size(1920, 1080)
                    
                except Exception as e:
                    print(f"Mobile testing error: {e}")
            
            # Check for mobile-unfriendly elements
            flash_objects = soup.find_all(['object', 'embed'])
            flash_count = 0
            for obj in flash_objects:
                if any(flash_type in str(obj).lower() for flash_type in ['flash', 'application/x-shockwave']):
                    flash_count += 1
            
            if flash_count > 0:
                responsive_issues.append(f"{flash_count} Flash-Elemente gefunden")
                details.append("Flash wird auf mobilen Geräten nicht unterstützt")
            
            total_responsive_issues = len(responsive_issues) + len(mobile_issues)
            
            if total_responsive_issues > 0:
                severity = 'MANDATORY' if len(mobile_issues) > 2 else 'SHOULD DO'
                
                all_issues = responsive_issues + mobile_issues
                
                issues.append({
                    'category': severity,
                    'type': 'Responsive Design & Mobile',
                    'description': f'{len(responsive_issues)} Responsive-Probleme, {len(mobile_issues)} Mobile-Probleme',
                    'count': total_responsive_issues,
                    'effort_hours': (len(responsive_issues) * 0.35) + (len(mobile_issues) * 0.5),  # 21min per responsive, 30min per mobile issue
                    'details': details[:8] + ["Beispiel: Viewport-Tag fehlt oder unvollständig", "Lösung: <meta name='viewport' content='width=device-width, initial-scale=1'>", "Touch-Targets: Buttons mindestens 44x44px groß machen", "Text: Schriftgröße mindestens 12px für mobile Lesbarkeit", "Horizontal-Scroll: CSS max-width: 100% verwenden"],
                    'wcag_criterion': '1.4.10 Reflow, 2.5.5 Zielgröße',
                    'impact': 'SCHWERWIEGEND - 60% der Nutzer (Mobile) werden ausgeschlossen'
                })
                
        except Exception as e:
            print(f"Responsive check error for {url}: {e}")
            
        return issues
    
    def check_aria_labels(self, url):
        """Enhanced ARIA labels and accessibility markup analysis"""
        issues = []
        details = []
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check interactive elements
            interactive_selectors = [
                ('button', 'Buttons'),
                ('input[type="button"]', 'Button-Inputs'),
                ('input[type="submit"]', 'Submit-Buttons'),
                ('[role="button"]', 'Button-Roles'),
                ('[onclick]', 'Clickable Elements'),
                ('select', 'Select-Elemente'),
                ('textarea', 'Textareas')
            ]
            
            missing_labels = 0
            total_interactive = 0
            
            for selector, element_type in interactive_selectors:
                elements = soup.select(selector)
                total_interactive += len(elements)
                
                for element in elements:
                    has_label = False
                    
                    # Check various labeling methods
                    if element.get('aria-label'):
                        has_label = True
                    elif element.get('aria-labelledby'):
                        has_label = True
                    elif element.name == 'input' and element.get('id'):
                        label = soup.find('label', attrs={'for': element.get('id')})
                        if label:
                            has_label = True
                    elif element.get_text().strip():
                        has_label = True
                    elif element.get('title'):
                        has_label = True
                    elif element.get('value') and element.get('type') in ['submit', 'button']:
                        has_label = True
                    
                    if not has_label:
                        missing_labels += 1
                        element_desc = f"{element_type}: {element.name}"
                        if element.get('class'):
                            element_desc += f" (class: {' '.join(element.get('class')[:2])})"
                        details.append(element_desc)
            
            # Check for missing landmark roles
            landmark_issues = 0
            if not soup.find('main') and not soup.find('[role="main"]'):
                landmark_issues += 1
                details.append("Kein <main> Element oder role='main' gefunden")
            
            if not soup.find('nav') and not soup.find('[role="navigation"]'):
                landmark_issues += 1
                details.append("Keine <nav> Elemente oder role='navigation' gefunden")
            
            total_aria_issues = missing_labels + landmark_issues
            
            if total_aria_issues > 0:
                severity = 'MANDATORY' if missing_labels > 5 else 'SHOULD DO'
                
                issues.append({
                    'category': severity,
                    'type': 'ARIA Labels und Rollen',
                    'description': f'{missing_labels} interaktive Elemente ohne Beschriftung, {landmark_issues} fehlende Landmarks',
                    'count': total_aria_issues,
                    'effort_hours': max(0.5, (missing_labels * 0.15) + (landmark_issues * 0.75)),  # 9min per label, 45min per landmark
                    'details': details[:10],  # Show more examples
                    'wcag_criterion': '4.1.2 Name, Rolle, Wert',
                    'impact': 'KRITISCH - Assistive Technologien versagen bei der Elementidentifikation'
                })
                
        except Exception as e:
            print(f"ARIA check error for {url}: {e}")
            
        return issues
    
    def check_navigation_structure(self, url):
        """Enhanced navigation and heading structure analysis"""
        issues = []
        details = []
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Detailed heading analysis
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            h1_elements = soup.find_all('h1')
            h1_count = len(h1_elements)
            
            # Check H1 structure
            if h1_count > 1:
                h1_texts = [h1.get_text().strip()[:50] for h1 in h1_elements]
                details.append(f"Mehrere H1 gefunden: {', '.join(h1_texts)}")
                issues.append({
                    'category': 'SHOULD DO',
                    'type': 'Überschriftenstruktur - Mehrere H1',
                    'description': f'{h1_count} H1-Überschriften gefunden (sollte nur eine pro Seite sein)',
                    'count': h1_count - 1,
                    'effort_hours': 0.25,  # 15 minutes to fix heading structure
                    'details': details[-1:] + [f"Beispiel: Mehrere H1-Tags pro Seite erschweren Navigation", "Lösung: Nur eine H1 pro Seite verwenden"],
                    'wcag_criterion': '1.3.1 Info und Beziehungen',
                    'impact': 'ERHEBLICH - Screenreader-Navigation wird massiv beeinträchtigt'
                })
            elif h1_count == 0:
                details.append("Keine H1-Überschrift gefunden")
                issues.append({
                    'category': 'SHOULD DO',
                    'type': 'Überschriftenstruktur - Fehlende H1',
                    'description': 'Keine H1-Überschrift gefunden',
                    'count': 1,
                    'effort_hours': 0.15,  # 9 minutes to add H1
                    'details': details[-1:] + ["Beispiel: Seite ohne Hauptüberschrift", "Lösung: H1 mit aussagekräftigem Seitentitel hinzufügen", "Best Practice: H1 sollte den Seiteninhalt beschreiben"],
                    'wcag_criterion': '1.3.1 Info und Beziehungen',
                    'impact': 'Mittel - Keine klare Seitenhierarchie'
                })
            
            # Check heading hierarchy
            heading_levels = [int(h.name[1]) for h in headings]
            skipped_levels = 0
            hierarchy_issues = []
            
            for i in range(1, len(heading_levels)):
                if heading_levels[i] - heading_levels[i-1] > 1:
                    skipped_levels += 1
                    hierarchy_issues.append(f"Von H{heading_levels[i-1]} zu H{heading_levels[i]} gesprungen")
            
            if skipped_levels > 0:
                issues.append({
                    'category': 'SHOULD DO',
                    'type': 'Überschriftenhierarchie',
                    'description': f'{skipped_levels} übersprungene Überschriftenebenen',
                    'count': skipped_levels,
                    'effort_hours': skipped_levels * 0.15,  # 9 minutes per skipped level
                    'details': hierarchy_issues + ["Beispiel: Von H1 direkt zu H3 springen", "Lösung: Logische Reihenfolge H1 → H2 → H3 verwenden", "Best Practice: Überschriften strukturieren Inhalte hierarchisch"],
                    'wcag_criterion': '1.3.1 Info und Beziehungen',
                    'impact': 'Mittel - Unlogische Inhaltsstruktur'
                })
            
            # Check navigation landmarks
            nav_elements = soup.find_all('nav')
            main_elements = soup.find_all('main')
            
            landmark_issues = []
            if len(nav_elements) == 0:
                landmark_issues.append("Keine <nav> Elemente gefunden")
            if len(main_elements) == 0:
                landmark_issues.append("Kein <main> Element gefunden")
            if len(main_elements) > 1:
                landmark_issues.append(f"{len(main_elements)} <main> Elemente gefunden (sollte nur eines sein)")
                
            if landmark_issues:
                issues.append({
                    'category': 'SHOULD DO',
                    'type': 'Semantische Landmarks',
                    'description': 'Fehlende oder falsche semantische HTML-Elemente',
                    'count': len(landmark_issues),
                    'effort_hours': len(landmark_issues) * 0.35,  # 21 minutes per landmark
                    'details': landmark_issues + ["Beispiel: <div> statt <main> für Hauptinhalt", "Lösung: <main>, <nav>, <header>, <footer> verwenden", "Best Practice: Semantische HTML5-Elemente strukturieren die Seite", "Nutzen: Screenreader können Seitenbereiche identifizieren"],
                    'wcag_criterion': '1.3.1 Info und Beziehungen',
                    'impact': 'Mittel - Erschwert Navigation mit Hilfstechnologien'
                })
                
        except Exception as e:
            print(f"Navigation structure check error for {url}: {e}")
            
        return issues
    
    def check_forms(self, url):
        """Enhanced form accessibility analysis"""
        issues = []
        details = []
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            forms = soup.find_all('form')
            if not forms:
                return issues
                
            form_issues = 0
            error_handling_issues = 0
            
            for form_idx, form in enumerate(forms):
                form_details = []
                
                # Check all form controls
                controls = form.find_all(['input', 'select', 'textarea'])
                
                for control in controls:
                    control_type = control.get('type', control.name)
                    has_label = False
                    label_method = None
                    
                    # Skip hidden inputs
                    if control.get('type') == 'hidden':
                        continue
                    
                    # Check various labeling methods
                    control_id = control.get('id')
                    if control_id:
                        label = soup.find('label', attrs={'for': control_id})
                        if label:
                            has_label = True
                            label_method = "label[for]"
                    
                    if not has_label and control.get('aria-label'):
                        has_label = True
                        label_method = "aria-label"
                    
                    if not has_label and control.get('aria-labelledby'):
                        has_label = True
                        label_method = "aria-labelledby"
                    
                    if not has_label and control.get('title'):
                        has_label = True
                        label_method = "title"
                    
                    # Placeholder is not sufficient but note it
                    if not has_label and control.get('placeholder'):
                        form_details.append(f"{control_type}: nur Placeholder vorhanden (unzureichend)")
                        form_issues += 1
                    elif not has_label:
                        form_details.append(f"{control_type}: keine Beschriftung")
                        form_issues += 1
                
                # Check for error handling
                error_elements = form.find_all(attrs={'role': 'alert'}) or form.find_all(class_=re.compile(r'error|invalid'))
                if not error_elements:
                    error_handling_issues += 1
                    form_details.append("Keine Fehlerbehandlung erkennbar")
                
                if form_details:
                    details.extend([f"Formular {form_idx + 1}: {detail}" for detail in form_details[:3]])
            
            total_form_issues = form_issues + error_handling_issues
            
            if total_form_issues > 0:
                severity = 'MANDATORY' if form_issues > 0 else 'SHOULD DO'
                
                issues.append({
                    'category': severity,
                    'type': 'Formular-Barrierefreiheit',
                    'description': f'{form_issues} unlabeled controls, {error_handling_issues} Formulare ohne Fehlerbehandlung',
                    'count': total_form_issues,
                    'effort_hours': (form_issues * 0.15) + (error_handling_issues * 0.75),  # 9min per label, 45min per error handling
                    'details': details[:8] + ["Beispiel: Input-Feld ohne <label> Element", "Lösung: <label for='email'>E-Mail:</label> hinzufügen", "Alternative: aria-label='E-Mail Adresse' verwenden", "Fehlerbehandlung: Klare Fehlermeldungen bei ungültigen Eingaben"],
                    'wcag_criterion': '3.3.1 Fehlererkennung, 3.3.2 Beschriftungen oder Anweisungen',
                    'impact': 'KRITISCH - Formulare sind für behinderte Nutzer völlig unzugänglich'
                })
                
        except Exception as e:
            print(f"Form check error for {url}: {e}")
            
        return issues
    
    def check_basic_accessibility(self, url):
        """Enhanced basic accessibility checks"""
        issues = []
        details = []
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            page_issues = []
            
            # Check page title
            title = soup.find('title')
            if not title or not title.get_text().strip():
                page_issues.append("Fehlender oder leerer Seitentitel")
                details.append("Seitentitel ist essentiell für Screenreader und Browser-Tabs")
            elif len(title.get_text()) < 10:
                page_issues.append(f"Seitentitel zu kurz: '{title.get_text()}'")
            elif len(title.get_text()) > 60:
                page_issues.append(f"Seitentitel zu lang ({len(title.get_text())} Zeichen)")
            
            # Check language attribute
            html_tag = soup.find('html')
            if not html_tag or not html_tag.get('lang'):
                page_issues.append("HTML-Element ohne lang-Attribut")
                details.append("Sprachattribut hilft Screenreadern bei korrekter Aussprache")
            
            # Check for viewport meta tag (responsive design)
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport_meta:
                page_issues.append("Viewport Meta-Tag fehlt")
                details.append("Wichtig für mobile Barrierefreiheit")
            
            # Check for skip links
            skip_links = soup.find_all('a', href=re.compile(r'^#'))
            skip_to_content = [link for link in skip_links if 'content' in link.get_text().lower() or 'inhalt' in link.get_text().lower()]
            
            if not skip_to_content:
                page_issues.append("Keine 'Skip to Content' Links gefunden")
                details.append("Skip-Links helfen Tastaturnutzern bei der Navigation")
            
            if page_issues:
                # Split into categories
                critical_issues = [issue for issue in page_issues if any(word in issue.lower() for word in ['titel', 'lang'])]
                nice_to_have_issues = [issue for issue in page_issues if issue not in critical_issues]
                
                if critical_issues:
                    issues.append({
                        'category': 'MANDATORY',
                        'type': 'Grundlegende Seitenstruktur',
                        'description': f'{len(critical_issues)} kritische Seitenprobleme',
                        'count': len(critical_issues),
                        'effort_hours': len(critical_issues) * 0.15,  # 9 minutes per basic issue
                        'details': critical_issues + ["Beispiel: <html> ohne lang='de' Attribut", "Lösung: <html lang='de'> für deutsche Inhalte", "Seitentitel: Aussagekräftige <title> Tags verwenden", "Best Practice: Jede Seite sollte einzigartigen Titel haben"],
                        'wcag_criterion': '3.1.1 Sprache der Seite, 2.4.2 Seitentitel',
                        'impact': 'KRITISCH - Grundlegende Webstandards werden nicht erfüllt'
                    })
                
                if nice_to_have_issues:
                    issues.append({
                        'category': 'NICE TO HAVE',
                        'type': 'Erweiterte Zugänglichkeit',
                        'description': f'{len(nice_to_have_issues)} Verbesserungsmöglichkeiten',
                        'count': len(nice_to_have_issues),
                        'effort_hours': len(nice_to_have_issues) * 0.35,  # 21 minutes per enhancement
                        'details': nice_to_have_issues + ["Beispiel: Skip-Link 'Zum Hauptinhalt springen'", "Lösung: <a href='#main'>Zum Hauptinhalt</a> am Seitenanfang", "Viewport: <meta name='viewport' content='width=device-width'> hinzufügen", "Nutzen: Verbessert Tastatur-Navigation und mobile Darstellung"],
                        'wcag_criterion': '2.4.1 Blöcke umgehen',
                        'impact': 'Niedrig - Verbessert Benutzererfahrung'
                    })
                
        except Exception as e:
            print(f"Basic accessibility check error for {url}: {e}")
            
        return issues
    
    def check_advanced_accessibility(self, url):
        """Additional advanced accessibility checks"""
        issues = []
        details = []
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for tables without proper headers
            tables = soup.find_all('table')
            table_issues = 0
            
            for table in tables:
                if not table.find('th') and not table.find('thead'):
                    table_issues += 1
                    details.append("Tabelle ohne Kopfzeilen (th/thead) gefunden")
            
            # Check for media elements
            videos = soup.find_all('video')
            audio = soup.find_all('audio')
            media_issues = 0
            
            for media in videos + audio:
                if not media.find('track') and not media.get('controls'):
                    media_issues += 1
                    details.append(f"{media.name}-Element ohne Untertitel oder Controls")
            
            # Check for color-only information (basic heuristic)
            color_indicators = soup.find_all(string=re.compile(r'(rot|grün|blau|red|green|blue)', re.I))
            if len(color_indicators) > 3:
                details.append("Möglicherweise farbbasierte Informationsvermittlung erkannt")
                
            advanced_issues = table_issues + media_issues + (1 if len(color_indicators) > 3 else 0)
            
            if advanced_issues > 0:
                issues.append({
                    'category': 'SHOULD DO',
                    'type': 'Erweiterte Inhaltstypen',
                    'description': f'{table_issues} Tabellen-, {media_issues} Medien-Probleme',
                    'count': advanced_issues,
                    'effort_hours': (table_issues * 0.35) + (media_issues * 0.75) + (0.35 if len(color_indicators) > 3 else 0),  # 21min per table, 45min per media, 21min for color
                    'details': details + ["Beispiel: <table> ohne <th> Kopfzeilen", "Lösung: <th scope='col'>Spalte</th> verwenden", "Video: <track kind='subtitles'> für Untertitel hinzufügen", "Farben: Nicht nur Farbe für wichtige Informationen verwenden"],
                    'wcag_criterion': '1.3.1 Info und Beziehungen, 1.4.1 Verwendung von Farbe',
                    'impact': 'Mittel - Spezielle Inhaltstypen nicht zugänglich'
                })
                
        except Exception as e:
            print(f"Advanced accessibility check error for {url}: {e}")
            
        return issues
    
    def analyze_page(self, url):
        """Analyze a single page with enhanced detail"""
        print(f"Analyzing: {url}")
        page_issues = []
        
        try:
            # Get page content once for performance stats
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            self.analyze_page_performance(url, soup)
        except Exception as e:
            print(f"Error getting page content: {e}")
        
        # Run all checks with enhanced detail
        page_issues.extend(self.check_alt_texts(url))
        page_issues.extend(self.check_aria_labels(url))
        page_issues.extend(self.check_navigation_structure(url))
        page_issues.extend(self.check_forms(url))
        page_issues.extend(self.check_basic_accessibility(url))
        page_issues.extend(self.check_advanced_accessibility(url))
        page_issues.extend(self.check_responsive_design(url))
        
        # Add page context to issues
        for issue in page_issues:
            issue['page'] = url
            issue['page_title'] = urlparse(url).path or 'Homepage'
                
        self.detailed_findings.extend(page_issues)
        self.analyzed_pages.append(url)
        
    def consolidate_issues(self):
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
        
        # Convert back to list format with consolidated descriptions
        self.issues = {'MANDATORY': [], 'SHOULD DO': [], 'NICE TO HAVE': []}
        
        for category in consolidated:
            for issue_type, issue_data in consolidated[category].items():
                page_count = len(issue_data['pages'])
                unique_pages = list(set(issue_data['pages']))  # Remove duplicates
                page_count = len(unique_pages)
                
                if page_count > 1:
                    # Multiple pages - show consolidated
                    description = f"Auf {page_count} Seiten: {issue_data['descriptions'][0].split(':')[0] if ':' in issue_data['descriptions'][0] else issue_data['descriptions'][0]}"
                    page_info = f"Betroffen: {', '.join(unique_pages[:3])}" + ("..." if len(unique_pages) > 3 else "")
                else:
                    # Single page - show original description
                    description = issue_data['descriptions'][0]
                    page_info = f"Seite: {unique_pages[0]}"
                
                consolidated_issue = {
                    'type': issue_data['type'],
                    'category': issue_data['category'],
                    'description': description,
                    'count': issue_data['total_count'],
                    'effort_hours': issue_data['total_hours'],
                    'details': [page_info] + issue_data['details'][:4],  # Page info + up to 4 detail examples
                    'wcag_criterion': issue_data['wcag_criterion'],
                    'impact': issue_data['impact'],
                    'page_count': page_count
                }
                
                self.issues[category].append(consolidated_issue)
        
    def run_analysis(self):
        """Run complete accessibility analysis"""
        print(f"Starting accessibility analysis for: {self.base_url}")
        
        # Detect technologies first
        print("Detecting website technologies...")
        self.technologies = self.detect_technologies(self.base_url)
        
        pages = self.get_pages_to_analyze()
        print(f"Found {len(pages)} pages to analyze (language pages filtered):")
        for page in pages[:10]:  # Show first 10 in console
            page_path = urlparse(page).path or '/'
            print(f"  ✓ {page_path}")
        if len(pages) > 10:
            print(f"  ... and {len(pages) - 10} more pages")
        
        for i, page in enumerate(pages):
            try:
                print(f"Analyzing page {i+1}/{len(pages)}: {urlparse(page).path or 'Homepage'}")
                self.analyze_page(page)
                time.sleep(0.5)  # Be nice to the server
            except Exception as e:
                print(f"Error analyzing {page}: {e}")
                continue
        
        print(f"\nAnalysis complete! Consolidating issues...")
        self.consolidate_issues()
        
        print(f"Found issues:")
        for category, issues in self.issues.items():
            print(f"  {category}: {len(issues)} issues")
            
        # Clean up driver
        if self.driver:
            self.driver.quit()
    
    def generate_conclusion(self):
        """Generate detailed conclusion and recommendations"""
        total_mandatory = len(self.issues['MANDATORY'])
        total_should = len(self.issues['SHOULD DO'])
        total_nice = len(self.issues['NICE TO HAVE'])
        
        total_hours = {
            'MANDATORY': sum(issue['effort_hours'] for issue in self.issues['MANDATORY']),
            'SHOULD DO': sum(issue['effort_hours'] for issue in self.issues['SHOULD DO']),
            'NICE TO HAVE': sum(issue['effort_hours'] for issue in self.issues['NICE TO HAVE'])
        }
        
        # Determine overall compliance level
        if total_mandatory == 0:
            compliance_level = "WCAG 2.1 AA konform"
            compliance_description = "Die Website erfüllt die grundlegenden Barrierefreiheits-Anforderungen."
        elif total_mandatory <= 3:
            compliance_level = "Weitgehend konform"
            compliance_description = "Die Website hat kleinere Mängel, die kurzfristig behoben werden sollten."
        elif total_mandatory <= 8:
            compliance_level = "Teilweise konform"
            compliance_description = "Die Website weist mittlere Mängel auf, die systematisch angegangen werden müssen."
        else:
            compliance_level = "Nicht konform"
            compliance_description = "Die Website hat schwerwiegende Barrierefreiheitsprobleme, die umgehend behoben werden müssen."
        
        # Priority recommendations
        priority_actions = []
        
        if any('Alt-Texte' in issue['type'] for issue in self.issues['MANDATORY']):
            priority_actions.append("1. SOFORT: Alt-Texte für alle Bilder implementieren (rechtskritisch)")
        
        if any('Formular' in issue['type'] for issue in self.issues['MANDATORY']):
            priority_actions.append("2. DRINGEND: Formular-Accessibility und Fehlerbehandlung umsetzen")
        
        if any('ARIA' in issue['type'] for issue in self.issues['MANDATORY']):
            priority_actions.append("3. KRITISCH: ARIA-Labels für alle interaktiven Elemente ergänzen")
        
        if any('Seitenstruktur' in issue['type'] for issue in self.issues['MANDATORY']):
            priority_actions.append("4. FUNDAMENTAL: HTML-Grundstruktur standardkonform korrigieren")
        
        # Risk assessment
        legal_risk = "HOCH" if total_mandatory > 5 else "MITTEL" if total_mandatory > 0 else "NIEDRIG"
        
        return {
            'compliance_level': compliance_level,
            'compliance_description': compliance_description,
            'total_issues': total_mandatory + total_should + total_nice,
            'total_hours': sum(total_hours.values()),
            'legal_risk': legal_risk,
            'priority_actions': priority_actions,
            'quick_wins': [issue for issue in self.issues['SHOULD DO'] if issue['effort_hours'] <= 2],
            'major_improvements': [issue for issue in self.issues['MANDATORY'] if issue['effort_hours'] > 3]
        }
    
    def generate_pdf_report(self, filename=None):
        """Generate detailed PDF report with professional layout"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(self.base_url).netloc
            filename = f"accessibility_report_{domain}_{timestamp}.pdf"
        
        # Enhanced margins and layout
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, 
                               leftMargin=0.75*inch, rightMargin=0.75*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Enhanced custom styles
        title_style = ParagraphStyle(
            'DetailedTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        heading_style = ParagraphStyle(
            'DetailedHeading',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2d3748'),
            spaceBefore=25,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=8,
            backColor=colors.HexColor('#f7fafc')
        )
        
        subheading_style = ParagraphStyle(
            'DetailedSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#4a5568'),
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'DetailedNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceBefore=4,
            spaceAfter=4,
            fontName='Helvetica',
            leading=14
        )
        
        highlight_style = ParagraphStyle(
            'Highlight',
            parent=normal_style,
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2b6cb0')
        )
        
        # Category styles with enhanced colors
        mandatory_style = ParagraphStyle(
            'MandatoryDetailed',
            parent=normal_style,
            fontSize=13,
            textColor=colors.HexColor('#c53030'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#fed7d7'),
            borderWidth=1,
            borderColor=colors.HexColor('#fc8181'),
            borderPadding=6
        )
        
        should_style = ParagraphStyle(
            'ShouldDetailed',
            parent=normal_style,
            fontSize=13,
            textColor=colors.HexColor('#d69e2e'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#faf089'),
            borderWidth=1,
            borderColor=colors.HexColor('#f6e05e'),
            borderPadding=6
        )
        
        nice_style = ParagraphStyle(
            'NiceDetailed',
            parent=normal_style,
            fontSize=13,
            textColor=colors.HexColor('#38a169'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#c6f6d5'),
            borderWidth=1,
            borderColor=colors.HexColor('#68d391'),
            borderPadding=6
        )

        story.append(Paragraph("WCAG 2.1 AA Compliance Assessment", subtitle_style))
        story.append(Spacer(1, 25))
        
        # Enhanced website info with better styling
        tech_summary = []
        if self.technologies.get('cms'):
            tech_summary.extend(self.technologies['cms'])
        if self.technologies.get('frameworks'):
            tech_summary.extend(self.technologies['frameworks'][:2])
        tech_text = ', '.join(tech_summary) if tech_summary else 'Nicht erkannt'
        
        info_data = [
            ['Website URL:', self.base_url],
            ['Analysierte Seiten:', str(len(self.analyzed_pages))],
            ['Erkannte Technologien:', tech_text],
            ['Analyse-Datum:', datetime.now().strftime('%d.%m.%Y')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Executive Summary with enhanced styling
        story.append(Paragraph("Executive Summary", heading_style))
        
        conclusion = self.generate_conclusion()
        
        # Enhanced compliance status with visual indicator
        compliance_color = colors.HexColor('#c53030') if 'Nicht konform' in conclusion['compliance_level'] else \
                          colors.HexColor('#d69e2e') if 'Teilweise' in conclusion['compliance_level'] else \
                          colors.HexColor('#38a169')
        
        compliance_bg = colors.HexColor('#fed7d7') if 'Nicht konform' in conclusion['compliance_level'] else \
                       colors.HexColor('#faf089') if 'Teilweise' in conclusion['compliance_level'] else \
                       colors.HexColor('#c6f6d5')
        
        status_data = [
            ['Compliance Status', conclusion['compliance_level']],
            ['Rechtliches Risiko', conclusion['legal_risk']],
            ['Gesamtaufwand', f"{conclusion['total_hours']:.1f} Arbeitsstunden"]
        ]
        
        status_table = Table(status_data, colWidths=[2*inch, 3*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
            ('BACKGROUND', (1, 0), (1, 0), compliance_bg),
            ('BACKGROUND', (1, 1), (1, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (1, 0), compliance_color),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0'))
        ]))
        
        story.append(status_table)
        story.append(Spacer(1, 15))
        
        # Detailed summary text
        summary_text = f"""
        <b>Bewertung:</b> {conclusion['compliance_description']}<br/>
        <br/>
        <b>Kritische Analyseergebnisse:</b> Bei der umfassenden Untersuchung von {len(self.analyzed_pages)} Seiten wurden 
        <b>{conclusion['total_issues']} potentiell rechtskritische Verbesserungsbereiche</b> identifiziert. 
        Der Gesamtaufwand zur vollständigen WCAG-Konformität beträgt {conclusion['total_hours']:.1f} Arbeitsstunden.<br/>
        <br/>
        <b>Rechtliche Risikobewertung:</b> Das Haftungsrisiko wird als <b>{conclusion['legal_risk']}</b> eingestuft. 
        {'KRITISCH: Sofortige Maßnahmen erforderlich um rechtliche Konsequenzen zu vermeiden!' if conclusion['legal_risk'] == 'HOCH' else 
         'WICHTIG: Zeitnahe Behebung empfohlen um Compliance-Risiken zu minimieren.' if conclusion['legal_risk'] == 'MITTEL' else
         'STABIL: Grundlegende Rechtssicherheit gegeben, strategische Optimierungen empfohlen.'}
        """
        
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 20))
        
        # Enhanced overview table with better styling
        overview_data = [
            ['Kategorie', 'Issues', 'Aufwand', 'Priorität', 'Beschreibung'],
            ['MANDATORY', 
             str(len(self.issues['MANDATORY'])), 
             f"{sum(issue['effort_hours'] for issue in self.issues['MANDATORY']):.1f}",
             'SOFORT',
             'Rechtskritische Mängel'],
            ['SHOULD DO', 
             str(len(self.issues['SHOULD DO'])), 
             f"{sum(issue['effort_hours'] for issue in self.issues['SHOULD DO']):.1f}",
             'Kurzfristig',
             'dringend empfohlen'],
            ['NICE TO HAVE', 
             str(len(self.issues['NICE TO HAVE'])), 
             f"{sum(issue['effort_hours'] for issue in self.issues['NICE TO HAVE']):.1f}",
             'Mittelfristig',
             'Strategische Optimierungen']
        ]
        
        overview_table = Table(overview_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 1*inch, 2.7*inch])
        overview_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            
            # MANDATORY row
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fed7d7')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#c53030')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            
            # SHOULD DO row
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#faf089')),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#d69e2e')),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            
            # NICE TO HAVE row
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#c6f6d5')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#38a169')),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 30))
        
        # Page Break for detailed issues
        story.append(PageBreak())
        
        # Detailed Issues Analysis
        story.append(Paragraph("Detaillierte Problemanalyse", heading_style))
        story.append(Spacer(1, 15))
        
        categories = [
            ('MANDATORY', mandatory_style, 'Rechtskritische Mängel', 'Diese Issues bergen erhebliches Haftungsrisiko und müssen SOFORT behoben werden um rechtliche Konsequenzen zu vermeiden.'),
            ('SHOULD DO', should_style, 'Compliance-Lücken', 'Diese Probleme gefährden die WCAG-Konformität und sollten dringend angegangen werden um Compliance-Risiken zu minimieren.'),
            ('NICE TO HAVE', nice_style, 'Strategische Optimierungen', 'Diese Verbesserungen schaffen Wettbewerbsvorteile und demonstrieren Branchenführerschaft in digitaler Inklusion.')
        ]
        
        for category, style, title, description in categories:
            if self.issues[category]:
                story.append(Paragraph(title, style))
                story.append(Spacer(1, 5))
                story.append(Paragraph(description, normal_style))
                story.append(Spacer(1, 10))
                
                for i, issue in enumerate(self.issues[category]):
                    # Detailed issue presentation
                    effort_str = f"{issue['effort_hours']:.1f}".rstrip('0').rstrip('.')
                    page_indicator = f" (auf {issue.get('page_count', 1)} Seite{'n' if issue.get('page_count', 1) > 1 else ''})" if issue.get('page_count', 1) > 1 else ""
                    
                    issue_title = f"{i+1}. {issue['type']} - {effort_str}h{page_indicator}"
                    story.append(Paragraph(issue_title, subheading_style))
                    
                    # Issue details in structured format
                    issue_details = f"""
                    <b>Problem:</b> {issue['description']}<br/>
                    <b>WCAG Kriterium:</b> {issue.get('wcag_criterion', 'Nicht spezifiziert')}<br/>
                    <b>Auswirkung:</b> {issue.get('impact', 'Nicht bewertet')}<br/>
                    <b>Geschätzter Aufwand:</b> {effort_str} Stunden
                    """
                    
                    story.append(Paragraph(issue_details, normal_style))
                    
                    # Show details in a proper list format
                    if issue.get('details'):
                        # Create a table with each detail as a separate row for better formatting
                        details_data = [['Details & Beispiele:', '']]  # Header row
                        
                        for detail in issue['details'][:6]:  # Show up to 6 details
                            # Clean up long details for better display
                            if len(detail) > 120:
                                detail = detail[:117] + "..."
                            details_data.append(['', f"• {detail}"])
                        
                        details_table = Table(details_data, colWidths=[1.2*inch, 5.3*inch])
                        details_table.setStyle(TableStyle([
                            # Header row styling
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (0, 0), 10),
                            ('SPAN', (0, 0), (-1, 0)),  # Merge header cells
                            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                            
                            # Detail rows styling
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            
                            # General styling
                            ('PADDING', (0, 0), (-1, -1), 6),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                            ('LEADING', (0, 0), (-1, -1), 12),
                            
                            # Remove left padding for bullet points
                            ('LEFTPADDING', (1, 1), (1, -1), 12),
                        ]))
                        
                        story.append(details_table)
                    
                    story.append(Spacer(1, 15))
                
                story.append(Spacer(1, 20))
        
        # Recommendations section
        story.append(PageBreak())
        story.append(Paragraph("Handlungsempfehlungen", heading_style))
        
        if conclusion['priority_actions']:
            story.append(Paragraph("Prioritäre Sofortmaßnahmen", subheading_style))
            story.append(Spacer(1, 8))
            
            for action in conclusion['priority_actions']:
                story.append(Paragraph(f"• {action}", highlight_style))
                story.append(Spacer(1, 4))
            
            story.append(Spacer(1, 15))
        
        # Quick wins section
        if conclusion['quick_wins']:
            story.append(Paragraph("Quick Wins (≤ 2 Stunden)", subheading_style))
            story.append(Spacer(1, 8))
            
            for win in conclusion['quick_wins'][:4]:
                story.append(Paragraph(f"• {win['type']}: {win['description']}", normal_style))
                story.append(Spacer(1, 4))
            
            story.append(Spacer(1, 15))
        
        # Final conclusion
        story.append(Paragraph("Fazit und nächste Schritte", subheading_style))
        
        conclusion_text = f"""
        Die durchgeführte Barrierefreiheits-Analyse zeigt einen <b>{conclusion['compliance_level']}</b>-Status 
        für die Website {self.base_url}. {conclusion['compliance_description']}
        <br/><br/>
        <b>Zentrale Befunde:</b><br/>
        • Analysierte Seiten: {len(self.analyzed_pages)}<br/>
        • Identifizierte Compliance-Lücken: <b>{conclusion['total_issues']}</b><br/>
        • Investition für vollständige WCAG-Konformität: {conclusion['total_hours']:.1f} Arbeitsstunden<br/>
        • Rechtliches Haftungsrisiko: <b>{conclusion['legal_risk']}</b><br/>
        <br/>
        <b>Strategische Handlungsempfehlung:</b><br/>
        1. SOFORTIGE Behebung aller rechtskritischen Mängel (Phase 1)<br/>
        2. Entwicklungsteam-Schulung zu WCAG-Standards (Phase 2)<br/>
        3. Systematische Umsetzung nach Risikoprioritäten (Phase 3)<br/>
        4. Compliance-Validierung durch Folgeaudit (Phase 4)<br/>
        5. Integration permanenter Accessibility-Qualitätssicherung (Phase 5)<br/>
        <br/>
        <b>ROI-Hinweis:</b> Proaktive Barrierefreiheit vermeidet rechtliche Risiken, erschließt neue Zielgruppen 
        und verbessert SEO-Rankings nachhaltig.
        """
        
        story.append(Paragraph(conclusion_text, normal_style))
        
        # Build PDF
        try:
            doc.build(story)
            print(f"Detailed PDF report generated: {filename}")
            return filename
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None


def main():
    """Main function to run the compact accessibility analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compact Website Accessibility Analyzer')
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('--max-pages', type=int, default=10, help='Maximum number of pages to analyze (default: 10)')
    parser.add_argument('--output', help='Output PDF filename')
    parser.add_argument('--analyze-all', action='store_true', help='Analyze all found pages (overrides --max-pages)')
    
    args = parser.parse_args()
    
    # Ensure URL has protocol
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Set max_pages to None if analyze-all flag is used
    max_pages = None if args.analyze_all else args.max_pages
    
    analyzer = AccessibilityAnalyzer(url, max_pages=max_pages)
    
    try:
        analyzer.run_analysis()
        pdf_file = analyzer.generate_pdf_report(args.output)
        
        if pdf_file:
            print(f"\n🎉 Compact analysis complete! Report saved as: {pdf_file}")
            
            # Print summary
            conclusion = analyzer.generate_conclusion()
            print(f"\n📊 Summary:")
            print(f"  Pages analyzed: {len(analyzer.analyzed_pages)}")
            print(f"  Technologies: {', '.join(analyzer.technologies.get('cms', []) + analyzer.technologies.get('frameworks', [])) or 'Not detected'}")
            print(f"  Compliance Level: {conclusion['compliance_level']}")
            print(f"  Legal Risk: {conclusion['legal_risk']}")
            print(f"  Total Issues: {conclusion['total_issues']}")
            print(f"  Total Effort: {conclusion['total_hours']:.2f} hours")
            
            for category, issues in analyzer.issues.items():
                total_hours = sum(issue['effort_hours'] for issue in issues)
                print(f"  {category}: {len(issues)} issues ({total_hours:.2f} hours)")
                
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()