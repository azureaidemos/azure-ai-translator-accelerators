"""
Module for processing documents and interacting with Azure Blob Storage and GPT model.

This module provides functions to:
1. Create a CSV string from data.
2. Process and upload data to Azure Blob Storage.
3. Process input files and extract text using a GPT model.
4. Parse CSV files from Azure Blob Storage.
"""

import logging
import io
import os
import csv
from io import BytesIO
import pandas as pd
from azure.storage.blob import BlobServiceClient
from blob_handler import upload_to_blob
from gpt_handler import get_gpt_response
from utils import read_docx_from_url, read_pdf_from_url


def create_csv_string(data):
    """
    Creates a CSV string from the given data.

    Args:
        data (list): A list of data to be written to CSV.

    Returns:
        str: The CSV string.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    for item in data:
        cleaned_item = item.replace(",", "")  # Remove commas
        writer.writerow([cleaned_item, cleaned_item])

    return output.getvalue()


def process_and_upload_data(
    file_name, entries, storage_account, SAS_TOKEN, CONTAINER_NAME, GLOSSARY_PREFIX
):
    """
    Processes the extracted text and uploads it as a CSV file to Azure Blob Storage.

    Args:
        file_name (str): The name of the source file.
        entries (list): The extracted text entries.
        storage_account (str): The Azure storage account name.
        SAS_TOKEN (str): The SAS token for authentication.
        CONTAINER_NAME (str): The name of the container in Azure Blob Storage.
        GLOSSARY_PREFIX (str): The prefix for the glossary blob.

    Returns:
        str: The URL of the uploaded glossary file.
    """
    # Extract the base name without extension and prepare the new file name
    base_name = os.path.splitext(file_name)[0]
    new_file_name = f"glossaries_{base_name}.csv"

    logging.info("Processing entries for new file name: %s", new_file_name)

    # Create CSV content from the list
    csv_content = create_csv_string(entries)

    # Upload CSV to Azure Blob Storage and get the URL
    glossary_url = upload_to_blob(
        storage_account,
        SAS_TOKEN,
        CONTAINER_NAME,
        GLOSSARY_PREFIX,
        new_file_name,
        csv_content,
    )

    logging.info("Glossary URL: %s", glossary_url)
    return glossary_url


def process_file(
    file_name, source_url, SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, CHAT_PARAMETERS
):
    """
    Processes the input file, sends its content to the GPT model, and extracts relevant text.

    Args:
        file_name (str): The name of the file to process.
        source_url (str): The URL of the source file.
        SYSTEM_PROMPT (str): The system prompt to guide the GPT model.
        FEW_SHOT_EXAMPLES (list): Examples to help guide the GPT model.
        CHAT_PARAMETERS (dict): Parameters for the GPT model.

    Returns:
        list: A list of extracted text lines.
    """
    logging.info("Starting to process file: %s", file_name)
    if file_name.endswith(".docx"):
        text = read_docx_from_url(source_url)
    elif file_name.endswith(".pdf"):
        text = read_pdf_from_url(source_url)
    else:
        logging.error("Unsupported file type: %s", file_name)
        raise ValueError("Unsupported file type. URL must end with .docx or .pdf")

    response = get_gpt_response(text, SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, CHAT_PARAMETERS)
    logging.info("get_gpt_response: %s", response)

    return response


def parse_csv_from_azure_blob(CONTAINER_NAME, blob_name, connection_string):
    """
    Parse a CSV file from an Azure Blob Storage.

    Args:
        CONTAINER_NAME (str): The name of the container.
        blob_name (str): The name of the blob file.
        connection_string (str): The connection string for the Azure Blob Storage account.

    Returns:
        pd.DataFrame: The parsed CSV file as a pandas DataFrame.

    Raises:
        Exception: If there is an error in downloading or parsing the CSV file.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)

        # Download the blob's content as a stream
        stream = BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)

        # Parse the CSV file using pandas
        df = pd.read_csv(stream)
        return df
    except Exception as e:
        logging.error("Error parsing CSV from Azure Blob: %s", e)
        raise
