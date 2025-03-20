import os
import json
from datetime import datetime
import logging
import markdown
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Setup logging
logger = logging.getLogger(__name__)

def export_to_pdf(content, risk_score, file_name, output_dir):
    """
    Exports analysis results to a professionally formatted PDF
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        export_path = os.path.join(output_dir, f"{file_name}_analysis.pdf")
        
        doc = SimpleDocTemplate(
            export_path, 
            pagesize=LETTER,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Enhanced styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Heading1',
            parent=styles['Heading1'],
            spaceAfter=12,
            spaceBefore=24,
            textColor=colors.darkblue
        ))
        styles.add(ParagraphStyle(
            name='Heading2',
            parent=styles['Heading2'],
            spaceAfter=10,
            spaceBefore=18,
            textColor=colors.darkblue
        ))
        styles.add(ParagraphStyle(
            name='Normal',
            parent=styles['Normal'],
            spaceBefore=6,
            spaceAfter=6
        ))
        
        # Convert markdown to HTML for Paragraph elements
        html_content = markdown.markdown(content)
        # Split by headers for better organization
        sections = html_content.split('<h1>')
        content_elements = []
        
        # Add title and metadata
        content_elements.append(Paragraph("Legal Document Analysis", styles['Title']))
        content_elements.append(Spacer(1, 0.1*inch))
        
        # Add document info table
        risk_level = "Low" if risk_score < 20 else "Medium" if risk_score < 50 else "High"
        risk_color = colors.green if risk_score < 20 else colors.orange if risk_score < 50 else colors.red
        
        data = [
            ["Document", file_name],
            ["Analysis Date", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Risk Score", f"{risk_score} ({risk_level} Risk)"]
        ]
        
        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (1, 2), (1, 2), risk_color),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        content_elements.append(t)
        content_elements.append(Spacer(1, 0.2*inch))
        
        # Process each section from markdown
        for section in sections:
            if not section.strip():
                continue
                
            if '<h1>' not in section:
                section = f'<h1>Summary</h1>{section}'
                
            parts = section.split('</h1>')
            header = parts[0].strip()
            body = parts[1] if len(parts) > 1 else ""
            
            # Add section header
            content_elements.append(Paragraph(header, styles['Heading1']))
            
            # Process body text which might contain h2 tags
            body_parts = body.split('<h2>')
            
            for i, part in enumerate(body_parts):
                if i == 0:
                    # First part is text before any h2
                    if part.strip():
                        content_elements.append(Paragraph(part, styles['Normal']))
                else:
                    # Subsequent parts contain h2 headers
                    subparts = part.split('</h2>')
                    subheader = subparts[0].strip()
                    subbody = subparts[1] if len(subparts) > 1 else ""
                    
                    content_elements.append(Paragraph(subheader, styles['Heading2']))
                    if subbody.strip():
                        content_elements.append(Paragraph(subbody, styles['Normal']))
        
        # Build the PDF
        doc.build(content_elements)
        logger.info(f"Exported analysis to PDF: {export_path}")
        return export_path
        
    except Exception as e:
        logger.error(f"Failed to export PDF: {e}")
        return None

def export_to_text(content, risk_score, file_name, output_dir):
    """
    Exports analysis results to a text file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        export_path = os.path.join(output_dir, f"{file_name}_analysis.txt")
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(f"LEGAL DOCUMENT ANALYSIS\n")
            f.write(f"======================\n\n")
            
            f.write(f"Document: {file_name}\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            risk_level = "Low" if risk_score < 20 else "Medium" if risk_score < 50 else "High"
            f.write(f"Risk Score: {risk_score} ({risk_level} Risk)\n\n")
            
            f.write(content)
        
        logger.info(f"Exported analysis to text: {export_path}")
        return export_path
        
    except Exception as e:
        logger.error(f"Failed to export text: {e}")
        return None

def export_to_json(content, risk_score, file_name, output_dir, risk_details=None):
    """
    Exports analysis results to a structured JSON file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        export_path = os.path.join(output_dir, f"{file_name}_analysis.json")
        
        risk_level = "Low" if risk_score < 20 else "Medium" if risk_score < 50 else "High"
        
        data = {
            "document": {
                "name": file_name,
                "analysis_date": datetime.now().isoformat()
            },
            "risk": {
                "score": risk_score,
                "level": risk_level,
                "details": risk_details if risk_details else []
            },
            "content": content
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported analysis to JSON: {export_path}")
        return export_path
        
    except Exception as e:
        logger.error(f"Failed to export JSON: {e}")
        return None