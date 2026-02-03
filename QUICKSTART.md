# Quick Start Guide

Get started with Jira Report Automation in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Your Jira Connection

Create a `config.ini` file from the template:

```bash
cp config.example.ini config.ini
```

Edit `config.ini` with your Jira details:

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

### Getting Your Jira API Token

1. Log in to your Atlassian account
2. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
3. Click "Create API token"
4. Give it a name (e.g., "Report Automation")
5. Copy the token and paste it in your `config.ini`

## Step 3: Run Your First Report

Generate a CSV report:

```bash
python jira_automation.py
```

That's it! Your report will be saved in the `reports/` directory.

## Next Steps

- Generate a PDF report: `python jira_automation.py --format pdf`
- Generate both formats: `python jira_automation.py --format both`
- Retrieve more tickets: `python jira_automation.py --max-results 500`
- Use a different project: `python jira_automation.py --project MYPROJ`

## Troubleshooting

**Authentication failed?**
- Double-check your email and API token in config.ini
- Verify your Jira instance URL is correct

**No tickets found?**
- Make sure the project key is correct (case-sensitive)
- Verify you have access to the project

For more details, see the [full README](README.md).
