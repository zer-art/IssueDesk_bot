# IssueDesk Bot

A Python bot that monitors GitHub issues across multiple organizations and sends notifications to Telegram based on configurable rules.

## Features

- **Multi-Organization Monitoring**: Track issues across multiple GitHub organizations
- **Rule-Based Filtering**: Define custom rules to filter and categorize issues
- **Telegram Notifications**: Send issue alerts to Telegram topics with emoji labels
- **Scheduled Checks**: Run periodic checks to detect newly created issues
- **Label Customization**: Organize notifications with custom labels (e.g., 🔥 URGENT, 🌱 EASY)

## Prerequisites

- Python 3.7+
- GitHub Personal Access Token
- Telegram Bot Token
- Telegram Chat ID (Group with Topics enabled)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd IssueDesk_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
GH_TOKEN=your_github_token
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## Configuration

Edit the `RULES` dictionary in `tracker.py` to customize monitoring:

```python
RULES = {
    "rule_name": {
        "names": ["org1", "org2"],           # GitHub organizations to monitor
        "filters": "label:\"label1\",\"label2\"",  # GitHub search filters
        "topic_id": 1,                       # Telegram topic ID
        "label": "🔥 URGENT"                 # Display label for notifications
    }
}
```

## Usage

Run the bot manually:
```bash
python tracker.py
```

### Scheduling with Cron

To run checks every 15 minutes, add to your crontab:
```bash
*/15 * * * * cd /path/to/IssueDesk_bot && python tracker.py
```

## How It Works

1. **Search**: Queries GitHub API for recent issues (15-minute window) matching your rules
2. **Filter**: Applies organization and label filters based on RULES configuration
3. **Notify**: Sends formatted Telegram messages to the appropriate topic
4. **Track**: Monitors unassigned, open issues without linked PRs

## Dependencies

- **requests**: HTTP library for Telegram API calls
- **PyGithub**: GitHub API client library
- **python-dotenv**: Environment variable management

## Notes

- Replace `topic_id` values with your actual Telegram Topic IDs
- Ensure your Telegram group has Topics enabled
- GitHub token requires `public_repo` and `read:org` permissions at minimum
