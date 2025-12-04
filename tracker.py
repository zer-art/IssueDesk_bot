import os
import requests
from github import Github
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- 1. CONFIGURATION ---
GH_TOKEN = os.environ.get("GH_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(
    os.environ.get("TELEGRAM_CHAT_ID", 0)
)  # The main Group ID (starts with -100 usually)

# Define your logic here
RULES = {
    "active_orgs": {
        "names": [
            "deepchem",
            "Cloud-CV",
            "keras-team",
            "cBioPortal",
            "google-deepmind",
            "kornia",
            "JdeRobot",
            "openclimatefix",
            "opencv",
        ],
        "filters": "",
        "topic_id": 2,
        "label": "🔥 URGENT",
    },
    "passive_orgs": {
        "names": ["Cloud-CV", "cBioPortal", "opencv", "kornia"],
        "filters": 'label:"good first issue","help wanted"',
        "topic_id": 3,
        "label": "🌱 EASY",
    },
}

g = Github(GH_TOKEN)


# --- 2. NOTIFICATION FUNCTION ---
def send_telegram(issue, rule_config):
    """Sends message to a specific Topic ID based on the rule"""

    # Custom message format based on the 'label' in config
    msg = (
        f"{rule_config['label']} **New Issue**\n"
        f"📂 **Org:** {issue.repository.organization.login}\n"
        f"📝 **Title:** {issue.title}\n"
        f"🏷️ **Labels:** {', '.join([l.name for l in issue.labels])}\n"
        f"🔗 <a href='{issue.html_url}'>Open Issue</a>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "message_thread_id": rule_config[
            "topic_id"
        ],  # This directs it to the specific topic
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Sent to Telegram: {issue.title}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending Telegram message: {e}")


# --- 3. SEARCH LOGIC ---
def run_checks():
    # Look back 15 mins (matching cron schedule)
    since_time = datetime.utcnow() - timedelta(minutes=15)

    # Loop through our different rules (Active vs Passive)
    for rule_name, config in RULES.items():
        print(f"Checking {rule_name}...")

        # Build Query: (org:A OR org:B) + filters + created_time
        org_block = "(" + " OR ".join([f"org:{name}" for name in config["names"]]) + ")"
        query = (
            f"is:issue is:open no:assignee -linked:pr -label:question "
            f"created:>{since_time.isoformat()} "
            f"{org_block} {config['filters']}"
        )

        print(f"Query: {query}")
        issues = g.search_issues(query=query, sort="created", order="desc")

        for issue in issues:
            print(f"Found: {issue.title}")
            send_telegram(issue, config)


if __name__ == "__main__":
    run_checks()
