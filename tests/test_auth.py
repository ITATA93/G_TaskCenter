"""test_auth.py — Tests for src/auth/cli_auth.py.

Tests cover Gmail and Microsoft credential management without requiring
real API access. External dependencies are mocked.
"""

import os
import sys
import pickle
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, mock_open

# Ensure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auth.cli_auth import (
    init_gmail_auth,
    get_gmail_credentials,
    init_microsoft_auth,
    get_microsoft_credentials,
    refresh_token,
    get_credentials,
)


class TestGmailAuth(unittest.TestCase):
    """Tests for Gmail OAuth2 authentication functions."""

    def test_init_gmail_auth_missing_secrets(self):
        """init_gmail_auth raises FileNotFoundError when secrets file missing."""
        with self.assertRaises(FileNotFoundError):
            init_gmail_auth(client_secrets_path="/nonexistent/path.json")

    @patch("auth.cli_auth.pickle.dump")
    @patch("auth.cli_auth.InstalledAppFlow.from_client_secrets_file")
    def test_init_gmail_auth_success(self, mock_flow_cls, mock_pickle_dump):
        """init_gmail_auth runs the OAuth flow and persists the token."""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_flow = MagicMock()
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_cls.return_value = mock_flow

        with tempfile.TemporaryDirectory() as tmpdir:
            secrets_path = os.path.join(tmpdir, "secrets.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            # Create a dummy secrets file
            with open(secrets_path, "w") as f:
                f.write("{}")

            result = init_gmail_auth(
                client_secrets_path=secrets_path, token_path=token_path
            )

            self.assertEqual(result, mock_creds)
            mock_pickle_dump.assert_called_once()
            mock_flow.run_local_server.assert_called_once()

    @patch("auth.cli_auth.pickle.dump")
    @patch("auth.cli_auth.InstalledAppFlow.from_client_secrets_file")
    def test_init_gmail_auth_headless(self, mock_flow_cls, mock_pickle_dump):
        """init_gmail_auth uses console flow when headless=True."""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_flow = MagicMock()
        mock_flow.run_console.return_value = mock_creds
        mock_flow_cls.return_value = mock_flow

        with tempfile.TemporaryDirectory() as tmpdir:
            secrets_path = os.path.join(tmpdir, "secrets.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            with open(secrets_path, "w") as f:
                f.write("{}")

            init_gmail_auth(
                client_secrets_path=secrets_path,
                token_path=token_path,
                headless=True,
            )
            mock_flow.run_console.assert_called_once()

    def test_get_gmail_credentials_no_token(self):
        """get_gmail_credentials returns None when no token file exists."""
        result = get_gmail_credentials(token_path="/nonexistent/token.pickle")
        self.assertIsNone(result)

    @patch("auth.cli_auth.pickle.load")
    def test_get_gmail_credentials_valid_token(self, mock_pickle_load):
        """get_gmail_credentials returns valid creds from pickle."""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds

        with tempfile.TemporaryDirectory() as tmpdir:
            token_path = os.path.join(tmpdir, "token.pickle")
            # Create the file so os.path.exists returns True
            with open(token_path, "wb") as f:
                f.write(b"placeholder")

            result = get_gmail_credentials(token_path=token_path)
            self.assertIsNotNone(result)
            self.assertTrue(result.valid)

    @patch("auth.cli_auth.pickle.dump")
    @patch("auth.cli_auth.pickle.load")
    @patch("auth.cli_auth.Request")
    def test_get_gmail_credentials_refresh(self, mock_request_cls, mock_pickle_load, mock_pickle_dump):
        """get_gmail_credentials refreshes expired token."""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_tok"

        def do_refresh(req):
            mock_creds.valid = True

        mock_creds.refresh.side_effect = do_refresh
        mock_pickle_load.return_value = mock_creds

        with tempfile.TemporaryDirectory() as tmpdir:
            token_path = os.path.join(tmpdir, "token.pickle")
            with open(token_path, "wb") as f:
                f.write(b"placeholder")

            result = get_gmail_credentials(token_path=token_path)
            self.assertIsNotNone(result)
            mock_creds.refresh.assert_called_once()


class TestMicrosoftAuth(unittest.TestCase):
    """Tests for Microsoft Graph authentication functions."""

    def test_init_microsoft_auth_no_client_id(self):
        """init_microsoft_auth raises ValueError without client_id."""
        with self.assertRaises(ValueError):
            init_microsoft_auth(client_id="", use_device_code=True)

    @patch("auth.cli_auth.msal.ConfidentialClientApplication")
    def test_init_microsoft_auth_client_credentials(self, mock_app_cls):
        """init_microsoft_auth uses client-credentials flow."""
        mock_app = MagicMock()
        mock_app.acquire_token_for_client.return_value = {
            "access_token": "test_token_123"
        }
        mock_app_cls.return_value = mock_app

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "cache.bin")
            result = init_microsoft_auth(
                client_id="test-client-id",
                tenant_id="test-tenant",
                client_secret="test-secret",
                cache_path=cache_path,
                use_device_code=False,
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["access_token"], "test_token_123")

    @patch("auth.cli_auth.msal.PublicClientApplication")
    def test_init_microsoft_auth_device_code_cached(self, mock_app_cls):
        """init_microsoft_auth returns cached token silently."""
        mock_app = MagicMock()
        mock_app.get_accounts.return_value = [{"username": "user@test.com"}]
        mock_app.acquire_token_silent.return_value = {
            "access_token": "cached_token"
        }
        mock_app_cls.return_value = mock_app

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "cache.bin")
            result = init_microsoft_auth(
                client_id="test-client-id",
                cache_path=cache_path,
                use_device_code=True,
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["access_token"], "cached_token")

    @patch("auth.cli_auth.msal.PublicClientApplication")
    def test_get_microsoft_credentials_no_accounts(self, mock_app_cls):
        """get_microsoft_credentials returns None when no cached accounts."""
        mock_app = MagicMock()
        mock_app.get_accounts.return_value = []
        mock_app_cls.return_value = mock_app

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "cache.bin")
            result = get_microsoft_credentials(
                client_id="test-client-id",
                cache_path=cache_path,
            )
            self.assertIsNone(result)


class TestUnifiedCredentials(unittest.TestCase):
    """Tests for the unified refresh_token() and get_credentials() functions."""

    @patch("auth.cli_auth.get_gmail_credentials")
    def test_refresh_token_gmail(self, mock_gmail_creds):
        """refresh_token for gmail delegates to get_gmail_credentials."""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_gmail_creds.return_value = mock_creds

        self.assertTrue(refresh_token("gmail"))

    @patch("auth.cli_auth.get_microsoft_credentials")
    def test_refresh_token_microsoft(self, mock_ms_creds):
        """refresh_token for microsoft delegates to get_microsoft_credentials."""
        mock_ms_creds.return_value = "some_token"
        self.assertTrue(refresh_token("microsoft"))

    def test_refresh_token_unknown_provider(self):
        """refresh_token returns False for unknown provider."""
        self.assertFalse(refresh_token("unknown_provider"))

    @patch("auth.cli_auth.get_gmail_credentials")
    def test_get_credentials_gmail(self, mock_gmail_creds):
        """get_credentials routes gmail to the right function."""
        mock_gmail_creds.return_value = "gmail_creds"
        self.assertEqual(get_credentials("gmail"), "gmail_creds")

    @patch("auth.cli_auth.get_microsoft_credentials")
    def test_get_credentials_outlook(self, mock_ms_creds):
        """get_credentials routes 'outlook' to Microsoft handler."""
        mock_ms_creds.return_value = "ms_token"
        self.assertEqual(get_credentials("outlook"), "ms_token")

    def test_get_credentials_unknown(self):
        """get_credentials returns None for unknown provider."""
        self.assertIsNone(get_credentials("dropbox"))


if __name__ == "__main__":
    unittest.main()
