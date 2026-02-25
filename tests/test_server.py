"""
test_server.py - Basic server structure tests for G_TaskCenter.

Tests that the server module structure is correct without starting
the actual MCP server or connecting to external services.
"""

import os
import sys
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_DIR)


class TestServerModuleStructure:
    """Validate the server module files exist and are well-formed."""

    def test_server_py_exists(self):
        assert os.path.exists(os.path.join(SRC_DIR, "server.py"))

    def test_models_py_exists(self):
        assert os.path.exists(os.path.join(SRC_DIR, "models.py"))

    def test_sync_engine_py_exists(self):
        assert os.path.exists(os.path.join(SRC_DIR, "sync_engine.py"))

    def test_integrations_dir_exists(self):
        assert os.path.isdir(os.path.join(SRC_DIR, "integrations"))

    def test_init_py_exists(self):
        assert os.path.exists(os.path.join(SRC_DIR, "__init__.py"))


class TestIntegrationsStructure:
    """Validate integration modules exist."""

    INTEGRATIONS_DIR = os.path.join(SRC_DIR, "integrations")

    def test_notion_integration_exists(self):
        assert os.path.exists(os.path.join(self.INTEGRATIONS_DIR, "notion.py"))

    def test_outlook_integration_exists(self):
        assert os.path.exists(os.path.join(self.INTEGRATIONS_DIR, "outlook.py"))

    def test_gmail_integration_exists(self):
        assert os.path.exists(os.path.join(self.INTEGRATIONS_DIR, "gmail.py"))

    def test_n8n_integration_exists(self):
        assert os.path.exists(os.path.join(self.INTEGRATIONS_DIR, "n8n.py"))


class TestModelsImport:
    """Test that models can be imported independently of server."""

    def test_import_models(self):
        from models import UnifiedTask, TaskSource, TaskPriority
        assert UnifiedTask is not None
        assert TaskSource is not None
        assert TaskPriority is not None

    def test_unified_task_is_pydantic_model(self):
        from models import UnifiedTask
        # Pydantic models have model_fields attribute
        assert hasattr(UnifiedTask, "model_fields")

    def test_task_model_has_expected_fields(self):
        from models import UnifiedTask
        fields = set(UnifiedTask.model_fields.keys())
        expected = {"id", "source", "title", "snippet", "status", "priority", "due_date", "link"}
        assert expected == fields


class TestRequirements:
    """Validate that requirements.txt lists expected dependencies."""

    @pytest.fixture(autouse=True)
    def load_requirements(self):
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
        assert os.path.exists(req_path)
        with open(req_path, "r", encoding="utf-8") as f:
            self.requirements = [
                line.strip().lower() for line in f if line.strip() and not line.startswith("#")
            ]

    def test_fastmcp_listed(self):
        assert any("fastmcp" in r for r in self.requirements)

    def test_pydantic_listed(self):
        assert any("pydantic" in r for r in self.requirements)

    def test_python_dotenv_listed(self):
        assert any("python-dotenv" in r or "dotenv" in r for r in self.requirements)
