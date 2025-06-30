# components/accessibility_checks.py
"""
All accessibility checks consolidated into one module.
"""

import requests
import re
from bs4 import BeautifulSoup


class AccessibilityChecker:
    def __init__(self):
        self.timeout = 10
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    
    def analyze_page(self, url):
        """Analyze a single page with all checks"""
        issues = []
        
        try:
            # Get page content once
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Run all checks
            issues.extend(self.check_alt_texts(url, soup))
            issues.extend(self.check_aria_labels(url, soup))
            issues.extend(self.check_navigation_structure(url, soup))
            issues.extend(self.check_forms(url, soup))
            issues.extend(self.check_basic_accessibility(url, soup))
            issues.extend(self.check_advanced_accessibility(url, soup))
            
        except Exception as e:
            print(f"Error analyzing {url}: {e}")
        
        return issues
    
    def check_alt_texts(self, url, soup):
        """Check for proper alt text implementation"""
        issues = []
        
        try:
            images = soup.find_all('img')
            if not images:
                return issues
            
            missing_alt = 0
            empty_alt = 0
            decorative_images = 0
            total_images = len(images)
            details = []
            
            for img in images:
                alt = img.get('alt')
                src = img.get('src', 'unknown')
                
                if alt is None:
                    missing_alt += 1
                    details.append(f"Bild ohne Alt-Text: {src[:50]}...")
                elif alt.strip() == '':
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
                    'effort_hours': max(0.25, total_issues * 0.15),
                    'details': details[:8],
                    'wcag_criterion': '1.1.1 Nicht-Text-Inhalte',
                    'impact': 'KRITISCH - Screenreader-Nutzer können essenzielle Bildinformationen nicht erfassen'
                })
        
        except Exception as e:
            print(f"Alt text check error: {e}")
        
        return issues
    
    def check_aria_labels(self, url, soup):
        """Check ARIA labels and accessibility markup"""
        issues = []
        
        try:
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
            details = []
            
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
                    'effort_hours': max(0.5, (missing_labels * 0.15) + (landmark_issues * 0.75)),
                    'details': details[:10],
                    'wcag_criterion': '4.1.2 Name, Rolle, Wert',
                    'impact': 'KRITISCH - Assistive Technologien versagen bei der Elementidentifikation'
                })
        
        except Exception as e:
            print(f"ARIA check error: {e}")
        
        return issues
    
    def check_navigation_structure(self, url, soup):
        """Check navigation and heading structure"""
        issues = []
        
        try:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            h1_elements = soup.find_all('h1')
            h1_count = len(h1_elements)
            details = []
            
            # Check H1 structure
            if h1_count > 1:
                h1_texts = [h1.get_text().strip()[:50] for h1 in h1_elements]
                details.append(f"Mehrere H1 gefunden: {', '.join(h1_texts)}")
                issues.append({
                    'category': 'SHOULD DO',
                    'type': 'Überschriftenstruktur - Mehrere H1',
                    'description': f'{h1_count} H1-Überschriften gefunden (sollte nur eine pro Seite sein)',
                    'count': h1_count - 1,
                    'effort_hours': 0.25,
                    'details': details + ["Lösung: Nur eine H1 pro Seite verwenden"],
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
                    'effort_hours': 0.15,
                    'details': details + ["Lösung: H1 mit aussagekräftigem Seitentitel hinzufügen"],
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
                    'effort_hours': skipped_levels * 0.15,
                    'details': hierarchy_issues + ["Lösung: Logische Reihenfolge H1 → H2 → H3 verwenden"],
                    'wcag_criterion': '1.3.1 Info und Beziehungen',
                    'impact': 'Mittel - Unlogische Inhaltsstruktur'
                })
        
        except Exception as e:
            print(f"Navigation check error: {e}")
        
        return issues
    
    def check_forms(self, url, soup):
        """Check form accessibility"""
        issues = []
        
        try:
            forms = soup.find_all('form')
            if not forms:
                return issues
            
            form_issues = 0
            error_handling_issues = 0
            details = []
            
            for form_idx, form in enumerate(forms):
                form_details = []
                
                controls = form.find_all(['input', 'select', 'textarea'])
                
                for control in controls:
                    control_type = control.get('type', control.name)
                    has_label = False
                    
                    if control.get('type') == 'hidden':
                        continue
                    
                    # Check various labeling methods
                    control_id = control.get('id')
                    if control_id:
                        label = soup.find('label', attrs={'for': control_id})
                        if label:
                            has_label = True
                    
                    if not has_label and control.get('aria-label'):
                        has_label = True
                    
                    if not has_label and control.get('aria-labelledby'):
                        has_label = True
                    
                    if not has_label and control.get('title'):
                        has_label = True
                    
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
                    'effort_hours': (form_issues * 0.15) + (error_handling_issues * 0.75),
                    'details': details[:8] + ["Lösung: <label for='email'>E-Mail:</label> hinzufügen"],
                    'wcag_criterion': '3.3.1 Fehlererkennung, 3.3.2 Beschriftungen oder Anweisungen',
                    'impact': 'KRITISCH - Formulare sind für behinderte Nutzer völlig unzugänglich'
                })
        
        except Exception as e:
            print(f"Form check error: {e}")
        
        return issues
    
    def check_basic_accessibility(self, url, soup):
        """Check basic accessibility requirements"""
        issues = []
        
        try:
            page_issues = []
            details = []
            
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
            
            # Check for viewport meta tag
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
                critical_issues = [issue for issue in page_issues if any(word in issue.lower() for word in ['titel', 'lang'])]
                nice_to_have_issues = [issue for issue in page_issues if issue not in critical_issues]
                
                if critical_issues:
                    issues.append({
                        'category': 'MANDATORY',
                        'type': 'Grundlegende Seitenstruktur',
                        'description': f'{len(critical_issues)} kritische Seitenprobleme',
                        'count': len(critical_issues),
                        'effort_hours': len(critical_issues) * 0.15,
                        'details': critical_issues + ["Lösung: <html lang='de'> für deutsche Inhalte"],
                        'wcag_criterion': '3.1.1 Sprache der Seite, 2.4.2 Seitentitel',
                        'impact': 'KRITISCH - Grundlegende Webstandards werden nicht erfüllt'
                    })
                
                if nice_to_have_issues:
                    issues.append({
                        'category': 'NICE TO HAVE',
                        'type': 'Erweiterte Zugänglichkeit',
                        'description': f'{len(nice_to_have_issues)} Verbesserungsmöglichkeiten',
                        'count': len(nice_to_have_issues),
                        'effort_hours': len(nice_to_have_issues) * 0.35,
                        'details': nice_to_have_issues + ["Lösung: Skip-Link 'Zum Hauptinhalt springen' am Seitenanfang"],
                        'wcag_criterion': '2.4.1 Blöcke umgehen',
                        'impact': 'Niedrig - Verbessert Benutzererfahrung'
                    })
        
        except Exception as e:
            print(f"Basic accessibility check error: {e}")
        
        return issues
    
    def check_advanced_accessibility(self, url, soup):
        """Check advanced accessibility features"""
        issues = []
        
        try:
            # Check for tables without proper headers
            tables = soup.find_all('table')
            table_issues = 0
            details = []
            
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
            
            # Check for color-only information
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
                    'effort_hours': (table_issues * 0.35) + (media_issues * 0.75) + (0.35 if len(color_indicators) > 3 else 0),
                    'details': details + ["Lösung: <th scope='col'>Spalte</th> verwenden"],
                    'wcag_criterion': '1.3.1 Info und Beziehungen, 1.4.1 Verwendung von Farbe',
                    'impact': 'Mittel - Spezielle Inhaltstypen nicht zugänglich'
                })
        
        except Exception as e:
            print(f"Advanced accessibility check error: {e}")
        
        return issues