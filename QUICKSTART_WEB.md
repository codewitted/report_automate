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

In the web interface:

1. **Enter your Jira credentials**:
   - Jira Instance URL (e.g., https://your-company.atlassian.net)
   - Your email address
   - Your API token ([Generate one here](https://id.atlassian.com/manage-profile/security/api-tokens))
   - Project key (e.g., PROJ, DEV)

2. **Select report format**:
   - CSV (spreadsheet)
   - PDF (document)
   - Both

3. **Click "Generate Report"**

4. **Download your reports** using the download buttons

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
