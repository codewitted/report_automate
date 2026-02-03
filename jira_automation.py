#!/usr/bin/env python3
"""
Jira Report Automation

Main script to automate Jira ticket retrieval and report generation.
This script integrates with Jira API to fetch tickets and generate comprehensive reports.

Usage:
    python jira_automation.py [options]
    
Options:
    --format {csv,pdf,both}     Report format (default: csv)
    --project PROJECT_KEY       Override project key from config
    --max-results N             Maximum number of tickets to retrieve (default: 100)
    --output OUTPUT_FILE        Custom output filename (without extension)
    --help                      Show this help message

Examples:
    # Generate CSV report using config file settings
    python jira_automation.py
    
    # Generate PDF report for specific project
    python jira_automation.py --format pdf --project MYPROJ
    
    # Generate both CSV and PDF reports
    python jira_automation.py --format both
    
    # Retrieve more tickets with custom filename
    python jira_automation.py --max-results 500 --output my_custom_report
"""

import argparse
import sys
import logging
from typing import Optional

from jira_client import JiraClient, JiraAPIError
from report_generator import ReportGenerator
from config_manager import ConfigManager, ConfigError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Jira Report Automation - Retrieve tickets and generate reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jira_automation.py
  python jira_automation.py --format pdf --project MYPROJ
  python jira_automation.py --format both --max-results 500
        """
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'pdf', 'both'],
        default=None,
        help='Report format (default: from config file or csv)'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        help='Jira project key (overrides config file)'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Maximum number of tickets to retrieve (default: 100)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Custom output filename without extension (optional)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.ini',
        help='Path to configuration file (default: config.ini)'
    )
    
    return parser.parse_args()


def run_automation(
    jira_config: dict,
    report_config: dict,
    project_key: Optional[str] = None,
    max_results: int = 100,
    report_format: Optional[str] = None,
    output_filename: Optional[str] = None
) -> bool:
    """
    Run the Jira report automation.
    
    Args:
        jira_config: Jira API configuration dictionary
        report_config: Report generation configuration dictionary
        project_key: Optional project key override
        max_results: Maximum number of tickets to retrieve
        report_format: Optional report format override
        output_filename: Optional custom output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use overrides if provided
        project = project_key or jira_config['project_key']
        format_type = report_format or report_config['default_format']
        
        logger.info("=" * 60)
        logger.info("Starting Jira Report Automation")
        logger.info("=" * 60)
        
        # Initialize Jira client
        logger.info(f"Connecting to Jira instance: {jira_config['base_url']}")
        client = JiraClient(
            base_url=jira_config['base_url'],
            email=jira_config['email'],
            api_token=jira_config['api_token']
        )
        
        # Test connection
        client.test_connection()
        
        # Retrieve tickets
        logger.info(f"Retrieving tickets from project: {project}")
        tickets = client.get_project_tickets(
            project_key=project,
            max_results=max_results
        )
        
        if not tickets:
            logger.warning(f"No tickets found in project {project}")
            return False
        
        logger.info(f"Found {len(tickets)} tickets")
        
        # Initialize report generator
        report_gen = ReportGenerator(output_dir=report_config['output_dir'])
        
        # Generate reports based on format
        generated_files = []
        
        if format_type in ['csv', 'both']:
            logger.info("Generating CSV report...")
            csv_file = report_gen.generate_csv_report(
                tickets=tickets,
                project_key=project,
                filename=output_filename
            )
            if csv_file:
                generated_files.append(csv_file)
                logger.info(f"✓ CSV report saved: {csv_file}")
        
        if format_type in ['pdf', 'both']:
            logger.info("Generating PDF report...")
            pdf_file = report_gen.generate_pdf_report(
                tickets=tickets,
                project_key=project,
                filename=output_filename
            )
            if pdf_file:
                generated_files.append(pdf_file)
                logger.info(f"✓ PDF report saved: {pdf_file}")
        
        # Summary
        logger.info("=" * 60)
        logger.info("Report generation completed successfully!")
        logger.info(f"Total tickets processed: {len(tickets)}")
        logger.info(f"Reports generated: {len(generated_files)}")
        for file in generated_files:
            logger.info(f"  - {file}")
        logger.info("=" * 60)
        
        return True
        
    except JiraAPIError as e:
        logger.error(f"Jira API Error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return False


def main():
    """Main entry point for the automation."""
    args = parse_arguments()
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")
        config_mgr = ConfigManager(config_file=args.config)
        
        jira_config = config_mgr.get_jira_config()
        report_config = config_mgr.get_report_config()
        
        # Run automation
        success = run_automation(
            jira_config=jira_config,
            report_config=report_config,
            project_key=args.project,
            max_results=args.max_results,
            report_format=args.format,
            output_filename=args.output
        )
        
        sys.exit(0 if success else 1)
        
    except ConfigError as e:
        logger.error(f"Configuration Error: {str(e)}\n"
                    "Please ensure you have either:\n"
                    "1. A config.ini file (see config.example.ini for template)\n"
                    "2. Required environment variables set (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY)")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nAutomation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
