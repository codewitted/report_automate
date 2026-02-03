#!/usr/bin/env python3
"""
Example Usage Script

This script demonstrates how to use the Jira automation programmatically
instead of via command line.
"""

import logging
from jira_client import JiraClient, JiraAPIError
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_usage():
    """Example of using the Jira automation modules programmatically."""
    
    # Configuration (in practice, load these from config file or environment)
    JIRA_BASE_URL = "https://your-instance.atlassian.net"
    JIRA_EMAIL = "your-email@example.com"
    JIRA_API_TOKEN = "your-api-token-here"
    PROJECT_KEY = "PROJ"
    
    try:
        # 1. Initialize Jira client
        logger.info("Initializing Jira client...")
        client = JiraClient(
            base_url=JIRA_BASE_URL,
            email=JIRA_EMAIL,
            api_token=JIRA_API_TOKEN
        )
        
        # 2. Test connection
        logger.info("Testing connection to Jira...")
        client.test_connection()
        logger.info("✓ Connection successful")
        
        # 3. Retrieve tickets
        logger.info(f"Retrieving tickets from project {PROJECT_KEY}...")
        tickets = client.get_project_tickets(
            project_key=PROJECT_KEY,
            max_results=50
        )
        logger.info(f"✓ Retrieved {len(tickets)} tickets")
        
        # 4. Generate reports
        logger.info("Generating reports...")
        report_gen = ReportGenerator(output_dir='reports')
        
        # Generate CSV report
        csv_file = report_gen.generate_csv_report(
            tickets=tickets,
            project_key=PROJECT_KEY,
            filename="example_report"
        )
        logger.info(f"✓ CSV report generated: {csv_file}")
        
        # Generate PDF report
        pdf_file = report_gen.generate_pdf_report(
            tickets=tickets,
            project_key=PROJECT_KEY,
            filename="example_report"
        )
        logger.info(f"✓ PDF report generated: {pdf_file}")
        
        logger.info("Example completed successfully!")
        
    except JiraAPIError as e:
        logger.error(f"Jira API Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == '__main__':
    print("=" * 60)
    print("Jira Automation - Example Usage")
    print("=" * 60)
    print()
    print("NOTE: This is an example script. To run it:")
    print("1. Update the configuration values at the top of this file")
    print("2. Or use the main jira_automation.py script instead")
    print()
    print("Uncomment the line below to run the example:")
    print()
    print("=" * 60)
    
    # Uncomment the line below to run the example
    # example_usage()
