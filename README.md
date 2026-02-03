# Jira Report Automation

Automated tool for retrieving Jira tickets and generating comprehensive reports in CSV or PDF format.

## 🌟 NEW: Web Interface

**Generate reports with just a few clicks!** No configuration files needed.

```bash
pip install -r requirements.txt
python start.py
```

Then fill in the form in your browser and click "Generate Report" - that's it!

See [QUICKSTART_WEB.md](QUICKSTART_WEB.md) for details.

## Features

- 🌐 **Simple Web Interface**: Generate reports with a user-friendly web form (NEW!)
- 🔐 **Secure Authentication**: Uses Jira API tokens for secure authentication
- 📊 **Multiple Report Formats**: Generate reports in CSV or PDF format
- 📈 **Comprehensive Data**: Includes ticket ID, status, summary, assignee, priority, custom fields, and more
- 📉 **Summary Statistics**: Automatic calculation of ticket distribution by status, type, priority, and assignee
- ⚡ **Error Handling**: Robust error handling for authentication, timeouts, and API issues
- 🔧 **Modular Design**: Clean, modular code structure for easy maintenance and extension
- 🎯 **Flexible Configuration**: Web interface, config files, or environment variables

## Prerequisites

- Python 3.7 or higher
- Jira account with API access
- Jira API token (generate from: https://id.atlassian.com/manage-profile/security/api-tokens)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/codewitted/report_automate.git
   cd report_automate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your method**:

   **Method 1: Web Interface (Easiest)**
   ```bash
   python start.py
   ```
   Then use the web form to enter your Jira details and generate reports!

   **Method 2: Configuration file**
   
   Copy the example configuration file and edit it with your details:
   ```bash
   cp config.example.ini config.ini
   ```
   
   Edit `config.ini` and fill in your Jira details:
   ```ini
   [jira]
   base_url = https://your-instance.atlassian.net
   email = your-email@example.com
   api_token = your-api-token-here
   project_key = PROJ
   
   [report]
   output_dir = reports
   default_format = csv
   ```

   **Method 3: Environment variables**
   
   Set the following environment variables:
   ```bash
   export JIRA_BASE_URL="https://your-instance.atlassian.net"
   export JIRA_EMAIL="your-email@example.com"
   export JIRA_API_TOKEN="your-api-token-here"
   export JIRA_PROJECT_KEY="PROJ"
   export REPORT_OUTPUT_DIR="reports"
   export REPORT_FORMAT="csv"
   ```

## Usage

### Web Interface (Recommended)

The easiest way to generate reports:

```bash
python start.py
```

This will:
1. Start a local web server
2. Open your browser automatically
3. Show a simple form where you can:
   - Enter your Jira credentials
   - Select report format (CSV, PDF, or both)
   - Click "Generate Report"
   - Download your reports

### Command Line Interface

Generate a CSV report with default settings:
```bash
python jira_automation.py
```

### Command Line Options

```bash
python jira_automation.py [options]

Options:
  --format {csv,pdf,both}     Report format (default: csv)
  --project PROJECT_KEY       Override project key from config
  --max-results N             Maximum number of tickets to retrieve (default: 100)
  --output OUTPUT_FILE        Custom output filename (without extension)
  --config CONFIG_FILE        Path to configuration file (default: config.ini)
  --help                      Show help message
```

### Examples

**Generate a CSV report**:
```bash
python jira_automation.py --format csv
```

**Generate a PDF report**:
```bash
python jira_automation.py --format pdf
```

**Generate both CSV and PDF reports**:
```bash
python jira_automation.py --format both
```

**Retrieve tickets from a specific project**:
```bash
python jira_automation.py --project DEVOPS --format pdf
```

**Retrieve more tickets with custom filename**:
```bash
python jira_automation.py --max-results 500 --output monthly_report
```

**Use a custom configuration file**:
```bash
python jira_automation.py --config /path/to/custom_config.ini
```

## Report Contents

### CSV Report
The CSV report includes the following fields:
- **Ticket ID**: Jira ticket key (e.g., PROJ-123)
- **Summary**: Brief description of the ticket
- **Status**: Current status (e.g., To Do, In Progress, Done)
- **Type**: Issue type (e.g., Bug, Story, Task)
- **Priority**: Priority level (e.g., High, Medium, Low)
- **Assignee**: Person assigned to the ticket
- **Reporter**: Person who created the ticket
- **Created**: Creation timestamp
- **Updated**: Last update timestamp
- **Resolution Date**: When the ticket was resolved (if applicable)
- **Labels**: Associated labels
- **Components**: Associated components
- **Description**: Detailed description
- **Custom Fields**: Any project-specific custom fields

### PDF Report
The PDF report includes:
- **Summary Statistics**: 
  - Total number of tickets
  - Breakdown by status
  - Breakdown by type
  - Breakdown by priority
  - Breakdown by assignee
- **Detailed Ticket Information**: 
  - All key fields for each ticket
  - Formatted in an easy-to-read table layout
- **Timestamps**: Report generation date and time

## Security Best Practices

⚠️ **IMPORTANT**: Never commit your `config.ini` file with real API tokens to version control!

- The `.gitignore` file is configured to exclude `config.ini` and `.env` files
- Always use `config.example.ini` as a template
- Store sensitive credentials in environment variables or secure configuration management systems
- Rotate API tokens regularly
- Use read-only API tokens when possible

## Error Handling

The automation includes comprehensive error handling for:

- **Authentication Errors**: Invalid credentials or expired API tokens
- **Connection Errors**: Network issues or incorrect Jira URL
- **Timeout Errors**: Requests that take too long to complete
- **API Errors**: Invalid requests or missing permissions
- **Data Parsing Errors**: Issues with API response format
- **Configuration Errors**: Missing or invalid configuration values

All errors are logged with descriptive messages to help troubleshoot issues.

## Module Structure

```
report_automate/
├── start.py                # Quick start script for web interface (NEW!)
├── app.py                  # Web application (NEW!)
├── templates/              # Web interface templates (NEW!)
│   └── index.html          # Main web page (NEW!)
├── jira_automation.py      # Command-line automation script
├── jira_client.py          # Jira API client with authentication and ticket retrieval
├── report_generator.py     # Report generation in CSV and PDF formats
├── config_manager.py       # Configuration management
├── requirements.txt        # Python dependencies
├── config.example.ini      # Example configuration file
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── QUICKSTART.md           # CLI quick start guide
└── QUICKSTART_WEB.md       # Web interface quick start guide (NEW!)
```

### Module Descriptions

- **start.py**: Easy launcher for the web interface
- **app.py**: Flask web application for browser-based report generation
- **templates/index.html**: Beautiful, user-friendly web interface
- **jira_automation.py**: Main entry point for command-line usage
- **jira_client.py**: Handles all Jira API interactions including authentication, connection testing, and ticket retrieval
- **report_generator.py**: Generates formatted reports in CSV and PDF formats with summary statistics
- **config_manager.py**: Manages configuration from files and environment variables

## Troubleshooting

### "Authentication failed" error
- Verify your email and API token are correct
- Ensure the API token hasn't expired
- Check that you're using the correct Jira instance URL

### "Project not found" error
- Verify the project key is correct (case-sensitive)
- Ensure you have permission to access the project
- Check that the project exists in your Jira instance

### "Connection timeout" error
- Check your internet connection
- Verify the Jira instance URL is accessible
- Consider increasing the timeout in `jira_client.py` if you have a slow connection

### No tickets returned
- Verify the project has tickets
- Check your JQL query permissions
- Ensure the project key is correct

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for automation purposes.

## Support

For issues or questions, please open an issue in the GitHub repository.
