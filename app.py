#!/usr/bin/env python3
"""
Web-based Jira Report Automation

Simple web interface for generating Jira reports with just a few clicks.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename

from jira_client import JiraClient, JiraAPIError
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # For flash messages

# Configuration
REPORT_DIR = 'reports'
os.makedirs(REPORT_DIR, exist_ok=True)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_report():
    """Generate Jira report based on form submission."""
    try:
        # Get form data
        base_url = request.form.get('base_url', '').strip()
        email = request.form.get('email', '').strip()
        api_token = request.form.get('api_token', '').strip()
        report_format = request.form.get('format', 'csv')
        
        # Get report mode
        report_mode = request.form.get('report_mode', 'project')
        
        # Validate basic inputs
        if not all([base_url, email, api_token]):
            return jsonify({
                'success': False,
                'error': 'Base URL, email, and API token are required'
            }), 400
        
        # Initialize Jira client
        client = JiraClient(
            base_url=base_url,
            email=email,
            api_token=api_token
        )
        
        # Test connection
        client.test_connection()
        
        # Retrieve tickets based on mode
        tickets = []
        identifier = ""
        
        if report_mode == 'single':
            # Single ticket mode
            ticket_id = request.form.get('ticket_id', '').strip()
            if not ticket_id:
                return jsonify({
                    'success': False,
                    'error': 'Ticket ID is required for single ticket mode'
                }), 400
            
            logger.info(f"Retrieving single ticket: {ticket_id}")
            ticket = client.get_single_ticket(ticket_id)
            tickets = [ticket]
            identifier = ticket_id
            
        elif report_mode == 'jql':
            # Custom JQL mode
            jql = request.form.get('jql_query', '').strip()
            max_results = int(request.form.get('max_results', 100))
            
            if not jql:
                return jsonify({
                    'success': False,
                    'error': 'JQL query is required for JQL mode'
                }), 400
            
            logger.info(f"Retrieving tickets with JQL: {jql}")
            tickets = client.get_tickets_by_jql(jql, max_results=max_results)
            identifier = "custom_query"
            
        else:
            # Project mode (default)
            project_key = request.form.get('project_key', '').strip()
            max_results = int(request.form.get('max_results', 100))
            
            if not project_key:
                return jsonify({
                    'success': False,
                    'error': 'Project key is required for project mode'
                }), 400
            
            logger.info(f"Generating report for project {project_key}")
            tickets = client.get_project_tickets(
                project_key=project_key,
                max_results=max_results
            )
            identifier = project_key
        
        if not tickets:
            error_msg = 'No tickets found'
            if report_mode == 'single':
                error_msg = f'Ticket not found: {ticket_id}'
            elif report_mode == 'jql':
                error_msg = f'No tickets match the query: {jql}'
            elif report_mode == 'project':
                error_msg = f'No tickets found in project {project_key}'
            
            return jsonify({
                'success': False,
                'error': error_msg
            }), 404
        
        # Generate reports
        report_gen = ReportGenerator(output_dir=REPORT_DIR)
        generated_files = []
        
        if report_format in ['csv', 'both']:
            csv_file = report_gen.generate_csv_report(
                tickets=tickets,
                project_key=identifier
            )
            if csv_file:
                generated_files.append({
                    'path': csv_file,
                    'name': os.path.basename(csv_file),
                    'type': 'csv'
                })
        
        if report_format in ['pdf', 'both']:
            pdf_file = report_gen.generate_pdf_report(
                tickets=tickets,
                project_key=identifier
            )
            if pdf_file:
                generated_files.append({
                    'path': pdf_file,
                    'name': os.path.basename(pdf_file),
                    'type': 'pdf'
                })
        
        logger.info(f"Successfully generated {len(generated_files)} report(s)")
        
        return jsonify({
            'success': True,
            'message': f'Successfully generated {len(generated_files)} report(s) from {len(tickets)} ticket(s)',
            'files': generated_files,
            'ticket_count': len(tickets)
        })
        
    except JiraAPIError as e:
        logger.error(f"Jira API Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Jira API Error: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download a generated report."""
    try:
        # Secure the filename to prevent directory traversal
        safe_filename = secure_filename(filename)
        file_path = os.path.join(REPORT_DIR, safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename
        )
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Error downloading file'}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("Jira Report Automation - Web Interface")
    print("=" * 60)
    print()
    print("Starting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run in debug mode only if DEBUG env var is set
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
