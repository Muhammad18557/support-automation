"""
This module serves as the entrypoint of the repository. The script checks for unreplied emails in the inbox and sends an automated reply.

This is designed to run indefinitely, checking for new emails at regular intervals  (TIME_INTERVAL). 
It processes unreplied emails by generating a reply using OpenAI's language model and sends the reply back to the sender.
"""

from auth import authenticate_gmail
from gmail_operations import (
    create_label,
    fetch_unreplied_inbox_emails,
    send_reply,
    mark_as_replied,
    is_last_message_from_self,
)
from reply_generator import generate_reply
import os
import time

# read my email from .env
MY_EMAIL_ID = os.getenv("MY_EMAIL_ID")

# Time interval in seconds to check for new emails
TIME_INTERVAL = 60


def get_thread_messages(service, thread_id):
    """Retrieve all messages in a thread."""
    thread = service.users().threads().get(userId="me", id=thread_id).execute()
    messages = []
    for msg in thread["messages"]:
        msg_content = msg["snippet"]
        headers = msg["payload"]["headers"]
        sender = next(
            (header["value"] for header in headers if header["name"] == "From"),
            "Unknown Sender",
        )
        messages.append({"sender": sender, "content": msg_content})
    return messages


def process_unreplied_inbox_emails(
    service, auto_replied_label_id, my_email, max_days_before=1
):
    messages = fetch_unreplied_inbox_emails(
        service, auto_replied_label_id, my_email, max_days_before
    )
    if not messages:
        print("No new unreplied emails found.")
        return

    print(f"Found {len(messages)} unreplied emails to process.")
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        thread_id = msg["threadId"]
        message_id = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "Message-ID"
            ),
            None,
        )

        # Skip if the last message in the thread is from the automation account
        if is_last_message_from_self(service, thread_id, my_email):
            print("Skipping thread as the last message is from the automation account.")
            continue

        # Retrieve the entire thread to pass to generate_reply
        thread_messages = get_thread_messages(service, thread_id)

        # Separate current message from previous messages
        previous_messages = thread_messages[:-1]  # All messages except the last one
        current_message = thread_messages[-1]  # The latest message

        # Get the email subject for reply
        headers = msg["payload"]["headers"]
        subject = next(
            (header["value"] for header in headers if header["name"] == "Subject"), None
        )
        if not subject:
            subject = "Re: Your Inquiry"

        # Generate a reply based on the previous and current messages
        reply_text = generate_reply(previous_messages, current_message, subject)

        # Reply in the same thread
        if message_id:
            send_reply(
                service,
                current_message["sender"],
                f"Re: {subject}",
                reply_text,
                thread_id,
                message_id,
            )

        # Mark as replied immediately
        mark_as_replied(service, message["id"], auto_replied_label_id)


def main():
    service = authenticate_gmail()

    # Ensure "Auto-Replied" label exists
    auto_replied_label_id = create_label(service, "Auto-Replied")

    while True:
        process_unreplied_inbox_emails(
            service=service,
            auto_replied_label_id=auto_replied_label_id,
            my_email=MY_EMAIL_ID,
        )
        print(f"Sleeping for {TIME_INTERVAL} seconds...", flush=True)
        time.sleep(TIME_INTERVAL)


if __name__ == "__main__":
    main()
