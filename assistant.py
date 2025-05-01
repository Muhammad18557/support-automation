"""This module can be used to create and manage OpenAI assistants for various tasks. 
It provides functions to 
1) create a new assistant, 
2) modify an existing assistant,
3) create a new vector store and upload files to it for file search,
4) add additional files to an existing vector store and link it to an assistant.
"""

# Created vector store with ID: vs_OyoTN4poPBF2c07XLwYNRplN
# Created assistant with ID: asst_JU8k3dtCs7qSHLMDmOylQATX

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client with your API key
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

assistant_id = os.getenv("ASSISTANT_ID")

# Define the path to the documents directory
DOCUMENTS_DIR = "documents/"


def create_new_assistant(name, instructions, model="gpt-4o"):
    """Creates a new assistant and returns its ID."""
    # Create the assistant
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "file_search"}],
        model=model,
    )

    print("Assistant created successfully.")
    print(assistant)

    assistant_id = assistant.id
    print(f"Assistant created with ID: {assistant_id}")

    return assistant_id


def modify_assistant(assistant_id, name, instructions, model="gpt-4o"):
    """Modifies an existing assistant with new details."""
    response = client.beta.assistants.update(
        assistant_id=assistant_id,
        name=name,
        instructions=instructions,
        model=model,
    )

    print("Assistant modified successfully.")
    return response


def create_and_upload_files_to_vector_store(assistant_id):
    """Creates a new vector store and uploads files under DOCUMENTS_DIR to it for file search."""
    # Step 1: Create a vector store
    vector_store = client.beta.vector_stores.create(name="Defog Documentation")
    vector_store_id = vector_store.id
    print(f"Created vector store with ID: {vector_store_id}")

    # Step 2: Prepare files for upload
    file_paths = [
        os.path.join(DOCUMENTS_DIR, filename)
        for filename in os.listdir(DOCUMENTS_DIR)
        if os.path.isfile(os.path.join(DOCUMENTS_DIR, filename))
    ]
    file_streams = [open(path, "rb") for path in file_paths]

    # Step 3: Upload files to the vector store and poll until processing is complete
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id, files=file_streams
    )
    print(f"File batch upload status: {file_batch.status}")
    print(f"Files in batch: {file_batch.file_counts}")

    # Step 4: Update the assistant to use this vector store for file search
    client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    print("Vector store linked to assistant's file search tool successfully.")

    # Close file streams
    for file_stream in file_streams:
        file_stream.close()


def add_files_to_existing_vector_store(vector_store_id, assistant_id, file_names=None):
    """
    Uploads additional files to an existing vector store and links it to an assistant.
    If file_names is None, all files in the DOCUMENTS_DIR are uploaded.
    """
    # Use all files in DOCUMENTS_DIR if file_names is not specified
    file_paths = [
        os.path.join(DOCUMENTS_DIR, filename)
        for filename in (file_names or os.listdir(DOCUMENTS_DIR))
        if os.path.isfile(os.path.join(DOCUMENTS_DIR, filename))
    ]

    # Open file streams for the files
    file_streams = [open(path, "rb") for path in file_paths]

    # Check if there are files to upload
    if not file_streams:
        print("No new files to upload.")
        return

    # Upload files to the vector store and poll until processing is complete
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id, files=file_streams
    )
    print(f"File batch upload status: {file_batch.status}")
    print(f"Files in batch: {file_batch.file_counts}")

    # Link the assistant to the updated vector store for file search
    client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    print(
        "Vector store updated with new files and linked to assistant's file search tool successfully."
    )

    # Close file streams
    for file_stream in file_streams:
        file_stream.close()


def list_files_in_vector_store(vector_store_id):
    """Lists all files in a specific vector store. This does not support file names yet."""
    # Fetch files from the vector store
    files = client.beta.vector_stores.files.list(vector_store_id=vector_store_id)

    # Print details of each file in the vector store
    for file in files:
        print(
            f"File ID: {file.id}, Status: {file.status}, Usage Bytes: {file.usage_bytes}"
        )