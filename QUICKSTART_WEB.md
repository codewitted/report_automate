# 🚀 Quick Start - Web Interface

The easiest way to generate Jira reports!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Start the Application

```bash
python start.py
```

That's it! The web interface will open automatically in your browser.

## 3. Generate Reports

The tool supports **three report modes**:

### 📊 Project Report
Export all tickets from a Jira project:
1. Enter Jira credentials
2. Select "Project Report" mode
3. Enter project key (e.g., PROJ, DEV)
4. Choose format (CSV/PDF/Both)
5. Click "Generate Report"

### 🎯 Single Ticket
Export a specific ticket by its ID:
1. Enter Jira credentials
2. Select "Single Ticket" mode
3. Enter ticket ID (e.g., PROJ-123)
4. Choose format
5. Click "Generate Report"

### 🔍 Custom Query (JQL)
Use Jira Query Language for advanced filtering:
1. Enter Jira credentials
2. Select "Custom Query (JQL)" mode
3. Enter your JQL query (e.g., `assignee = currentUser() AND status != Done`)
4. Choose format
5. Click "Generate Report"

### JQL Examples:
- `status = 'In Progress' AND assignee = currentUser()`
- `created >= -7d AND priority = High`
- `project = PROJ AND labels = urgent`

## Features

✅ **Three Report Modes**: Project reports, single ticket, or custom JQL queries  
✅ **Multiple Formats**: Export as CSV, PDF, or both  
✅ **Built-in Help**: Inline instructions and examples  
✅ **Advanced Filtering**: Use JQL for complex queries  
✅ **No Config Files**: Enter credentials directly in the web form  

## Alternative: Command Line

If you prefer the command line, you can still use it:

```bash
# Setup config file first
cp config.example.ini config.ini
# Edit config.ini with your details

# Generate report
python jira_automation.py --format both
```

## Getting Your Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Report Automation")
4. Copy the token and use it in the web interface

## Need Help?

See the [full README](README.md) for more details and troubleshooting.
