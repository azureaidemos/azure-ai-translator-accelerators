"""
Module for handling blob operations in Azure Blob Storage.

This module provides functions to validate the existence of a source URL and
upload content to Azure Blob Storage.
"""

import logging
import requests
from azure.storage.blob import BlobServiceClient
from environment_variables import AZURE_STORAGE_ACCOUNT, SAS_TOKEN

# Construct the Blob service client
blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=SAS_TOKEN,
)


def validate_source_url(source_url):
    """
    Validates the existence of the source URL.

    Args:
        source_url (str): URL of the source document.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    logging.info("Validating source URL: %s", source_url)
    try:
        response = requests.head(source_url, timeout=10)
        if response.status_code == 200:
            logging.info("Source file exists")
            return True
        logging.error("Source file does not exist. Status code: %s", response.status_code)
        return False
    except requests.RequestException as e:
        logging.error("Error validating source URL: %s", e)
        return False


def upload_to_blob(
    storage_account, token, container, blob_directory, file_name, content
):
    """
    Uploads content to Azure Blob Storage.

    Args:
        storage_account (str): The Azure storage account name.
        token (str): The SAS token for authentication.
        container (str): The name of the container.
        blob_directory (str): The directory in the blob storage.
        file_name (str): The name of the file to be uploaded.
        content (str): The content to be uploaded.

    Returns:
        str: The full URL for the uploaded blob.
    """
    blob_service = BlobServiceClient(
        account_url=f"https://{storage_account}.blob.core.windows.net",
        credential=token,
    )
    blob_path = f"{blob_directory}/{file_name}"
    blob_client = blob_service.get_blob_client(
        container=container, blob=blob_path
    )

    logging.info("Uploading CSV to Azure Blob Storage: %s", blob_path)
    try:
        blob_client.upload_blob(content, overwrite=True)
    except Exception as e:
        logging.error("Failed to upload blob: %s", e)
        raise
    logging.info("Upload successful.")

    # Construct and return the full URL for the uploaded blob
    glossary_url = (f"https://{storage_account}.blob.core.windows.net/"
                    f"{container}/{blob_path}?{token}")
    return glossary_url
