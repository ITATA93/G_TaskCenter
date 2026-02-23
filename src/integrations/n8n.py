"""n8n.py — n8n API integration for G_TaskCenter."""

import os
import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Constants for N8N Auth & Host
N8N_HOST = os.environ.get("N8N_HOST")  # e.g., "https://n8n.mydomain.com"
N8N_API_KEY = os.environ.get("N8N_API_KEY")


def _get_headers() -> Dict[str, str]:
    if not N8N_API_KEY:
        logger.warning("N8N_API_KEY is not set.")
        return {}
    return {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_workflows() -> List[Dict[str, Any]]:
    """Retrieve all workflows from the n8n instance."""
    if not N8N_HOST:
        return []

    url = f"{N8N_HOST.rstrip('/')}/api/v1/workflows"
    try:
        response = requests.get(url, headers=_get_headers())
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            logger.error(f"Failed to fetch workflows: {response.text}")
            return []
    except Exception as e:
        logger.error(f"Exception fetching n8n workflows: {e}")
        return []


def activate_workflow(workflow_id: str, active: bool = True) -> bool:
    """Enable or disable an n8n workflow."""
    if not N8N_HOST:
        return False

    url = (
        f"{N8N_HOST.rstrip('/')}/api/v1/workflows/{workflow_id}/activate"
        if active
        else f"{N8N_HOST.rstrip('/')}/api/v1/workflows/{workflow_id}/deactivate"
    )
    try:
        response = requests.post(url, headers=_get_headers())
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to change workflow activation state: {e}")
        return False


def test_execute_workflow(
    workflow_id: str, payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute a workflow directly (via Webhook URL or Test Execution API if available).

    Using the Test Execution approach requires n8n enterprise or specific setups,
    but for standard config, hitting a direct execution trigger or webhook is preferred.
    """
    if not N8N_HOST:
        return {"error": "N8N_HOST not configured"}

    url = f"{N8N_HOST.rstrip('/')}/api/v1/executions"
    data = {"workflowId": workflow_id}

    try:
        # Request a test execution dynamically. (Varies based on n8n version, assumes standard API /executions POST)
        response = requests.post(url, headers=_get_headers(), json=data)
        if response.status_code in [200, 201]:
            return {"success": True, "execution_id": response.json().get("id")}
        return {"error": response.text}
    except Exception as e:
        logger.error(f"Exception executing workflow {workflow_id}: {e}")
        return {"error": str(e)}


def get_execution_status(execution_id: str) -> Dict[str, Any]:
    """Retrieve the status and log of a specific execution ID to debug/test."""
    if not N8N_HOST:
        return {"error": "N8N_HOST not configured"}

    url = f"{N8N_HOST.rstrip('/')}/api/v1/executions/{execution_id}"
    try:
        response = requests.get(url, headers=_get_headers())
        if response.status_code == 200:
            data = response.json()
            return {
                "id": data.get("id"),
                "finished": data.get("finished", False),
                "mode": data.get("mode"),
                "status": data.get("status", "unknown"),
                "stoppedAt": data.get("stoppedAt"),
            }
        return {"error": f"Status lookup failed: {response.text}"}
    except Exception as e:
        return {"error": str(e)}
