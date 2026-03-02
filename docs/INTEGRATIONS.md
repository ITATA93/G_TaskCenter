# G_TaskCenter — Integration Guide

This document describes each integration available in G_TaskCenter, including
setup instructions, authentication flows, environment variables, and sync
capabilities.

## Table of Contents

1. [Gmail](#gmail)
2. [Notion](#notion)
3. [Outlook / Microsoft To-Do](#outlook--microsoft-to-do)
4. [Slack](#slack)
5. [Jira](#jira)
6. [n8n (Workflow Automation)](#n8n-workflow-automation)

---

## Gmail

**Module:** `src/integrations/gmail.py`
**Auth module:** `src/auth/cli_auth.py` (Gmail OAuth2 flow)

### Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or select an existing one).
3. Enable the **Gmail API**.
4. Create **OAuth 2.0 Client ID** credentials (Desktop application).
5. Download the JSON file and save it as `credentials/gmail_credentials.json`.

### Environment Variables

| Variable               | Required | Description                          |
|------------------------|----------|--------------------------------------|
| `GMAIL_CREDENTIALS_PATH` | Yes    | Path to the OAuth2 client secrets JSON |
| `GMAIL_TOKEN_PATH`      | No      | Path to the persisted token pickle (default: `credentials/gmail_token.pickle`) |

### Authentication Flow

```bash
python -m src.auth.cli_auth
# Select option 1 (Gmail)
# A browser window will open for Google OAuth consent
# Token is saved automatically to GMAIL_TOKEN_PATH
```

Alternatively, use headless mode (no browser):
```python
from src.auth.cli_auth import init_gmail_auth
init_gmail_auth(headless=True)
```

### Sync Capabilities

| Operation           | Supported | MCP Tool              |
|---------------------|-----------|-----------------------|
| List task emails    | Yes       | `list_unified_tasks`, `get_source_tasks` |
| Archive email       | Yes       | `archive_gmail`       |
| Create task         | No        | --                    |

### How It Works

- Queries Gmail for messages matching `label:todo OR label:task OR subject:task AND is:unread`.
- Extracts subject as task title, snippet as description.
- Infers priority from keywords (urgent, asap = HIGH).
- Supports pagination up to a configurable limit.

---

## Notion

**Module:** `src/integrations/notion.py`

### Setup

1. Go to [Notion Integrations](https://www.notion.so/my-integrations).
2. Create a new **Internal Integration**.
3. Copy the **Internal Integration Token**.
4. Share the target database with your integration.
5. Copy the database ID from the database URL.

### Environment Variables

| Variable              | Required | Description                        |
|-----------------------|----------|------------------------------------|
| `NOTION_TOKEN`        | Yes      | Notion Internal Integration Token  |
| `NOTION_TASKS_DB_ID`  | Yes      | ID of the Notion tasks database    |

### Authentication Flow

No interactive flow needed. Set the environment variables in `.env`:

```env
NOTION_TOKEN=ntn_xxxxxxxxxxxxx
NOTION_TASKS_DB_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Sync Capabilities

| Operation           | Supported | MCP Tool              |
|---------------------|-----------|-----------------------|
| List tasks          | Yes       | `list_unified_tasks`, `get_source_tasks` |
| Create task         | Yes       | `create_notion_task`  |
| Update task         | No        | --                    |
| Bi-directional sync | Yes       | Via `sync_engine.py`  |

### How It Works

- Queries the configured database filtering for Status != Done.
- Uses cursor-based pagination for large databases.
- Parses title, status, priority, and due date from Notion properties.
- The sync engine creates new Notion pages for tasks ingested from Gmail/Outlook.

### Database Schema Requirements

The Notion database should have these properties:

| Property   | Type   | Notes                    |
|------------|--------|--------------------------|
| Name       | Title  | Task title               |
| Status     | Select | Values: Not started, In progress, Done |
| Priority   | Select | Values: High, Normal, Low |
| Due Date   | Date   | Optional                 |

---

## Outlook / Microsoft To-Do

**Module:** `src/integrations/outlook.py`
**Auth module:** `src/auth/cli_auth.py` (Microsoft Graph flow)

### Setup

1. Go to [Azure AD App Registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade).
2. Register a new application.
3. Under **API permissions**, add `Tasks.ReadWrite` (Microsoft Graph).
4. For delegated access: Add `User.Read` scope and enable public client flows.
5. For app-only access: Create a **Client Secret** under Certificates & Secrets.

### Environment Variables

| Variable               | Required | Description                          |
|------------------------|----------|--------------------------------------|
| `OUTLOOK_CLIENT_ID`    | Yes      | Azure AD Application (Client) ID    |
| `OUTLOOK_TENANT_ID`    | Yes      | Azure AD Tenant ID                   |
| `OUTLOOK_CLIENT_SECRET`| Conditional | Required for daemon/app-only flow  |
| `OUTLOOK_TOKEN_CACHE`  | No       | Path for MSAL token cache (default: `credentials/outlook_cache.bin`) |

### Authentication Flow

**Device Code Flow (recommended for delegated access):**
```bash
python -m src.auth.cli_auth
# Select option 2 (Microsoft)
# A device code and URL will be displayed
# Visit the URL and enter the code in a browser
# Token is cached automatically
```

**Client Credentials Flow (daemon/app-only):**
```python
from src.auth.cli_auth import init_microsoft_auth
init_microsoft_auth(use_device_code=False)
```

### Sync Capabilities

| Operation           | Supported | MCP Tool                     |
|---------------------|-----------|------------------------------|
| List tasks          | Yes       | `list_unified_tasks`, `get_source_tasks` |
| Complete task       | Yes       | `complete_task_in_outlook`   |
| Create task         | No        | --                           |

### How It Works

- Fetches all To-Do lists via Microsoft Graph API.
- Iterates each list to retrieve non-completed tasks.
- Maps Outlook importance (high/normal/low) to TaskPriority.
- Supports pagination via `@odata.nextLink`.

---

## Slack

**Module:** `src/integrations/slack.py`

### Setup

1. Go to [Slack API Apps](https://api.slack.com/apps).
2. Create a new App (or use an existing one).
3. Under **OAuth & Permissions**, add the following Bot Token Scopes:
   - `channels:history`
   - `channels:read`
   - `reactions:read`
   - `reactions:write`
   - `stars:read`
   - `users:read`
4. Install the app to your workspace and copy the **Bot User OAuth Token**.

### Environment Variables

| Variable              | Required | Description                          |
|-----------------------|----------|--------------------------------------|
| `SLACK_BOT_TOKEN`     | Yes      | Bot User OAuth Token (`xoxb-...`)    |
| `SLACK_TASK_CHANNELS` | No       | Comma-separated channel IDs to monitor (auto-discovers if empty) |
| `SLACK_TASK_REACTION` | No       | Emoji name that marks a message as a task (default: `white_check_mark`) |

### Authentication Flow

No interactive flow. Set the bot token in `.env`:
```env
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
SLACK_TASK_CHANNELS=C01ABC123,C02DEF456
```

### Sync Capabilities

| Operation           | Supported | Notes                        |
|---------------------|-----------|------------------------------|
| List tasks          | Yes       | Messages with task reaction  |
| Mark task done      | Yes       | Adds a done reaction         |
| Create task         | No        | --                           |

### How It Works

- Scans configured channels (or all joined public channels) for messages
  with the designated reaction emoji.
- Extracts first 120 characters of message text as task title.
- Infers priority from text keywords (urgent, asap, critical = HIGH).
- Uses Slack message timestamps as task IDs for uniqueness.

---

## Jira

**Module:** `src/integrations/jira.py`

### Setup

1. Log in to your Jira instance.
2. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) (for Jira Cloud).
3. Create a new API token.

### Environment Variables

| Variable           | Required | Description                           |
|--------------------|----------|---------------------------------------|
| `JIRA_BASE_URL`    | Yes      | Jira instance URL (e.g., `https://myorg.atlassian.net`) |
| `JIRA_USER_EMAIL`  | Yes      | Email associated with the Jira account |
| `JIRA_API_TOKEN`   | Yes      | API token (Jira Cloud) or password     |
| `JIRA_PROJECT_KEY` | No       | Filter to a specific project (e.g., `PROJ`) |
| `JIRA_JQL_FILTER`  | No       | Custom JQL query override              |

### Authentication Flow

No interactive flow. Uses HTTP Basic Auth with email + API token:
```env
JIRA_BASE_URL=https://myorg.atlassian.net
JIRA_USER_EMAIL=user@example.com
JIRA_API_TOKEN=ATATTxxxxxxxxxxxxxxxxxxxxxxxx
```

### Sync Capabilities

| Operation           | Supported | Notes                          |
|---------------------|-----------|--------------------------------|
| List assigned issues| Yes       | Non-Done issues via JQL        |
| Transition issue    | Yes       | Move to Done, In Progress, etc.|
| Create issue        | No        | --                             |

### How It Works

- Queries the Jira REST API v2 with JQL: `assignee = currentUser() AND statusCategory != Done`.
- Optionally filters by project key.
- Maps Jira priority names (Highest, High, Medium, Low, Lowest) to TaskPriority.
- Supports pagination via `startAt` / `maxResults`.
- Transitions use the Jira workflow engine (available transitions are queried dynamically).

---

## n8n (Workflow Automation)

**Module:** `src/integrations/n8n.py`

### Setup

1. Deploy an n8n instance (self-hosted or cloud).
2. Enable the API and generate an API key in n8n Settings.

### Environment Variables

| Variable       | Required | Description                     |
|----------------|----------|---------------------------------|
| `N8N_HOST`     | Yes      | n8n instance URL (e.g., `https://n8n.mydomain.com`) |
| `N8N_API_KEY`  | Yes      | n8n API key                     |

### Sync Capabilities

| Operation             | Supported | MCP Tool                    |
|-----------------------|-----------|-----------------------------|
| List workflows        | Yes       | `list_n8n_workflows`        |
| Activate/deactivate   | Yes       | `toggle_n8n_workflow`       |
| Test execute workflow  | Yes       | `test_n8n_workflow`         |
| Check execution status | Yes      | `check_n8n_execution`       |

### Pre-built Workflows

The `n8n_workflows/` directory contains importable workflow JSON files:

- `gmail_to_notion.json` — Automatically creates Notion tasks from labeled Gmail messages.
- `outlook_to_notion.json` — Syncs Outlook tasks to Notion.
- `error_notifier.json` — Sends notifications when sync operations fail.
