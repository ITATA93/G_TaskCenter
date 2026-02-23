# G_TaskCenter MCP Setup Guide

This project provides a unified Model Context Protocol (MCP) server for managing tasks from Gmail, Notion, and Outlook.

## Prerequisites

1.  **Python 3.10+**: Ensure Python is installed.
2.  **Dependencies**: Install the required libraries using:
    ```bash
    pip install -r requirements.txt
    ```

## Integration Configuration

1.  Copy `.env.example` to `.env`.
2.  **Gmail**:
    *   Obtain a `credentials.json` from the [Google Cloud Console](https://console.cloud.google.com/).
    *   Run a manual authentication script to generate `token.pickle`.
3.  **Notion**:
    *   Create an integration at [Notion Developers](https://www.notion.so/my-integrations).
    *   Share your task database with the integration.
    *   Set `NOTION_TOKEN` and `NOTION_TASKS_DB_ID` in `.env`.
4.  **Outlook**:
    *   Register an application in [Azure AD / Entra portal](https://portal.azure.com/).
    *   Enable Microsoft Graph permissions: `Tasks.ReadWrite`.
    *   Set `OUTLOOK_CLIENT_ID`, `OUTLOOK_TENANT_ID`, and `OUTLOOK_CLIENT_SECRET` in `.env`.

## Running the MCP Server

Start the server using:
```bash
python scripts/mcp_server.py
```

## Available Tools

*   `get_all_tasks`: Fetches a unified list of tasks from all sources.
*   `list_recent_emails`: Specifically lists task-related Gmail messages.
*   `sync_notion_backlog`: Fetches pending tasks from Notion.
*   `list_outlook_todo`: Fetches pending tasks from Microsoft To-Do.
