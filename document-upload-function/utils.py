"""
Utility functions for handling file uploads and logging in an Azure Functions app.

Functions:
- extract_request_data: Extracts data from the HTTP request.
- get_azure_storage_info: Retrieves Azure storage account information.
- log_file_upload: Logs file upload details to the database.
- save_file_temporarily: Saves the uploaded file to a temporary location.
- upload_to_blob_storage: Uploads the file to Azure Blob Storage.
- generate_blob_url: Generates a URL for the uploaded blob.
- clean_up_temporary_file: Removes the temporary file.
"""

import logging
import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from database_handler import DatabaseHandler

# Azure Blob Storage connection string
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
UPLOAD_DIRECTORY = "landing-zone"

# Log environment variables to check if they exist
logging.debug("AZURE_CONNECTION_STRING: %s", '****' if AZURE_CONNECTION_STRING else None)

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)


def extract_request_data(req):
    """
    Extract data from the HTTP request.

    Args:
        req (func.HttpRequest): The HTTP request object.

    Returns:
        tuple: Extracted file, from_lang, to_lang, exclusion_text, and uploaded_by.
    """
    file = req.files.get("file")
    logging.info("File: %s", file.filename if file else "None")

    from_lang = req.form.get("fromLang")
    logging.info("From Language: %s", from_lang)

    to_lang = req.form.get("toLang")
    logging.info("To Language: %s", to_lang)
    exclusion_text = req.form.get("exclusion_text")
    logging.info("Exclusion Text: %s", exclusion_text)

    uploaded_by = req.form.get("uploaded_by", "unknown")
    logging.info("Uploaded By: %s", uploaded_by)

    prompt_id = req.form.get("prompt_id")
    logging.info("Prompt ID: %s", prompt_id)

    return file, from_lang, to_lang, exclusion_text, uploaded_by, prompt_id


def get_azure_storage_info():
    """
    Retrieve Azure storage account information.

    Returns:
        tuple: Azure storage account, SAS token, and container name.
    """
    azure_storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
    sas_token = os.getenv("SAS_TOKEN")
    container_name = os.getenv("CONTAINER_NAME")
    logging.info("SAS_TOKEN: %s", sas_token)
    logging.info("AZURE_STORAGE_ACCOUNT: %s", azure_storage_account)
    logging.info("CONTAINER_NAME: %s", container_name)
    return azure_storage_account, sas_token, container_name


def log_file_upload(
    new_file_name,
    landing_zone_path,
    file,
    uploaded_by,
    from_lang,
    to_lang,
    exclusion_text,
    prompt_id,
    status="done",
):
    """
    Log file upload details to the database.

    Args:
        new_file_name (str): The new file name.
        landing_zone_path (str): The path to the landing zone.
        file (werkzeug.datastructures.FileStorage): The uploaded file.
        uploaded_by (str): The user who uploaded the file.
        from_lang (str): The source language.
        to_lang (str): The target language.
        exclusion_text (str): The exclusion text.
        status (str, optional): The upload status. Defaults to "done".
    """
    logging.info("Inserting file = %s record into the database", new_file_name)
    file_type = os.path.splitext(file.filename)[1][1:].lower()
    upload_date = datetime.now().date()
    upload_datetime = datetime.now()
    database_handler = DatabaseHandler()
    database_handler.insert_file_record(
        new_file_name,
        landing_zone_path,
        file_type,
        upload_date,
        upload_datetime,
        status,
        uploaded_by,
        from_lang,
        to_lang,
        exclusion_text,
        prompt_id
    )
    logging.info("File %s record inserted successfully", new_file_name)


def save_file_temporarily(file, database_handler):
    """
    Save the uploaded file to a temporary location.

    Args:
        file (werkzeug.datastructures.FileStorage): The uploaded file.
        database_handler (DatabaseHandler): The database handler.

    Returns:
        tuple: The new file name and new file path.
    """
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.stream.read())
    logging.info("Starting upload for file: %s", file_path)

    if not (file_path.lower().endswith(".pdf") or file_path.lower().endswith(".docx")):
        raise ValueError("Only PDF and DOCX files are allowed")

    new_file_name = database_handler.check_file_name(file.filename)
    new_file_path = f"/tmp/{new_file_name}"
    os.rename(file_path, new_file_path)
    logging.info("New file name: %s", new_file_name)
    return new_file_name, new_file_path


def upload_to_blob_storage(new_file_path, new_file_name, container_name):
    """
    Upload the file to Azure Blob Storage.

    Args:
        new_file_path (str): The path to the new file.
        new_file_name (str): The new file name.
    """
    logging.debug("Getting container client")
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob=f"{UPLOAD_DIRECTORY}/{new_file_name}")
    logging.debug("Uploading file to blob")

    with open(new_file_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)

    logging.info("File %s uploaded successfully", new_file_name)


def generate_blob_url(azure_storage_account, container_name, new_file_name, sas_token):
    """
    Generate a URL for the uploaded blob.

    Args:
        azure_storage_account (str): The Azure storage account.
        container_name (str): The container name.
        new_file_name (str): The new file name.
        sas_token (str): The SAS token.

    Returns:
        str: The generated blob URL.
    """
    return (
        f"https://{azure_storage_account}.blob.core.windows.net/"
        f"{container_name}/{UPLOAD_DIRECTORY}/{new_file_name}?{sas_token}"
    )


def clean_up_temporary_file(file_path):
    """
    Remove the temporary file.

    Args:
        file_path (str): The path to the temporary file.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
