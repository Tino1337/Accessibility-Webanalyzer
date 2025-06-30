"""
Utility functions for technology detection and helpers.
"""

import requests
from bs4 import BeautifulSoup


def detect_technologies(url):
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
        
        # Check for JavaScript frameworks
        if 'react' in content.lower() and ('react-dom' in content or 'ReactDOM' in content):
            technologies['frameworks'].append('React')
        elif 'vue' in content.lower() and ('vue.js' in content or 'Vue.js' in content):
            technologies['frameworks'].append('Vue.js')
        elif 'angular' in content.lower() and ('angular.js' in content or '@angular' in content):
            technologies['frameworks'].append('Angular')
        elif 'next.js' in content.lower() or '_next' in content:
            technologies['frameworks'].append('Next.js')
        elif 'nuxt' in content.lower():
            technologies['frameworks'].append('Nuxt.js')
        
        # Check for CSS frameworks
        if 'bootstrap' in content.lower():
            technologies['frameworks'].append('Bootstrap')
        elif 'tailwind' in content.lower():
            technologies['frameworks'].append('Tailwind CSS')
        
        # Check for JavaScript libraries
        if 'jquery' in content.lower():
            technologies['libraries'].append('jQuery')
        
        # Check meta tags
        generator_meta = soup.find('meta', attrs={'name': 'generator'})
        if generator_meta:
            generator_content = generator_meta.get('content', '').lower()
            if 'wordpress' in generator_content and 'WordPress' not in technologies['cms']:
                technologies['cms'].append('WordPress')
            elif 'drupal' in generator_content and 'Drupal' not in technologies['cms']:
                technologies['cms'].append('Drupal')
        
        # Clean up empty categories
        technologies = {k: v for k, v in technologies.items() if v}
        
    except Exception as e:
        print(f"Technology detection error: {e}")
    
    return technologies


def get_page_title(url):
    """Get a readable title for a page"""
    from urllib.parse import urlparse
    return urlparse(url).path or 'Homepage'