"""
Module for handling blob operations including validating the existence of a blob URL
and uploading content to Azure Blob Storage.
"""

import logging
import requests
from azure.storage.blob import BlobServiceClient
from environment_variables import AZURE_STORAGE_ACCOUNT, CONTAINER_NAME, SAS_TOKEN


def validate_blob_url(blob_url):
    """
    Validates the existence of the source URL.

    Input:
    - blob_url: URL of the blob.

    Output:
    - True if the file exists, False otherwise.
    """
    logging.info("Validating source URL: %s", blob_url)
    response = requests.head(blob_url, timeout=10)
    if response.status_code == 200:
        logging.info("Source file exists")
        return True
    logging.error("Source file does not exist. Status code: %s", response.status_code)
    return False


def upload_to_blob(blob_directory, file_name, content):
    """
    Uploads content to Azure Blob Storage.

    Input:
    - blob_directory: Directory in the blob storage.
    - file_name: Name of the file to be uploaded.
    - content: Content of the file to be uploaded.

    Output:
    - URL of the uploaded file.
    """
    blob_service_client = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=SAS_TOKEN,
    )
    blob_path = f"{blob_directory}/{file_name}"
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME, blob=blob_path
    )

    logging.info("Uploading file to Azure Blob Storage: %s", blob_path)
    try:
        blob_client.upload_blob(content, overwrite=True)
    except Exception as e:
        logging.error("Failed to upload blob: %s", e)
        raise
    logging.info("Upload successful.")

    # Construct and return the full URL for the uploaded blob
    file_url = (
        f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/"
        f"{CONTAINER_NAME}/{blob_path}?{SAS_TOKEN}"
    )
    return file_url
 