import os
import sys
import requests
from github import Github
from datetime import datetime, timedelta
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

# --- 1. CONFIGURATION ---
GH_TOKEN = os.environ.get("GH_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(
    os.environ.get("TELEGRAM_CHAT_ID", 0)
)  # The main Group ID (starts with -100 usually)

# Define your logic here
AI_RELATED_GSOC_ORGS = [
    "Cloud-CV",
    "cBioPortal",
    "google-deepmind",
    "kornia",
    "JdeRobot",
    "openclimatefix",
    "scikit-learn",
    "pandas-dev",
    "numpy",
    "huggingface",
    "pytorch",
    "openvinotoolkit",
    "JabRef",
    "kubeflow",
    "opencv",
    "keras-team",
    "deepchem",
    "projectmesa",
    "hsf",
    "HumanAI",
    "unifyai",
    "jina-ai",
    "skit-ai",
    "apidash",
    "fossi-foundation",
    "LiquidGalaxyLAB",
    "AOSSIE",
]

# Comprehensive list (AI related + other popular GSOC orgs)
ALL_GSOC_ORGS = list(set(AI_RELATED_GSOC_ORGS + [
    "52North", "aboutcode-org", "accordproject", "AFLplusplus", "ankidroid", "apache", "apertium", "ArduPilot",
    "BeagleBoard-org", "blender", "BRL-CAD", "carbon-language", "django", "gcc-mirror", "inkscape", "OpenAstronomy",
    "organicmaps", "ruby", "spcl", "torproject", "GNOME", "KDE", "libvirt", "openMF", "openhealthcare", "OSGeo",
    "polypheny", "RTEMS", "su2code", "videolan", "zulip", "CircuitVerse", "CGAL", "c2si", "gnu-octave", "json-schema-org",
    "mozilla", "eclipse", "linuxfoundation", "cncf", "kubernetes", "prometheus", "envoyproxy", "grpc", "opentracing",
    "fluentd", "linkerd", "goharbor", "helm", "etcd", "tikv", "coredns", "containerd", "rkt", "cni", "notary", "tuf",
    "rook", "vitess", "nats-io", "opa", "spiffe", "spire", "cloudevents", "telepresence", "open-policy-agent",
    "pravega", "curiefense", "longhorn", "keda", "smi", "volcano", "k3s", "argoproj", "crossplane", "dapr", "kudobuilder",
    "open-telemetry", "thanos-io", "fluxcd", "zowe", "jenkins", "gradle", "maven", "spring-projects", "spring-io",
    "hibernate", "jakartaee", "quarkusio", "micronaut-projects", "helidon-io", "eclipse-ee4j", "eclipse-microprofile",
    "nodejs", "denoland", "typescript", "rust-lang", "golang", "swiftlang", "kotlin", "scala", "groovy", "clojure",
    "haskell", "ocaml", "erlang", "elixir-lang", "php", "laravel", "symfony", "codeigniter", "cakephp", "yiisoft",
    "zendframework", "slimphp", "phalcon", "fuelphp", "joomla", "drupal", "wordpress", "moodle", "edx", "freecodecamp",
    "exercism"
]))

RULES = {
    "active_orgs": {
        "names": [
            "Cloud-CV",
            "cBioPortal",
            "google-deepmind",
            "kornia",
            "JdeRobot",
            "openclimatefix",
            "scikit-learn",
            "pandas-dev",
            "numpy",
            "huggingface",
            "pytorch",
        ],
        "filters": "",
        "topic_id": 2,
        "label": "🔥 MOST WORKED ON",
    },
    "python_issues": {
        "names": AI_RELATED_GSOC_ORGS,
        "filters": "language:python",
        "topic_id": 198,
        "label": "🐍 PYTHON ISSUE",
        "check_cross_org_membership": True,
    },
    "maintainer_issues": {
        "names": ALL_GSOC_ORGS,
        "filters": "",
        "topic_id": 208,
        "label": "🛡️ MAINTAINER ISSUE",
        "check_cross_org_membership": True,
    },
    "good_first_issues": {
        "names": [
            "openvinotoolkit",
            "JabRef",
            "kubeflow",
            "Cloud-CV",
            "opencv",
            "google-deepmind",
            "keras-team",
            "kornia",
            "openclimatefix",
            "deepchem",
            "JdeRobot",
            "projectmesa",
            "hsf",
            "scikit-learn",
            "pandas-dev",
            "numpy",
            "huggingface",
            "pytorch",
        ],
        "filters": 'label:"good first issue","help wanted"',
        "topic_id": 3,
        "label": "🌱 GOOD FIRST ISSUE",
    },
}

g = Github(GH_TOKEN)


# --- 2. NOTIFICATION FUNCTION ---
def send_telegram(issue, rule_config, is_member=False):
    """Sends message to a specific Topic ID based on the rule"""

    # Custom message format based on the 'label' in config
    msg = (
        f"{rule_config['label']} **New Issue**\n"
        f"📂 **Org:** {issue.repository.organization.login}\n"
        f"📝 **Title:** {issue.title}\n"
        f"🏷️ **Labels:** {', '.join([l.name for l in issue.labels])}\n"
        f"🔗 <a href='{issue.html_url}'>Open Issue</a>"
    )

    if is_member:
        msg += "\n💡 **Opened by Member/Collaborator**"

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
    # Look back 30 mins to catch recently created issues
    since_time = datetime.utcnow() - timedelta(minutes=30)
    print(f"⏰ Checking issues created after: {since_time.isoformat()}")

    # Loop through our different rules (Active vs Passive)
    for rule_name, config in RULES.items():
        print(f"Checking {rule_name}...")

        # Split organizations into smaller batches to avoid GitHub API query complexity limits
        org_names = config["names"]
        batch_size = 5  # Increased from 2 for better performance with large org lists

        for batch_start in range(0, len(org_names), batch_size):
            batch_names = org_names[batch_start : batch_start + batch_size]
            # Don't use parentheses - GitHub search doesn't work well with them
            org_block = " ".join([f"org:{name}" for name in batch_names])
            created_filter = f"created:>{since_time.isoformat()}"

            # Different filters for different rule types
            if rule_name == "good_first_issues":
                # For good first issues, we also want to exclude assigned issues now
                query = f"is:issue is:open no:assignee -linked:pr -label:question {created_filter} {org_block} {config['filters']}"
            else:
                # For active orgs, only unassigned
                query = f"is:issue is:open no:assignee -linked:pr -label:question {created_filter} {org_block} {config['filters']}"

            print(f"Query: {query[:100]}...")  # Print first 100 chars only
            try:
                issues = g.search_issues(query=query, sort="created", order="desc")
                issue_count = 0
                for issue in issues:
                    # Double check if assigned (sometimes search API is eventually consistent)
                    if issue.assignee:
                        continue
                        
                    
                    # Check if the author is a member/collaborator
                    author_assoc = issue.author_association
                    is_privileged = author_assoc in ["MEMBER", "OWNER", "COLLABORATOR"]

                    
                    # Logic for Cross-Org Membership Checks (Python Topic & Maintainer Topic)
                    if config.get("check_cross_org_membership"):
                        # If already privileged in the local repo, good.
                        # If not, check if they are a member of any listed org for this rule.
                        if not is_privileged:
                            try:
                                user_orgs = [o.login for o in issue.user.get_orgs()]
                                # Check intersection with the orgs defined in this specific rule
                                # config["names"] contains the list of orgs we are monitoring (AI_RELATED_GSOC_ORGS or ALL_GSOC_ORGS)
                                if any(org in config["names"] for org in user_orgs):
                                    is_privileged = True
                                    print(f" -> User {issue.user.login} is member of tracked GSOC orgs.")
                            except Exception as e:
                                print(f"⚠️ Could not fetch orgs for user {issue.user.login}: {e}")

                        # If still not privileged after check, skip sending
                        if not is_privileged:
                            # Only noisy in debug/verbose, maybe reduce print?
                            # print(f"Skipping {issue.title} (User {issue.user.login} not a known maintainer)")
                            continue
                    
                    # For Active Orgs (Most Worked On), we don't strictly filter by membership 
                    # for *sending* (based on original code logic sending everything found), 
                    # but we mark is_member for the badge.
                    # HOWEVER, verify if original intent for 'active_orgs' was to filter? 
                    # Original code: send_telegram(..., is_member=is_privileged)
                    # It sent ALL issues found by query.
                    
                    issue_count += 1
                    print(f"Found: {issue.title} (Author: {issue.user.login}, Assoc: {author_assoc})")
                    send_telegram(issue, config, is_member=is_privileged)
                print(f"✅ {rule_name}: Found {issue_count} issue(s)")
            except Exception as e:
                print(f"❌ Error searching {rule_name}: {e}")
                import traceback

                traceback.print_exc()


# --- 4. TEST FUNCTION ---
def send_test_message():
    """Send a test message to verify Telegram is working"""
    test_config = {
        "label": "🧪 TEST",
        "topic_id": 2,
    }

    msg = (
        f"{test_config['label']} **Test Message**\n"
        f"✅ Telegram integration is working!\n"
        f"⏰ Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"🤖 Issue Tracker Bot is ready to receive notifications."
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "message_thread_id": test_config["topic_id"],
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Test message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending test message: {e}")


# --- 5. TEST LAST ISSUE FROM EACH ORG ---
def send_last_issue_from_each_org():
    """Send the last issue from each organization as a test"""
    all_orgs = []

    # Collect all orgs from both rules
    for rule_name, config in RULES.items():
        all_orgs.extend(config["names"])

    # Remove duplicates
    all_orgs = list(set(all_orgs))

    print(f"🔍 Fetching last issue from {len(all_orgs)} organizations...\n")

    for org in sorted(all_orgs):
        try:
            # Get the last open issue from this org
            query = f"org:{org} is:issue is:open"
            issues = g.search_issues(query=query, sort="created", order="desc")

            issue = None
            for i in issues:
                issue = i
                break

            if issue:
                # Format message
                msg = (
                    f"🧪 **Last Issue from {org}**\n"
                    f"📝 **Title:** {issue.title}\n"
                    f"🏷️ **Labels:** {', '.join([l.name for l in issue.labels]) if issue.labels else 'None'}\n"
                    f"👤 **Assignee:** {issue.assignee.login if issue.assignee else 'None'}\n"
                    f"🔗 <a href='{issue.html_url}'>Open Issue</a>"
                )

                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                payload = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": msg,
                    "parse_mode": "HTML",
                    "message_thread_id": 2,  # Send to active_orgs topic
                }

                response = requests.post(url, json=payload)
                response.raise_for_status()
                print(f"✅ {org}: {issue.title[:50]}...")
            else:
                print(f"❌ {org}: No issues found")

        except Exception as e:
            print(f"⚠️  {org}: {str(e)[:50]}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        send_test_message()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-orgs":
        send_last_issue_from_each_org()
    else:
        run_checks()
