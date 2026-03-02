# TASKS - G_TaskCenter

## Pending

(No pending tasks)

## Completed

- [x] Implement user authentication CLI for Gmail and Microsoft Graph — `src/auth/cli_auth.py`
- [x] Refine the task unification logic to handle duplicate tasks across platforms — `src/dedup/unifier.py`
- [x] Add more sources (Slack, Jira) — `src/integrations/slack.py`, `src/integrations/jira.py`
- [x] Implement data persistence in a local SQLite DB — `src/db/sqlite_store.py`
- [x] Implement automated tests for all integrations — `tests/test_auth.py`, `tests/test_unifier.py`, `tests/test_sqlite_store.py`
- [x] Configure `GEN_OS` pre-classifier to route task-related queries to `g-taskcenter` — `config/routing.json`
