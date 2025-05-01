"""This module provides function to authenticate the Gmail API and defines the SCOPE."""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

# Define the scopes needed for full Gmail API access
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.labels",
]


def authenticate_gmail():
    """Authenticate and return the Gmail API service instance."""
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"

    # Load credentials from token.json if it exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Check if credentials are invalid, expired, or revoked
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print("Token refreshed successfully.", flush=True)
            else:
                raise ValueError("Token needs reauthentication.")
        except (ValueError, google.auth.exceptions.RefreshError):
            # Reauthenticate if refresh fails
            print("Token expired or revoked. Re-authenticating...", flush=True)
            if os.path.exists(token_path):
                os.remove(token_path)  # Remove old token file
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
            print("New token created and saved.", flush=True)

    return build("gmail", "v1", credentials=creds)
