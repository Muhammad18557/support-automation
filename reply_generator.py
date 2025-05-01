"""
Uses openAI to generate a professional and courteous reply to an email. It uses the previous messages in the thread as context for generating the reply.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import logging

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

# Get the assistant ID from the environment variable
assistant_id = os.getenv("ASSISTANT_ID")


def generate_reply(
    previous_messages: list, current_message: dict, subject: str = None
) -> str:
    """
    Generate a professional and courteous reply to an email using OpenAI's assistant with thread history.

    Args:
        previous_messages (list): List of dictionaries with previous messages in the email thread.
                                  Each dictionary contains "sender" and "content" keys.
        current_message (dict): The current message to respond to, containing "sender" and "content".

    Returns:
        str: A generated response to the email.
    """
    sender_name = current_message["sender"]
    email_content = current_message["content"]

    print(f"Generating reply for {sender_name}...", flush=True)

    # Format previous messages for context
    context = "\n\n".join(
        [f"{msg['sender']}: {msg['content']}" for msg in previous_messages]
    )

    # Step 1: Create a new thread for the conversation
    thread = client.beta.threads.create()

    # Step 2: Add current message as a prompt in the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"The sender name is {sender_name} and the email subject is {subject}\n\n"
        f"and their latest email message is: {email_content}\n\n"
        f"Here is the previous conversation history with them in the same thread:\n{context}\n\n",
    )

    # Step 3: Run the assistant on the thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id
    )

    # Wait for completion
    while run.status != "completed":
        print("Waiting for the assistant to complete the run...", flush=True)
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve and print assistant's response
    messages = list(client.beta.threads.messages.list(thread_id=thread.id))
    assistant_reply_text = ""
    for msg in messages:
        if msg.role == "assistant":
            assistant_reply_text = " ".join(
                block.text.value for block in msg.content if hasattr(block, "text")
            )
            break

    logging.info(f"Generated reply for {sender_name}:\n{assistant_reply_text}")

    return assistant_reply_text
