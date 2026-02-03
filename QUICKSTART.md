# Quick Start Guide

Get started with Jira Report Automation in just 2 steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Generate Reports

### Option A: Web Interface (Easiest! 🚀)

Just run:

```bash
python start.py
```

The web interface will open in your browser. Then:

1. Enter your Jira details in the form
2. Select report format (CSV, PDF, or both)
3. Click "Generate Report"
4. Download your reports!

**No configuration files needed!**

### Option B: Command Line

If you prefer the command line:

**Step 2a:** Create a `config.ini` file from the template:

```bash
cp config.example.ini config.ini
```

**Step 2b:** Edit `config.ini` with your Jira details:

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

**Step 2c:** Run Your First Report

Generate a CSV report:

```bash
python jira_automation.py
```

That's it! Your report will be saved in the `reports/` directory.

### Getting Your Jira API Token

1. Log in to your Atlassian account
2. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
3. Click "Create API token"
4. Give it a name (e.g., "Report Automation")
5. Copy the token and use it in the web form or paste it in your `config.ini`

## More Options

### Web Interface Advanced Settings

Click "Advanced Options" in the web form to:
- Change the maximum number of tickets to retrieve (default: 100)

### Command Line Options

Generate a PDF report:

```bash
python jira_automation.py --format pdf
```

Generate both formats:

```bash
python jira_automation.py --format both
```

Retrieve more tickets:

```bash
python jira_automation.py --max-results 500
```

Use a different project:

```bash
python jira_automation.py --project MYPROJ
```

## Troubleshooting

**Web Interface:**
- If the browser doesn't open automatically, manually go to http://localhost:5000
- Make sure port 5000 is not already in use

**Authentication failed?**
- Double-check your email and API token in config.ini
- Verify your Jira instance URL is correct

**No tickets found?**
- Make sure the project key is correct (case-sensitive)
- Verify you have access to the project

For more details, see the [full README](README.md).
