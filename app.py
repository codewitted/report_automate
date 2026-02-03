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
app.secret_key = os.urandom(24)  # For flash messages

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
        project_key = request.form.get('project_key', '').strip()
        report_format = request.form.get('format', 'csv')
        max_results = int(request.form.get('max_results', 100))
        
        # Validate inputs
        if not all([base_url, email, api_token, project_key]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        logger.info(f"Generating report for project {project_key}")
        
        # Initialize Jira client
        client = JiraClient(
            base_url=base_url,
            email=email,
            api_token=api_token
        )
        
        # Test connection
        client.test_connection()
        
        # Retrieve tickets
        tickets = client.get_project_tickets(
            project_key=project_key,
            max_results=max_results
        )
        
        if not tickets:
            return jsonify({
                'success': False,
                'error': f'No tickets found in project {project_key}'
            }), 404
        
        # Generate reports
        report_gen = ReportGenerator(output_dir=REPORT_DIR)
        generated_files = []
        
        if report_format in ['csv', 'both']:
            csv_file = report_gen.generate_csv_report(
                tickets=tickets,
                project_key=project_key
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
                project_key=project_key
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
            'message': f'Successfully generated {len(generated_files)} report(s) from {len(tickets)} tickets',
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
    
    app.run(debug=True, host='0.0.0.0', port=5000)
