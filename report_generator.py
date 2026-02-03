"""
Report Generator Module

This module provides functionality to generate comprehensive reports from Jira tickets
in various formats (CSV, PDF).
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generator for creating reports from Jira ticket data.
    
    Supports CSV and PDF formats with comprehensive ticket information,
    summary statistics, and timestamps.
    """
    
    def __init__(self, output_dir: str = 'reports'):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save generated reports (default: 'reports')
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _extract_ticket_data(self, tickets: List[Dict]) -> List[Dict]:
        """
        Extract and normalize ticket data from Jira API response.
        
        Args:
            tickets: List of ticket dictionaries from Jira API
            
        Returns:
            List of normalized ticket data dictionaries
        """
        extracted_data = []
        
        for ticket in tickets:
            fields = ticket.get('fields', {})
            
            # Extract assignee information
            assignee = fields.get('assignee')
            assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
            
            # Extract reporter information
            reporter = fields.get('reporter')
            reporter_name = reporter.get('displayName', 'Unknown') if reporter else 'Unknown'
            
            # Extract status
            status = fields.get('status')
            status_name = status.get('name', 'Unknown') if status else 'Unknown'
            
            # Extract priority
            priority = fields.get('priority')
            priority_name = priority.get('name', 'None') if priority else 'None'
            
            # Extract issue type
            issuetype = fields.get('issuetype')
            issuetype_name = issuetype.get('name', 'Unknown') if issuetype else 'Unknown'
            
            # Extract labels and components
            labels = ', '.join(fields.get('labels', []))
            components = ', '.join([c.get('name', '') for c in fields.get('components', [])])
            
            ticket_data = {
                'Ticket ID': ticket.get('key', 'N/A'),
                'Summary': fields.get('summary', 'N/A'),
                'Status': status_name,
                'Type': issuetype_name,
                'Priority': priority_name,
                'Assignee': assignee_name,
                'Reporter': reporter_name,
                'Created': fields.get('created', 'N/A'),
                'Updated': fields.get('updated', 'N/A'),
                'Resolution Date': fields.get('resolutiondate', 'N/A'),
                'Labels': labels,
                'Components': components,
                'Description': fields.get('description', 'N/A')
            }
            
            # Add custom fields if present
            for key, value in fields.items():
                if key.startswith('customfield_') and value:
                    # Format custom field name
                    field_name = f"Custom_{key.replace('customfield_', '')}"
                    ticket_data[field_name] = str(value)
            
            extracted_data.append(ticket_data)
        
        return extracted_data
    
    def _calculate_statistics(self, ticket_data: List[Dict]) -> Dict:
        """
        Calculate summary statistics from ticket data.
        
        Args:
            ticket_data: List of normalized ticket dictionaries
            
        Returns:
            Dictionary containing summary statistics
        """
        if not ticket_data:
            return {
                'total_tickets': 0,
                'by_status': {},
                'by_type': {},
                'by_priority': {},
                'by_assignee': {}
            }
        
        # Count tickets by various categories
        status_counts = {}
        type_counts = {}
        priority_counts = {}
        assignee_counts = {}
        
        for ticket in ticket_data:
            # Count by status
            status = ticket.get('Status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by type
            ticket_type = ticket.get('Type', 'Unknown')
            type_counts[ticket_type] = type_counts.get(ticket_type, 0) + 1
            
            # Count by priority
            priority = ticket.get('Priority', 'None')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Count by assignee
            assignee = ticket.get('Assignee', 'Unassigned')
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        return {
            'total_tickets': len(ticket_data),
            'by_status': status_counts,
            'by_type': type_counts,
            'by_priority': priority_counts,
            'by_assignee': assignee_counts
        }
    
    def generate_csv_report(self, tickets: List[Dict], project_key: str,
                           filename: Optional[str] = None) -> str:
        """
        Generate a CSV report from Jira tickets.
        
        Args:
            tickets: List of ticket dictionaries from Jira API
            project_key: The project key for naming the report
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the generated CSV file
        """
        # Extract and normalize ticket data
        ticket_data = self._extract_ticket_data(tickets)
        
        if not ticket_data:
            logger.warning("No ticket data to generate report")
            return None
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if filename:
            csv_filename = f"{filename}.csv"
        else:
            csv_filename = f"{project_key}_report_{timestamp}.csv"
        
        csv_path = os.path.join(self.output_dir, csv_filename)
        
        # Get all unique field names (keys) from all tickets
        all_fields = set()
        for ticket in ticket_data:
            all_fields.update(ticket.keys())
        
        # Define field order (standard fields first, then custom fields)
        standard_fields = ['Ticket ID', 'Summary', 'Status', 'Type', 'Priority', 
                          'Assignee', 'Reporter', 'Created', 'Updated', 
                          'Resolution Date', 'Labels', 'Components', 'Description']
        
        # Add custom fields at the end
        custom_fields = sorted([f for f in all_fields if f not in standard_fields])
        fieldnames = [f for f in standard_fields if f in all_fields] + custom_fields
        
        # Write CSV file
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(ticket_data)
        
        logger.info(f"CSV report generated: {csv_path}")
        return csv_path
    
    def generate_pdf_report(self, tickets: List[Dict], project_key: str,
                           filename: Optional[str] = None) -> str:
        """
        Generate a PDF report from Jira tickets.
        
        Args:
            tickets: List of ticket dictionaries from Jira API
            project_key: The project key for naming the report
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the generated PDF file
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            logger.error("reportlab is required for PDF generation. Install it with: pip install reportlab")
            raise
        
        # Extract and normalize ticket data
        ticket_data = self._extract_ticket_data(tickets)
        
        if not ticket_data:
            logger.warning("No ticket data to generate report")
            return None
        
        # Calculate statistics
        stats = self._calculate_statistics(ticket_data)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if filename:
            pdf_filename = f"{filename}.pdf"
        else:
            pdf_filename = f"{project_key}_report_{timestamp}.pdf"
        
        pdf_path = os.path.join(self.output_dir, pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                               rightMargin=0.5*inch, leftMargin=0.5*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        title = Paragraph(f"Jira Project Report: {project_key}", title_style)
        elements.append(title)
        
        # Timestamp
        report_time = Paragraph(
            f"<para align=center>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</para>",
            styles['Normal']
        )
        elements.append(report_time)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary Statistics Section
        elements.append(Paragraph("Summary Statistics", heading_style))
        
        summary_data = [
            ['Total Tickets:', str(stats['total_tickets'])],
            ['', '']
        ]
        
        # Add status breakdown
        summary_data.append(['Status Breakdown:', ''])
        for status, count in sorted(stats['by_status'].items()):
            summary_data.append([f"  {status}:", str(count)])
        
        summary_data.append(['', ''])
        
        # Add type breakdown
        summary_data.append(['Type Breakdown:', ''])
        for type_name, count in sorted(stats['by_type'].items()):
            summary_data.append([f"  {type_name}:", str(count)])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detailed Tickets Section
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Ticket Information", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table for each ticket (simplified view)
        for ticket in ticket_data:
            # Extract values for better readability
            summary = ticket.get('Summary', 'N/A')
            summary_display = summary[:80] + '...' if len(summary) > 80 else summary
            created = ticket.get('Created', 'N/A')
            created_display = created[:10] if created != 'N/A' else 'N/A'
            updated = ticket.get('Updated', 'N/A')
            updated_display = updated[:10] if updated != 'N/A' else 'N/A'
            
            ticket_table_data = [
                ['Ticket ID:', ticket.get('Ticket ID', 'N/A')],
                ['Summary:', summary_display],
                ['Status:', ticket.get('Status', 'N/A')],
                ['Type:', ticket.get('Type', 'N/A')],
                ['Priority:', ticket.get('Priority', 'N/A')],
                ['Assignee:', ticket.get('Assignee', 'N/A')],
                ['Created:', created_display],
                ['Updated:', updated_display],
            ]
            
            ticket_table = Table(ticket_table_data, colWidths=[1.5*inch, 5*inch])
            ticket_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E6F2FF')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            elements.append(ticket_table)
            elements.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(elements)
        
        logger.info(f"PDF report generated: {pdf_path}")
        return pdf_path
