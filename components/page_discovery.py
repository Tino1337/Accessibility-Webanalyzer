# components/page_discovery.py
"""
Page discovery functionality for finding pages to analyze.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class PageDiscovery:
    def __init__(self):
        self.language_codes = [
            'en', 'de', 'fr', 'es', 'it', 'nl', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar',
            'pl', 'cz', 'cs', 'sk', 'hu', 'ro', 'bg', 'hr', 'sl', 'fi', 'sv', 
            'no', 'da', 'tr', 'el', 'he', 'th', 'vi', 'uk', 'lt', 'lv', 'et'
        ]
        
        self.priority_keywords = [
            'home', 'about', 'über', 'contact', 'kontakt', 'services', 'dienstleistungen',
            'impressum', 'datenschutz', 'privacy', 'team', 'portfolio', 'produkte', 'products',
            'blog', 'news', 'faq', 'support', 'help', 'pricing', 'preise'
        ]
    
    def get_pages_to_analyze(self, base_url, max_pages=10):
        """Get list of pages to analyze"""
        pages = []
        
        # Handle unlimited pages case
        if max_pages is None:
            max_pages = 999  # Set a reasonable upper limit
        
        try:
            response = requests.get(base_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            content = response.content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Add homepage
            pages.append(base_url)
            found_pages = []
            
            # Method 1: Traditional link discovery
            found_pages.extend(self._discover_from_links(soup, base_url))
            
            # Method 2: Check for SPA frameworks
            if self._is_spa(content):
                print("🔍 SPA detected - trying common route patterns...")
                found_pages.extend(self._discover_spa_routes(base_url))
            
            # Method 3: Look for sitemap.xml
            found_pages.extend(self._discover_from_sitemap(base_url, max_pages))
            
            # Add found pages (all if unlimited, otherwise respect limit)
            if max_pages == 999:
                pages.extend(found_pages)  # Add all found pages
            else:
                pages.extend(found_pages[:max_pages-1])  # Limit pages
            
        except Exception as e:
            print(f"Error getting pages: {e}")
            pages = [base_url]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_pages = []
        for page in pages:
            if page not in seen:
                seen.add(page)
                unique_pages.append(page)
        
        # Return all pages if max_pages was set to 999 (unlimited), otherwise limit
        if max_pages == 999:
            print(f"📄 Found {len(unique_pages)} total pages (unlimited mode)")
            return unique_pages
        else:
            return unique_pages[:max_pages]
    
    def _is_language_page(self, url_or_path):
        """Check if URL path starts with a language code"""
        if url_or_path.startswith('http'):
            parsed = urlparse(url_or_path)
            url_path = parsed.path
        else:
            url_path = url_or_path
            
        if not url_path or url_path == '/':
            return False
        
        path_parts = url_path.lstrip('/').split('/')
        if not path_parts or not path_parts[0]:
            return False
            
        first_segment = path_parts[0].lower()
        is_lang = first_segment in self.language_codes
        
        if is_lang:
            print(f"  🚫 Skipped language page: {url_path}")
        
        return is_lang
    
    def _discover_from_links(self, soup, base_url):
        """Discover pages from HTML links"""
        found_pages = []
        priority_pages = []
        regular_pages = []
        
        links = soup.find_all('a', href=True)
        parsed_base = urlparse(base_url)
        
        for link in links:
            href = link['href']
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            
            # Check if it's from same domain and valid
            if (parsed_url.netloc == parsed_base.netloc and 
                not any(ext in full_url.lower() for ext in ['.pdf', '.doc', '.zip', '.jpg', '.png', 'mailto:', 'tel:', '#']) and
                not self._is_language_page(full_url)):
                
                link_text = link.get_text().lower().strip()
                href_lower = href.lower()
                
                # Check for priority keywords first
                is_priority = False
                for keyword in self.priority_keywords:
                    if keyword in link_text or keyword in href_lower:
                        if full_url not in priority_pages:
                            priority_pages.append(full_url)
                            is_priority = True
                        break
                
                # If not priority, add to regular pages
                if not is_priority and full_url not in regular_pages:
                    regular_pages.append(full_url)
        
        # Return priority pages first, then regular pages
        found_pages = priority_pages + regular_pages
        print(f"  🎯 Found {len(priority_pages)} priority pages, {len(regular_pages)} regular pages")
        
        return found_pages
    
    def _is_spa(self, content):
        """Check if website is a Single Page Application"""
        return any(framework in content.lower() for framework in ['nuxt', 'next.js', 'vue', 'react', 'angular'])
    
    def _discover_spa_routes(self, base_url):
        """Try common SPA routes"""
        found_pages = []
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
            test_url = urljoin(base_url, route)
            if not self._is_language_page(test_url):
                try:
                    test_response = requests.head(test_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    if test_response.status_code == 200:
                        found_pages.append(test_url)
                        print(f"  ✓ Found SPA route: {route}")
                except:
                    pass
        
        return found_pages
    
    def _discover_from_sitemap(self, base_url, max_pages):
        """Discover pages from sitemap.xml"""
        found_pages = []
        sitemap_urls = [
            '/sitemap.xml',
            '/page-sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap-pages.xml'
        ]
        
        for sitemap_path in sitemap_urls:
            try:
                sitemap_url = urljoin(base_url, sitemap_path)
                sitemap_response = requests.get(sitemap_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                
                if sitemap_response.status_code == 200:
                    print(f"🗺️ Found {sitemap_path} - extracting URLs...")
                    
                    try:
                        sitemap_soup = BeautifulSoup(sitemap_response.content, 'xml')
                    except:
                        sitemap_soup = BeautifulSoup(sitemap_response.content, 'html.parser')
                    
                    loc_tags = sitemap_soup.find_all('loc')
                    sitemap_count = 0
                    if max_pages == 999:
                        max_per_sitemap = 50  # More aggressive in unlimited mode
                    else:
                        max_per_sitemap = min(20, max_pages - len(found_pages))
                    
                    for loc in loc_tags:
                        if sitemap_count >= max_per_sitemap:
                            break
                            
                        sitemap_url_text = loc.get_text().strip()
                        parsed_url = urlparse(sitemap_url_text)
                        parsed_base = urlparse(base_url)
                        
                        if (parsed_url.netloc == parsed_base.netloc and 
                            sitemap_url_text not in found_pages and 
                            not any(ext in sitemap_url_text.lower() for ext in ['.xml', '.pdf', '.jpg', '.png']) and
                            not self._is_language_page(sitemap_url_text)):
                            
                            found_pages.append(sitemap_url_text)
                            print(f"  ✓ Added from {sitemap_path}: {parsed_url.path}")
                            sitemap_count += 1
                    
                    if sitemap_count > 0:
                        print(f"  📄 Found {sitemap_count} URLs in {sitemap_path}")
                    
                    if len(found_pages) >= max_pages - 1:
                        break
                        
            except Exception:
                continue
        
        return found_pages