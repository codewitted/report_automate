"""
#!/usr/bin/env python3
"""
"""
KSCO Jira Agent
- GUI prompts for Jira base URL, email, and API token (token is stored in OS credential store via keyring)
- User selects a local folder (recommend: a OneDrive-synced folder that maps to the SharePoint library)
- Agent polls Jira every N seconds (default 300s), fetches tickets for a project or JQL, generates CSV reports into the selected folder
- Minimal dependencies: requests, keyring, tkinter (builtin), python-dateutil (optional)
"""
import os
import json
import threading
import time
import csv
import sys
import traceback
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, StringVar, Text, IntVar, filedialog, messagebox
import requests
import keyring

APP_NAME = "ksco_jira_agent"
CONFIG_DIR = os.path.join(os.getenv('APPDATA') or os.path.expanduser("~/.config"), APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    ensure_config_dir()
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
    except Exception:
        pass
    # defaults
    return {
        "base_url": "",
        "email": "",
        "project_key": "",
        "jql": "",
        "poll_seconds": 300,
        "target_folder": ""
    }

def save_config(cfg):
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)

def store_token(email, token):
    # store under service=APP_NAME, username=email
    keyring.set_password(APP_NAME, email, token)

def get_stored_token(email):
    return keyring.get_password(APP_NAME, email)

def jira_test_connection(base_url, email, token):
    # Test with GET /rest/api/3/myself
    url = base_url.rstrip("/") + "/rest/api/3/myself"
    resp = requests.get(url, auth=(email, token), timeout=15)
    if resp.status_code == 200:
        return True, resp.json()
    elif resp.status_code == 401:
        return False, "Authentication failed (401). Check email/token."
    else:
        return False, f"Status {resp.status_code}: {resp.text}"

def jira_fetch_tickets(base_url, email, token, jql, max_results=200):
    # Uses Jira Cloud REST API search
    url = base_url.rstrip("/") + "/rest/api/3/search"
    params = {"jql": jql, "maxResults": max_results, "fields": "*all"}
    resp = requests.get(url, auth=(email, token), params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("issues", [])

def extract_ticket_row(issue):
    fields = issue.get("fields", {})
    assignee = fields.get("assignee")
    reporter = fields.get("reporter")
    status = fields.get("status")
    priority = fields.get("priority")
    issuetype = fields.get("issuetype")
    labels = fields.get("labels", [])
    components = fields.get("components", [])
    return {
        "Ticket ID": issue.get("key"),
        "Summary": fields.get("summary"),
        "Status": status.get("name") if status else None,
        "Type": issuetype.get("name") if issuetype else None,
        "Priority": priority.get("name") if priority else None,
        "Assignee": assignee.get("displayName") if assignee else None,
        "Reporter": reporter.get("displayName") if reporter else None,
        "Created": fields.get("created"),
        "Updated": fields.get("updated"),
        "Resolution Date": fields.get("resolutiondate"),
        "Labels": ", ".join(labels) if labels else "",
        "Components": ", ".join([c.get("name","") for c in components]) if components else "",
        "Description": (fields.get("description") or "")[:4000]
    }

def generate_csv_report(issues, project_key_or_id, output_dir):
    if not issues:
        return None
    rows = [extract_ticket_row(i) for i in issues]
    # determine fieldnames
    fieldnames = []
    for r in rows:
        for k in r.keys():
            if k not in fieldnames:
                fieldnames.append(k)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{project_key_or_id}_report_{timestamp}.csv"
    path = os.path.join(output_dir, fname)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return path

class AgentThread(threading.Thread):
    def __init__(self, get_config_func, log_func, stop_event):
        super().__init__(daemon=True)
        self.get_config = get_config_func
        self.log = log_func
        self.stop_event = stop_event

    def run(self):
        self.log("Agent started. Polling Jira...")
        last_count = None
        while not self.stop_event.is_set():
            cfg = self.get_config()
            base = cfg.get("base_url", "").strip()
            email = cfg.get("email", "").strip()
            token = get_stored_token(email) if email else None
            jql = cfg.get("jql", "").strip()
            project = cfg.get("project_key", "").strip()
            if not jql and project:
                jql = f"project = {project}"
            target = cfg.get("target_folder", "").strip()
            poll_seconds = int(cfg.get("poll_seconds", 300))
            if not base or not email or not token or not target:
                self.log("Waiting for complete configuration (base_url, email, token stored, target folder)...")
                # sleep a bit and retry
                for _ in range(10):
                    if self.stop_event.wait(1):
                        return
                continue
            try:
                ok, info = jira_test_connection(base, email, token)
                if not ok:
                    self.log(f"Connection test failed: {info}")
                    # wait and retry
                    if self.stop_event.wait(10):
                        return
                    continue
                # fetch tickets
                self.log("Fetching tickets...")
                issues = jira_fetch_tickets(base, email, token, jql, max_results=500)
                count = len(issues)
                self.log(f"Fetched {count} issues")
                # If count changed or always generate, write CSV
                # Here we will always generate a timestamped report each poll
                csv_path = generate_csv_report(issues, project or "JQL", target)
                if csv_path:
                    self.log(f"Report written: {csv_path}")
                else:
                    self.log("No report generated (no issues)")
            except requests.HTTPError as he:
                self.log(f"HTTP error: {he} - {getattr(he, 'response', '')}")
            except Exception as e:
                self.log(f"Error while polling: {e}")
                self.log(traceback.format_exc())
            # wait for next poll with early exit
            for _ in range(int(poll_seconds)):
                if self.stop_event.wait(1):
                    self.log("Agent stopping.")
                    return

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KSCO Jira Agent")
        self.cfg = load_config()
        self.stop_event = threading.Event()
        self.agent = None

        # variables
        self.base_var = StringVar(value=self.cfg.get("base_url", ""))
        self.email_var = StringVar(value=self.cfg.get("email", ""))
        self.project_var = StringVar(value=self.cfg.get("project_key", ""))
        self.jql_var = StringVar(value=self.cfg.get("jql", ""))
        self.poll_var = IntVar(value=self.cfg.get("poll_seconds", 300))
        self.target_var = StringVar(value=self.cfg.get("target_folder", ""))
        # widgets
        Label(root, text="Jira Base URL:").grid(row=0, column=0, sticky="w")
        Entry(root, textvariable=self.base_var, width=60).grid(row=0, column=1, columnspan=3, sticky="we")
        Label(root, text="Email:").grid(row=1, column=0, sticky="w")
        Entry(root, textvariable=self.email_var, width=40).grid(row=1, column=1, sticky="we")
        Button(root, text="Set/Update API Token", command=self.set_token).grid(row=1, column=2, sticky="we")

        Label(root, text="Project Key (or leave blank and use JQL):").grid(row=2, column=0, sticky="w")
        Entry(root, textvariable=self.project_var, width=20).grid(row=2, column=1, sticky="we")
        Label(root, text="OR JQL:").grid(row=3, column=0, sticky="w")
        Entry(root, textvariable=self.jql_var, width=60).grid(row=3, column=1, columnspan=3, sticky="we")

        Label(root, text="Poll interval (seconds):").grid(row=4, column=0, sticky="w")
        Entry(root, textvariable=self.poll_var, width=10).grid(row=4, column=1, sticky="w")

        Label(root, text="Target folder (select your OneDrive-synced SharePoint folder):").grid(row=5, column=0, sticky="w")
        Entry(root, textvariable=self.target_var, width=60).grid(row=5, column=1, columnspan=2, sticky="we")
        Button(root, text="Browse...", command=self.browse_target).grid(row=5, column=3, sticky="we")

        Button(root, text="Save settings", command=self.save_settings).grid(row=6, column=1, sticky="we")
        Button(root, text="Start agent", command=self.start_agent).grid(row=6, column=2, sticky="we")
        Button(root, text="Stop agent", command=self.stop_agent).grid(row=6, column=3, sticky="we")

        Label(root, text="Log:").grid(row=7, column=0, sticky="nw")
        self.log_box = Text(root, height=12, width=80)
        self.log_box.grid(row=7, column=1, columnspan=3, sticky="we")

        # layout tweaks
        for c in range(4):
            root.grid_columnconfigure(c, weight=1)

        self.write_log("KSCO Jira Agent ready.")
        # auto-save initial config
        self.save_settings()

    def browse_target(self):
        folder = filedialog.askdirectory(title="Select local folder that syncs to SharePoint (OneDrive)")
        if folder:
            self.target_var.set(folder)

    def set_token(self):
        # prompt user to enter token in a simple dialog (hidden)
        from tkinter.simpledialog import askstring
        email = self.email_var.get().strip()
        if not email:
            messagebox.showwarning("Email required", "Please fill your email first (used as credential key).")
            return
        token = askstring("Jira API token", "Enter your Jira API token (input hidden):", show="*")
        if token:
            store_token(email, token)
            messagebox.showinfo("Token saved", "API token stored securely in your OS credential store.")
            self.write_log("API token stored for " + email)

    def save_settings(self):
        self.cfg["base_url"] = self.base_var.get().strip()
        self.cfg["email"] = self.email_var.get().strip()
        self.cfg["project_key"] = self.project_var.get().strip()
        self.cfg["jql"] = self.jql_var.get().strip()
        self.cfg["poll_seconds"] = int(self.poll_var.get())
        self.cfg["target_folder"] = self.target_var.get().strip()
        save_config(self.cfg)
        self.write_log("Settings saved.")

    def start_agent(self):
        if self.agent and self.agent.is_alive():
            self.write_log("Agent already running.")
            return
        self.stop_event.clear()
        self.agent = AgentThread(get_config_func=lambda: load_config(), log_func=self.write_log, stop_event=self.stop_event)
        self.agent.start()
        self.write_log("Agent thread started.")

    def stop_agent(self):
        if self.agent and self.agent.is_alive():
            self.stop_event.set()
            self.agent.join(timeout=5)
            self.write_log("Agent stopped.")
        else:
            self.write_log("Agent is not running.")

    def write_log(self, text):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_box.insert("end", f"[{ts}] {text}\n")
        self.log_box.see("end")


def main():
    root = Tk()
    app = GUI(root)
    # create a stop event in the GUI instance for agent control
    app.stop_event = threading.Event()
    try:
        root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_agent(), root.destroy()))
        root.mainloop()
    except KeyboardInterrupt:
        app.stop_agent()
        sys.exit(0)


if __name__ == "__main__":
    main()
