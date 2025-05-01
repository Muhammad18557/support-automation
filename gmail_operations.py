"""
This module contains functions to interact with Gmail using the Gmail API.
"""

import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from utils import clean_response_text, convert_markdown_to_html


def create_label(service, label_name):
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"] == label_name:
            return label["id"]
    label_body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    label = service.users().labels().create(userId="me", body=label_body).execute()
    return label["id"]


def fetch_unreplied_inbox_emails(service, label_id, my_email, max_days_before=1):
    """
    Fetch unread emails in the inbox from the last `max_days_before` days, excluding ones from our automated account.

    Args:
        service: The Gmail API service instance.
        label_id: The ID of the auto-replied label to exclude.
        my_email: The automated account email to exclude.
        max_days_before: The maximum number of days before today to include emails from.

    Returns:
        List of messages within the specified time range.
    """
    # Gmail uses "d" for days, "m" for months, and "y" for years in queries.
    query = f"is:unread in:inbox -from:{my_email} -label:{label_id} newer_than:{max_days_before}d"
    results = service.users().messages().list(userId="me", q=query).execute()
    return results.get("messages", [])


def send_reply(service, to, subject, message_text, thread_id, message_id):
    # cleanup mardown and convert to html
    cleaned_message_text = clean_response_text(message_text)
    html_message_text = convert_markdown_to_html(cleaned_message_text)

    message = MIMEText(html_message_text, "html")
    message["to"] = to
    message["subject"] = subject
    message["In-Reply-To"] = message_id
    message["References"] = message_id
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"raw": raw, "threadId": thread_id}

    try:
        sent_message = service.users().messages().send(userId="me", body=body).execute()
        print(
            f"Auto-reply sent to {to} within the same thread, message ID: {sent_message['id']}",
            flush=True,
        )
    except Exception as error:
        print(f"An error occurred while sending email: {error}", flush=True)


def mark_as_replied(service, msg_id, label_id):
    service.users().messages().modify(
        userId="me", id=msg_id, body={"addLabelIds": [label_id]}
    ).execute()
    print(f"Marked message ID {msg_id} as replied.", flush=True)


def is_last_message_from_self(service, thread_id, my_email):
    # Fetch the thread details
    thread = service.users().threads().get(userId="me", id=thread_id).execute()
    messages = thread.get("messages", [])
    last_message = messages[-1]  # Get the last message in the thread

    # Check if the last message was sent by the automated email account
    headers = last_message["payload"]["headers"]
    sender = next(
        (header["value"] for header in headers if header["name"] == "From"), ""
    )
    return my_email.lower() in sender.lower()
