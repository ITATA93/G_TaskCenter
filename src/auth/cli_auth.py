"""cli_auth.py — CLI authentication flows for Gmail OAuth2 and Microsoft Graph.

Provides interactive command-line authentication for:
  - Gmail via Google OAuth2 (google-auth-oauthlib)
  - Microsoft Graph via MSAL device-code or interactive browser flow

Credentials are NEVER stored in code. Tokens are persisted to local files
specified by environment variables, defaulting to the credentials/ directory.
"""

import os
import json
import pickle
import logging
import sys
from typing import Optional, Dict, Any

import msal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gmail OAuth2
# ---------------------------------------------------------------------------

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

GMAIL_CLIENT_SECRETS_PATH = os.environ.get(
    "GMAIL_CREDENTIALS_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "credentials", "gmail_credentials.json"),
)
GMAIL_TOKEN_PATH = os.environ.get(
    "GMAIL_TOKEN_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "credentials", "gmail_token.pickle"),
)


def init_gmail_auth(
    client_secrets_path: Optional[str] = None,
    token_path: Optional[str] = None,
    scopes: Optional[list] = None,
    headless: bool = False,
) -> Credentials:
    """Run the Gmail OAuth2 consent flow and persist the resulting token.

    Args:
        client_secrets_path: Path to the Google OAuth2 client secrets JSON.
                             Falls back to GMAIL_CREDENTIALS_PATH env var.
        token_path: Where to persist the token pickle.
                    Falls back to GMAIL_TOKEN_PATH env var.
        scopes: OAuth2 scopes to request. Defaults to gmail.modify.
        headless: If True, use console-based (OOB) flow instead of local server.

    Returns:
        google.oauth2.credentials.Credentials object ready for API calls.

    Raises:
        FileNotFoundError: If client secrets file does not exist.
        RuntimeError: If the OAuth flow fails.
    """
    secrets = client_secrets_path or GMAIL_CLIENT_SECRETS_PATH
    token_out = token_path or GMAIL_TOKEN_PATH
    requested_scopes = scopes or GMAIL_SCOPES

    if not os.path.exists(secrets):
        raise FileNotFoundError(
            f"Gmail client secrets not found at {secrets}. "
            "Download from Google Cloud Console and set GMAIL_CREDENTIALS_PATH."
        )

    # Ensure output directory exists
    os.makedirs(os.path.dirname(token_out), exist_ok=True)

    flow = InstalledAppFlow.from_client_secrets_file(secrets, requested_scopes)

    if headless:
        creds = flow.run_console()
    else:
        creds = flow.run_local_server(port=0)

    # Persist token
    with open(token_out, "wb") as f:
        pickle.dump(creds, f)

    logger.info("Gmail token saved to %s", token_out)
    return creds


def get_gmail_credentials(
    token_path: Optional[str] = None,
) -> Optional[Credentials]:
    """Load existing Gmail credentials, refreshing if expired.

    Returns None if no valid token exists (caller should run init_gmail_auth).
    """
    token_file = token_path or GMAIL_TOKEN_PATH
    if not os.path.exists(token_file):
        logger.warning("No Gmail token at %s. Run init_gmail_auth() first.", token_file)
        return None

    with open(token_file, "rb") as f:
        creds: Credentials = pickle.load(f)

    if creds.valid:
        return creds

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
            logger.info("Gmail token refreshed successfully.")
            return creds
        except Exception as exc:
            logger.error("Failed to refresh Gmail token: %s", exc)
            return None

    logger.warning("Gmail credentials invalid and cannot be refreshed.")
    return None


# ---------------------------------------------------------------------------
# Microsoft Graph (MSAL)
# ---------------------------------------------------------------------------

MS_CLIENT_ID = os.environ.get("OUTLOOK_CLIENT_ID", "")
MS_TENANT_ID = os.environ.get("OUTLOOK_TENANT_ID", "common")
MS_CLIENT_SECRET = os.environ.get("OUTLOOK_CLIENT_SECRET", "")
MS_AUTHORITY = f"https://login.microsoftonline.com/{MS_TENANT_ID}"
MS_SCOPES = ["https://graph.microsoft.com/Tasks.ReadWrite"]
MS_CACHE_PATH = os.environ.get(
    "OUTLOOK_TOKEN_CACHE",
    os.path.join(os.path.dirname(__file__), "..", "..", "credentials", "outlook_cache.bin"),
)


def _load_ms_cache(cache_path: Optional[str] = None) -> msal.SerializableTokenCache:
    """Load MSAL serializable token cache from disk."""
    path = cache_path or MS_CACHE_PATH
    cache = msal.SerializableTokenCache()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            cache.deserialize(f.read())
    return cache


def _save_ms_cache(cache: msal.SerializableTokenCache, cache_path: Optional[str] = None) -> None:
    """Persist MSAL token cache to disk if state changed."""
    path = cache_path or MS_CACHE_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if cache.has_state_changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(cache.serialize())
        logger.info("Microsoft token cache saved to %s", path)


def init_microsoft_auth(
    client_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    scopes: Optional[list] = None,
    cache_path: Optional[str] = None,
    use_device_code: bool = True,
) -> Optional[Dict[str, Any]]:
    """Run Microsoft Graph authentication via device-code or client-credentials flow.

    For delegated (user) access, use device-code flow (default).
    For daemon/app-only access, set use_device_code=False and provide client_secret.

    Args:
        client_id: Azure AD application (client) ID.
        tenant_id: Azure AD tenant ID or 'common'.
        client_secret: Client secret for confidential app flow.
        scopes: Microsoft Graph scopes to request.
        cache_path: File path to persist the MSAL token cache.
        use_device_code: If True, use interactive device-code flow.

    Returns:
        Token result dict with 'access_token' key, or None on failure.
    """
    cid = client_id or MS_CLIENT_ID
    tid = tenant_id or MS_TENANT_ID
    secret = client_secret or MS_CLIENT_SECRET
    requested_scopes = scopes or MS_SCOPES
    authority = f"https://login.microsoftonline.com/{tid}"

    if not cid:
        raise ValueError(
            "OUTLOOK_CLIENT_ID not set. Register an app in Azure AD and set the env var."
        )

    cache = _load_ms_cache(cache_path)

    if use_device_code:
        # Public client app (device-code flow for delegated permissions)
        app = msal.PublicClientApplication(
            cid,
            authority=authority,
            token_cache=cache,
        )

        # Try silent acquisition first
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(requested_scopes, account=accounts[0])

        if not result:
            flow = app.initiate_device_flow(scopes=requested_scopes)
            if "user_code" not in flow:
                logger.error("Device flow initiation failed: %s", flow)
                return None

            print("\n" + "=" * 60)
            print("Microsoft Authentication Required")
            print("=" * 60)
            print(flow["message"])
            print("=" * 60 + "\n")
            sys.stdout.flush()

            result = app.acquire_token_by_device_flow(flow)

    else:
        # Confidential client (client-credentials, daemon)
        if not secret:
            raise ValueError(
                "Client secret required for non-device-code flow. "
                "Set OUTLOOK_CLIENT_SECRET."
            )
        app = msal.ConfidentialClientApplication(
            cid,
            authority=authority,
            client_credential=secret,
            token_cache=cache,
        )
        result = app.acquire_token_for_client(scopes=requested_scopes)

    _save_ms_cache(cache, cache_path)

    if result and "access_token" in result:
        logger.info("Microsoft Graph authentication successful.")
        return result
    else:
        error = result.get("error_description", result.get("error", "Unknown error")) if result else "No result"
        logger.error("Microsoft authentication failed: %s", error)
        return None


def get_microsoft_credentials(
    cache_path: Optional[str] = None,
    client_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    scopes: Optional[list] = None,
) -> Optional[str]:
    """Retrieve a cached Microsoft Graph access token silently.

    Returns the access_token string or None if interactive auth is needed.
    """
    cid = client_id or MS_CLIENT_ID
    tid = tenant_id or MS_TENANT_ID
    requested_scopes = scopes or MS_SCOPES
    authority = f"https://login.microsoftonline.com/{tid}"

    if not cid:
        return None

    cache = _load_ms_cache(cache_path)
    app = msal.PublicClientApplication(cid, authority=authority, token_cache=cache)

    accounts = app.get_accounts()
    if not accounts:
        logger.info("No cached Microsoft accounts. Run init_microsoft_auth().")
        return None

    result = app.acquire_token_silent(requested_scopes, account=accounts[0])
    if result and "access_token" in result:
        return result["access_token"]

    logger.info("Silent token acquisition failed. Re-run init_microsoft_auth().")
    return None


def refresh_token(provider: str, **kwargs) -> bool:
    """Refresh an existing token for the given provider.

    Args:
        provider: 'gmail' or 'microsoft'
        **kwargs: Forwarded to the provider-specific credential loader.

    Returns:
        True if refresh succeeded, False otherwise.
    """
    provider = provider.lower().strip()

    if provider == "gmail":
        creds = get_gmail_credentials(**kwargs)
        return creds is not None and creds.valid
    elif provider in ("microsoft", "outlook", "msgraph"):
        token = get_microsoft_credentials(**kwargs)
        return token is not None
    else:
        logger.error("Unknown provider '%s'. Use 'gmail' or 'microsoft'.", provider)
        return False


def get_credentials(provider: str, **kwargs) -> Optional[Any]:
    """Unified credential accessor.

    Args:
        provider: 'gmail' or 'microsoft'
        **kwargs: Forwarded to the provider-specific function.

    Returns:
        For gmail: google.oauth2.credentials.Credentials
        For microsoft: access_token string
        None if credentials are unavailable.
    """
    provider = provider.lower().strip()

    if provider == "gmail":
        return get_gmail_credentials(**kwargs)
    elif provider in ("microsoft", "outlook", "msgraph"):
        return get_microsoft_credentials(**kwargs)
    else:
        logger.error("Unknown provider '%s'. Use 'gmail' or 'microsoft'.", provider)
        return None


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    """Interactive CLI to authenticate with Gmail and/or Microsoft Graph."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("\n=== G_TaskCenter Authentication Setup ===\n")
    print("Available providers:")
    print("  1) Gmail (Google OAuth2)")
    print("  2) Microsoft Graph (Outlook / To-Do)")
    print("  3) Both")
    print("  q) Quit\n")

    choice = input("Select provider [1/2/3/q]: ").strip()

    if choice in ("1", "3"):
        print("\n--- Gmail OAuth2 Setup ---")
        try:
            creds = init_gmail_auth()
            print(f"Gmail auth successful. Token valid: {creds.valid}")
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"Gmail auth failed: {e}")

    if choice in ("2", "3"):
        print("\n--- Microsoft Graph Setup ---")
        try:
            result = init_microsoft_auth(use_device_code=True)
            if result:
                print("Microsoft auth successful. Access token acquired.")
            else:
                print("Microsoft auth failed.")
        except ValueError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"Microsoft auth failed: {e}")

    if choice == "q":
        print("Exiting.")
        return

    if choice not in ("1", "2", "3", "q"):
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()
