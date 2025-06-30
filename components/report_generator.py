# components/report_generator.py
"""
PDF report generation for accessibility analysis.
Creates professional, detailed PDF reports with styling and recommendations.
"""

import os
from datetime import datetime
from urllib.parse import urlparse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ReportGenerator:
    """Generates professional PDF reports for accessibility analysis."""
    
    def __init__(self):
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create custom styles for the PDF report."""
        base_styles = getSampleStyleSheet()
        
        styles = {
            'title': ParagraphStyle(
                'DetailedTitle',
                parent=base_styles['Heading1'],
                fontSize=28,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=20,
                spaceBefore=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            
            'subtitle': ParagraphStyle(
                'Subtitle',
                parent=base_styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#4a5568'),
                spaceAfter=25,
                alignment=TA_CENTER,
                fontName='Helvetica'
            ),
            
            'heading': ParagraphStyle(
                'DetailedHeading',
                parent=base_styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#2d3748'),
                spaceBefore=25,
                spaceAfter=12,
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=colors.HexColor('#e2e8f0'),
                borderPadding=8,
                backColor=colors.HexColor('#f7fafc')
            ),
            
            'subheading': ParagraphStyle(
                'DetailedSubHeading',
                parent=base_styles['Heading3'],
                fontSize=14,
                textColor=colors.HexColor('#4a5568'),
                spaceBefore=15,
                spaceAfter=8,
                fontName='Helvetica-Bold'
            ),
            
            'normal': ParagraphStyle(
                'DetailedNormal',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceBefore=4,
                spaceAfter=4,
                fontName='Helvetica',
                leading=14
            ),
            
            'highlight': ParagraphStyle(
                'Highlight',
                parent=base_styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#2b6cb0'),
                spaceBefore=4,
                spaceAfter=4,
                leading=14
            ),
            
            'mandatory': ParagraphStyle(
                'MandatoryDetailed',
                parent=base_styles['Normal'],
                fontSize=13,
                textColor=colors.HexColor('#c53030'),
                fontName='Helvetica-Bold',
                backColor=colors.HexColor('#fed7d7'),
                borderWidth=1,
                borderColor=colors.HexColor('#fc8181'),
                borderPadding=6
            ),
            
            'should': ParagraphStyle(
                'ShouldDetailed',
                parent=base_styles['Normal'],
                fontSize=13,
                textColor=colors.HexColor('#d69e2e'),
                fontName='Helvetica-Bold',
                backColor=colors.HexColor('#faf089'),
                borderWidth=1,
                borderColor=colors.HexColor('#f6e05e'),
                borderPadding=6
            ),
            
            'nice': ParagraphStyle(
                'NiceDetailed',
                parent=base_styles['Normal'],
                fontSize=13,
                textColor=colors.HexColor('#38a169'),
                fontName='Helvetica-Bold',
                backColor=colors.HexColor('#c6f6d5'),
                borderWidth=1,
                borderColor=colors.HexColor('#68d391'),
                borderPadding=6
            )
        }
        
        return styles
    
    def generate_pdf_report(self, base_url, analyzed_pages, issues, technologies, filename=None):
        """Generate comprehensive PDF report."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(base_url).netloc
            filename = f"output/reports/accessibility_report_{domain}_{timestamp}.pdf"
        elif not filename.startswith('output/'):
            filename = f"output/reports/{filename}"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, 
                               leftMargin=0.75*inch, rightMargin=0.75*inch)
        story = []
        
        # Build report content
        self._add_title_page(story, base_url, analyzed_pages, technologies)
        self._add_executive_summary(story, issues)
        story.append(PageBreak())
        self._add_detailed_analysis(story, issues)
        # Let content flow naturally - no forced page break
        self._add_recommendations(story, issues)
        
        try:
            doc.build(story)
            print(f"PDF report generated: {filename}")
            return filename
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def _has_recommendations(self, issues):
        """Check if there are recommendations to show."""
        conclusion = self._generate_conclusion(issues)
        return (conclusion['priority_actions'] or 
                conclusion['quick_wins'] or 
                any(issues.values()))
    
    def _add_title_page(self, story, base_url, analyzed_pages, technologies):
        """Add title page and basic information."""
        story.append(Paragraph("Website Accessibility Analysis", self.styles['title']))
        story.append(Paragraph("WCAG 2.1 AA Compliance Assessment", self.styles['subtitle']))
        story.append(Spacer(1, 25))
        
        # Website info table
        tech_summary = []
        if technologies.get('cms'):
            tech_summary.extend(technologies['cms'])
        if technologies.get('frameworks'):
            tech_summary.extend(technologies['frameworks'][:2])
        tech_text = ', '.join(tech_summary) if tech_summary else 'Nicht erkannt'
        
        info_data = [
            ['Website URL:', base_url],
            ['Analysierte Seiten:', str(len(analyzed_pages))],
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
    
    def _add_executive_summary(self, story, issues):
        """Add executive summary section."""
        story.append(Paragraph("Executive Summary", self.styles['heading']))
        
        conclusion = self._generate_conclusion(issues)
        
        # Compliance status table
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
        
        # Summary text
        summary_text = f"""
        <b>Bewertung:</b> {conclusion['compliance_description']}<br/>
        <br/>
        <b>Kritische Analyseergebnisse:</b> Bei der umfassenden Untersuchung wurden 
        <b>{conclusion['total_issues']} potentiell rechtskritische Verbesserungsbereiche</b> identifiziert. 
        Der Gesamtaufwand zur vollständigen WCAG-Konformität beträgt {conclusion['total_hours']:.1f} Arbeitsstunden.<br/>
        <br/>
        <b>Rechtliche Risikobewertung:</b> Das Haftungsrisiko wird als <b>{conclusion['legal_risk']}</b> eingestuft. 
        {'KRITISCH: Sofortige Maßnahmen erforderlich um rechtliche Konsequenzen zu vermeiden!' if conclusion['legal_risk'] == 'HOCH' else 
         'WICHTIG: Zeitnahe Behebung empfohlen um Compliance-Risiken zu minimieren.' if conclusion['legal_risk'] == 'MITTEL' else
         'STABIL: Grundlegende Rechtssicherheit gegeben, strategische Optimierungen empfohlen.'}
        """
        
        story.append(Paragraph(summary_text, self.styles['normal']))
        story.append(Spacer(1, 20))
        
        # Overview table
        overview_data = [
            ['Kategorie', 'Issues', 'Aufwand', 'Priorität', 'Beschreibung'],
            ['MANDATORY', 
             str(len(issues['MANDATORY'])), 
             f"{sum(issue['effort_hours'] for issue in issues['MANDATORY']):.1f}",
             'SOFORT',
             'Rechtskritische Mängel'],
            ['SHOULD DO', 
             str(len(issues['SHOULD DO'])), 
             f"{sum(issue['effort_hours'] for issue in issues['SHOULD DO']):.1f}",
             'Kurzfristig',
             'dringend empfohlen'],
            ['NICE TO HAVE', 
             str(len(issues['NICE TO HAVE'])), 
             f"{sum(issue['effort_hours'] for issue in issues['NICE TO HAVE']):.1f}",
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
    
    def _add_detailed_analysis(self, story, issues):
        """Add detailed issues analysis."""
        story.append(Paragraph("Detaillierte Problemanalyse", self.styles['heading']))
        story.append(Spacer(1, 15))
        
        categories = [
            ('MANDATORY', self.styles['mandatory'], 'Rechtskritische Mängel', 
             'Diese Issues bergen erhebliches Haftungsrisiko und müssen SOFORT behoben werden.'),
            ('SHOULD DO', self.styles['should'], 'Compliance-Lücken', 
             'Diese Probleme gefährden die WCAG-Konformität und sollten dringend angegangen werden.'),
            ('NICE TO HAVE', self.styles['nice'], 'Strategische Optimierungen', 
             'Diese Verbesserungen schaffen Wettbewerbsvorteile in digitaler Inklusion.')
        ]
        
        for category, style, title, description in categories:
            if issues[category]:
                story.append(Paragraph(title, style))
                story.append(Spacer(1, 5))
                story.append(Paragraph(description, self.styles['normal']))
                story.append(Spacer(1, 10))
                
                for i, issue in enumerate(issues[category]):
                    # Issue header
                    effort_str = f"{issue['effort_hours']:.1f}".rstrip('0').rstrip('.')
                    page_indicator = f" (auf {issue.get('page_count', 1)} Seite{'n' if issue.get('page_count', 1) > 1 else ''})" if issue.get('page_count', 1) > 1 else ""
                    
                    issue_title = f"{i+1}. {issue['type']} - {effort_str}h{page_indicator}"
                    story.append(Paragraph(issue_title, self.styles['subheading']))
                    
                    # Issue details
                    issue_details = f"""
                    <b>Problem:</b> {issue['description']}<br/>
                    <b>WCAG Kriterium:</b> {issue.get('wcag_criterion', 'Nicht spezifiziert')}<br/>
                    <b>Auswirkung:</b> {issue.get('impact', 'Nicht bewertet')}<br/>
                    <b>Geschätzter Aufwand:</b> {effort_str} Stunden
                    """
                    
                    story.append(Paragraph(issue_details, self.styles['normal']))
                    
                    # Details table
                    if issue.get('details'):
                        details_data = [['Details & Beispiele:', '']]
                        
                        for detail in issue['details'][:6]:
                            if len(detail) > 120:
                                detail = detail[:117] + "..."
                            details_data.append(['', f"• {detail}"])
                        
                        details_table = Table(details_data, colWidths=[1.2*inch, 5.3*inch])
                        details_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (0, 0), 10),
                            ('SPAN', (0, 0), (-1, 0)),
                            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('PADDING', (0, 0), (-1, -1), 6),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                            ('LEADING', (0, 0), (-1, -1), 12),
                            ('LEFTPADDING', (1, 1), (1, -1), 12),
                        ]))
                        
                        story.append(details_table)
                    
                    story.append(Spacer(1, 15))
                
                # Reduce spacing after each category, especially the last one
                if category != 'NICE TO HAVE':
                    story.append(Spacer(1, 20))
                else:
                    story.append(Spacer(1, 5))  # Minimal space after the last category
    
    def _add_recommendations(self, story, issues):
        """Add recommendations section."""
        story.append(Paragraph("Handlungsempfehlungen", self.styles['heading']))
        
        conclusion = self._generate_conclusion(issues)
        
        if conclusion['priority_actions']:
            story.append(Paragraph("Prioritäre Sofortmaßnahmen", self.styles['subheading']))
            story.append(Spacer(1, 5))  # Reduced spacing
            
            for action in conclusion['priority_actions']:
                story.append(Paragraph(f"• {action}", self.styles['highlight']))
                story.append(Spacer(1, 3))  # Reduced spacing
            
            story.append(Spacer(1, 12))  # Reduced spacing
        
        # Quick wins
        if conclusion['quick_wins']:
            story.append(Paragraph("Quick Wins (≤ 2 Stunden)", self.styles['subheading']))
            story.append(Spacer(1, 5))  # Reduced spacing
            
            for win in conclusion['quick_wins'][:4]:
                story.append(Paragraph(f"• {win['type']}: {win['description']}", self.styles['normal']))
                story.append(Spacer(1, 3))  # Reduced spacing
            
            story.append(Spacer(1, 12))  # Reduced spacing
        
        # Final conclusion
        story.append(Paragraph("Fazit und nächste Schritte", self.styles['subheading']))
        
        conclusion_text = f"""
        Die durchgeführte Barrierefreiheits-Analyse zeigt einen <b>{conclusion['compliance_level']}</b>-Status. 
        {conclusion['compliance_description']}
        <br/><br/>
        <b>Zentrale Befunde:</b><br/>
        • Identifizierte Compliance-Lücken: <b>{conclusion['total_issues']}</b><br/>
        • Investition für vollständige WCAG-Konformität: {conclusion['total_hours']:.1f} Arbeitsstunden<br/>
        • Rechtliches Haftungsrisiko: <b>{conclusion['legal_risk']}</b><br/>
        <br/>
        <b>Strategische Handlungsempfehlung:</b><br/>
        1. SOFORTIGE Behebung aller rechtskritischen Mängel<br/>
        2. Entwicklungsteam-Schulung zu WCAG-Standards<br/>
        3. Systematische Umsetzung nach Risikoprioritäten<br/>
        4. Compliance-Validierung durch Folgeaudit<br/>
        5. Integration permanenter Accessibility-Qualitätssicherung<br/>
        <br/>
        <b>ROI-Hinweis:</b> Proaktive Barrierefreiheit vermeidet rechtliche Risiken, erschließt neue Zielgruppen 
        und verbessert SEO-Rankings nachhaltig.
        """
        
        story.append(Paragraph(conclusion_text, self.styles['normal']))
    
    def _generate_conclusion(self, issues):
        """Generate conclusion and recommendations."""
        total_mandatory = len(issues['MANDATORY'])
        total_should = len(issues['SHOULD DO'])
        total_nice = len(issues['NICE TO HAVE'])
        
        total_hours = {
            'MANDATORY': sum(issue['effort_hours'] for issue in issues['MANDATORY']),
            'SHOULD DO': sum(issue['effort_hours'] for issue in issues['SHOULD DO']),
            'NICE TO HAVE': sum(issue['effort_hours'] for issue in issues['NICE TO HAVE'])
        }
        
        # Determine compliance level
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
        
        # Priority actions
        priority_actions = []
        
        if any('Alt-Texte' in issue['type'] for issue in issues['MANDATORY']):
            priority_actions.append("1. SOFORT: Alt-Texte für alle Bilder implementieren (rechtskritisch)")
        
        if any('Formular' in issue['type'] for issue in issues['MANDATORY']):
            priority_actions.append("2. DRINGEND: Formular-Accessibility und Fehlerbehandlung umsetzen")
        
        if any('ARIA' in issue['type'] for issue in issues['MANDATORY']):
            priority_actions.append("3. KRITISCH: ARIA-Labels für alle interaktiven Elemente ergänzen")
        
        if any('Seitenstruktur' in issue['type'] for issue in issues['MANDATORY']):
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
            'quick_wins': [issue for issue in issues['SHOULD DO'] if issue['effort_hours'] <= 2],
            'major_improvements': [issue for issue in issues['MANDATORY'] if issue['effort_hours'] > 3]
        }